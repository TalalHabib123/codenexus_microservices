import ast
import re
import keyword


class NamingRefactorer(ast.NodeTransformer):
    def __init__(self, target_convention, refactor_functions=True, refactor_classes=True, refactor_vars=True):
        self.target_convention = target_convention
        self.refactor_functions = refactor_functions
        self.refactor_classes = refactor_classes
        self.refactor_vars = refactor_vars
        self.imported_names = set()
        self.defined_classes = set()
        self.defined_functions = set() 
        self.defined_variables = set()
        self.instance_to_class = {}  # Track variable-to-class mapping
        self.name_mappings = {}  # Store the mappings of original names to refactored names

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_names.add(alias.asname or alias.name.split('.')[0])
        return node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imported_names.add(alias.asname or alias.name)
        return node

    def visit_FunctionDef(self, node):
        self.defined_functions.add(node.name)
        refactored_name = self.refactor_name(node.name, self.target_convention)
        node.name = refactored_name
        print(refactored_name)
        self.name_mappings[node.name] = refactored_name
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        self.defined_classes.add(node.name)
        refactored_name = self.pascal_case(node.name)
        node.name = refactored_name
        self.name_mappings[node.name] = refactored_name
        self.generic_visit(node)
        return node

    def visit_Assign(self, node):
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if isinstance (node.ctx, ast.Store):
            self.defined_variables.add(node.id)
            self.refactor_name(node.id, self.target_convention)
        if isinstance (node.ctx, ast.Load):
            if node.id in self.defined_classes:
                original_name = node.id
                node.id = self.pascal_case(node.id)
                self.store_mapping(original_name, node.id)
            elif node.id in self.defined_functions or node.id in self.defined_variables:
                original_name = node.id
                node.id = self.refactor_name(node.id, self.target_convention)
                self.store_mapping(original_name, node.id)
        return node

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            instance_name = node.value.id
            if instance_name in self.instance_to_class:
                class_name = self.instance_to_class[instance_name]
                if class_name in self.defined_classes:
                    original_name = node.attr
                    node.attr = self.refactor_name(node.attr, self.target_convention)
                    self.store_mapping(original_name, node.attr)
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node):
        if self.refactor_vars and isinstance(node.target, ast.Name):
            original_name = node.target.id
            node.target.id = self.refactor_name(node.target.id, self.target_convention)
            self.store_mapping(original_name, node.target.id)
        if node.annotation:
            self.generic_visit(node.annotation)
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        return node

    def store_mapping(self, original_name, refactored_name):
        """Store the mapping between the original name and the refactored name."""
        if original_name != refactored_name:
            self.name_mappings[original_name] = refactored_name

    def get_name_mappings(self):
        """Return the stored name mappings."""
        return self.name_mappings

    # Utility functions for naming conventions
    def snake_case(self, name):
        """Convert a given name to snake_case."""
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def camel_case(self, name):
        """Convert a given name to camelCase."""
        parts = name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    def pascal_case(self, name):
        """Convert a given name to PascalCase."""
        name = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
        return ''.join(word.capitalize() for word in name.split('_'))

    def is_valid_name(self, name):
        """Check if a name is a valid Python identifier and not a reserved word."""
        return name.isidentifier() and not keyword.iskeyword(name)

    def refactor_name(self, name, target_convention):
        """Convert a name to the target naming convention."""
        if target_convention == "snake_case":
            new_name = self.snake_case(name)
        elif target_convention == "camelCase":
            new_name = self.camel_case(name)
        elif target_convention == "PascalCase":
            new_name = self.pascal_case(name)
        else:
            raise ValueError("Unsupported naming convention: " + target_convention)

        return new_name if self.is_valid_name(new_name) else name

    def refactor_docstring(self, docstring, target_convention):
        """Replace variable names in docstring to match the target naming convention."""
        pattern = r"\b[A-Za-z_][A-Za-z0-9_]*\b"
        return re.sub(pattern, lambda m: self.refactor_name(m.group(0), target_convention), docstring)
