"""Phase 4 — Secure Execution of LLM-Generated Pandas Code.

Generated code is parsed with Python's `ast` module and rejected if it touches
imports, the filesystem, the network, reflection builtins, loops, or dunder
attributes. Only code that survives is executed — against a deep copy of the
session's DataFrame, with a restricted `__builtins__` dict.

A defensible sandbox for a demo deployment, not airtight isolation: `exec`
still runs in-process. A production system would add a separate,
resource-limited process or container on top of this static check.
"""
import ast
import builtins
import logging

from app.utils.plotting import fig_to_base64

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)

FORBIDDEN_NAMES = {
    "os", "sys", "subprocess", "shutil", "socket", "requests", "pathlib", "importlib",
    "open", "eval", "exec", "compile", "__import__", "input",
    "globals", "locals", "vars", "getattr", "setattr", "delattr",
    "exit", "quit", "help", "breakpoint", "memoryview",
}

# Direct pandas one-liners never need imports, defs, loops, or exception handling.
FORBIDDEN_NODE_TYPES = (
    ast.Import, ast.ImportFrom,
    ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
    ast.With, ast.AsyncWith, ast.Try,
    ast.For, ast.AsyncFor, ast.While,
    ast.Global, ast.Nonlocal,
)

_SAFE_BUILTIN_NAMES = [
    "len", "range", "sum", "min", "max", "round", "abs", "sorted",
    "list", "dict", "set", "tuple", "str", "int", "float", "bool",
    "enumerate", "zip", "map", "filter", "any", "all", "reversed",
    "isinstance", "type",
]
SAFE_BUILTINS = {name: getattr(builtins, name) for name in _SAFE_BUILTIN_NAMES}
SAFE_BUILTINS.update({"None": None, "True": True, "False": False})


class CodeSafetyError(Exception):
    """Raised when LLM-generated code fails the static safety check."""


class CodeExecutionError(Exception):
    """Raised when code that passed the safety check still fails at runtime."""


def validate_code_safety(code: str) -> ast.AST:
    """Parse `code` and raise CodeSafetyError if it violates any sandbox rule."""
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise CodeSafetyError(f"Generated code has a syntax error: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, FORBIDDEN_NODE_TYPES):
            raise CodeSafetyError(f"Generated code uses a disallowed construct: {type(node).__name__}.")
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise CodeSafetyError(f"Generated code references a disallowed name: '{node.id}'.")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise CodeSafetyError("Generated code accesses a disallowed dunder attribute.")

    return tree


def _serialize_result(result: object, max_rows: int = 50) -> object:
    """Turn whatever the generated code assigned to `result` into JSON-safe data."""
    if result is None:
        return None
    if isinstance(result, pd.DataFrame):
        return result.head(max_rows).to_dict(orient="records")
    if isinstance(result, pd.Series):
        return result.head(max_rows).to_dict()
    if isinstance(result, np.integer):
        return int(result)
    if isinstance(result, np.floating):
        return float(result)
    if isinstance(result, np.ndarray):
        return result.tolist()[:max_rows]
    if isinstance(result, (int, float, str, bool, list, dict)):
        return result
    return str(result)


def execute_pandas_code(code: str, df: pd.DataFrame) -> dict:
    """Validate then execute generated code against a *copy* of the session's DataFrame.

    Returns {"result": <JSON-safe value>, "chart_base64": <str | None>}.
    """
    validated_tree = validate_code_safety(code)

    plt.close("all")
    sandbox_locals = {
        "df": df.copy(deep=True),
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
        "result": None,
    }
    sandbox_globals = {"__builtins__": SAFE_BUILTINS}

    try:
        compiled = compile(validated_tree, filename="<llm_generated_code>", mode="exec")
        exec(compiled, sandbox_globals, sandbox_locals)
    except Exception as exc:
        plt.close("all")
        raise CodeExecutionError(str(exc)) from exc

    chart_base64 = None
    if plt.get_fignums():
        chart_base64 = fig_to_base64(plt.gcf())
        plt.close("all")

    return {"result": _serialize_result(sandbox_locals.get("result")), "chart_base64": chart_base64}
