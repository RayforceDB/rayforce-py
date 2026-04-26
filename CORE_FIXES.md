# v2 Core Fixes Required

These are issues that **must be fixed in `~/rayforce2/`**, not worked around in
the Python binding. They are listed here so the rayforce-py side knows what
to file upstream and when to delete the corresponding Python workaround.

Each entry includes:
- **Problem** — what v2 does today, with file:line in v2 source.
- **Why core** — why a Python-side fix is wrong or insufficient.
- **Example** — minimal reproducer.
- **What to delete in rayforce-py** when the fix lands.

Numbered §1–§N. Tier ordering reflects severity / blast radius for downstream.

---

## §1 — Division semantics: `F64/F64` floors, `I64/I64` promotes to F64

### Problem
v2 `ray_div_fn` (`~/rayforce2/src/ops/arith.c`) returns floor-div behavior for
double operands and promotes integer operands to F64 instead of truncating.

- `F64 / F64` → integer-floored result (should be IEEE 754 division).
- `I64 / I64` → F64 (should truncate to I64; or split into `div`/`fdiv`).

### Why core
Arithmetic semantics are a contract. A Python-side rewrite (e.g., wrapping
every `/` in `Expression` to emit `(div x (* y 1.0))`) is fragile, breaks
when the user calls `eval_str("(/ a b)")` directly, and double-evaluates
operand `y`.

### Example
```python
import rayforce as rf
rf.eval_str("(/ 7.0 2.0)")  # expected 3.5; v2 returns 3.0
rf.eval_str("(/ 7 2)")       # expected 3 (I64); v2 returns 3.5 (F64)
```

### Affected tests (currently xfail)
- `tests/types/test_operators.py:58` — `test_operation_divide_scalars`
  (reason: "GAPS Cat 6 — v2 ray_div_fn floors F64/F64 to int")
- `tests/types/test_fn.py:20` — `_INT_DIV_PROMOTED_TO_FLOAT` marker
- `tests/plugins/test_sql.py:13` — `_F64_DIVIDE_FLOORS` marker

### What to delete when fixed
- All three xfail markers above.
- No active workaround code in rayforce-py.

### Suggested v2 design
- `(/ x y)` performs IEEE 754 division when either operand is F64; truncates
  when both are integral.
- Or: split into two builtins, `div` (integer) and `fdiv` (float), with `/`
  defaulting to fdiv.

---

## §2 — DAG β-reduction does not bind `self` for recursive lambdas

### Problem
v2 DAG compiler (`~/rayforce2/src/ops/query.c`, named-lambda inliner) inlines
lambda bodies during `compile_expr_dag` but does not introduce a binding for
`self` in the closure environment. As a result, recursive lambdas work in
direct-eval (because the runtime evaluator maintains a full environment) but
fail when applied to a column inside `SELECT`.

### Why core
The Python workaround would be: detect recursion in the lambda body
syntactically, force the literal-call path even inside `SELECT`, and accept
re-evaluation cost per row. This is (a) a parser dependency that should not
live in Python, (b) defeats the DAG fusion benefit precisely on the queries
that need it most, (c) silently differs from v1 semantics.

### Example
```python
fib = rf.Fn("(fn [n] (if (< n 2) n (+ (self (- n 1)) (self (- n 2)))))")
fib(5)  # works: returns 5

t = rf.Table({"x": rf.Vector([1, 2, 3, 4, 5], ray_type=rf.I64)})
t.select(y=fib.apply(rf.Column("x"))).execute()
# fails / wrong result: DAG inlined fib body but `self` is unbound
```

### Affected tests (currently xfail)
- `tests/types/test_fn.py:27` — `_RECURSIVE_SELF_IN_DAG` marker.

### What to delete when fixed
- xfail marker `_RECURSIVE_SELF_IN_DAG`.
- The `self`-detection branch in `Fn.apply` (`rayforce/types/fn.py`) — once
  core handles it, the named-call shape works for all lambdas uniformly.

### Suggested v2 design
- During lambda inlining in the DAG, push a binding `self → <the lambda
  itself>` into the compile-time env before walking the body.

---

## §3 — DAG type inference demotes TIMESTAMP through arithmetic

### Problem
v2 DAG `promote_type` (`~/rayforce2/src/ops/opt.c`, type-inference pass)
collapses `TIMESTAMP + I64` to `I64`, losing the TIMESTAMP type tag. The
resulting column is correct in raw nanoseconds but reports its dtype as I64.

### Why core
The Python workaround (`shift_tz` recovers the type via post-hoc cast in
`table.py:~250, 297, 1124`) is reactive: every new temporal op needs the
same treatment, and any user query that does `Column("ts") + Column("offset")`
without going through our wrappers gets the wrong dtype. Type inference
belongs in the optimizer, not in every consumer.

### Example
```python
import datetime as dt
t = rf.Table({"ts": rf.Vector([rf.Timestamp(dt.datetime(2024,1,1, tzinfo=dt.UTC))])})
shifted = t.select(ts2=rf.Column("ts").shift_tz(dt.timezone(dt.timedelta(hours=3)))).execute()
shifted.dtypes  # core says: {"ts2": "I64"} ; expected: {"ts2": "TIMESTAMP"}
```

### Affected code (workarounds in place, no xfail)
- W2: `rayforce/types/table.py:~250, 285, 1124` — TIMESTAMP recast after SELECT.
- W3: `rayforce/types/table.py:~297` — `_ShiftTzExpression` rebuilds via add.
- M20 in `plan.md` consolidates these into one helper, but does not remove
  them.

### What to delete when fixed
- `_ShiftTzExpression` class.
- `_TEMPORAL_RECOVERY_OPS` registry and its caller (introduced in M20).
- The targeted recast in `SelectQuery.execute`.

### Suggested v2 design
- Promotion table for arithmetic on temporal-vs-integral operands: result
  type = temporal type (TIMESTAMP, DATE, TIME), not common arithmetic type.
- Apply uniformly to `+`, `-`, `*` (where meaningful), `shift_tz`.

---

## §4 — Parted/splayed tables silently mutate via COW

### Problem
v2 `ray_cow` (`~/rayforce2/src/store/part.c` / `cow.c`) clones-on-write when
a destructive operation (`update`, `insert`, `upsert`) is invoked on a table
loaded from a splayed or parted directory. The on-disk files are not
modified, but the in-memory clone is — silently. The user expects either
"writes through to disk" or "raises `RayforcePartedTableError`"; v2 does
neither.

### Why core
A Python-side guard (tag the table with `_is_readonly = True` after
`from_parted`/`from_splayed`, check in `update`/`insert`/`upsert`) is
trivially bypassable: any user who constructs queries via `eval_str` or
`Operation`-level expression building gets the silent clone. The check
must be at the storage layer.

### Example
```python
t = rf.Table.from_splayed("/tmp/mytable")
t.update(x=rf.Column("x") + 1).execute()
# v2: silently produces an in-memory clone with x+1; /tmp/mytable untouched
# expected: raises RayforcePartedTableError, OR: writes through to disk
```

### Affected tests (currently xfail)
- `tests/types/table/test_misc.py:173` —
  `test_splayed_table_destructive_operations_raise_error`
- `tests/types/table/test_misc.py:208` —
  `test_parted_table_destructive_operations_raise_error`

### What to delete when fixed
- Both xfail markers.
- Any Python-side `_is_readonly` flag that gets added defensively (none
  added by this loop — we explicitly chose to leave the xfail).

### Suggested v2 design
- A new entrypoint: `ray_table_open_for_write(path)` that bypasses COW.
  Default `ray_table_open(path)` produces a read-only handle that **rejects**
  destructive ops with an explicit error code, instead of silently cloning.
- Or: add an attribute flag `RAY_ATTR_READONLY` checked at every mutation
  site.

---

## §5 — DAG rejects literal RAY_LAMBDA in head position

### Problem
v2 DAG compiler accepts only two lambda-call shapes:
1. `((fn [args] body) args)` — literal lambda in head with body inline.
2. `(name args)` where `name` is globally env-bound to a `RAY_LAMBDA`.

A raw `RAY_LAMBDA` pointer in the head (which is what Python naturally
produces from `Fn(...)`) is rejected.

### Why core
Today rayforce-py works around this by **synthesizing a global env name**
(`__pyfn_<counter>`), binding the lambda there, and emitting the named-call
shape. This (a) leaks `__pyfn_*` symbols into the global env on every
distinct apply, (b) requires a counter to avoid collision, (c) makes
debugging harder (stack traces show `__pyfn_42` not the user's lambda).

### Example
```python
double = rf.Fn("(fn [x] (* x 2))")
t.select(y=double.apply(rf.Column("x"))).execute()
# Today: synthesizes (.__pyfn_3 x) and binds __pyfn_3 globally.
# Expected: emit ((fn [x] (* x 2)) x) and have DAG accept it.
```

### Affected code (workarounds in place, no xfail)
- W1, W9: `rayforce/types/table.py:_make_name_sym` (~line 90),
  `rayforce/types/fn.py:_bind_to_env` (~lines 40-53).

### What to delete when fixed
- `Fn._bind_to_env` and the `__pyfn_*` counter.
- `_make_name_sym` callers; replace with literal lambda emission.
- Any test that asserts `__pyfn_*` names exist in env.

### Suggested v2 design
- DAG compiler accepts shape (3): `((<RAY_LAMBDA pointer>) args)` — inline the
  pointed-to lambda body during DAG construction without requiring an env name.

---

## §6 — DAG cannot project `distinct`, `as`-cast, or tz-shift

### Problem
v2 DAG `compile_expr_dag` (`~/rayforce2/src/ops/query.c`) rejects three
projection shapes that are perfectly valid in v1's direct evaluator:

- `(distinct col)` as a projection — DAG falls back to materialize-then-dedup,
  but only if the Python side knows to route around it.
- `(as 'TYPE col)` cast inside SELECT.
- Timestamp `shift_tz` inside SELECT (handled by §3, but the symptom is the
  same — DAG rejects the AST).

### Why core
Today rayforce-py routes around DAG by performing each as a separate
post-SELECT step. This costs an extra full-table pass per workaround. The
DAG could simply accept these projections; they are pure column-wise
transforms.

### Example
```python
t.select(z=rf.Column("x").distinct()).execute()
# Today: DAG rejects; Python materializes and dedups manually (W7).

t.select(z=rf.Column("x").cast("F64")).execute()
# Today: DAG rejects; Python rebuilds table with cast column (W6).
```

### Affected code (workarounds in place)
- W6: `rayforce/types/table.py:~727` (cast).
- W7: `rayforce/types/table.py:~1104` (distinct).
- W3: tz-shift (also covered by §3).

### What to delete when fixed
- The DAG-rejection routing branches in `SelectQuery._compile_projections`
  and the post-pass distinct/cast loops.

### Suggested v2 design
- Whitelist `distinct`, `as`, and `shift_tz` (or its v2 equivalent) as valid
  projection-position operators in the DAG compiler. They are pure functions
  of one column; no fusion blocker.

---

## §7 — DAG filter path rejects untyped `RAY_LIST` columns

### Problem
A Table column that is a `RAY_LIST` (heterogeneous, e.g., constructed from
mixed Python list with no inferable scalar dtype) is rejected by v2 DAG's
filter path, even when the filter predicate is type-agnostic (`is null`,
`==`, `in`).

### Why core
The Python-side workaround (`_coerce_column` in `table.py:~306`) silently
promotes the column to a typed `Vector` if all elements happen to be
homogeneous. This **changes the column's stored type as a side effect of
filtering** — surprising behavior. The DAG should accept LIST in the filter
path and leave column types alone.

### Example
```python
t = rf.Table({"x": rf.List([1, 2, None, 4])})
t.select("x").where(rf.Column("x").is_(None)).execute()
# Today: Python silently coerces "x" to Vector[I64] before filtering.
# Expected: filter on LIST column directly; column type preserved.
```

### Affected code (workaround in place)
- W4: `rayforce/types/table.py:_coerce_column` (~line 306).

### What to delete when fixed
- `_coerce_column` and its callers.

### Suggested v2 design
- DAG filter operators dispatch on element type at runtime for `RAY_LIST`
  columns. Slow path is acceptable — the user opted into LIST semantics.

---

## §8 — `meta table` returns summary, not full schema

### Problem
v2 `meta` builtin (`~/rayforce2/src/ops/builtins.c`) returns a summary dict
with row count and column count, but not the per-column type and attribute
map that v1's `meta` returned.

### Why core
`Table.dtypes` reconstructs the schema by iterating columns and inspecting
each one — O(cols) FFI calls instead of O(1). For wide tables this is a
real cost. The metadata is already known to v2; just expose it.

### Example
```python
t = rf.Table({"a": rf.I64(1), "b": rf.F64(2.0), "c": rf.Symbol("x")})
rf.eval_str("(meta table_t)")  # returns row/col count only
t.dtypes  # rayforce-py reconstructs schema column-by-column
```

### Affected code (workaround in place)
- W5: `rayforce/types/table.py:~676` — Python-side schema reconstruction.

### What to delete when fixed
- `Table.dtypes` reconstruction loop; replace with single `meta` call.

### Suggested v2 design
- `meta table` returns a dict with `name`, `type`, `attrs` per column.

---

## §9 — No-GROUP-BY scalar aggregation broadcasts across input rows

### Problem
`SELECT count(*)`, `SELECT sum(x)` etc. in v2 broadcast the scalar result
across all input rows instead of collapsing to a single row. v1 collapsed
to one row.

### Why core
M17 in `plan.md` patches this Python-side by detecting "all projections
are aggregations & no `.by()`" and applying `.take(1)`. This works but:
(a) every consumer of `Table.select` repeats the detection; (b) the SQL
plugin already had its own copy; (c) `eval_str("(select [count x] t)")`
bypasses the Python detection entirely. The collapse should happen in the
DAG executor.

### Example
```python
t = rf.Table({"x": rf.Vector([1, 2, 3, 4, 5], ray_type=rf.I64)})
t.select(n=rf.Column("x").count()).execute()
# v2 today: 5 rows of [5]
# v1 / expected: 1 row of [5]
```

### Affected code (workaround in place after M17)
- W8: `rayforce/plugins/sql.py:399-403` (existing).
- M17: lifts the same logic into `Table.select`.
- xfail closed by M17 (`_AGG_BROADCASTS`).

### What to delete when fixed
- M17's collapse logic.
- The SQL plugin's pre-existing `.take(1)`.

### Suggested v2 design
- `select` with no GROUP BY and only aggregation projections collapses to
  one row in the DAG executor. Explicit `select [.row x]` style queries
  retain their per-row semantics.

---

## §10 (optional) — `env_get_internal_name_by_fn` reverse lookup

### Problem
v2 dropped this introspection builtin. v1 had it.

### Why core (debatable)
This is a marginal case. M18 in `plan.md` builds the reverse map Python-side
at module import. The Python solution is small (~15 LOC) and self-contained.
There is no strong reason to put this in core unless v2 wants to support
introspection from `eval_str` directly.

### Suggested v2 design (if accepted)
- Add `env_get_internal_name_by_fn` as a unary builtin returning a SYM atom
  for known internals, NULL otherwise.

---

## Summary: what stays as `xfail` after the loop closes

After M17–M25 land, these remain xfail in `tests/`, each pointing at this file:

| Test | Reason / `CORE_FIXES.md` ref |
|---|---|
| `test_operation_divide_scalars` | §1 |
| `_INT_DIV_PROMOTED_TO_FLOAT` (test_fn.py) | §1 |
| `_F64_DIVIDE_FLOORS` (test_sql.py) | §1 |
| `_RECURSIVE_SELF_IN_DAG` (test_fn.py) | §2 |
| `test_splayed_table_destructive_operations_raise_error` | §4 |
| `test_parted_table_destructive_operations_raise_error` | §4 |

= 6 xfails covering 3 distinct core issues (§1, §2, §4). M25 retitles the
existing reasons to point at this file's section IDs.

§3, §5, §6, §7, §8, §9 have **no xfail** — they are silently masked by
Python workarounds (W1–W9, W10–W15). Each section above documents what to
delete when the corresponding core fix lands.
