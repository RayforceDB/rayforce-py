# v1 wire-format fixtures

Hand-crafted v1 IPC-headered serialized blobs, one per scalar atom type.
Used by `tests/test_migrate.py` to verify that
`rayforce.migrate.transcode_v1_blob` rewrites them into v2 wire format
that `de_obj` can decode.

## Wire format these fixtures encode

Each file is `<16-byte IPC header><1-byte v1 type tag><value bytes>`. The
IPC header layout (little-endian):

| offset | size | field   | value used here              |
|--------|------|---------|------------------------------|
| 0      | 4    | prefix  | `0xcefadefa`                 |
| 4      | 1    | version | `2` (v1 wire version)        |
| 5      | 1    | flags   | `0`                          |
| 6      | 1    | endian  | `0` (little)                 |
| 7      | 1    | msgtype | `0`                          |
| 8      | 8    | size    | length of payload that follows |

v1 atoms had **no** `flags` byte after the type tag (v2's wire-version-3
added it to carry the typed-null marker). Per-type value bytes:

| file              | v1 type | bytes                               | decoded value                      |
|-------------------|---------|-------------------------------------|------------------------------------|
| `i32.bin`         | `-4`    | `i32` (4 LE bytes)                  | `42`                               |
| `i64.bin`         | `-5`    | `i64` (8 LE bytes)                  | `12345`                            |
| `f64.bin`         | `-10`   | `f64` (8 LE IEEE-754 bytes)         | `3.14`                             |
| `date.bin`        | `-7`    | `i32` days since rayforce epoch     | `8000`                             |
| `time.bin`        | `-8`    | `i32` ms since midnight             | `1234`                             |
| `timestamp.bin`   | `-9`    | `i64` nanoseconds since epoch       | `1700000000000000000`              |
| `sym.bin`         | `-6`    | null-terminated UTF-8 bytes         | `"hello"`                          |
| `c8.bin`          | `-12`   | one byte (char value)               | `'X'` (ASCII `0x58`)               |

## Regenerating

These bytes are committed to the repo so the test runs deterministically
without any v1 binary on hand. To regenerate, run:

```bash
python tests/fixtures/v1_blobs/generate.py
```

The generator is a pure-Python `struct.pack` script; it does not import
`rayforce` so it works even on a clean checkout before `make app`.
