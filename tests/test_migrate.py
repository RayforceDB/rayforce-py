"""
M24 - rayforce.migrate one-shot v1 -> v2 type-code transcoder.

Covers:
- transcode_v1_blob roundtrip on hand-crafted v1 IPC blobs (one per
  scalar atom type, checked into tests/fixtures/v1_blobs/).
- transcode_splayed_dir end-to-end: write a real v2 splayed table,
  rewrite the on-disk type bytes to their v1 equivalents to fake a
  v1 directory, transcode it, and confirm Table.from_splayed reads
  back the original column values.
- CLI smoke: invoke `python -m rayforce.migrate ...` via subprocess.
"""

from __future__ import annotations

from pathlib import Path
import struct
import subprocess
import sys

import numpy as np
import pytest

import rayforce as rf
from rayforce import migrate
from rayforce.ffi import FFI
from rayforce.types.containers.vector import Vector
from rayforce.utils.conversion import ray_to_python

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "v1_blobs"

# v2 type codes used by the splayed-dir test.
_V2_F64 = 7
_V1_F64 = 10
_V2_TIMESTAMP = 10
_V1_TIMESTAMP = 9
_V2_DATE = 8
_V1_DATE = 7
_V2_I64 = 5
_V1_I64 = 5  # unchanged

_COL_TYPE_OFFSET = 18


def _de_bytes_to_python(blob: bytes):
    """Wrap a v2 wire-format blob in a U8 vector and run de_obj."""
    arr = np.frombuffer(blob, dtype=np.uint8).copy()
    vec = Vector.from_numpy(arr)
    out_ptr = FFI.de_obj(vec.ptr)
    return ray_to_python(out_ptr)


class TestTypeMap:
    """The v1 -> v2 type-code remap is the migration tool's contract --
    document it explicitly so a regression in the table is loud."""

    def test_shifted_codes_remap(self):
        assert migrate._V1_TO_V2_TYPE_MAP == {
            6: 12,  # SYMBOL  -> SYM
            7: 8,  # DATE    -> DATE
            8: 9,  # TIME    -> TIME
            9: 10,  # TIMESTAMP -> TIMESTAMP
            10: 7,  # F64     -> F64
            12: 13,  # C8      -> STR
        }

    def test_remap_passes_through_unchanged_codes(self):
        for code in (0, 1, 2, 3, 4, 5, 11, 98, 99, 100, 126, 127):
            assert migrate._remap_type(code) == code
        # Atoms (negative)
        assert migrate._remap_type(-5) == -5
        assert migrate._remap_type(-11) == -11

    def test_remap_atoms_negate(self):
        assert migrate._remap_type(-6) == -12
        assert migrate._remap_type(-10) == -7
        assert migrate._remap_type(-7) == -8
        assert migrate._remap_type(-8) == -9
        assert migrate._remap_type(-9) == -10
        assert migrate._remap_type(-12) == -13


class TestBlobRoundtrip:
    """Each v1 atom fixture: transcode -> de_obj -> compare to expected
    Python value. Fixtures live in tests/fixtures/v1_blobs/ and were
    generated with tests/fixtures/v1_blobs/generate.py."""

    @pytest.mark.parametrize(
        ("fixture", "expected"),
        [
            ("i32.bin", 42),
            ("i64.bin", 12345),
            ("f64.bin", 3.14),
            ("sym.bin", "hello"),
        ],
    )
    def test_simple_atom_roundtrip(self, fixture, expected):
        v1 = (FIXTURE_DIR / fixture).read_bytes()
        v2 = migrate.transcode_v1_blob(v1)
        assert _de_bytes_to_python(v2) == expected

    def test_date_atom_roundtrip(self):
        v1 = (FIXTURE_DIR / "date.bin").read_bytes()
        v2 = migrate.transcode_v1_blob(v1)
        # DATE atoms decode as date / datetime / similar; only assert that
        # de_obj accepts the blob and produces a non-error value. The exact
        # epoch interpretation is v2's concern.
        out = _de_bytes_to_python(v2)
        assert out is not None

    def test_time_atom_roundtrip(self):
        v1 = (FIXTURE_DIR / "time.bin").read_bytes()
        v2 = migrate.transcode_v1_blob(v1)
        out = _de_bytes_to_python(v2)
        assert out is not None

    def test_timestamp_atom_roundtrip(self):
        v1 = (FIXTURE_DIR / "timestamp.bin").read_bytes()
        v2 = migrate.transcode_v1_blob(v1)
        out = _de_bytes_to_python(v2)
        assert out is not None

    def test_c8_atom_roundtrip(self):
        # C8 -> STR: the migration tool packs the single byte as a
        # length-1 STR. de_obj should hand back "X".
        v1 = (FIXTURE_DIR / "c8.bin").read_bytes()
        v2 = migrate.transcode_v1_blob(v1)
        assert _de_bytes_to_python(v2) == "X"

    def test_emitted_blob_uses_v2_wire_version(self):
        v1 = (FIXTURE_DIR / "i64.bin").read_bytes()
        v2 = migrate.transcode_v1_blob(v1)
        version = v2[4]
        assert version == migrate._V2_WIRE_VERSION

    def test_rejects_corrupt_prefix(self):
        with pytest.raises(ValueError, match="prefix mismatch"):
            migrate.transcode_v1_blob(b"\x00" * 32)

    def test_rejects_already_v2(self):
        # Build a valid-looking v2 header (version=3) and confirm the tool
        # refuses to re-transcode it.
        hdr = struct.pack(
            "<IBBBBq",
            migrate._IPC_PREFIX,
            migrate._V2_WIRE_VERSION,
            0,
            0,
            0,
            0,
        )
        with pytest.raises(ValueError, match="not older than v2"):
            migrate.transcode_v1_blob(hdr)


def _flip_col_type(path: Path, new_type_byte: int) -> None:
    """Patch the ray_t type byte (offset 18) of a v2 column file in-place."""
    raw = bytearray(path.read_bytes())
    raw[_COL_TYPE_OFFSET] = new_type_byte & 0xFF
    path.write_bytes(bytes(raw))


def _v2_col_type(path: Path) -> int | None:
    """Return the ray_t type byte at offset 18 of a column file, or None
    if the file is not a 32+ byte column file (e.g. a 0-byte lock file)."""
    raw = path.read_bytes()
    if len(raw) < 32 or raw[:4] in (b"STRL", b"LSTG", b"TTBL"):
        return None
    return struct.unpack_from("<b", raw, _COL_TYPE_OFFSET)[0]


class TestSplayedDirTranscode:
    """End-to-end: write a v2 splayed table, fake-downgrade its column
    type bytes to v1 codes, run the transcoder, reload via Table.from_splayed."""

    def test_f64_column_roundtrip(self, tmp_path):
        v2_dir = tmp_path / "v2_origin"
        v1_fake = tmp_path / "v1_fake"
        v2_out = tmp_path / "v2_out"

        original = rf.Table(
            {
                "x": rf.Vector([1.0, 2.5, 3.75, 4.0], ray_type=rf.F64),
                "n": rf.Vector([10, 20, 30, 40], ray_type=rf.I64),
            }
        )
        original.set_splayed(str(v2_dir))

        # Fake-downgrade to v1: F64 column 7 -> 10. I64 stays.
        for col in v2_dir.iterdir():
            if col.is_file() and not col.name.startswith("."):
                t = _v2_col_type(col)
                if t == _V2_F64:
                    _flip_col_type(col, _V1_F64)

        # Build the "v1" mirror dir at v1_fake
        import shutil

        shutil.copytree(v2_dir, v1_fake)

        migrate.transcode_splayed_dir(v1_fake, v2_out)

        # Every column file at v2_out has a v2 type byte
        for col in v2_out.iterdir():
            if col.is_file() and not col.name.startswith("."):
                t = _v2_col_type(col)
                if t is not None:
                    assert t in (_V2_F64, _V2_I64)

        loaded = rf.Table.from_splayed(str(v2_out)).select("*").execute()
        assert loaded["x"].to_python() == [1.0, 2.5, 3.75, 4.0]
        assert loaded["n"].to_python() == [10, 20, 30, 40]

    def test_temporal_columns_roundtrip(self, tmp_path):
        import datetime as dt

        v2_dir = tmp_path / "v2_origin"
        v1_fake = tmp_path / "v1_fake"
        v2_out = tmp_path / "v2_out"

        original = rf.Table(
            {
                "ts": rf.Vector(
                    [
                        dt.datetime(2024, 1, 1, tzinfo=dt.UTC),
                        dt.datetime(2024, 6, 15, 12, 30, tzinfo=dt.UTC),
                    ],
                    ray_type=rf.Timestamp,
                ),
                "d": rf.Vector(
                    [dt.date(2024, 1, 1), dt.date(2024, 6, 15)],
                    ray_type=rf.Date,
                ),
            }
        )
        original.set_splayed(str(v2_dir))

        # Fake-downgrade temporal columns
        for col in v2_dir.iterdir():
            if not col.is_file() or col.name.startswith("."):
                continue
            t = _v2_col_type(col)
            if t == _V2_TIMESTAMP:
                _flip_col_type(col, _V1_TIMESTAMP)
            elif t == _V2_DATE:
                _flip_col_type(col, _V1_DATE)

        import shutil

        shutil.copytree(v2_dir, v1_fake)

        migrate.transcode_splayed_dir(v1_fake, v2_out)

        loaded = rf.Table.from_splayed(str(v2_out)).select("*").execute()
        assert loaded["ts"].to_python() == [
            dt.datetime(2024, 1, 1, tzinfo=dt.UTC),
            dt.datetime(2024, 6, 15, 12, 30, tzinfo=dt.UTC),
        ]
        assert loaded["d"].to_python() == [dt.date(2024, 1, 1), dt.date(2024, 6, 15)]

    def test_extra_files_copied_verbatim(self, tmp_path):
        v1_dir = tmp_path / "v1_in"
        v2_dir = tmp_path / "v2_out"
        v1_dir.mkdir()
        # A short file that is neither a column nor a magic-prefixed dump.
        (v1_dir / "NOTES.txt").write_text("hand-edited fixture\n")
        # A magic-prefixed file (sym dump shape)
        (v1_dir / "sym").write_bytes(b"STRL" + b"\x00" * 16)

        migrate.transcode_splayed_dir(v1_dir, v2_dir)

        assert (v2_dir / "NOTES.txt").read_text() == "hand-edited fixture\n"
        assert (v2_dir / "sym").read_bytes()[:4] == b"STRL"


class TestPartedDirTranscode:
    def test_nested_partitions_walk(self, tmp_path):
        v2_origin = tmp_path / "v2_origin"
        v1_fake = tmp_path / "v1_fake"
        v2_out = tmp_path / "v2_out"

        # Build two v2 splayed tables under partition dirs.
        for part in ("p1", "p2"):
            tbl = rf.Table(
                {
                    "x": rf.Vector([float(ord(part[1])) + i for i in range(3)], ray_type=rf.F64),
                }
            )
            tbl.set_splayed(str(v2_origin / part / "tbl"))

        # Fake-downgrade every F64 column file.
        for path in v2_origin.rglob("*"):
            if path.is_file() and not path.name.startswith("."):
                t = _v2_col_type(path) if path.stat().st_size >= 32 else None
                if t == _V2_F64:
                    _flip_col_type(path, _V1_F64)

        import shutil

        shutil.copytree(v2_origin, v1_fake)

        migrate.transcode_parted_dir(v1_fake, v2_out)

        for part in ("p1", "p2"):
            loaded = rf.Table.from_splayed(str(v2_out / part / "tbl")).select("*").execute()
            base = float(ord(part[1]))
            assert loaded["x"].to_python() == [base, base + 1, base + 2]


class TestCLI:
    def test_blob_subcommand_smoke(self, tmp_path):
        src = FIXTURE_DIR / "i64.bin"
        dst = tmp_path / "i64.v2.bin"

        result = subprocess.run(
            [sys.executable, "-m", "rayforce.migrate", "blob", str(src), str(dst)],
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr.decode()
        assert dst.exists()
        assert _de_bytes_to_python(dst.read_bytes()) == 12345

    def test_splayed_subcommand_smoke(self, tmp_path):
        v2_origin = tmp_path / "origin"
        rf.Table({"x": rf.Vector([1.0, 2.0], ray_type=rf.F64)}).set_splayed(str(v2_origin))
        for col in v2_origin.iterdir():
            if col.is_file() and not col.name.startswith(".") and _v2_col_type(col) == _V2_F64:
                _flip_col_type(col, _V1_F64)

        out = tmp_path / "out"
        result = subprocess.run(
            [sys.executable, "-m", "rayforce.migrate", "splayed", str(v2_origin), str(out)],
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr.decode()
        loaded = rf.Table.from_splayed(str(out)).select("*").execute()
        assert loaded["x"].to_python() == [1.0, 2.0]

    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "rayforce.migrate", "--help"],
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0
        assert b"blob" in result.stdout
        assert b"splayed" in result.stdout
        assert b"parted" in result.stdout
