import ast

def extract_classes_from_code(code_string):
    """
    Extracts all classes from a Python code string.

    Args:
        code_string (str): Python code as a string.

    Returns:
        list: A list of strings, where each string is the full code of a class.
    """
    try:
        # Parse the code into an abstract syntax tree (AST)
        tree = ast.parse(code_string)
        
        # List to store extracted class strings
        classes = []
        
        # Iterate through all top-level nodes in the AST
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):  # Check if the node is a class definition
                # Extract the start and end line numbers for the class
                start_lineno = node.lineno - 1  # Convert to zero-based index
                end_lineno = max(n.end_lineno for n in ast.walk(node) if hasattr(n, 'end_lineno'))
                
                # Extract the full class code as a string
                class_code = '\n'.join(code_string.splitlines()[start_lineno:end_lineno])
                classes.append(class_code)
        
        return classes
    except Exception as e:
        print(f"Error processing the code: {e}")
        return []

# Example usage
if __name__ == "__main__":
    python_code = """
def foo(x):
    return x + 1

class MyClass:
    def method(self):
        print("Method in MyClass")

class AnotherClass:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}"

def bar(y):
    print("Outside function")
    return y * 2
    """
    extracted_classes = extract_classes_from_code(python_code)
    print("Extracted Classes:")
    for cls in extracted_classes:
        print(cls)
