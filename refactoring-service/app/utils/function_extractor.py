import ast
from typing import Dict, Optional, List

def extract_function_snippet(
    code: str, 
    func_name: str
) -> str:
    """Extracts a function definition from the given code as a snippet."""
    try:
        tree = ast.parse(code)
        lines = code.splitlines()
        
        if '.' in func_name:
            class_name, func_name = func_name.split('.')
            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for sub_node in node.body:
                        if isinstance(sub_node, ast.FunctionDef) and sub_node.name == func_name:
                            start_line = sub_node.lineno - 1
                            end_line = sub_node.end_lineno if hasattr(sub_node, 'end_lineno') else None
                            return '\n'.join(lines[start_line:end_line])
        else:
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == func_name:
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else None
                    return '\n'.join(lines[start_line:end_line])
        
        return f"Function '{func_name}' not found in the given code."
    except Exception as e:
        return f"Error processing code: {e}"

# ──────────────────────────────────────────────────────────────────────────────
# helper: build full dotted name of a Call’s callee
# ──────────────────────────────────────────────────────────────────────────────
def _get_full_name(node: ast.AST) -> str | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


# ──────────────────────────────────────────────────────────────────────────────
# helper: map every child → parent so we can climb to the surrounding statement
# ──────────────────────────────────────────────────────────────────────────────
def _build_parent_map(tree: ast.AST) -> Dict[ast.AST, ast.AST]:
    parent_map: Dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parent_map[child] = parent
    return parent_map


# ──────────────────────────────────────────────────────────────────────────────
# main extractor
# ──────────────────────────────────────────────────────────────────────────────
def extract_function_calls(
    additional_files: Dict[str, str],
    function_name: str,
) -> Optional[Dict[str, str]]:
    """
    For each file, return **one string** containing every call-site to
    *function_name* (including assignments), separated by a blank line.
    """
    extracted: Dict[str, str] = {}

    for file_path, code in additional_files.items():
        try:
            tree  = ast.parse(code)
            pmap  = _build_parent_map(tree)
            lines = code.splitlines()
            calls_src: List[str] = []

            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue

                callee = _get_full_name(node.func)
                if callee != function_name:
                    continue

                # climb to the enclosing statement (Assign, Expr, Return, …)
                stmt = node
                while stmt and not isinstance(stmt, ast.stmt):
                    stmt = pmap.get(stmt)          # move to parent

                if stmt is None:
                    continue

                # get the full source segment of that statement
                src = ast.get_source_segment(code, stmt)
                if src is None:  # < Py3.8 fallback
                    start = stmt.lineno - 1
                    end   = getattr(stmt, "end_lineno", stmt.lineno)
                    src   = "\n".join(lines[start:end])

                calls_src.append(src.rstrip())

            if calls_src:
                # join every extracted call-site with a blank line
                extracted[file_path] = "\n\n".join(calls_src)

        except Exception as exc:
            print(f"[extract_function_calls] Error in '{file_path}': {exc}")

    return extracted or None

if __name__ == "__main__":
    import textwrap

    additional_files = {
        "file1.py": textwrap.dedent(
            """
            import math

            def foo():
                var1 = func1(var2, var3, var4 \\
                             ,var5)

            def bar():
                func2(func1(var1, var2, var3))
                other.func1(alpha, beta)
            """
        ),
        "file2.py": textwrap.dedent(
            """
            def baz():
                # This call should NOT appear (different name)
                func2(1, 2, 3)
                
            def func1():
                func2(1, 2, 3)
            """
        ),
    }
    
    calls = extract_function_calls(additional_files, "func1")

    # Pretty-print the result
    if not calls:
        print("No calls found.")
    else:
        for path, snippet in calls.items():
            print(f"--- {path} ---")
            print(snippet)
            print()