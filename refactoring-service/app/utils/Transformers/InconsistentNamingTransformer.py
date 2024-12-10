
import ast
import astor
import re

def snake_case(name):
    """Convert a given name to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def camel_case(name):
    """Convert a given name to camelCase."""
    parts = name.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def pascal_case(name):
    """Convert a given name to PascalCase."""
    return ''.join(word.capitalize() for word in name.split('_'))

def refactor_name(name, target_convention):
    """Convert a name to the target naming convention."""
    if target_convention == "snake_case":
        return snake_case(name)
    elif target_convention == "camelCase":
        return camel_case(name)
    elif target_convention == "PascalCase":
        return pascal_case(name)
    else:
        raise ValueError("Unsupported naming convention: " + target_convention)
    
class NamingRefactorer(ast.NodeTransformer):
    def __init__(self, target_convention):
        self.target_convention = target_convention
        self.imported_names = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_names.add(alias.asname or alias.name.split('.')[0])
        return node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imported_names.add(alias.asname or alias.name)
        return node

    def visit_FunctionDef(self, node):
        # Refactor function names
        if node.name not in self.imported_names:
            node.name = refactor_name(node.name, self.target_convention)

        # Refactor argument names
        for arg in node.args.args:
            if arg.arg not in self.imported_names:
                arg.arg = refactor_name(arg.arg, self.target_convention)

        # Recursively refactor function body
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        # Refactor class names
        if node.name not in self.imported_names:
            node.name = pascal_case(node.name)

        # Recursively refactor class body
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        # Refactor variable names
        if node.id not in self.imported_names:
            node.id = refactor_name(node.id, self.target_convention)
        return node