# Recursive `self` not bound during DAG β-reduction

A lambda that calls itself via `self` evaluates correctly at the top level but
fails with `error: domain` when applied to a column inside `select`. The DAG's
named-lambda inliner treats `self` as a free variable instead of as a binding
to the enclosing lambda.

## Reproduction

Reproduced against `~/rayforce` head, commit `b3e7bdb3`.

```rfl
;; Define a recursive Fibonacci using `self`.
(set fib (fn [x] (if (< x 2) 1 (+ (self (- x 1)) (self (- x 2))))))

;; Direct application — works.
(println (fib 5))           ;; => 8

;; The same lambda inside select against a column — fails.
(set t (table [n] (list (til 6))))
(println (select [n (fib n)] from t))
;; => error: domain
```

Stdin transcript:

```
$ printf '%s\n' \
    '(set fib (fn [x] (if (< x 2) 1 (+ (self (- x 1)) (self (- x 2))))))' \
    '(println (fib 5))' \
    '(set t (table [n] (list (til 6))))' \
    '(println (select [n (fib n)] from t))' \
  | ~/rayforce/rayforce
lambda
8
┌─ … 6 rows of n ─┐
select:
error: domain
```

## Expected behavior

`(select [n (fib n)] from t)` should produce a 2-column table where the
second column is `[1 1 2 3 5 8]` — the per-row application of `fib`.

The DAG β-reducer must bind `self` to the lambda being inlined, the same way
direct evaluation does, so a recursive lambda passed into a column expression
behaves identically to one called directly.

## Tracking

- xfail marker: `tests/types/test_fn.py::test_fn_fibonacci_with_aggregation`
- Expected resolution: bind `self` during DAG inlining of named lambdas
  (likely in `~/rayforce/src/lang/compile.c` or wherever the named-lambda
  inliner lives).
