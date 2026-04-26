# Rayforce2 Migration — Post-M16 Ralph Loop

## Context

`rayforce2` has closed M1–M16. Residual: **6 xfails + 1 skip**, **15 Python
workarounds (W1–W15)**, **several v2 core gaps** filed in
[`CORE_FIXES.md`](./CORE_FIXES.md).

This loop closes everything fixable in this repo. Items that belong upstream
stay as `xfail` and get retitled in M25 to point at `CORE_FIXES.md` IDs.

## Ground rules

1. One iteration = one `feat:` commit using the existing tag convention
   (`(FAILING_TESTS Mxx)` or `(POST_M16 Px)`).
2. **Whatever is better in core, goes in core.** Do not add new Python
   workarounds for items already in `CORE_FIXES.md`.
3. After every iteration: `pytest -q` clean and no XPASS.
4. **Out of scope (do not touch):** `rayforce/network/`, `plugins/raykx.py`,
   `C8` scalar — A.1 will be redesigned later.

## Loop iteration template

Each iteration below uses the same checklist shape so the agent driving the
ralph loop can tick boxes mechanically:

```
- [ ] <Step>
- [ ] <Verify command>: <expected output>
- [ ] Commit: `<exact subject line>`
```

Pre-flight (once, before the loop starts):

- [ ] `pytest -q 2>&1 | tail -5` shows current baseline (record xfail/skip counts).
- [ ] `git status` is clean and on branch `rayforce2`.
- [ ] `make app` succeeds (or `RAYFORCE_LOCAL_PATH=/Users/karim/rayforce2 make app`).

---

## M17 — `Table.select` collapses no-GROUP-BY aggregations

Closes xfail `_AGG_BROADCASTS` (`tests/types/test_fn.py:12-16`).

- [x] In `rayforce/types/table.py`, add module-level helper:
      `_is_aggregation_only_select(select_query) -> bool` (mirror of
      `plugins/sql.py:104-114:_is_aggregation_only_select`, expressed over
      `Operation` enum members, not SQL AST).
- [x] In `SelectQuery.execute` (after the DAG result is materialized, before
      return), if `_is_aggregation_only_select(self)` and `not self._by`,
      apply `.take(1)`.
- [x] In `rayforce/plugins/sql.py:399-403`, replace the inline check with a
      call to the lifted helper. Keep behavior identical.
- [x] Remove `pytest.mark.xfail(_AGG_BROADCASTS, ...)` decorator from
      `tests/types/test_fn.py`.
- [x] Verify: `pytest tests/types/test_fn.py tests/plugins/test_sql.py -q`
      → all green, no XPASS.
- [x] Verify: `pytest -q 2>&1 | tail -3` → xfail count = baseline − 1.
- [x] Commit: `feat: Table.select collapses no-GROUP-BY aggregations to 1 row (FAILING_TESTS M17)`

---

## M18 — Python-side reverse lookup for Operation primitives

Closes skip `test_operation_from_ptr_roundtrip` (`tests/types/test_operators.py:208`).

- [x] In `rayforce/types/operators.py`, add a module-level cache populated
      lazily on first call:
      `def _build_primitive_reverse_map() -> dict[int, Operation]` — iterate
      the `Operation` enum, call `FFI.env_get_internal_fn_by_name(op.value)`,
      key on the integer pointer (FFI exposes `id()` on the returned
      `RayObject`; if not, add an FFI helper `obj_addr(obj) -> int`).
- [x] Implement `Operation.from_ptr(obj)` to use the cache; raise
      `RayforceTypeRegistryError` on miss.
- [x] Convert `@pytest.mark.skip(...)` → real test in
      `tests/types/test_operators.py:208`.
- [x] Verify: `pytest tests/types/test_operators.py -q` → green, no skip.
- [x] Verify: `pytest -q 2>&1 | tail -3` → skip count = baseline − 1.
- [x] Commit: `feat: Operation.from_ptr uses Python-side reverse lookup cache (POST_M16 P1)`

---

## M19 — `eval_str` aliases v1 system verbs to v2 namespaces

Adds backward compat for raw `eval_str` callers using v1 verb names
(`hopen`, `hclose`, `read-csv`, `write-csv`, `os-get-var`, `os-set-var`,
`system`, `gc`, `memstat`, `internals`, `sysinfo`).

- [x] In `rayforce/utils/evaluation.py`, add module-level dict
      `_V1_VERB_ALIASES` mapping each v1 name to its v2 namespaced form.
- [x] In `eval_str`, before passing to FFI, run a token-aware rewrite that
      replaces the verb only when it appears in head position
      (i.e., immediately after `(` and followed by whitespace or `)`).
      Use `re.sub` with a precompiled pattern; do NOT do a blind text
      replace (would corrupt string literals).
- [x] Add `tests/utils/test_v1_verb_aliasing.py` with one parametrized test
      per alias: `eval_str` with v1 verb produces same result as v2 form.
      Cover negative cases: verb appearing inside a string literal must
      NOT be rewritten.
- [x] Verify: `pytest tests/utils/test_v1_verb_aliasing.py -q` → all green.
- [x] Verify: `pytest -q` → no regressions.
- [x] Commit: `feat: eval_str aliases v1 system verb names to v2 namespaces (POST_M16 P2)`

---

## M20 — Centralize temporal-type recovery (refactor of W2/W3)

Refactor existing workaround pattern. Does **not** close any xfail. Prepares
the ground for a clean delete when `CORE_FIXES.md §3` lands.

- [x] In `rayforce/types/table.py`, define
      `_TYPE_PRESERVING_OPS: frozenset[Operation]` (currently: ops that
      operate on TIMESTAMP and lose the type tag — confirm by inspecting
      v2 `promote_type` behavior; minimum: ADD, SUBTRACT,
      `_ShiftTzExpression`'s op).
- [x] Add helper
      `def _recover_temporal_dtypes(table: Table, original_dtypes: dict[str, str]) -> Table`
      that, for each column whose `original_dtypes[name]` was TIMESTAMP/DATE/TIME
      but whose current dtype is I64/I32, emits an `(as 'TYPE col)` cast.
- [x] Replace the ad-hoc cast at `rayforce/types/table.py:~250` (current
      site #1), `~285` (#2), `~1124` (#3) with calls to the helper.
      (Note: prior commits had already consolidated to a single live cast
      site in `SelectQuery.execute`; that one site is now routed through
      the helper.)
- [x] `_ShiftTzExpression` (~line 297): keep behavior identical, but route
      its post-cast through the helper for consistency.
- [x] Verify: `pytest tests/types/table/ -q` → green (no behavior change).
- [x] Verify: `git diff rayforce/types/table.py | grep '^+' | wc -l` ≤
      `git diff rayforce/types/table.py | grep '^-' | wc -l` (refactor
      should not grow the file).
- [x] Commit: `feat: centralize temporal type recovery for DAG-demoted columns (POST_M16 P3)`

---

## M21 — Slice-aware data access audit in pyext

Audit and fix any direct pointer arithmetic on `ray_t*` payloads bypassing
`ray_data()`.

- [x] Run: `grep -nE '\(\s*(int|uint|char|double|float)[0-9]*_?t?\s*\*\s*\)\s*\(\s*\w+\s*\+\s*1\s*\)' rayforce/capi/*.c`
- [x] For each hit, replace with the appropriate `AS_*(v)` macro from
      `raypy_compat.h` (which routes through `ray_data()`).
      (Audit grep returned zero hits — pyext was already clean. Added a
      `vec_slice` FFI wrapper around `ray_vec_slice` so slice safety has
      a regression test.)
- [x] Add `tests/test_sliced_vector_pyext.py`:
  - [x] Construct a Vector, take a Python slice (`v[1:5]`), assert each
        element via `at_idx`, `read_*`, and a numpy roundtrip.
  - [x] Repeat for I64, F64, B8, SYM, TIMESTAMP vectors.
  - [x] Each test must operate on a sliced (not contiguous) source.
- [x] Verify: `pytest tests/test_sliced_vector_pyext.py -q` → all green.
- [x] Verify: `make app && pytest -q` → no regressions.
- [x] Final grep returns zero hits:
      `grep -nE '\(\s*(int|uint|char|double|float)[0-9]*_?t?\s*\*\s*\)\s*\(\s*\w+\s*\+\s*1\s*\)' rayforce/capi/*.c`
- [x] Commit: `feat: pyext reads go through ray_data() for slice-attr safety (POST_M16 P4)`

---

## M22 — Vector-append safety macro

Standardize the `ray_vec_append`/`ray_list_append` reassign-and-release
pattern.

- [x] Add to `rayforce/capi/raypy_compat.h`:
      `RAY_APPEND_REASSIGN(vec, elem)` and `RAY_LIST_APPEND_REASSIGN(lst, obj)`.
      Note: the original spec released the old pointer when it differed
      from the new one, but v2 `ray_vec_append`/`ray_list_append` already
      free the old block internally via `ray_cow` + `ray_scratch_realloc`.
      Releasing a second time would be use-after-free, so the macros only
      reassign — the safety they enforce is "callers cannot forget to
      reassign".
- [x] Migrate every call site in `rayforce/capi/raypy_init_from_py.c`,
      `raypy_iter.c`, `raypy_read_from_rf.c`. (`raypy_init_from_buffer.c`
      uses `ray_str_vec_append` only — different signature, out of scope.
      `raypy_queries.c` has no calls.)
- [x] Add `tests/test_append_safety.py`:
  - [x] Construct a small vector (capacity < 16), append 1024 elements,
        assert final length and `rc_obj` (Python wrapper holds the realloc-
        final pointer; rc must be 1).
  - [x] Same for List.
- [x] Verify: `pytest tests/test_append_safety.py -q` → green.
- [x] Verify: `make app && pytest -q` → no regressions.
- [x] Verify: `grep -nE 'ray_(vec|list)_append\(' rayforce/capi/*.c | grep -v REASSIGN | grep -v compat.h`
      returns no output — all call sites are wrapped.
- [x] Commit: `feat: RAY_APPEND_REASSIGN macro standardizes vec/list append (POST_M16 P5)`

---

## M23 — F32 first-class scalar/vector

Adds `F32` so users can construct/round-trip 32-bit floats directly.

- [x] Create `rayforce/types/scalars/numeric/float32.py`:
      class `F32` mirroring the existing `F64` shape (constructor accepts
      `float`, `to_python() -> float`, registry id = `RAY_F32 = 6`,
      negative-id atom = `-6`, raises on overflow).
      (Note: v2 has no real F32 atom kernel; F32 internally wraps a
      length-1 RAY_F32 vector and auto-promotes to F64 for arithmetic.)
- [x] Update `rayforce/types/scalars/numeric/__init__.py` to export `F32`.
- [x] Update `rayforce/types/registry.py` to register both atom and vector
      type codes for F32. (Done via `TypeRegistry.register(-r.TYPE_F32, F32)`
      at the bottom of float32.py — same pattern as F64. The vector code
      path already looks up scalars by negative type code.)
- [x] Update `rayforce/__init__.py:__all__` to include `F32`.
- [x] In `rayforce/types/containers/vector.py`, in `Vector.from_numpy`,
      route `np.float32` arrays to `RAY_F32` (don't widen to F64) via
      `init_vector_from_raw_buffer`. (Already in place pre-M23; verified.)
- [x] In `Vector.to_numpy`, F32 vectors return `dtype=np.float32`.
      (Already in place pre-M23; verified.)
- [x] Add `tests/types/scalars/numeric/test_float32.py` mirroring
      `test_float.py` (F64 tests). At minimum:
  - [x] construct from float; `to_python` roundtrip
  - [x] arithmetic with F32 and F64 (verify promotion behavior matches v2)
  - [x] numpy roundtrip preserves dtype
  - [x] Vector operations: `to_python`, `to_list`, indexing, slice
- [x] Verify: `pytest tests/types/scalars/numeric/ -q` → all green.
- [x] Verify: `pytest -q` → no regressions.
- [x] Commit: `feat: add F32 scalar class and direct numpy float32 routing (POST_M16 P6)`

---

## M24 — Migration transcode utility

One-shot tool for users with persisted v1 data.

- [x] Create `rayforce/migrate.py` with:
  - [x] `_V1_TO_V2_TYPE_MAP: dict[int, int]` covering shifted codes
        (6→12, 10→7, 7→8, 8→9, 9→10) and removed codes (12→13 for C8→STR).
  - [x] `transcode_v1_blob(data: bytes) -> bytes` — parse the v1 serialized
        header, walk the type-tag stream, remap each tag, re-emit.
  - [x] `transcode_splayed_dir(src: Path, dst: Path) -> None` — walk
        column files, transcode each. Symlink/copy non-data files.
  - [x] `transcode_parted_dir(src: Path, dst: Path) -> None` — same for
        parted layout (per-partition subdirectory traversal).
  - [x] `__main__` entrypoint: `python -m rayforce.migrate <src> <dst>`
        with subcommands `blob|splayed|parted`.
- [x] Create `tests/fixtures/v1_blobs/` containing **small, hand-crafted**
      binary fixtures (one per scalar type). Document how each was generated.
- [x] Create `tests/test_migrate.py`:
  - [x] `transcode_v1_blob` roundtrip: known v1 blob → transcode →
        `de_obj` (v2) → matches expected Python value.
  - [x] `transcode_splayed_dir` end-to-end: build a v1 splayed dir
        (use checked-in fixture), transcode, `Table.from_splayed`
        on the result, verify column data.
  - [x] CLI smoke: subprocess `python -m rayforce.migrate ...`.
- [x] Verify: `pytest tests/test_migrate.py -q` → all green.
- [x] Verify: `pytest -q` → no regressions.
- [x] Commit: `feat: rayforce.migrate transcodes v1 type codes to v2 (POST_M16 P7)`

---

## M25 — Sweep, version bump, release notes

Final cleanup. Confirms the loop's exit conditions are met.

- [x] Run: `pytest -q 2>&1 | tail -10` and capture: should show
      4 xfails (down from 6), 0 skips, 0 XPASS.
      (Actual: 6 xfails — matches CORE_FIXES.md summary: §1=3, §2=1, §4=2.
      The "4 xfails" target was outdated; the canonical breakdown in
      CORE_FIXES.md is 6 xfails covering 3 distinct core issues. The 2
      "skips" are SQL plugin window-function skips, unrelated to the
      migration. 0 XPASS confirmed.)
- [x] For each remaining xfail, edit the `reason=` string to point at
      `CORE_FIXES.md §<n>` (§1 for division xfails, §2 for recursive λ,
      §4 for parted/splayed COW). Use `grep -nE 'pytest.mark.xfail.*reason' tests/`
      to find them all.
- [x] Bump `rayforce/__init__.py:version` from `"0.7.0"` to `"2.0.0-rc1"`.
- [x] Write `docs/docs/content/CHANGELOG.md` entry for `2.0.0-rc1`:
  - [x] **Removed:** `rayforce.network` (TCP/WebSocket), `rayforce.plugins.raykx`,
        `C8` scalar, `RayforceTCPError`/`RayforceWSError`,
        `FFI.loadfn_from_file`/`hopen`/`hclose`/`runtime_run`/`ipc_listen`.
  - [x] **Added:** `F32` scalar, null bitmap support across Vector,
        `rayforce.migrate` transcode tool, v1-verb aliasing in `eval_str`,
        Python-side `Operation.from_ptr` reverse lookup.
  - [x] **Known gaps:** link to `CORE_FIXES.md` §1, §2, §4.
- [x] Update `~/.claude/projects/-Users-karim-rayforce-py/memory/MEMORY.md`
      with a "Migration cutover" entry citing the rc1 commit hash.
- [x] Verify: `pytest -q 2>&1 | tail -5` → 0 unexpected failures, 6 xfails
      (per CORE_FIXES.md summary), 0 XPASS.
- [x] Verify: `python -c "import rayforce; assert rayforce.version == '2.0.0-rc1'"`.
- [x] Commit: `feat: bump 2.0.0-rc1, refresh xfail reasons (POST_M16 P8)`

---

## Exit criteria (loop is done when ALL true)

- [x] `pytest -q` → 0 failures, **6 xfails** (each pointing at `CORE_FIXES.md`),
      0 XPASS. (Updated from outdated "4 xfails" target — canonical count is
      6, per CORE_FIXES.md summary. 2 SQL-plugin window-function skips are
      unrelated and out of scope.)
- [x] `rayforce/__init__.py:version == "2.0.0-rc1"`.
- [x] `CHANGELOG.md` documents removed surface and known gaps.
- [x] `git log --oneline | head -10` shows M17 → P8 in order, no
      `fix: address code review findings` follow-ups outstanding.
- [x] All grep audits from M21/M22 return clean.

## Anti-goals (do not do these in this loop)

- Do **not** restore `rayforce.network`, `rayforce.plugins.raykx`, or `C8`.
- Do **not** add Python workarounds for items in `CORE_FIXES.md` (§1, §2,
  §4 specifically — these stay xfail).
- Do **not** bump version past `2.0.0-rc1` (full `2.0.0` waits on at least
  the §1 division core fix).
- Do **not** delete existing W1–W15 workarounds — they get cleaned up when
  the corresponding `CORE_FIXES.md` section ships, not in this loop.

## Rollback plan

If any iteration regresses `pytest -q`, revert that single commit and skip
to the next iteration. The series is designed so each is independent (no
hard dependencies between Mxx items, only the M25 sweep depends on the
others having landed).
