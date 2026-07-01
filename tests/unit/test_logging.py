from __future__ import annotations

import ast
from pathlib import Path


def test_core_library_has_no_direct_print_calls():
    for path in Path("src/py_dlt_client").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            assert not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ), f"direct print() found in {path}"
