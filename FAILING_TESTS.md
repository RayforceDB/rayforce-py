# Failing Tests — Root-Cause Analysis & Next-Round Plan

Run: `make test` on 2026-04-20 against rayforce2 GitHub (commit `dd30260`).
Counts: **930 passed, 4 skipped, 3 deselected, 0 hard-failed, 50 xfailed.**

GAPS.md L1–L9 closed out most of the migration debt; what remains is a
narrower, more semantic set of gaps. This document pairs each of the 50
xfails with (a) the real root cause, (b) whether it is a by-design v2
change we must accept, and (c) the concrete library-only fix if one exists.

Where a gap is by-design in v2, the fix is always an *adapter* in
rayforce-py — either rewriting the test, rewriting the Python wrapper to
emit a different AST, or materializing data Python-side so the new engine
sees the shape it expects.

---

## Breakdown by Root Cause

| # | Root cause                                           | xfails | Fixable in library? |
|---|------------------------------------------------------|-------:|---------------------|
| A | `PivotQuery` relies on `Column.distinct()` at DAG   |     12 | **Yes** (rewrite)   |
| B | `Fn.apply(col)` head is a `RAY_LAMBDA` pointer      |      8 | **Yes** (env-bind)  |
| C | `v2 meta` returns `_StaticRepr` Vector shape         |      4 | **Yes** (adapter)   |
| D | CSV reader/writer not exposed in pyext               |      3 | **Yes** (new exports)|
| E | TIMESTAMP + I64 → I64 in v2 DAG arithmetic           |      3 | **Yes** (coerce)    |
| F | Aggregation w/o GROUP BY broadcasts scalar           |      2 | **Yes** (detect)    |
| G | RAY_LIST columns don't go through DAG filter         |      2 | **Yes** (materialize) |
| H | `Column.where(pred).agg()` → not DAG-lowerable       |      2 | **Yes** (rewrite)   |
| I | Empty v2 error message text                          |      2 | **Yes** (fix tests) |
| J | Negative-index row access `(at tbl -1)`              |      2 | **Yes** (wrap)      |
| K | Parted/splayed COW destructive semantics             |      2 | **No — core**       |
| L | `/` F64÷F64 returns I64                              |      2 | **No — core**       |
| M | Splayed/parted table I/O exposure                    |      1 | **Yes** (new exports)|
| N | left-join dedup semantics changed                    |      1 | By-design — rewrite |
| O | asof-join missing match → I64(0) not null            |      1 | **No — core**       |
| P | Order-by with null values                            |      1 | **Yes** (use bitmap)|
| Q | `(== bool_expr True)` matches 0 rows                 |      1 | **Yes** (strip)     |
| R | `distinct` in SELECT projection                      |      1 | **Yes** (Python uniq)|

Library-fixable: **45 xfails**. Core-only: **5 xfails** (K ×2, L ×2, O ×1).

---

## Per-Cause Detail

### A. Pivot uses `Column.distinct()` inside a SELECT — 12 xfails

**Tests:** all in `tests/types/table/test_pivot.py`.

**Symptom.** `PivotQuery.execute` (`rayforce/types/table.py:1211`) starts
with:

```python
distinct = self.table.select(_col=Column(self.columns).distinct()).execute()
```

which compiles to `(select {from: T, _col: (distinct columns)})`. The v2
DAG lowering pass treats `distinct` as a non-streamable aggregation that
isn't wired into SELECT projection — it raises the generic
`RayforceDomainError: {'code': 'domain', 'message': ''}` before reaching
the evaluator.

**Why it's by-design.** v2's DAG compiler keeps SELECT projection strictly
element-wise/aggregating; set-returning helpers like `distinct` belong in
a pipeline stage, not a projected column. Asking the DAG to support
`distinct` here would conflict with its morsel model.

**Library fix.** Sidestep the DAG entirely for this one Python method.
Replace lines 1211–1212 with:

```python
col_vec = self.table[self.columns]   # Vector materialized in Python
unique_values = list(dict.fromkeys(col_vec.to_python()))  # order-preserving uniq
```

This also removes a full table scan from pivot's prologue — a perf win.

---

### B. `Fn.apply(col)` head is a raw `RAY_LAMBDA` pointer — 8 xfails

**Tests:** all 8 in `tests/types/test_fn.py` (module-level xfail).

**Symptom.** `Fn.apply(col)` builds `Expression(self, col)` where
`self.operation` is a `Fn` (RAY_LAMBDA atom), not an `Operation` enum. In
`Expression.compile()` this becomes a list whose head is a RAY_LAMBDA ptr
rather than a registered builtin. v2's DAG compiler only knows two lambda
call shapes:

1. `((fn (...args) body) expr)` — literal lambda in head position.
2. `(name args)` — name resolved to a lambda registered in env.

A raw RAY_LAMBDA object in the head is a third shape the compiler rejects.

**Why it's by-design.** v2 compiles lambdas to bytecode lazily; the DAG
optimizer needs to know the lambda body at lowering time either by its
env binding or by seeing the literal AST.

**Library fix.** Intern the lambda into the env before each use. Modify
`Fn.apply` to register itself under a generated symbol name and emit the
`(name col)` form:

```python
class Fn(RayObject):
    _apply_counter = 0

    def apply(self, *args):
        from rayforce.types.table import Expression
        # Register this lambda under a stable, unique name.
        name = f"__pyfn_{id(self):x}"
        if not getattr(self, "_bound_name", None):
            utils.eval_obj(List([Operation.SET, QuotedSymbol(name), self]))
            self._bound_name = name
        # Emit (name arg1 arg2 …) using the bound symbol.
        return Expression(QuotedSymbol(self._bound_name), *args)
```

Then teach `Expression.compile()` to treat a `QuotedSymbol` head as an
env-resolved call: `(name args)` not `(quote name args)`.

If that proves fragile, fall back to inlining: replace the head with the
lambda's stored AST (via `meta`, which already works — see §C).

---

### C. `meta` returns `_StaticRepr` that Python can't iterate — 4 xfails

**Tests:** `test_dtypes`, `test_cast_i64_to_f64`, `test_cast_f64_to_i64`,
`test_cast_with_incompatible_types` (all in `test_misc.py`).

**Symptom.** `TableInitMixin.dtypes` (line 529) calls
`(as 'DICT (meta table))`. In v2 `meta` returns a table where each cell
of the `type` column is a `_StaticRepr`-wrapped type name, not a plain
string. Python iteration throws
`TypeError: '_StaticRepr' object is not iterable`. Downstream, `cast()`
consumes `dtypes`, so it fails for the same reason.

**Why it's not by-design.** `_StaticRepr` is defined in
`rayforce/types/null.py:9` as a metaclass used only by the `Null`
sentinel. Something in the ray→Python conversion path is returning the
`Null` class instead of a string. Likely `ray_to_python` for a typed null
cell in the meta table — v2's null bitmap flagged those cells.

**Library fix.** In `rayforce/types/containers/vector.py::Vector.__iter__`
or in `ray_to_python`, treat a null cell as `Null` value, not the `Null`
*class*. Also update `TableInitMixin.dtypes`:

```python
names = [n.value if hasattr(n, "value") else str(n) for n in meta["name"].to_python()]
types = [t.value if hasattr(t, "value") else str(t) for t in meta["type"].to_python()]
return dict(zip(names, types, strict=True))
```

`.to_python()` first, then dict-comprehend — avoids the iteration of raw
RayObject cells.

---

### D. CSV reader/writer not exposed to Python — 3 xfails

**Tests:** `test_table_from_csv_all_types`, `test_set_csv`,
`test_set_csv_with_custom_separator` in `test_misc.py`.

**Library fix.** Thin pyext wrappers that forward to `ray_read_csv_fn`
and `ray_write_csv_fn` (already in `lang/internal.h`). Add to
`raypy_io.c` (create new; small replacement for deleted one) or
`raypy_queries.c`:

```c
PyObject *raypy_read_csv(PyObject *self, PyObject *args) {
  (void)self; CHECK_MAIN_THREAD();
  RayObject *path;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &path)) return NULL;
  ray_t *call_args[1] = {path->obj};
  ray_t *result = ray_read_csv_fn(call_args, 1);
  return raypy_wrap_ray_object(result);
}
```

Register in the method table, add to FFI and to `Table.from_csv` /
`Table.to_csv` helpers.

---

### E. TIMESTAMP + I64 nanosecond atom → I64 — 3 xfails

**Tests:** `test_shift_tz_positive_offset`, `test_shift_tz_negative_offset`,
`test_shift_tz_with_zoneinfo` in `test_select.py`.

**Symptom.** `Column.shift_tz(tz)` emits
`Expression(Operation.ADD, self, tz_offset_nanos(tz))`. In v2 DAG
arithmetic, `TIMESTAMP_col + i64_atom` returns an `I64` column —
the temporal type is lost.

**Why it's by-design.** v2 type inference in arith: TIMESTAMP is encoded
as i64 nanoseconds; adding an I64 atom follows numeric promotion
rules and drops the temporal tag.

**Library fix.** Cast the offset to a TIMESTAMP atom (i64 wrapped) so v2
sees homogeneous types. In `Column.shift_tz`:

```python
def shift_tz(self, tz: dt.tzinfo) -> Expression:
    offset_ts = Timestamp(tz_offset_nanos(tz))  # box as TIMESTAMP atom
    return Expression(Operation.ADD, self, offset_ts)
```

Verify `Timestamp(ns)` constructor in `rayforce/types/scalars/temporal/`
accepts a raw nanosecond int — if not, add that overload.

---

### F. Aggregation without GROUP BY broadcasts — 2 xfails

**Tests:** `test_min_max`, `test_multiple_aggregations_no_group` in
`tests/plugins/test_sql.py`.

**Symptom.** `SELECT max(price) FROM trades` compiles to
`(select {from: T, max: (max price)})`. v2's DAG executes `(max price)`
per row (broadcasting the scalar), returning N rows of `max_val` instead
of 1 row.

**Why it's by-design.** v2's SELECT projection is element-wise by
definition; aggregation without `by` was a v1-ism that v2 dropped. The
canonical v2 form is to not wrap the aggregation in SELECT at all:
`(max price)` evaluated directly against the table's column returns a
single-row table.

**Library fix.** In `SelectQuery.compile()` (line 859), detect the
"no-by aggregation only" case — i.e., every projected column is an
Expression whose root op is in `{SUM, AVG, MIN, MAX, FIRST, LAST, COUNT,
MEDIAN, DEVIATION}` — and emit a different AST:

```python
# Before:  (select {from: T, max: (max price), min: (min price)})
# After:   (dict '(max min) (list (max (at T "price")) (min (at T "price"))))
```

Or, simpler: keep the DAG path and `.take(1)` the result Python-side.
The SQL plugin's layer is a fine place to add that `.take(1)` — it
unblocks all SQL tests that use aggregation without group-by.

---

### G. RAY_LIST columns not handled by DAG filter — 2 xfails

**Tests:** `test_is_true_filters_true_rows_list`,
`test_is_false_filters_false_rows_list` in `test_is.py`.

**Symptom.** A column built from a Python `list[bool]` lands as a
`RAY_LIST` (heterogeneous) rather than `RAY_BOOL` vector. The v2 DAG
filter path rejects RAY_LIST.

**Why it's by-design.** v2 requires typed columns throughout the
execution path. RAY_LIST columns signal to the optimizer "I don't know
the element type" and are not streamable.

**Library fix.** In `Table.__init__` / dict-path init (line 242),
auto-unify bool lists (and other homogeneous lists) to the corresponding
typed Vector **before** passing to `FFI.init_table`. A small helper:

```python
def _coerce_column(col):
    if isinstance(col, list) and col and all(isinstance(x, bool) for x in col):
        return Vector(items=col, ray_type=B8)
    # … same for int/float/str …
    return col
```

Apply to every value in `ptr.values()` before `List(ptr.values()).ptr`.

---

### H. `Column.where(pred).agg()` emits non-lowerable form — 2 xfails

**Tests:** `test_is_with_group_by`, `test_group_by_with_filtered_aggregation`.

**Symptom.** `Column("x").where(x > 0).sum()` produces
`(sum (map (at) 'x (where (> x 0))))`. The v2 DAG lowerer doesn't
recognize `(map (at) name (where pred))` as a filter-then-project shape.

**Library fix.** Rewrite `Column.where` to emit the flatter form the DAG
accepts. The canonical v2 shape for "sum of x where x > 0" is something
like `(sum (filter (> x 0) (at T 'x)))` — filter first, then aggregate.
Confirm the exact form by grepping
`/Users/karim/rayforce-py/tmp/rayforce-c/src/ops/filter.c` and
`src/ops/agg.c` for accepted AST patterns.

In `Column.where` (`rayforce/types/table.py:224`):

```python
def where(self, condition: Expression) -> Expression:
    return Expression(Operation.FILTER, condition, self)  # new shape
```

This mirrors v2's `ray_filter_fn(mask, col)` signature (mask first).

---

### I. Empty v2 error-message text — 2 xfails

**Tests:** `test_concat_with_mismatched_column_names`,
`test_at_column_with_nonexistent_column`.

**Symptom.** Tests assert on a specific v1 error message string; v2
returns `RayforceDomainError: {'code': 'domain', 'message': ''}`.

**Why it's by-design.** v2's error system uses packed codes (see
`ray_err_code()`); readable messages are out-of-band via
`ray_error_msg()`. Not every error path calls that helper, so the
`message` field is empty for fast-path errors.

**Library fix.** Update tests to assert on the error **code** not the
message text:

```python
with pytest.raises(RayforceDomainError) as exc:
    ...
assert exc.value.args[0]['code'] == 'domain'  # was: assert "not found" in str(exc)
```

Core-side follow-up (optional): populate `message` in `ray_error` calls
from `ray_at_fn` / `ray_concat_fn`.

---

### J. Negative row index `(at tbl -1)` raises domain error — 2 xfails

**Tests:** `test_getitem_int_row`, `test_getitem_int_row_second_to_last`.

**Symptom.** `table[-1]` → `(at table -1)`. v2 errors out; it does not
wrap negative indices.

**Why it's by-design.** v2's `at` is a raw indexed access; Python-style
negative wrapping is a host-language convention.

**Library fix.** Wrap at Python level in `at_row` (`table.py:387`):

```python
def at_row(self, row_n: int) -> Dict:
    if not isinstance(row_n, int):
        raise errors.RayforceConversionError("Row number has to be an integer")
    if row_n < 0:
        row_n = len(self) + row_n
    if row_n < 0 or row_n >= len(self):
        raise errors.RayforceIndexError(f"Row out of bounds: {row_n}")
    return utils.eval_obj(List([Operation.AT, self.evaled_ptr, I64(row_n)]))
```

---

### K. Parted/splayed COW destructive semantics — 2 xfails (CORE)

Tests: `test_splayed_table_destructive_operations_raise_error`,
`test_parted_table_destructive_operations_raise_error`.

Needs `ray_part_set_col_inplace` (or similar non-COW mutation) in
`src/store/part.c`. Leave as is; gate behind core round.

---

### L. F64÷F64 → I64 — 2 xfails (CORE)

Tests: `tests/types/test_operators.py::test_operation_divide_scalars`,
`tests/plugins/test_sql.py::test_arithmetic_division`.

Needs `ray_div_fn` fix in `src/ops/arith.c`. Core round.

---

### M. Splayed/parted table I/O not exposed — 1 xfail

**Test:** `test_set_splayed_and_from_parted`.

**Library fix.** Expose `ray_set_splayed_fn` / `ray_get_splayed_fn` /
`ray_get_parted_fn` (all declared in `lang/internal.h`) via pyext
wrappers, same pattern as CSV (§D). Add `Table.to_splayed(path)` and
`Table.from_splayed(path)` / `.from_parted(path)` Python helpers.

---

### N. left-join dedup semantics changed — 1 xfail

**Test:** `test_left_join_with_duplicate_keys`.

v2's left-join returns one row per right-side match instead of one row
per left-side row when the join key is duplicated. This aligns with
SQL-standard left join.

**Fix.** Update test expectation to match v2 semantics (this is more
correct anyway). No Python change.

---

### O. asof-join null vs I64(0) — 1 xfail (CORE)

**Test:** `test_asof_join_with_no_matching_quotes`.

Needs `ray_asof_join_fn` in `src/ops/join.c` to emit typed nulls for
no-match rows. Core round.

---

### P. Order-by with null values — 1 xfail

**Test:** `test_order_by_with_null_values`.

**Library fix.** Same mechanism as GAPS L6: use `ray_vec_is_null` to
detect nulls, then either pre-sort nulls or post-process. Depends on the
`vec_is_null` FFI export from L6.

---

### Q. Nested `(== bool_expr True)` returns 0 rows — 1 xfail

**Test:** `test_is_on_expression`.

**Symptom.** `Column.is_(True)` emits `(== <bool_col> True)`. v2's DAG
`==` compares the bool column's element type against the `True` atom
via type-strict equality; the result is empty.

**Library fix.** Detect the `Expression.__eq__(bool_literal)` case and
elide the wrapper: if the LHS is already a bool-producing expression
and the RHS is `True`, return the LHS unchanged. Modify `Column.is_`:

```python
def is_(self, other: bool) -> Expression:
    if other is True:
        return self  # already a bool-producing Column/Expression
    if other is False:
        return Expression(Operation.NOT, self)
    return Expression(Operation.EQUALS, self, other)
```

---

### R. `distinct` in SELECT projection — 1 xfail

**Test:** `test_select_distinct`.

Same root cause as §A. The fix is scoped to the test path:
`select(_vals=Column("dept").distinct())`. Option 1: Python-side uniq
(as with pivot). Option 2: detect in `SelectQuery.compile` and emit a
separate `(distinct (at T 'dept))` pipeline stage instead of a
projected column.

---

## New Ralph-Loop Plan (library-only, post-GAPS)

Each task is self-contained, has explicit file paths and line numbers,
and ends with a verification command. Tasks are ordered by
`blast_radius × ease`. Completing all of them brings xfails from 50 to
~5 (the 5 genuine core-side gaps K, L, O).

### Task M1 — PivotQuery: Python-side distinct (§A)

- [x] Open `rayforce/types/table.py`, line 1211.
- [x] Replace the first two lines of `PivotQuery.execute`:
      ```python
      col_vec = self.table[self.columns]
      unique_values = list(dict.fromkeys(
          v.value if hasattr(v, "value") else v
          for v in col_vec.to_python()
      ))
      ```
- [x] Delete `pytestmark = pytest.mark.xfail(...)` at
      `tests/types/table/test_pivot.py:8`.
- [x] Verify: `python3 -m pytest tests/types/table/test_pivot.py -v`.
- [x] Expected: 12 tests pass; `test_pivot.py` xfail-free.

### Task M2 — SELECT distinct: Python-side uniq (§R)

- [x] In `SelectQuery.compile()` (`table.py:859`), detect if the only
      projected expression is `Expression(Operation.DISTINCT, Column(c))`
      and route it to a plain `(distinct (at T c))` expression (not a
      select-with-projection).
- [x] Verify:
      `python3 -m pytest tests/types/table/test_select.py::test_select_distinct -v`.

### Task M3 — Column.is_(True/False) elision (§Q)

- [x] Patch `Column.is_` and `Expression.is_` (if present) per §Q.
- [x] Verify: `python3 -m pytest tests/types/table/test_is.py::test_is_on_expression -v`.

### Task M4 — Table.__init__ coerces list columns to typed vectors (§G)

- [x] In `TableInitMixin.__init__` (line 236) add `_coerce_column`
      helper as in §G and apply to every value of `ptr.values()`.
- [x] Verify: `python3 -m pytest tests/types/table/test_is.py -v`.

### Task M5 — Negative row index Python-side wrap (§J)

- [x] Patch `at_row` (line 387) to wrap negatives per §J.
- [x] Verify: `python3 -m pytest tests/types/table/test_misc.py -k getitem_int_row -v`.

### Task M6 — Column.shift_tz coerces offset to TIMESTAMP (§E)

- [x] Patch `Column.shift_tz` (line 228) to wrap `tz_offset_nanos(tz)`
      in a `Timestamp` atom.
- [x] Verify: `python3 -m pytest tests/types/table/test_select.py -k shift_tz -v`.

### Task M7 — Fix dtypes / cast via `.to_python()` first (§C)

- [x] Rewrite `TableInitMixin.dtypes` per §C.
- [x] Verify: `python3 -m pytest tests/types/table/test_misc.py -k "dtypes or cast" -v`.

### Task M8 — Column.where emits `(filter mask col)` shape (§H)

- [x] Change `Column.where` to return
      `Expression(Operation.FILTER, condition, self)`.
- [x] Audit call sites — anything that previously matched `MAP/AT/WHERE`
      in `Expression.compile` should be updated or removed.
- [x] Verify: `python3 -m pytest tests/types/table/test_is.py tests/types/table/test_select.py -v`.

### Task M9 — Aggregation broadcast: `.take(1)` in SQL plugin (§F)

- [ ] In the SQL plugin layer, if the SELECT projection contains only
      aggregation calls and there's no GROUP BY, wrap the result with
      `.take(1)` (or detect before compile and emit a dict instead).
- [ ] Verify: `python3 -m pytest tests/plugins/test_sql.py -v`.

### Task M10 — Fn.apply: bind lambda into env, emit `(name args)` (§B)

- [ ] Modify `Fn.apply` and possibly `Expression.compile` head-handling
      per §B.
- [ ] Verify: `python3 -m pytest tests/types/test_fn.py -v`.

### Task M11 — CSV reader/writer pyext wrappers (§D)

- [ ] Add `raypy_read_csv` / `raypy_write_csv` wrappers; register in
      method table; expose via `Table.from_csv` / `Table.to_csv`.
- [ ] Rebuild (`make app`).
- [ ] Verify: `python3 -m pytest tests/types/table/test_misc.py -k csv -v`.

### Task M12 — Splayed/parted Python I/O wrappers (§M)

- [ ] Add `raypy_set_splayed` / `raypy_get_splayed` / `raypy_get_parted`
      pyext wrappers.
- [ ] Rebuild, expose via `Table.to_splayed` / `Table.from_splayed` /
      `Table.from_parted`.
- [ ] Verify: `python3 -m pytest tests/types/table/test_misc.py -k splayed -v`.

### Task M13 — Order-by null handling via vec_is_null (§P)

- [ ] Requires GAPS L6 to be done first (`FFI.vec_is_null`).
- [ ] In `SelectQuery.execute` (line 951), when `self._order_by_cols` is
      set, pre-compute a null mask per order key and splice nulls to
      the end (asc) or start (desc) Python-side.
- [ ] Verify:
      `python3 -m pytest tests/types/table/test_order_by.py::test_order_by_with_null_values -v`.

### Task M14 — Error-text tests → error-code assertions (§I)

- [ ] Update 2 tests in `test_misc.py` per §I.
- [ ] Verify those tests.

### Task M15 — left-join dedup: update expectation (§N)

- [ ] Update `test_left_join_with_duplicate_keys` to match v2 semantics.
- [ ] Verify.

### Task M16 — Sweep stale xfail markers (final hygiene)

- [ ] After M1–M15, run `make test | grep XPASS`. For any, remove the
      xfail marker. For modules that go clean, remove any lingering
      module-level `pytestmark = pytest.mark.xfail(...)`.
- [ ] Commit.

### Tasks deferred to core round (do NOT attempt now)

- **K** — parted/splayed COW destructive
- **L** — `/` F64÷F64 returns I64
- **O** — asof-join null vs 0

After core-side fixes land, the corresponding 5 xfails can be flipped to
strict xfail → strict pass with no Python change.

---

## Expected End State

| Run                       | passed | xfail | hard-fail |
|---------------------------|------:|------:|----------:|
| Today                     |   930 |    50 |         0 |
| After M1–M16 (library)    |  ~975 |   ~5  |         0 |
| After core round (K/L/O)  |   ~980 |     0 |         0 |

The ~5 residual xfails post-library-round will be strictly the core-side
gaps, each with a specific issue reference rather than the generic
"GAPS.md Phase 7" marker.

---

## Appendix — Verifying a Given Fix Didn't Break Something Else

After each M-task:

```
make test 2>&1 | tail -3
```

If the pass count dropped, you introduced a regression — revert and
narrow the fix. If the xfail count dropped without the pass count
rising, you removed a stale xfail marker but the underlying test was
never running; investigate.
