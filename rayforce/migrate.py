"""
One-shot v1 -> v2 type-code transcoder for persisted Rayforce data.

Use this if you have data persisted from rayforce v1 (which used a
different type-code assignment than v2). It rewrites:

- IPC-headered serialized blobs (e.g. the output of v1 `ser_obj` saved
  to a file or held in memory).
- Splayed table directories (per-column files + `.d` schema file).
- Parted directories (a parent directory holding per-partition
  sub-directories, each itself a splayed table).

The shifted/removed type codes that this tool remaps:

    v1 SYMBOL=6   -> v2 SYM=12
    v1 DATE=7     -> v2 DATE=8
    v1 TIME=8     -> v2 TIME=9
    v1 TIMESTAMP=9-> v2 TIMESTAMP=10
    v1 F64=10     -> v2 F64=7
    v1 C8=12      -> v2 STR=13

Codes that did not shift (B8=1, U8=2, I16=3, I32=4, I64=5, GUID=11,
LIST=0, TABLE=98, DICT=99, LAMBDA=100, ...) pass through unchanged.

CLI:

    python -m rayforce.migrate blob    <src.bin>    <dst.bin>
    python -m rayforce.migrate splayed <src_dir>    <dst_dir>
    python -m rayforce.migrate parted  <src_dir>    <dst_dir>

The tool is intentionally narrow: it understands the wire/disk shape
that v2 reads, and the (slightly different) shape that v1 wrote. It is
not a general "rewrite arbitrary v1 binary" facility -- features that
v2 dropped (TYPE_ENUM, TYPE_PARTEDLIST, etc.) raise NotImplementedError.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import struct
import sys

# ---------------------------------------------------------------------------
# Type codes (kept here so the tool can run without importing _rayforce_c).
# ---------------------------------------------------------------------------

_V2_RAY_LIST = 0
_V2_RAY_BOOL = 1
_V2_RAY_U8 = 2
_V2_RAY_I16 = 3
_V2_RAY_I32 = 4
_V2_RAY_I64 = 5
_V2_RAY_F32 = 6
_V2_RAY_F64 = 7
_V2_RAY_DATE = 8
_V2_RAY_TIME = 9
_V2_RAY_TIMESTAMP = 10
_V2_RAY_GUID = 11
_V2_RAY_SYM = 12
_V2_RAY_STR = 13
_V2_RAY_TABLE = 98
_V2_RAY_DICT = 99
_V2_RAY_LAMBDA = 100
_V2_RAY_NULL = 126
_V2_RAY_ERROR = 127
_V2_SERDE_NULL = 126

_V1_TO_V2_TYPE_MAP: dict[int, int] = {
    6: _V2_RAY_SYM,
    7: _V2_RAY_DATE,
    8: _V2_RAY_TIME,
    9: _V2_RAY_TIMESTAMP,
    10: _V2_RAY_F64,
    12: _V2_RAY_STR,
}

# v1 vector element sizes (bytes per element, on the wire). v1 SYMBOL
# vectors stored 8-byte int64 indices into the global sym table.
_V1_VEC_ELEM_SIZE: dict[int, int] = {
    _V2_RAY_BOOL: 1,
    _V2_RAY_U8: 1,
    _V2_RAY_I16: 2,
    _V2_RAY_I32: 4,
    _V2_RAY_I64: 8,
    6: 8,
    7: 4,
    8: 4,
    9: 8,
    10: 8,
    _V2_RAY_GUID: 16,
    12: 1,
}

# v1 atom value sizes (excluding the type byte; v1 had no flags byte).
_V1_ATOM_FIXED_SIZE: dict[int, int] = {
    _V2_RAY_BOOL: 1,
    _V2_RAY_U8: 1,
    _V2_RAY_I16: 2,
    _V2_RAY_I32: 4,
    _V2_RAY_I64: 8,
    7: 4,
    8: 4,
    9: 8,
    10: 8,
    _V2_RAY_GUID: 16,
    12: 1,
}

# IPC header layout (16 bytes; identical between v1 and v2 -- only the
# wire-version field differs).
_IPC_PREFIX = 0xCEFADEFA
_IPC_HDR_FMT = "<IBBBBq"
_IPC_HDR_SIZE = struct.calcsize(_IPC_HDR_FMT)
_V2_WIRE_VERSION = 3

# Attribute bit masks (ray_t.attrs). Mirrors src/mem/heap.h.
_ATTR_HAS_NULLS = 0x40
_ATTR_NULLMAP_EXT = 0x20
_ATTR_DICT = 0x02
_SYM_W_MASK = 0x03
_SYM_W64 = 0x03

# Column-file header layout: 32-byte ray_t prefix.
#   bytes 0..15  nullmap (or zeroed)
#   byte 16      mmod
#   byte 17      order
#   byte 18      type
#   byte 19      attrs
#   bytes 20..23 rc
#   bytes 24..31 union (vec len for vector files)
_COL_TYPE_OFFSET = 18
_COL_ATTRS_OFFSET = 19
_COL_LEN_OFFSET = 24
_COL_HDR_SIZE = 32


def _remap_type(v1_code: int) -> int:
    """Map a v1 type code to its v2 equivalent.

    Positive codes (vectors / compound objects) and the static singletons
    (RAY_NULL, RAY_ERROR, RAY_SERDE_NULL) pass through unchanged unless
    listed in `_V1_TO_V2_TYPE_MAP`. Negative codes (atoms) are mirrored:
    `-6 -> -12`, etc.
    """
    abs_code = abs(v1_code)
    new_abs = _V1_TO_V2_TYPE_MAP.get(abs_code, abs_code)
    return -new_abs if v1_code < 0 else new_abs


# ---------------------------------------------------------------------------
# Wire-format walk
# ---------------------------------------------------------------------------


class _Reader:
    __slots__ = ("buf", "pos")

    def __init__(self, buf: bytes) -> None:
        self.buf = buf
        self.pos = 0

    def read(self, n: int) -> bytes:
        if self.pos + n > len(self.buf):
            raise ValueError(
                f"v1 blob truncated at offset {self.pos}: need {n} bytes, "
                f"only {len(self.buf) - self.pos} remaining",
            )
        out = self.buf[self.pos : self.pos + n]
        self.pos += n
        return out

    def read_i8(self) -> int:
        return struct.unpack_from("<b", self.read(1))[0]

    def read_u8(self) -> int:
        return self.read(1)[0]

    def read_i64(self) -> int:
        return struct.unpack_from("<q", self.read(8))[0]

    def read_cstring(self) -> bytes:
        end = self.buf.find(b"\x00", self.pos)
        if end < 0:
            raise ValueError(f"unterminated v1 string at offset {self.pos}")
        out = self.buf[self.pos : end]
        self.pos = end + 1
        return out


def _emit_atom(out: bytearray, v2_type: int, value_bytes: bytes) -> None:
    out.append(v2_type & 0xFF)
    out.append(0)  # v3 atom flags byte (typed-null bit stays 0 for migrated v1 data)
    out.extend(value_bytes)


def _transcode_node(reader: _Reader, out: bytearray) -> None:
    """Read one v1-encoded ray_t off `reader` and emit its v2 equivalent."""

    type_byte = reader.read_i8()

    # SERDE_NULL marker (used in v2 for None args; v1 may emit it too).
    if (type_byte & 0xFF) == _V2_SERDE_NULL:
        out.append(_V2_SERDE_NULL)
        return

    if type_byte == _V2_RAY_ERROR:
        # ERROR record: 7 bytes of sdata + null terminator (v2 keeps this layout).
        out.append(_V2_RAY_ERROR)
        out.extend(reader.read(8))
        return

    # ---- Atoms (negative type) -------------------------------------------------
    if type_byte < 0:
        v1_abs = -type_byte
        v2_type = _remap_type(type_byte)

        if v1_abs == 12:  # C8 atom -> v2 STR atom
            char = reader.read(1)
            _emit_atom(out, v2_type, struct.pack("<q", 1) + char)
            return

        if v1_abs == 6:  # SYMBOL atom: null-terminated name (interned on decode)
            name = reader.read_cstring()
            _emit_atom(out, v2_type, name + b"\x00")
            return

        size = _V1_ATOM_FIXED_SIZE.get(v1_abs)
        if size is None:
            raise NotImplementedError(
                f"unsupported v1 atom type code {type_byte} at offset {reader.pos - 1}",
            )
        _emit_atom(out, v2_type, reader.read(size))
        return

    # ---- Compound ------------------------------------------------------------
    if type_byte == _V2_RAY_LIST:
        attrs = reader.read_u8()
        length = reader.read_i64()
        out.append(_V2_RAY_LIST)
        out.append(attrs)
        out.extend(struct.pack("<q", length))
        for _ in range(length):
            _transcode_node(reader, out)
        return

    if type_byte == _V2_RAY_TABLE:
        attrs = reader.read_u8()
        out.append(_V2_RAY_TABLE)
        out.append(attrs)
        # schema (I64 vec) + columns (LIST), serialized recursively.
        _transcode_node(reader, out)
        _transcode_node(reader, out)
        return

    if type_byte == _V2_RAY_DICT:
        attrs = reader.read_u8()
        out.append(_V2_RAY_DICT)
        out.append(attrs)
        _transcode_node(reader, out)  # keys
        _transcode_node(reader, out)  # values
        return

    # ---- Vectors -------------------------------------------------------------
    if type_byte == 12:  # C8 vector -> v2 STR vector.  Wire layout differs
        # significantly: v2 emits per-element 8-byte length + raw bytes plus
        # an optional null bitmap. Faithful conversion would require unpacking
        # the v1 char buffer into N length-1 STR entries; the migration tool
        # does not currently emit this shape -- splayed C8 columns are also
        # unsupported. Loop above the call site to re-encode if needed.
        raise NotImplementedError(
            "C8 vector -> STR vector transcoding is not implemented (M24 scope: "
            "atom-only). Re-emit the column from source data instead.",
        )

    v1_abs = type_byte
    if v1_abs not in _V1_VEC_ELEM_SIZE and v1_abs != 6:
        raise NotImplementedError(
            f"unsupported v1 vector type code {type_byte} at offset {reader.pos - 1}",
        )

    attrs = reader.read_u8()
    length = reader.read_i64()

    if v1_abs == 6:
        # SYM vector wire: each element is a null-terminated string. The
        # v2 wire shape is identical, so we just remap the type byte.
        new_attrs = attrs
        out.append(_V2_RAY_SYM)
        out.append(new_attrs)
        out.extend(struct.pack("<q", length))
        for _ in range(length):
            sym_bytes = reader.read_cstring()
            out.extend(sym_bytes)
            out.append(0)
        if attrs & _ATTR_HAS_NULLS:
            out.extend(reader.read((length + 7) // 8))
        return

    # Fixed-size element vector (BOOL/U8/I16/I32/I64/F64/DATE/TIME/TIMESTAMP/GUID).
    elem_size = _V1_VEC_ELEM_SIZE[v1_abs]
    data_size = length * elem_size
    data = reader.read(data_size)
    nullmap = b""
    if attrs & _ATTR_HAS_NULLS:
        nullmap = reader.read((length + 7) // 8)

    v2_type = _remap_type(type_byte)
    out.append(v2_type & 0xFF)
    out.append(attrs)
    out.extend(struct.pack("<q", length))
    out.extend(data)
    out.extend(nullmap)


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------


def transcode_v1_blob(data: bytes) -> bytes:
    """Rewrite a v1 IPC-headered serialized blob into v2 wire format.

    Accepts any v1 wire version that uses the legacy atom layout
    (type+value, no flags byte). Emits a v2 wire-version-3 blob ready
    for `de_obj`.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"transcode_v1_blob: expected bytes, got {type(data).__name__}")
    if len(data) < _IPC_HDR_SIZE:
        raise ValueError(f"v1 blob too small ({len(data)} bytes)")

    prefix, version, flags, endian, msgtype, size = struct.unpack_from(_IPC_HDR_FMT, data, 0)
    if prefix != _IPC_PREFIX:
        raise ValueError(f"v1 blob prefix mismatch: got {prefix:#010x}, want {_IPC_PREFIX:#010x}")
    if endian != 0:
        raise NotImplementedError("only little-endian v1 blobs are supported")
    if version >= _V2_WIRE_VERSION:
        raise ValueError(
            f"v1 blob wire version is {version}, which is not older than v2's "
            f"{_V2_WIRE_VERSION} -- nothing to transcode",
        )
    if size + _IPC_HDR_SIZE != len(data):
        raise ValueError(
            f"v1 blob length {len(data)} disagrees with header payload size {size}",
        )

    reader = _Reader(data[_IPC_HDR_SIZE:])
    payload = bytearray()
    _transcode_node(reader, payload)
    if reader.pos != len(reader.buf):
        raise ValueError(
            f"trailing {len(reader.buf) - reader.pos} bytes after transcoding v1 blob",
        )

    out_hdr = struct.pack(
        _IPC_HDR_FMT, _IPC_PREFIX, _V2_WIRE_VERSION, flags, endian, msgtype, len(payload)
    )
    return out_hdr + bytes(payload)


def _transcode_col_file(src: Path, dst: Path) -> None:
    """Patch the type byte in a v1 column file and copy to dst.

    Column files are 32-byte ray_t header + raw data + optional ext
    nullmap. v1 and v2 share the on-disk layout for fixed-size scalar
    columns; only the type code shifts. SYM columns get RAY_SYM_W64
    forced into the attrs nibble so v2 reads them as int64 indices
    (matching v1's storage).
    """
    raw = src.read_bytes()
    if len(raw) < _COL_HDR_SIZE:
        raise ValueError(f"{src}: column file too short ({len(raw)} bytes)")

    v1_type = struct.unpack_from("<b", raw, _COL_TYPE_OFFSET)[0]
    if v1_type == 12:
        raise NotImplementedError(
            f"{src}: C8 column files cannot be transcoded by this tool "
            "(byte-per-element layout differs from v2 STR's 16-byte ray_str_t).",
        )

    v2_type = _remap_type(v1_type)
    buf = bytearray(raw)
    buf[_COL_TYPE_OFFSET] = v2_type & 0xFF

    if v1_type == 6:  # SYM vector: enforce W64 width on attrs.
        attrs = buf[_COL_ATTRS_OFFSET]
        buf[_COL_ATTRS_OFFSET] = (attrs & ~_SYM_W_MASK) | _SYM_W64

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(bytes(buf))


def transcode_splayed_dir(src: Path, dst: Path) -> None:
    """Transcode every column file in a v1 splayed-table directory."""
    src = Path(src)
    dst = Path(dst)
    if not src.is_dir():
        raise ValueError(f"transcode_splayed_dir: {src} is not a directory")
    dst.mkdir(parents=True, exist_ok=True)

    for entry in sorted(src.iterdir()):
        target = dst / entry.name
        if entry.is_dir():
            # Defensive: real splayed dirs are flat, but copy nested data
            # just in case (nested sym files, hidden bookkeeping).
            shutil.copytree(entry, target, dirs_exist_ok=True)
            continue
        if not entry.is_file():
            continue
        head = entry.read_bytes()[:_COL_HDR_SIZE]
        # Magic-prefixed files (sym table dumps, generic LIST/TABLE columns)
        # have their own framing and must be copied verbatim. Everything else
        # is treated as a 32-byte ray_t-headered column file.
        if len(head) >= 4 and head[:4] in (b"STRL", b"LSTG", b"TTBL"):
            shutil.copy2(entry, target)
            continue
        if len(head) == _COL_HDR_SIZE:
            _transcode_col_file(entry, target)
        else:
            shutil.copy2(entry, target)


def transcode_parted_dir(src: Path, dst: Path) -> None:
    """Transcode a v1 parted-table directory.

    Parted layout: <root>/<partition>/<table>/<column>. Each partition
    sub-directory is itself a splayed table directory. Non-directory
    entries at the root (e.g. a `sym` file) are copied verbatim.
    """
    src = Path(src)
    dst = Path(dst)
    if not src.is_dir():
        raise ValueError(f"transcode_parted_dir: {src} is not a directory")
    dst.mkdir(parents=True, exist_ok=True)

    for entry in sorted(src.iterdir()):
        target = dst / entry.name
        if entry.is_dir():
            # A partition dir may directly contain column files (legacy
            # single-table parted layout) or one nested table dir per
            # logical table. Treat each first-level sub-dir as a splayed
            # dir; recurse into nested table dirs.
            target.mkdir(parents=True, exist_ok=True)
            for sub in sorted(entry.iterdir()):
                if sub.is_dir():
                    transcode_splayed_dir(sub, target / sub.name)
                else:
                    shutil.copy2(sub, target / sub.name)
            # If the partition dir contained no sub-dirs, also try the
            # splayed shape (rare but keeps single-table parted dirs working).
            if not any(p.is_dir() for p in entry.iterdir()):
                transcode_splayed_dir(entry, target)
        else:
            shutil.copy2(entry, target)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m rayforce.migrate",
        description="Transcode v1 Rayforce data into v2 type codes.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, helptext in (
        ("blob", "Transcode an IPC-headered serialized blob (file)."),
        ("splayed", "Transcode a splayed table directory."),
        ("parted", "Transcode a parted table directory."),
    ):
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("src", type=Path)
        sp.add_argument("dst", type=Path)

    args = parser.parse_args(argv)

    if args.cmd == "blob":
        data = args.src.read_bytes()
        out = transcode_v1_blob(data)
        args.dst.parent.mkdir(parents=True, exist_ok=True)
        args.dst.write_bytes(out)
    elif args.cmd == "splayed":
        transcode_splayed_dir(args.src, args.dst)
    elif args.cmd == "parted":
        transcode_parted_dir(args.src, args.dst)
    else:  # pragma: no cover -- argparse already rejects this
        parser.error(f"unknown command: {args.cmd}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli(sys.argv[1:]))
