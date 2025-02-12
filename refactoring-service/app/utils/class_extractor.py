import ast

def extract_class_snippet(code: str, class_name: str) -> str:
    """Extracts a class definition from the given code as a snippet."""
    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else None
                lines = code.splitlines()
                return '\n'.join(lines[start_line:end_line])
        return ""
    except Exception as e:
        return f"Error processing code: {e}"