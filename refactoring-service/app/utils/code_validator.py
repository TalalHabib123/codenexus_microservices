import ast

def is_valid_python_code(code: str) -> bool:
    """Checks if the given Python code is syntactically valid."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False