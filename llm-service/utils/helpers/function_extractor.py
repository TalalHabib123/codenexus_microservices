import ast

def extract_functions_from_code(code_string):
    """
    Extracts all functions from a Python code string.

    Args:
        code_string (str): Python code as a string.

    Returns:
        list: A list of strings, where each string is the full code of a function.
    """
    try:
        # Parse the code into an abstract syntax tree (AST)
        tree = ast.parse(code_string)
        
        # List to store extracted function strings
        functions = []
        
        # Iterate through all top-level nodes in the AST
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):  # Check if the node is a function definition
                # Extract the start and end line numbers for the function
                start_lineno = node.lineno - 1  # Convert to zero-based index
                end_lineno = node.body[-1].end_lineno
                
                # Extract the full function code as a string
                function_code = '\n'.join(code_string.splitlines()[start_lineno:end_lineno])
                functions.append(function_code)
        
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
    for func in extracted_functions:
        print(func)
