"""Regenerate the v1 wire-format fixtures used by tests/test_migrate.py.

Each fixture is `<16-byte IPC header><1-byte v1 type><value bytes>`.
v1 atoms carried no flags byte after the type tag (v2 wire version 3
added one). See README.md in this directory for the value table.

Idempotent; just run `python tests/fixtures/v1_blobs/generate.py`.
"""

from __future__ import annotations

from pathlib import Path
import struct

_PREFIX = 0xCEFADEFA
_HDR_FMT = "<IBBBBq"  # prefix u32, version u8, flags u8, endian u8, msgtype u8, size i64
_V1_VERSION = 2


def _v1_blob(type_byte: int, value: bytes) -> bytes:
    payload = struct.pack("<b", type_byte) + value
    return struct.pack(_HDR_FMT, _PREFIX, _V1_VERSION, 0, 0, 0, len(payload)) + payload


FIXTURES: dict[str, bytes] = {
    "i32.bin": _v1_blob(-4, struct.pack("<i", 42)),
    "i64.bin": _v1_blob(-5, struct.pack("<q", 12345)),
    "f64.bin": _v1_blob(-10, struct.pack("<d", 3.14)),
    "date.bin": _v1_blob(-7, struct.pack("<i", 8000)),
    "time.bin": _v1_blob(-8, struct.pack("<i", 1234)),
    "timestamp.bin": _v1_blob(-9, struct.pack("<q", 1700000000000000000)),
    "sym.bin": _v1_blob(-6, b"hello\x00"),
    "c8.bin": _v1_blob(-12, b"X"),
}


def main() -> None:
    here = Path(__file__).parent
    for name, blob in FIXTURES.items():
        (here / name).write_bytes(blob)
        print(f"wrote {name} ({len(blob)} bytes)")


if __name__ == "__main__":
    main()
