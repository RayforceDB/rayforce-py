# v1 → v2 audit (usage perspective)

This is a usage-perspective audit of the changes between rayforce-py
**v1 (`1.0.0`, `master` branch)** and **v2 (`2.0.0a1`, `rayforce2` branch)**.
Source of truth: actual diffs between the two branches plus the v1
documentation under `docs/docs/content/`. Not a changelog — the changelog
will be drafted from this later.

---

## 🔴 Removed (breaking)

### Top-level package surface (`from rayforce import …`)
| v1 import | v2 status |
|---|---|
| `from rayforce import C8` | gone — `C8` scalar class deleted; use `String` |
| `from rayforce import TCPClient` | moved → `from rayforce.network import TCPClient` |
| `from rayforce import TCPServer` | moved → `from rayforce.network import TCPServer` |
| `from rayforce import RayforceTCPError` | moved → `from rayforce.errors import RayforceTCPError` |

### Network layer
| v1 | v2 |
|---|---|
| `WSClient`, `WSClientConnection` | gone, no replacement |
| `WSServer`, `WSServerConnection` | gone, no replacement |
| `TCPClient(host="127.0.0.1:5000")` (combined string) | port is now a separate required `int` |

### Plugins
| v1 | v2 |
|---|---|
| `from rayforce.plugins.raykx import KDBEngine` | `from rayforce.plugins.kdb import KDBEngine` (same class shape) |
| `KDBEngine(host, port=None)` | `KDBEngine(host, port: int)` (port now required) |
| `libraykx.dylib` runtime dependency | gone — KDB+ wire format codec self-contained in pyext |

### Type codes (`r.TYPE_*` constants)
| v1 | v2 |
|---|---|
| `TYPE_C8 = 12` | gone — folded into `TYPE_STR = 13` |
| `TYPE_ENUM = 20` | gone, no replacement |
| `TYPE_MAPFILTER = 71`, `TYPE_MAPGROUP = 72`, `TYPE_MAPFD = 73`, `TYPE_MAPCOMMON = 74`, `TYPE_MAPLIST = 75` | gone |
| `TYPE_PARTEDLIST = 77` and all `TYPE_PARTED*` derivatives | gone (parted handled differently in v2) |
| `TYPE_TOKEN` | gone |

### `Operation` enum members
| v1 enum member | v2 status |
|---|---|
| `Operation.ENUM` | gone (TYPE_ENUM removed) |
| `Operation.HOPEN`, `Operation.HCLOSE` | gone — use `eval_str(".ipc.open ...")` etc. |
| `Operation.READ_CSV`, `Operation.WRITE_CSV` | gone — `Table.from_csv` / `Table.set_csv` still work; raw verb is `.csv.read` / `.csv.write` |
| `Operation.SET_PARTED` | gone, **no replacement** |
| `Operation.SYSTEM`, `Operation.GC`, `Operation.MEMSTAT`, `Operation.INTERNALS`, `Operation.SYSINFO` | gone — use `.sys.exec`, `.sys.gc`, `.sys.mem`, `.sys.build`, `.sys.info` via `eval_str` |
| `Operation.OS_GET_VAR`, `Operation.OS_SET_VAR` | gone — use `.os.getenv` / `.os.setenv` via `eval_str` |
| `Operation.LOADFN` | gone (raykx dynlib loading no longer exists) |

### Pyext / FFI methods
| v1 | v2 |
|---|---|
| `FFI.init_c8(value)`, `FFI.read_c8(obj)` | gone — use `FFI.init_string(value)` / `FFI.read_string(obj)` |
| `r.init_c8`, `r.read_c8`, `r.TYPE_C8` | gone |

### Tooling
| v1 | v2 |
|---|---|
| `python -m rayforce.migrate {blob,splayed,parted}` (v1 binary data → v2 wire format) | gone — `rayforce/migrate.py` deleted |

### Eval-time conveniences
| v1 | v2 |
|---|---|
| `eval_str("(hopen \"h:p\")")` (auto-rewritten to `.ipc.open`) | gone — must write `eval_str("(.ipc.open \"h:p\")")` directly. Affected verbs: `hopen`, `hclose`, `read-csv`, `write-csv`, `os-get-var`, `os-set-var`, `system`, `gc`, `memstat`, `internals`, `sysinfo` |

---

## 🟡 Renamed (key kept, value changed)

### `Operation` enum values
| Member | v1 value | v2 value |
|---|---|---|
| `Operation.SET_SPLAYED` | `"set-splayed"` | `".db.splayed.set"` |
| `Operation.GET_SPLAYED` | `"get-splayed"` | `".db.splayed.get"` |
| `Operation.GET_PARTED` | `"get-parted"` | `".db.parted.get"` |

### Module paths
| v1 | v2 |
|---|---|
| `rayforce.plugins.raykx` | `rayforce.plugins.kdb` |

---

## 🟠 Behavior changes

### Division semantics
v2 core fixed `/` to perform true division on all numeric types.

```python
# v1
Vector([10, 20, 30], ray_type=I64) / 4
# → [I64(2), I64(5), I64(7)]   (truncated)

# v2
Vector([10, 20, 30], ray_type=I64) / 4
# → [F64(2.5), F64(5.0), F64(7.5)]   (true division)

Vector([10, 20, 30], ray_type=I64) // 4
# → [I64(2), I64(5), I64(7)]   (floor division — use //)
```

`Operation.DIVIDE` now produces F64; `Operation.DIV_INT` is the
floor-division verb.

### Type-code value shifts (binary wire format)
| Type | v1 code | v2 code |
|---|---|---|
| `SYMBOL` | 6 | 12 |
| `DATE` | 7 | 8 |
| `TIME` | 8 | 9 |
| `TIMESTAMP` | 9 | 10 |
| `F64` | 10 | 7 |

**Practical impact:** v1-serialized binary blobs (`Table.set_csv` outputs,
`Table.ipcsave` outputs, `Table.set_splayed` directories holding
shifted-type columns) **cannot be read by v2** without the (now-deleted)
migration tool. Anyone with persisted v1 data needs a migration path.

### `String` inheritance
| | v1 | v2 |
|---|---|---|
| Class | `class String(Vector)` | `class String(Scalar)` |
| `isinstance(s, Vector)` | `True` | `False` |
| `isinstance(s, Scalar)` | `False` | `True` |

Duck-typed surface (`__len__`, `__getitem__`, `__iter__`) preserved, but
`isinstance` checks against `Vector` will silently change behavior.

### Date format input
| | v1 | v2 |
|---|---|---|
| Core verb `(as 'DATE …)` | accepts ISO `"2024-01-05"` and dotted `"2024.01.05"` | accepts only dotted `"2024.01.05"`; ISO yields `error: domain` |
| `FFI.init_date("2024-01-05")` | works | works (pyext normalizes `-` → `.` before calling core) |

User-facing Python API is preserved via the pyext normalization. Direct
rayfall via `eval_str` is the regression.

### Storage mutation (parted/splayed COW)
v2 core uses copy-on-write semantics for parted/splayed tables loaded
from disk.

```python
# Both v1 and v2: this is now a guarded operation in pyext
loaded = Table.from_splayed("…")   # is_parted == True
loaded.update(age=100)
# → raises RayforcePartedTableError("use .select() first …")
```

In v2, the underlying core would silently produce a non-parted clone via
COW — pyext's destructive-op guard explicitly refuses to build such a
query at the Python layer.

### F32 arithmetic
v2 core has F32 *vector* but no F32 *op kernels*. Python F32 widens to
F64 for binary numeric ops:

```python
F32(1.5) + F32(2.5)
# → F64(4.0)   (NOT F32; v2 core has no F32 add/sub/mul/div)
```

Differs from numpy semantics (where F32+F32 stays F32).

### Eval lazy semantics (transparent)
v2's `ray_eval` returns `RAY_LAZY=104` DAG handles for many graph-aware
operations. **Pyext materializes at the C→Python boundary**, so
user-facing behavior is preserved (eager values come back). This is
internal — flagged because it's a behavioral difference at the C layer.

### Internal-fn lookup behavior
v1 used `FFI.env_get_internal_fn_by_name("set-splayed")` directly. In
v2, the lookup target is the namespaced verb (`.db.splayed.set`) —
`Operation.SET_SPLAYED.primitive` resolves correctly because the enum
value is updated, but anyone calling
`env_get_internal_fn_by_name("set-splayed")` (or `"read-csv"`, etc.)
literal-string will get `RuntimeError: read: function not found`.

---

## 🟢 Added (new in v2)

### Types
- `rayforce.F32` — 32-bit float scalar (length-1 RAY_F32 vector under the hood)
- `r.TYPE_F32 = 6` (numeric)
- `r.TYPE_STR = 13` (string atom; replaces TYPE_C8 with any-length support)

### Pyext / FFI
- `FFI.vec_is_null(vec, idx) -> bool` — null-bitmap query
- `FFI.vec_set_null(vec, idx, is_null)` — null-bitmap update
- `FFI.vec_slice(vec, offset, length)` — zero-copy slice view
- `FFI.obj_addr(obj) -> int` — object identity / pointer
- `FFI.ipc_connect/close/send/send_async` — native IPC client
- `FFI.ipc_server_init/poll/destroy` — native IPC server (replaces v1's `ipc_listen`/`runtime_run`)
- `FFI.kdb_connect/close/send` — native KDB+ wire-format client (replaces v1's libraykx.dylib indirection)

### Network layer
- `TCPClient.send_async(data) -> None` — fire-and-forget IPC frame
- `TCPClient(host, port, *, user="", password="")` — auth credentials for `-u` / `-U` rayforce servers
- `TCPServer.listen(*, poll_interval_ms=100)` — Python-driven poll loop with Ctrl-C support (v1 had a kernel event loop)
- `TCPServer.stop() / close()` + context-manager — proper teardown (v1 only had `listen()`)

### Table layer
- `Table.update`/`insert`/`upsert` now refuse to construct on loaded parted/splayed tables (raises `RayforcePartedTableError`)

### Eval
- `eval_str(expr, *, raw: bool = False)` — pass `raw=True` to receive a `RayObject` instead of an auto-converted Python value (v1 always converted)

### Constants
- `core_version` — populated from the v2 core's `(.sys.build)` verb (when available)

---

## 📄 Documentation regressions to fix before release

These doc files describe surface that no longer exists or that changed:

- `docs/docs/content/documentation/data-types/char.md` — entire page documents `C8`; needs deletion or rewrite to `String` semantics.
- `docs/docs/content/documentation/plugins/kdb.md` — first line says "using a seamless raykx IPC", import line is `from rayforce.plugins.raykx import KDBEngine`. Both stale.
- `docs/docs/content/documentation/websocket.md` — entire page documents `WSClient`/`WSServer` which don't exist in v2.
- `docs/mkdocs.yml` (line 140) — nav still has `Websocket: content/documentation/websocket.md`.
- `docs/docs/index.md` — landing-page hero text mentions WebSocket prominently; needs revision.

---

## Summary by impact category

| Category | Items |
|---|---|
| 🔴 Hard breaks (compile/import-time) | 4 top-level imports, 5 `TYPE_MAP*`, `TYPE_C8`, `TYPE_ENUM`, `TYPE_PARTEDLIST`, `TYPE_TOKEN`, 11 `Operation.*` members, `FFI.init_c8`/`read_c8`, `rayforce.plugins.raykx` module path, all WS classes |
| 🟡 Soft breaks (silently different behavior) | division semantics, `String` MRO, type-code value shifts in persisted blobs, F32 arithmetic widening, `Operation.SET_SPLAYED`-style enum values |
| 🟢 New surface | `F32`, `TYPE_F32`/`TYPE_STR`, native IPC + KDB pyext, send_async, auth params, server lifecycle, vec null-bitmap + slice + obj_addr, parted-mutation guards, `eval_str(raw=True)` |
| 📄 Doc-only stale | `char.md`, `websocket.md`, `kdb.md` import path, `mkdocs.yml` nav, `index.md` hero |
