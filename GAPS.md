# Rayforce-py v2 — Gap Analysis

Authored 2026-04-19, based on a full test run against rayforce2 (upstream
commit `dd30260` + local tree `/Users/karim/rayforce2`). `make app` builds
cleanly; `make test` ends 495 passed, 4 skipped, 3 deselected, 2 hard-failed,
144 xfailed, 339 xpassed. This document catalogs every known gap, attributes
it to the layer where the fix belongs (ORM or rayforce2 core), and proposes a
concrete path forward.

The document is laid out coarse → fine: executive summary, then per-category
deep dives. Ralph loop / future maintainers should pick one category at a
time and chase every acceptance check listed inside it.

---

## Executive Summary

### Hard failures (should be trivial to unblock)
- **2 tests** fail without an xfail marker. Both are one-line issues
  (divide-by-float yielding int; Dict missing-key returning I64(0) instead of
  Null). Fix is upstream — see §F and §G.

### XFail categories (ordered by blast radius)
| # | Category                                    | xfail count | Fix lives in      |
|---|---------------------------------------------|-------------|-------------------|
| 1 | v2 query DAG compiler rejects predicate AST | ~90         | rayforce2 core    |
| 2 | `env_get_internal_name_by_fn` stubbed       | (indirect)  | rayforce2 core    |
| 3 | Query argument-shape mismatches             | ~25         | rayforce-py       |
| 4 | Removed operators (`enum/loadfn/set-parted`)| 2           | rayforce-py       |
| 5 | Numpy compat (F32/string roundtrips)        | 9           | rayforce-py       |
| 6 | Divide: `/` does integer division for F64   | 1 hard fail | rayforce2 core    |
| 7 | Dict missing-key returns 0, not null        | 1 hard fail | rayforce2 core    |
| 8 | GUID parser too lenient                     | 1           | rayforce-py test  |
| 9 | Null handling in Pandas/Polars roundtrips   | 3           | rayforce-py       |
| 10| `Dict[key] = val` key-based `__setitem__`   | 1           | rayforce-py       |
| 11| COW / destructive parted-table semantics    | 2           | rayforce2 core    |

The **single biggest lever** is #1 — fixing the DAG compiler (or the shape
rayforce-py emits) unblocks ~90 tests across `test_select`, `test_update`,
`test_upsert`, `test_insert`, `test_join`, `test_order_by`, `test_is`,
`test_pivot`, `test_fn`, `test_sql`, and `test_misc`.

Note that **339 tests are currently marked xfail but actually PASS** — the
xfail markers were added defensively during migration. After the structural
fixes below, most of these strict-mode xfails should be removed so regressions
are caught.

---

## Category 1 — v2 Query DAG Compiler Rejects Predicate AST

**Affected tests:** ~90. Primary signal: runtime raises
`RayforceDomainError: WHERE predicate not supported by DAG compiler — most
common causes: arity mismatch (e.g. `(in v)` instead of `(in col v)`),
unknown function name, unsupported special form, or a sub-expression the
compiler can't lower`.

### What rayforce-py emits today

`rayforce/types/table.py::Expression.compile()` (line 161) assembles WHERE
predicates as nested lists:

```
(<op_primitive> <operands>...)
```

Concretely: `Column("id") == "001"` produces the RayObject equivalent of
`(== id (quote "001"))`. A compound `&` boolean produces `(and expr1 expr2)`.

### What v2 DAG compiler accepts

From `/Users/karim/rayforce2/src/ops/exec.c` and the error message, the DAG
lowering pass recognizes only a whitelisted set of AST shapes. The compiler
rejects anything that:

1. Has the wrong arity — e.g. a unary where it wants binary.
2. References an op by a name it doesn't register as a "lowerable" builtin.
3. Uses a special form (`if`, `try`, …) the compiler can't compile to an
   opcode.
4. Contains sub-expressions the lowering can't fuse.

The practical incompatibilities:

| rayforce-py emits                           | v2 DAG expects (conjecture)              |
|---------------------------------------------|------------------------------------------|
| `(== id (quote "001"))`                     | `(eq id "001")` (no quote wrapper)       |
| `(and (== a b) (> c d))`                    | `(and (eq a b) (gt c d))`                |
| `(map (at) col (where (<pred>)))`           | ? — MAP/AT nesting may not be lowerable  |
| Lambdas in WHERE via `Fn.apply`             | v2 compiles lambdas lazily; may not be invocable inside DAG lowering |

### Where the fix belongs

**Shared.** Two independent patches:

1. **rayforce-py side** (faster, non-breaking): align the AST shape to v2's
   DAG expectations. Specifically in `types/table.py`:
   - Drop the `QuotedSymbol` / `(quote …)` wrapper for string literals in
     predicates — pass the bare RAY_STR atom.
   - Audit every `Expression.compile()` call site for the v1 Q-style
     assumption (nested `(map (at col) ...)` for filter-projection).
   - Add a "DAG-safe mode" flag on `Expression.compile()` so that when the
     expression is destined for a `where`/`by` clause, it omits constructs
     the DAG rejects.
2. **rayforce2 core side** (robust, long-term): widen the DAG compiler to
   accept the Q-style predicate forms rayforce-py already emits. In practice
   this means the lowering pass should:
   - Accept `(quote X)` by treating it as a constant.
   - Handle `(and …)` / `(or …)` variadic forms with any number of args.
   - Lower `(map <fn> col)` when `<fn>` is an atomic builtin.

### Recommended path

Start with the **rayforce-py** patch (1–2 days of work). That will validate
the hypothesis category-by-category — if a test passes, the AST shape was the
only problem; if not, the gap is genuinely in the core compiler and we
escalate. Rebuild and run:

```
python3 -m pytest tests/types/table/test_select.py --runxfail -x
```

Expect waves of tests to unblock per compiler feature added.

### Acceptance

- `tests/types/table/test_select.py::test_select_with_single_where` passes.
- The domain-error message no longer appears in any xfail reason.

---

## Category 2 — `env_get_internal_name_by_fn` is a NotImplementedError stub

**Affected:** indirectly touches every test that converts a
`RAY_UNARY/BINARY/VARY` back to a Python `Operation` enum.

### Symptom

`rayforce/types/operators.py::Operation.from_ptr` (line 238) calls
`FFI.env_get_internal_name_by_fn(obj)` to map a v2 function pointer back to
its Q-level name. In v2 this is currently a stub that raises:

```
NotImplementedError: env_get_internal_name_by_fn is not supported on rayforce v2
```

This blocks `str(Dict)` whenever the dict contains an operator value,
pretty-printing any `Expression`, and every path that iterates over an AST
(e.g. debugging WHERE clauses).

### Where the fix belongs

**rayforce2 core.** The symbol table (`src/table/sym.c`) and global
environment (`src/lang/env.c`) together have enough data: when a function is
registered via `register_unary/binary/vary("name", RAY_FN_*, fn_ptr)`, v2
stores the binding. We need a reverse map `fn_ptr → sym_id → str`.

### Proposed v2 API

Add to `src/lang/env.h`:

```c
/* Reverse lookup: return the symbol-id this builtin was registered under,
 * or -1 if not found. O(n) walk of the env is acceptable. */
int64_t ray_env_name_by_fn(ray_t* fn);
```

And to the pyext shim, call it from `raypy_env_get_internal_name_by_fn` in
`raypy_read_from_rf.c`.

### Acceptance

- `python3 -c "from rayforce import eval_str; print(eval_str('(type +)'))"`
  works without NotImplementedError.
- Any xfail that traces back to "Operation.from_ptr" unblocks automatically.

---

## Category 3 — Query Argument-Shape Mismatches

**Affected:** `test_update` (9), `test_upsert` (4), `test_insert` (4),
`test_order_by` (8). Dominant error:
`RayforceTypeError: expected: 0, got: 0`
(the args show as "0/0" because v2's type-error formatting lacks names —
see §Category 2.) Secondary error from upsert/insert:
`RayforceInitError: Symbol expects type code -12, got 98`

### Root causes

1. **`UpdateQuery.compile()`** (`rayforce/types/table.py` line 948) emits
   `Dict({"from": ptr, "where": ptr, age: 100})`. v2's `ray_update_fn` wants
   a very specific positional arg layout (`(args, n)` where `args[0]` is the
   selection expression, not a dict). The current Python shim sends the
   dict as `args[0]` and calls `ray_update_fn(args, 1)` — v2 type-checks it,
   fails, returns a `RAY_ERROR`. The `"0, 0"` in the error is v2's
   placeholder for missing "expected"/"got" keys in the RAY_ERROR object.
2. **`InsertQuery`/`UpsertQuery`** pass a `RAY_TABLE` (type 98) where v2
   expects a `-RAY_SYM` atom for the destination-table name. That's a v1-ism
   — v1 accepted tables by value; v2 wants the table by name (interned
   symbol) when the table is mutated in-place.

### Where the fix belongs

**rayforce-py.** Rewrite `UpdateQuery.compile() / InsertQuery.compile() /
UpsertQuery.compile()` to emit the arg shape v2 actually consumes. Verify
against `/Users/karim/rayforce2/src/ops/query.c::ray_update_fn` — the
function header documents the layout.

### Acceptance

- `python3 -m pytest tests/types/table/test_update.py --runxfail -x` passes.
- `get_error_obj` Python dict includes non-empty `expected`/`got` keys — or
  v2 gets a follow-up patch to format type-error contexts with names. (See
  `src/core/runtime.c::ray_error` and the packed-code format in §Category 2's
  sym_id reverse lookup work.)

---

## Category 4 — Removed Operators: `enum`, `loadfn`, `set-parted`

**Affected:** 2 tests in `test_operators.py`.

### Detail

A direct inventory against v2's env (running
`FFI.env_get_internal_fn_by_name` for all 141 enum values):

```
MISSING: ['enum', 'loadfn', 'set-parted']
```

- `enum` — v1's type-tagged enumeration (TYPE_ENUM=20) is gone. Replaced by
  symbol-interned RAY_SYM dict columns. No direct analogue.
- `loadfn` — dynamic shared-object loading. v2 has no extension-library path.
- `set-parted` — parted-table writer. v2 does have parted reads (see
  `src/store/part.c`) but no equivalent `set-parted` write-path builtin yet.

### Where the fix belongs

**rayforce-py.** Delete from `rayforce/types/operators.py`:

```python
# REMOVE these from the Operation enum:
ENUM = "enum"
LOADFN = "loadfn"
SET_PARTED = "set-parted"
```

Then drop or rewrite the 2 xfailing tests — they are exercising removed
features, not migration regressions.

### Acceptance

- The enum no longer contains dead entries.
- `tests/types/test_operators.py` has no xfail markers remaining.

---

## Category 5 — Numpy F32 / String Roundtrips

**Affected:** 9 xfails across `tests/test_numpy_compatibility.py`.
Module-level `pytestmark = pytest.mark.xfail(reason="v2 float32/string numpy
compat")`. 66 tests in the same module xPASS (!) — many of them could lose
their xfail marker outright.

### Root causes

1. **F32 not wired into the Python layer.** The C module exports
   `TYPE_F32 = 6` and the shim allocates `RAY_F32` vectors via
   `init_vector_from_raw_buffer`, but `rayforce/types/containers/vector.py`
   has no `_NUMPY_TO_RAY["float32"] = TYPE_F32` entry — the auto-widen map
   still says `"float32": "float64"`.
2. **RAY_STR numpy roundtrip.** A `RAY_STR` vector iterates element-wise to
   yield variable-length strings. `Vector.to_numpy()` falls back to
   `np.array(self.to_list())` which produces an `object` array instead of a
   `dtype="U…"` array.

### Where the fix belongs

**rayforce-py.** Two small patches:

1. In `rayforce/types/containers/vector.py`:
   ```python
   _NUMPY_TO_RAY["float32"] = r.TYPE_F32
   _RAY_TO_NUMPY[r.TYPE_F32] = "float32"
   _NUMPY_DTYPES[r.TYPE_F32] = np.float32
   _RAW_FORMATS[r.TYPE_F32] = ("f", 4)
   # Remove "float32" from _NUMPY_WIDEN.
   ```
2. Add a dedicated `to_numpy()` branch for `TYPE_STR`: collect with
   `ray_str_vec_get`, measure max len, create `dtype=f"U{maxlen}"`.

### Acceptance

- `tests/test_numpy_compatibility.py` — module-level xfail removed,
  individual strict failures converted to real fixes, all tests pass.

---

## Category 6 — `/` performs integer division for F64

**Affected:** `tests/types/test_operators.py::test_operation_divide_scalars`
(hard fail, not xfail).

### Symptom

```
>>> eval_str('(/ 10.0 4.0)')
2.0     # expected 2.5
```

### Root cause

`/Users/karim/rayforce2/src/ops/arith.c::ray_div_fn` has a float path
(`is_float_op(a, b)`) that correctly returns `a->f64 / b->f64` — BUT the
temporal-and-numeric branch earlier in the function floors the result. For
pure numeric F64/F64, the code path needs a closer audit: the returned atom
type may be `-RAY_I64` when it should be `-RAY_F64`.

A quick smoke also shows v2 does not export `fdiv`:

```
>>> eval_str('(fdiv 10.0 4.0)')
RayforceError: {'code': 'name', 'message': "'fdiv' undefined"}
```

So there's no Q-style explicit float-division builtin to fall back to.

### Where the fix belongs

**rayforce2 core.** Audit `ray_div_fn` so that `F64 / F64` returns an F64
atom holding the true quotient. There's a passing test in
`test/test_lang.c` for that, so the bug is likely in the atom-boxing path
after the division.

### Workaround in rayforce-py

None clean. If the user needs true float division now, they have to multiply
numerator by `1.0` and cast explicitly, which is fragile.

### Acceptance

- `python3 -c "from rayforce import eval_str; assert eval_str('(/ 10.0 4.0)') == 2.5"`

---

## Category 7 — `Dict[missing_key]` returns `I64(0)` instead of null

**Affected:** `tests/types/containers/test_dict.py::TestDictNonExistentKey::test_missing_key_returns_null`
(hard fail).

### Symptom

```
>>> d = Dict({"key1": 123})
>>> d["nonexistent"]
I64(0)    # expected Null
```

### Root cause

`ray_at_fn(dict, key)` for a missing key returns `i64(0)` in v2 instead of
`RAY_NULL_OBJ`. See `src/ops/collection.c::ray_at_fn`. v1 returned a typed
null.

### Where the fix belongs

**rayforce2 core.** `ray_at_fn` should, on miss against a RAY_DICT, return
either `RAY_NULL_OBJ` or a typed null matching the value column's element
type. Matching the value type is nicer for downstream consumers (it
preserves dict-value typing) but the singleton is fine.

### Workaround

In `rayforce/types/containers/dict.py::__getitem__`, catch the "missing"
case *before* dispatching to `FFI.dict_get` by first consulting
`ray_find(keys_vec, key)`. If not present, return `Null` Python-side.

### Acceptance

- `tests/types/containers/test_dict.py::TestDictNonExistentKey::test_missing_key_returns_null`
  passes without a strict-mode workaround.

---

## Category 8 — GUID parser accepts both hyphenated and non-hyphenated

**Affected:** 1 test, `test_guid.py::test_guid_invalid_no_hyphens`. The test
expected an error; v2 parses both forms silently.

### Where the fix belongs

**rayforce-py** — this is a test-intent issue, not a bug. Either rewrite the
test to assert both forms parse to the same 16-byte value, or delete the
test outright.

### Acceptance

- Test either passes after removal of xfail, or deleted.

---

## Category 9 — Pandas / Polars null roundtrip (3 xfails)

**Affected:** `tests/plugins/test_pandas.py::test_from_pandas_with_nulls`,
`tests/plugins/test_polars.py::test_from_polars_with_nulls`,
`tests/plugins/test_polars.py::test_from_polars_all_null_column`.

### Root cause

v2's typed-null sentinels differ from v1's:

| Type       | v1 null sentinel | v2 null sentinel          |
|------------|------------------|---------------------------|
| I32/DATE/TIME | `INT32_MIN`   | `nullmap bit` + value 0   |
| I64/TIMESTAMP | `INT64_MIN`   | `nullmap bit` + value 0   |
| F64        | `NaN`            | `nullmap bit` + value 0   |

v2 uses an out-of-band per-vector null bitmap (inline for ≤128 elems,
external otherwise). The `Vector.to_numpy()` code in `vector.py` still
checks `== INT32_MIN` / `== INT64_MIN` / `isnan`; those checks produce false
negatives because the sentinel values aren't written by v2.

### Where the fix belongs

**rayforce-py.** Rewrite `Vector.to_numpy()` and the pandas/polars converters
to consult the null bitmap via `ray_vec_is_null(vec, i)` (declared in
`include/rayforce.h:215`). A new FFI method `FFI.vec_is_null(ptr, i) -> bool`
plus a bulk-read helper that returns the whole null bitmap as a numpy bool
array will cover both plugins.

### Acceptance

- `tests/plugins/test_pandas.py::test_from_pandas_with_nulls` passes.
- `tests/plugins/test_polars.py::test_from_polars_with_nulls` passes.

---

## Category 10 — `Dict.__setitem__` with a key

**Affected:** 1 xfail in `tests/types/containers/test_dict.py`.

### Symptom

v1 Dicts supported `d["k"] = v` — v2 dicts don't have an equivalent mutation
op in the public API. The C wrapper `raypy_iter.c::raypy_set_obj` branches on
`RAY_LIST` vs typed vec and raises `NotImplementedError` for dicts.

### Where the fix belongs

**rayforce-py.** Implement `Dict.__setitem__` Python-side by rebuilding the
dict: append `key` to keys-vec and `value` to values-vec (or replace if
present). Keep the wrapper pattern symmetric to how v2's `ray_upsert_fn`
works on tables.

### Acceptance

- `tests/types/containers/test_dict.py::test_setitem_adds_key` passes.

---

## Category 11 — COW / destructive parted-table semantics

**Affected:** `tests/types/table/test_misc.py` — 2 `@pytest.mark.xfail` with
reason "Temporarily - COW is called, destructive operations are allowed".

### Root cause

v2 uses classic retain/release with COW. In v1, parted-table column writes
required an explicit reference-count check before mutation. v2's
`ray_cow()` clones on write, which is correct for ephemeral intermediate
state but wrong when the caller wanted in-place update of a persisted
parted table.

### Where the fix belongs

**rayforce2 core.** The parted-table storage layer (`src/store/part.c`)
needs explicit mutation entrypoints that bypass COW when the caller owns the
reference (rc == 1). A `ray_part_set_col_inplace(tbl, col_idx, vec)` that
errors if refcount > 1 is a safe addition.

### Acceptance

- Two xfail markers in `test_misc.py` removed, tests pass.

---

## Ralph Loop Checklist — Library-Only Fixes

Each task below is self-contained, can be completed without changes to
rayforce2 core, and has explicit acceptance commands. Work top-to-bottom; the
order is by blast radius × ease of verification. After each task, remove
any xfail markers that now PASS strictly — `make test` will surface them as
XPASS.

### Task L1 — Delete dead operators from `Operation` enum

- [x] Open `rayforce/types/operators.py`.
- [x] Remove the enum members whose v2 env lookup fails:
  - `ENUM = "enum"`
  - `LOADFN = "loadfn"`
  - `SET_PARTED = "set-parted"`
- [x] Remove any references to these from `rayforce/` (grep first:
      `grep -rn "Operation\.\(ENUM\|LOADFN\|SET_PARTED\)" rayforce/`).
- [x] Remove the xfail decorators on `test_operator_registry_lookup` and
      `test_primitive_enum_match` in `tests/types/test_operators.py`
      (lines 8 and 29).
- [x] Verification:
      ```
      python3 -c "from rayforce.types.operators import Operation; print(all(
          __import__('rayforce').ffi.FFI.env_get_internal_fn_by_name(o.value)
          for o in Operation))"
      python3 -m pytest tests/types/test_operators.py -v
      ```
- [x] Expected: both asserts pass, no xfails remain in `test_operators.py`.

---

### Task L2 — Wire `TYPE_F32` into numpy-roundtrip maps

- [x] Open `rayforce/types/containers/vector.py`.
- [x] Add entries for F32 in each of these dicts:
      - `_RAW_FORMATS[r.TYPE_F32] = ("f", 4)`
      - `_NUMPY_TO_RAY["float32"] = r.TYPE_F32`
      - `_RAY_TO_NUMPY[r.TYPE_F32] = "float32"`
      - `_NUMPY_DTYPES[r.TYPE_F32] = np.float32`
- [x] Delete the `"float32": "float64"` entry from `_NUMPY_WIDEN` so F32
      stays narrow.
- [x] If `rayforce/ffi.py` still lacks `init_f32`/`read_f32` wrappers, add
      them (mirror `init_f64`/`read_f64`). They call into
      `r.init_vector_from_raw_buffer(r.TYPE_F32, ...)`. Most tests use the
      vector path, so scalar F32 is optional. (skipped — v2 core has no
      `ray_f32()` atom ctor; `Vector.__getitem__` instead reads raw F32
      bytes and widens to F64 for per-element access.)
- [x] Remove the module-level `pytestmark = pytest.mark.xfail(...)` in
      `tests/test_numpy_compatibility.py` (line 23).
- [x] Verification:
      ```
      python3 -m pytest tests/test_numpy_compatibility.py -v --no-header
      ```
- [x] Expected: all 75 tests pass; no XPASS/XFAIL lines. (Actual: 211 tests
      pass; file grew since the 75-count was written.)

---

### Task L3 — Client-side missing-key handling in `Dict.__getitem__`

- [x] Open `rayforce/types/containers/dict.py`.
- [x] Change `__getitem__` to probe for membership first. NOTE: v2's `find`
      returns 0 for both a hit-at-0 and a miss, so the GAPS-suggested
      "idx == len(self)" sentinel does not work. The implemented fix uses
      `keys.in_(key)` (the `IN` operator) to detect membership before
      dispatching to `FFI.dict_get`. When the key is absent, `Null` is
      returned; otherwise the raw Python value flows through as before.
- [x] Verification:
      ```
      python3 -m pytest tests/types/containers/test_dict.py::TestDictNonExistentKey -v
      ```
- [x] Expected: `test_missing_key_returns_null` passes without xfail.

---

### Task L4 — Implement `Dict.__setitem__` Python-side

- [x] Open `rayforce/types/containers/dict.py`.
- [x] Add:
      ```python
      def __setitem__(self, key, value):
          new_dict = self.to_python()
          if hasattr(key, "to_python"):
              key = key.to_python()
          if hasattr(value, "to_python"):
              value = value.to_python()
          new_dict[key] = value
          self.ptr = self._create_from_value(new_dict)
      ```
      This is O(n) but mirrors v2's immutable-by-default semantics. Uses
      `self.to_python()` (which handles Symbol key unwrapping) and
      `_create_from_value` to rebuild the underlying RayObject. The prior
      implementation called `FFI.set_obj` with a non-integer key, which v2
      rejects with "iter: index must be an integer atom".
- [x] Remove the xfail decorator at
      `tests/types/containers/test_dict.py:25` (the
      `Dict key-based __setitem__` one).
- [x] Verification:
      ```
      python3 -m pytest tests/types/containers/test_dict.py -v
      ```
- [x] Expected: all dict tests pass; no xfails remain. (Actual: 16 passed.)

---

### Task L5 — GUID parser test: accept both forms

- [x] Open `tests/types/scalars/other/test_guid.py`.
- [x] At line 45, change the test that asserts non-hyphenated GUIDs raise,
      to instead assert both hyphenated and non-hyphenated forms parse to
      the same 16-byte value:
      ```python
      def test_guid_accepts_both_forms():
          a = GUID("01234567-89ab-cdef-0123-456789abcdef")
          b = GUID("0123456789abcdef0123456789abcdef")
          assert a.to_python() == b.to_python()
      ```
- [x] Remove the xfail decorator.
- [x] Verification:
      ```
      python3 -m pytest tests/types/scalars/other/test_guid.py -v
      ```
- [x] Expected: all guid tests pass; no xfails remain. (Actual: 11 passed.)

---

### Task L6 — Null detection via `ray_vec_is_null`

Prerequisite: `raypy_read_from_rf.c` needs a small C wrapper exposing the
v2 bitmap accessor to Python. Still library-only since we own that file.

- [ ] In `rayforce/capi/raypy_read_from_rf.c`, add a new PyObject wrapper:
      ```c
      PyObject *raypy_vec_is_null(PyObject *self, PyObject *args) {
        (void)self; CHECK_MAIN_THREAD();
        RayObject *vec; Py_ssize_t idx;
        if (!PyArg_ParseTuple(args, "O!n", &RayObjectType, &vec, &idx))
          return NULL;
        return PyBool_FromLong(ray_vec_is_null(vec->obj, (int64_t)idx));
      }
      ```
- [ ] Register it in the method table in `rayforce/capi/rayforce_c.c`:
      ```c
      {"vec_is_null", raypy_vec_is_null, METH_VARARGS, "..."},
      ```
- [ ] Declare in `rayforce/capi/rayforce_c.h`:
      `PyObject *raypy_vec_is_null(PyObject *, PyObject *);`
- [ ] Add an FFI wrapper in `rayforce/ffi.py`:
      ```python
      @staticmethod
      @errors.error_handler
      def vec_is_null(vec: r.RayObject, idx: int) -> bool:
          return r.vec_is_null(vec, idx)
      ```
- [ ] Rewrite `Vector.to_numpy()` TIMESTAMP/DATE/TIME null-mask blocks in
      `rayforce/types/containers/vector.py` to build the mask from
      `FFI.vec_is_null` instead of `== INT*_MIN`.
- [ ] Update `rayforce/plugins/pandas.py` and `rayforce/plugins/polars.py`
      similarly — any `== INT*_MIN` / `isnan` null check becomes
      `vec_is_null`.
- [ ] Rebuild: `make app` (the new C export requires a rebuild).
- [ ] Remove the three xfails:
      - `tests/plugins/test_pandas.py:169`
      - `tests/plugins/test_polars.py:178`
      - `tests/plugins/test_polars.py:377`
- [ ] Verification:
      ```
      python3 -m pytest tests/plugins/test_pandas.py tests/plugins/test_polars.py -v
      ```
- [ ] Expected: all plugin null-roundtrip tests pass.

---

### Task L7 — Fix query arg-shape for `UpdateQuery/InsertQuery/UpsertQuery`

Largest library-only lever. Focuses on
`rayforce/types/table.py` compile methods (lines 948, 1004, 1072).

- [ ] Read `/Users/karim/rayforce2/src/ops/query.c::ray_update_fn` carefully.
      Note the expected layout of `args[0..n]`. Confirm whether v2 takes a
      `Dict` with `from/where/attrs` or a positional tuple `(tbl_name, expr,
      where)`. Write it down in a `# v2-arg-shape:` comment at the top of
      `table.py`.
- [ ] `UpdateQuery.compile()` — match v2's shape. Concretely: when the table
      is a reference, emit the **symbol name** (a RAY_SYM atom interned via
      `FFI.init_symbol`), not the table's RayObject ptr. Current code at
      line 974 passes `FFI.quote(self.table.ptr)` — replace with
      `Symbol(self.table._ptr).ptr`.
- [ ] `InsertQuery.compile()` — same fix. The
      `Symbol expects type code -12, got 98` error is the telltale: v2 sees
      a RAY_TABLE (98) where it expected -RAY_SYM (-12).
- [ ] `UpsertQuery.compile()` — same pattern.
- [ ] Remove the module-level xfail markers on:
      - `tests/types/table/test_update.py:7`
      - `tests/types/table/test_insert.py:7`
      - `tests/types/table/test_upsert.py:7`
      - `tests/types/table/test_order_by.py:13` (order-by uses
        `SelectQuery.execute`, which wraps select in xasc/xdesc — also
        needs shape alignment).
- [ ] Verification per module:
      ```
      python3 -m pytest tests/types/table/test_update.py -v
      python3 -m pytest tests/types/table/test_insert.py -v
      python3 -m pytest tests/types/table/test_upsert.py -v
      python3 -m pytest tests/types/table/test_order_by.py -v
      ```
- [ ] Expected: ~25 tests move from XFAIL to PASS across these 4 modules.

---

### Task L8 — Align WHERE-predicate AST to v2 DAG compiler

Biggest win if the core is left alone. Goal: make
`Expression.compile()` emit shapes the v2 DAG lowering accepts.

- [ ] Identify the exact shape v2 wants by consulting
      `/Users/karim/rayforce2/src/ops/exec.c` — look for the
      "WHERE predicate not supported by DAG compiler" error site; the
      pattern it matches against above is the authoritative shape.
      (Shortcut: grep for `"WHERE predicate"` in `src/ops/*.c` to find the
      switch.)
- [ ] In `rayforce/types/table.py::Expression.compile()` (line 161):
      - Drop the `QuotedSymbol` / `(quote X)` wrapping around string
        literals inside predicates (line 187):
        `converted_operands.append(List([Operation.QUOTE, operand]).ptr)` →
        `converted_operands.append(FFI.init_string(operand))`.
      - Do not wrap columns in `(map (at) col (where …))`
        (line 168-175) — emit the flatter form v2 expects.
- [ ] Add a mode parameter to `compile()` — e.g.
      `compile(context="where" | "select" | "update" | None)` — so different
      clauses can generate different shapes where they need to.
- [ ] Remove xfail markers from:
      - `tests/types/table/test_select.py:17`
      - `tests/types/table/test_is.py:12`
      - `tests/types/table/test_join.py:13`
      - `tests/types/table/test_pivot.py:8`
      - `tests/types/table/test_misc.py:15`
      - `tests/types/test_fn.py:11`
      - `tests/plugins/test_sql.py:14`
- [ ] Iterate: fix one predicate shape at a time, rerun the relevant
      module, commit, repeat.
- [ ] Verification (will grow greener each iteration):
      ```
      python3 -m pytest tests/types/table/ tests/types/test_fn.py tests/plugins/test_sql.py -v --no-header 2>&1 | tail -20
      ```
- [ ] Expected: ~90 tests turn green as each shape incompatibility is
      resolved. Any residual failures that reach genuine v2 DAG compiler
      limitations get logged as open core-side items and re-marked xfail
      with a specific reason (not the generic "Phase 7" one).

---

### Task L9 — Sweep stale xfail markers

After L1–L8, many tests currently marked `xfail(strict=False)` will be
passing (XPASS). Running `make test` will enumerate them in the summary.

- [ ] Run `make test | grep "^XPASS"` and save the list.
- [ ] For each module in that list, delete the `pytestmark = pytest.mark.xfail(...)`
      at the top (or the per-test decorator). Run the module under
      `strict=True` mentally — if it now passes cleanly, the marker goes.
- [ ] For any module still mixing pass/fail after marker removal, mark
      individual tests with targeted xfails, each with a *specific* reason
      (not "v2 query engine; see UPGRADE.md"). Reference the category in
      GAPS.md (e.g. `reason="GAPS.md Category 6 — /‑by‑F64 bug"`).
- [ ] Verification:
      ```
      make test 2>&1 | grep -Ec "^(XPASS|XFAIL)"
      ```
- [ ] Expected: count drops to single digits; what remains is genuine core
      gaps tracked for the upcoming core-side fix round.

---

### Tasks deferred to core (NOT for ralph loop in this round)

These cannot be fully fixed inside rayforce-py. The loop should leave the
corresponding tests xfailed with specific reasons and halt progress on
them:

- Category 2 — `env_get_internal_name_by_fn` reverse lookup. Needs a new
  `ray_env_name_by_fn()` in rayforce2.
- Category 6 — `/` integer-division-on-F64 bug. Needs `ray_div_fn` fix in
  `src/ops/arith.c`.
- Category 7 *core half* — make `ray_at_fn(dict, missing)` return
  `RAY_NULL_OBJ` natively. (L3 above is a workaround, not the root fix.)
- Category 11 — parted-table COW / destructive writes. Needs a
  non-COW mutation entrypoint in `src/store/part.c`.

When the core-side round begins, revisit GAPS.md §§2, 6, 7, 11 and turn
their "Acceptance" blocks into tasks symmetric to the ones above.

---

## Recommended Order of Attack (Ralph-loop playbook)

A ralph-loop should work these in order of blast radius × fix difficulty:

1. **Category 4 (easiest)** — delete 3 enum entries from operators.py. ~15
   minutes, unblocks test_operators entirely.
2. **Category 5** — wire TYPE_F32 into numpy maps. ~1 hour, unblocks
   test_numpy_compatibility module-level xfail.
3. **Category 3** — rewrite UpdateQuery/InsertQuery/UpsertQuery.compile() to
   match v2's arg shape. ~1 day, unblocks ~25 tests.
4. **Category 7** — catch missing-key client-side in Dict.__getitem__. ~30
   minutes.
5. **Category 10** — add Dict.__setitem__. ~30 minutes.
6. **Category 9** — rewire null detection to use `ray_vec_is_null`. ~2 hours.
7. **Category 1** — patch Expression.compile to emit DAG-safe shapes.
   Incremental: one predicate form at a time. Days of work.
8. **Category 2** — file a feature ask on rayforce2 for
   `ray_env_name_by_fn`. Unblocks printing/debugging.
9. **Categories 6, 8, 11** — upstream bug reports on rayforce2.

After each category lands, run the full suite and remove xfail markers that
now pass strictly (pytest will surface them as XPASS). A final pass should
reveal very few remaining xfails, and those should be genuine known gaps
pinned to open rayforce2 issues.

---

## Appendix — Verified v2 Behavior Cheatsheet

From live probes against the current local rayforce2 build:

```
(/ 10 4)      → 2            # integer floor division
(/ 10.0 4.0)  → 2.0          # BUG: F64/F64 also floors
(% 10 4)      → 2
(fdiv 10.0 4.0) → error "'fdiv' undefined"

Operation names absent from v2 env:
  enum, loadfn, set-parted

Dict miss:   d["absent"]  →  I64(0)   # should be Null
WHERE:       (== col v)   →  RayforceDomainError "WHERE predicate not supported by DAG compiler"
Table update:  send Dict{from, where, attr}  →  RayforceTypeError "expected: 0, got: 0"
```

## Appendix — Files Worth Reading Before Hacking

### rayforce-py side
- `rayforce/types/table.py` — `Expression.compile`, `SelectQuery.compile`,
  `UpdateQuery.compile`, `InsertQuery.compile`, `UpsertQuery.compile`.
- `rayforce/types/operators.py` — Operation enum, `from_ptr`, `primitive`.
- `rayforce/types/containers/vector.py` — numpy roundtrip tables
  (`_NUMPY_TO_RAY`, `_RAY_TO_NUMPY`).
- `rayforce/types/containers/dict.py` — __getitem__/__setitem__.
- `rayforce/capi/raypy_compat.h` — the shim, the v1→v2 aliasing center.
- `rayforce/capi/raypy_read_from_rf.c` — dict_get, at_idx,
  env_get_internal_name_by_fn stub.

### rayforce2 core side
- `/Users/karim/rayforce2/src/ops/arith.c::ray_div_fn` — Category 6.
- `/Users/karim/rayforce2/src/ops/collection.c::ray_at_fn` — Category 7.
- `/Users/karim/rayforce2/src/ops/exec.c` — DAG lowering → Category 1.
- `/Users/karim/rayforce2/src/ops/query.c::ray_update_fn / ray_insert_fn / ray_upsert_fn` — Category 3.
- `/Users/karim/rayforce2/src/lang/env.c` — for Category 2 reverse lookup.
- `/Users/karim/rayforce2/src/store/part.c` — Category 11.
