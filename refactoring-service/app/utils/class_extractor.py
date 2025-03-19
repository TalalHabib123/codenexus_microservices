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
    
def extract_class_or_function_snippet(code: str, name: str) -> str:
    """
    Extracts either:
      - the entire class if `name` is 'ClassName', or
      - the specific method if `name` is 'ClassName.methodName'
    from the given code as a snippet.

    Returns an empty string if not found or upon error.
    """
    try:
        # Parse the user input to separate class and optional method
        parts = name.split('.')
        class_name = parts[0]
        method_name = parts[1] if len(parts) > 1 else None

        tree = ast.parse(code)
        # Look for the specific class definition
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                if not method_name:
                    # If no method is given, return the whole class
                    start_line = node.lineno - 1
                    end_line = getattr(node, 'end_lineno', None)
                    lines = code.splitlines()
                    return '\n'.join(lines[start_line:end_line])

                # If a method is specified, look for it inside the class
                for inner_node in node.body:
                    if isinstance(inner_node, ast.FunctionDef) and inner_node.name == method_name:
                        start_line = inner_node.lineno - 1
                        end_line = getattr(inner_node, 'end_lineno', None)
                        lines = code.splitlines()
                        return '\n'.join(lines[start_line:end_line])

                # If the method isn't found inside the class, return empty
                return ""

        # If the class is not found at all, return empty
        return ""

    except Exception as e:
        return f"Error processing code: {e}"
    

