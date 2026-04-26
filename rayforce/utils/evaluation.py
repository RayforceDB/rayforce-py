from __future__ import annotations

import re
import typing as t

from rayforce import _rayforce_c as r
from rayforce import errors
from rayforce.ffi import FFI
from rayforce.utils.conversion import ray_to_python

_V1_VERB_ALIASES: dict[str, str] = {
    "hopen": ".ipc.open",
    "hclose": ".ipc.close",
    "read-csv": ".csv.read",
    "write-csv": ".csv.write",
    "os-get-var": ".os.getenv",
    "os-set-var": ".os.setenv",
    "system": ".sys.exec",
    "gc": ".sys.gc",
    "memstat": ".sys.mem",
    "internals": ".sys.build",
    "sysinfo": ".sys.info",
}

# Match either a string literal (passthrough) or a v1 verb in head position
# (immediately after `(` and followed by whitespace or `)`).
_V1_VERB_PATTERN = re.compile(
    r'"(?:\\.|[^"\\])*"'
    r"|(?P<head>\(\s*)(?P<verb>" + "|".join(re.escape(k) for k in _V1_VERB_ALIASES) + r")(?=[\s)])"
)


def _rewrite_v1_verbs(expr: str) -> str:
    def repl(m: re.Match[str]) -> str:
        verb = m.group("verb")
        if verb is None:
            return m.group(0)
        return m.group("head") + _V1_VERB_ALIASES[verb]

    return _V1_VERB_PATTERN.sub(repl, expr)


def eval_str(expr: str, *, raw: bool = False) -> t.Any:
    if not isinstance(expr, str):
        raise errors.RayforceEvaluationError(f"Expression must be a string, got {type(expr)}")

    expr = _rewrite_v1_verbs(expr)
    result_ptr = FFI.eval_str(FFI.init_string(expr))
    if FFI.get_obj_type(result_ptr) == r.TYPE_ERR:
        raise errors.RayforceEvaluationError(f"Evaluation error: {FFI.get_error_obj(result_ptr)}")

    return result_ptr if raw else ray_to_python(result_ptr)


def eval_obj(obj: t.Any) -> t.Any:
    if hasattr(obj, "ptr"):
        ptr = obj.ptr
    elif isinstance(obj, r.RayObject):
        ptr = obj
    else:
        raise errors.RayforceEvaluationError(f"Cannot evaluate {type(obj)}")

    result_ptr = FFI.eval_obj(ptr)
    if FFI.get_obj_type(result_ptr) == r.TYPE_ERR:
        raise errors.RayforceEvaluationError(f"Evaluation error: {FFI.get_error_obj(result_ptr)}")

    return ray_to_python(result_ptr)
