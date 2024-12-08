import ast

def extract_functions_from_code(code_string):
    """
    Extracts all functions from a Python code string, including whether they are in a class.
    Returns a list of dictionaries with keys:
    - "class_name": str or None
    - "function_name": str (with class if applicable, e.g. ClassName_func)
    - "function_code": str (the full code of the function)
    """

    try:
        tree = ast.parse(code_string)
        lines = code_string.splitlines()

        functions = []

        # We will do a recursive walk of the AST, passing down the current class name context
        def visit(node, current_class=None):
            # If this node is a class, update the current_class context
            if isinstance(node, ast.ClassDef):
                new_class = node.name
                for child in node.body:
                    visit(child, current_class=new_class)
            elif isinstance(node, ast.FunctionDef):
                # Extract the start and end line numbers for the function
                start_lineno = node.lineno - 1
                end_lineno = node.body[-1].end_lineno
                function_code = '\n'.join(lines[start_lineno:end_lineno])

                # Format the function name
                if current_class:
                    function_name = f"{current_class}.{node.name}"
                else:
                    function_name = node.name

                functions.append({
                    "class_name": current_class,
                    "function_name": function_name,
                    "function_code": function_code
                })

                # Visit any nested definitions inside the function (e.g. inner functions)
                for child in node.body:
                    visit(child, current_class=current_class)
            else:
                # Visit children of other node types
                for child in ast.iter_child_nodes(node):
                    visit(child, current_class=current_class)

        visit(tree, current_class=None)
        return functions

    except Exception as e:
        print(f"Error processing the code: {e}")
        return []

# Example usage
if __name__ == "__main__":
    python_code = """
def foo(x):
    return x + 1

def bar(y):
    print("Hello")
    return y * 2

class MyClass:
    def method(self):
        pass
    """
    extracted_functions = extract_functions_from_code(python_code)
    print("Extracted Functions:")
    for func_info in extracted_functions:
        print(f"Class: {func_info['class_name']}, Function: {func_info['function_name']}\n{func_info['function_code']}\n")
