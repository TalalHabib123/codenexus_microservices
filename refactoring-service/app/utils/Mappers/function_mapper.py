import ast

def replace_function_in_code(original_code: str, func_name: str, refactored_code: str) -> str:
    """Replaces a function definition in the original code with the provided refactored function snippet."""
    try:
        tree = ast.parse(original_code)
        lines = original_code.splitlines()
        
        if '.' in func_name:
            class_name, func_name = func_name.split('.')
            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    start_line, end_line = None, None
                    for sub_node in node.body:
                        if isinstance(sub_node, ast.FunctionDef) and sub_node.name == func_name:
                            start_line = sub_node.lineno - 1
                            end_line = sub_node.end_lineno if hasattr(sub_node, 'end_lineno') else None
                            break
                    if start_line is not None:
                        indent = ' ' * 4
                        refactored_code = '\n'.join(indent + line for line in refactored_code.splitlines())
                        return '\n'.join(lines[:start_line] + [refactored_code] + lines[end_line:])
        else:
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == func_name:
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else None
                    return '\n'.join(lines[:start_line] + refactored_code.splitlines() + lines[end_line:])
        
        return f"Function '{func_name}' not found in the given code."
    except Exception as e:
        return f"Error processing code: {e}"