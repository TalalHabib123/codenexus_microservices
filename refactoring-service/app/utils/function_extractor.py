import ast

def extract_function_snippet(code: str, func_name: str) -> str:
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