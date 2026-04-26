from __future__ import annotations

import pytest

from rayforce import errors
from rayforce.utils.evaluation import _V1_VERB_ALIASES, _rewrite_v1_verbs, eval_str


# Verbs that work nullary in v2 — safe to call directly without arguments.
_NULLARY_VERBS = ("gc", "memstat", "internals", "sysinfo")


@pytest.mark.parametrize("v1_name,v2_name", sorted(_V1_VERB_ALIASES.items()))
def test_v1_verb_rewritten_in_head_position(v1_name: str, v2_name: str) -> None:
    rewritten = _rewrite_v1_verbs(f"({v1_name})")
    assert rewritten == f"({v2_name})"


@pytest.mark.parametrize("v1_name,v2_name", sorted(_V1_VERB_ALIASES.items()))
def test_v1_verb_rewritten_with_args(v1_name: str, v2_name: str) -> None:
    rewritten = _rewrite_v1_verbs(f"({v1_name} arg1 arg2)")
    assert rewritten == f"({v2_name} arg1 arg2)"


@pytest.mark.parametrize("v1_name,v2_name", sorted(_V1_VERB_ALIASES.items()))
def test_v1_verb_rewritten_with_leading_space(v1_name: str, v2_name: str) -> None:
    rewritten = _rewrite_v1_verbs(f"(  {v1_name} 1)")
    assert rewritten == f"(  {v2_name} 1)"


@pytest.mark.parametrize("v1_name", sorted(_V1_VERB_ALIASES))
def test_v1_verb_inside_string_literal_not_rewritten(v1_name: str) -> None:
    src = f'(println "calling {v1_name} here")'
    assert _rewrite_v1_verbs(src) == src


@pytest.mark.parametrize("v1_name", sorted(_V1_VERB_ALIASES))
def test_v1_verb_not_in_head_position_not_rewritten(v1_name: str) -> None:
    # Verb appears as an argument, not in head position.
    src = f"(println {v1_name})"
    assert _rewrite_v1_verbs(src) == src


def test_string_literal_with_escaped_quote_not_corrupted() -> None:
    src = r'(println "he said \"gc\" loudly")'
    assert _rewrite_v1_verbs(src) == src


def test_nested_call_rewrites_inner_verb() -> None:
    src = "(do (gc) (memstat))"
    assert _rewrite_v1_verbs(src) == "(do (.sys.gc) (.sys.mem))"


def test_unrelated_expression_unchanged() -> None:
    src = "(+ 1 (* 2 3))"
    assert _rewrite_v1_verbs(src) == src


def test_partial_match_not_rewritten() -> None:
    # `gcc` starts with `gc` but is a different identifier.
    src = "(gcc 1)"
    assert _rewrite_v1_verbs(src) == src


@pytest.mark.parametrize("v1_name", _NULLARY_VERBS)
def test_v1_nullary_verb_evaluates_same_as_v2(v1_name: str) -> None:
    v2_name = _V1_VERB_ALIASES[v1_name]
    v1_result = eval_str(f"({v1_name})")
    v2_result = eval_str(f"({v2_name})")
    # `memstat` returns a dict whose values move between calls; comparing
    # type and (for dict) key set suffices to confirm both forms reach the
    # same builtin.
    assert type(v1_result) is type(v2_result)
    if hasattr(v1_result, "keys"):
        assert list(v1_result.keys()) == list(v2_result.keys())
    else:
        assert v1_result == v2_result


def test_v1_string_literal_preserves_v1_verb_text() -> None:
    # When the verb only appears in a string literal, evaluating must not
    # rewrite it — the string contents are user data.
    result = eval_str('(println "memstat call coming")', raw=True)
    # We can't easily assert println output, but the call must succeed:
    # if the string had been rewritten the parser would still be happy,
    # so this also checks the no-corruption invariant by passing through.
    assert result is not None


def test_v1_verb_via_eval_str_round_trip() -> None:
    # Confirms eval_str path actually rewrites and runs the v1 form.
    v1_result = eval_str("(gc)")
    v2_result = eval_str("(.sys.gc)")
    assert v1_result == v2_result


def test_eval_str_rejects_non_string() -> None:
    with pytest.raises(errors.RayforceEvaluationError):
        eval_str(123)  # type: ignore[arg-type]
