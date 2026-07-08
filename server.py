import ast
import math
import operator

from fastmcp import FastMCP

mcp = FastMCP("my-new-mcp-server2")

_SAFE_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
    ast.Mod, ast.Pow, ast.UAdd, ast.USub,
    ast.Call, ast.Attribute, ast.Name, ast.Load,
)

_SAFE_NAMES = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}


def _safe_eval(expr: str) -> float:
    tree = ast.parse(expr.strip(), mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _SAFE_NODES):
            raise ValueError(f"Unsupported operation: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in _SAFE_NAMES:
            raise ValueError(f"Unknown name: {node.id!r}")
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name) and node.func.id in _SAFE_NAMES):
                raise ValueError("Only math functions are allowed")
    return eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, _SAFE_NAMES)


@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Supports +, -, *, /, **, % and all math module functions (sin, cos, sqrt, log, etc.)."""
    try:
        result = _safe_eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    mcp.run()
