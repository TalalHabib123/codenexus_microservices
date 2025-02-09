import ast

def replace_class_in_code(original_code: str, class_name: str, refactored_code: str) -> str:
    """Replaces a class definition in the original code with the provided refactored code snippet."""
    try:
        tree = ast.parse(original_code)
        lines = original_code.splitlines()
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else None
                return '\n'.join(lines[:start_line] + refactored_code.splitlines() + lines[end_line:])
        
        return f"Class '{class_name}' not found in the given code."
    except Exception as e:
        return f"Error processing code: {e}"
    
