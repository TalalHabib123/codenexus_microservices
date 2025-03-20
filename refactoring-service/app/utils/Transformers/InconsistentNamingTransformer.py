
import ast
import re
import keyword
from collections import defaultdict

class NamingRefactorer(ast.NodeTransformer):
    def __init__(self, target_convention, refactor_functions=True, refactor_classes=True, refactor_vars=True, definitions={}):
        self.target_convention = target_convention
        self.refactor_functions = refactor_functions
        self.refactor_classes = refactor_classes
        self.refactor_vars = refactor_vars
        self.imported_names = set()
        self.defined_classes = definitions.get('classes', set())    
        self.defined_functions = definitions.get('functions', set())
        self.defined_variables = definitions.get("variables", set())
        self.instance_to_class = {}
        self.name_mappings = {}
        self.used_names = set()  # Track all names that have been used
        self.scope_stack = []    # Track current scope for context
        self.name_counters = defaultdict(int)  # Count occurrences of each base name

    def enter_scope(self):
        """Enter a new scope (function or class)."""
        self.scope_stack.append(set())
    
    def exit_scope(self):
        """Exit the current scope."""
        if self.scope_stack:
            self.scope_stack.pop()
    
    def get_name_mappings(self):
        """Return the stored name mappings."""
        return self.name_mappings
    
    def is_name_available(self, name):
        """Check if a name is available in the current scope."""
        if name in self.imported_names:
            return False
        if keyword.iskeyword(name):
            return False
        # Check all scopes from current to global
        for scope in reversed(self.scope_stack):
            if name in scope:
                return False
        return True

    def make_unique_name(self, base_name):
        """Create a unique name based on the base name."""
        if self.is_name_available(base_name):
            self.used_names.add(base_name)
            # Add to current scope if one exists
            if self.scope_stack:
                self.scope_stack[-1].add(base_name)
            return base_name
        
        counter = self.name_counters[base_name]
        while True:
            counter += 1
            new_name = f"{base_name}{counter}"
            if self.is_name_available(new_name):
                self.name_counters[base_name] = counter
                self.used_names.add(new_name)
                # Add to current scope if one exists
                if self.scope_stack:
                    self.scope_stack[-1].add(new_name)
                return new_name

    def visit_FunctionDef(self, node):
        self.enter_scope()
        original_name = node.name
        base_name = self.refactor_name(original_name, self.target_convention)
        refactored_name = self.make_unique_name(base_name)
        node.name = refactored_name
        self.name_mappings[original_name] = refactored_name
        self.defined_functions.add(refactored_name)
        
        # Visit the function body
        self.generic_visit(node)
        self.exit_scope()
        return node

    def visit_ClassDef(self, node):
        self.enter_scope()
        original_name = node.name
        base_name = self.pascal_case(original_name)
        refactored_name = self.make_unique_name(base_name)
        node.name = refactored_name
        self.name_mappings[original_name] = refactored_name
        self.defined_classes.add(refactored_name)
        
        # Visit the class body
        self.generic_visit(node)
        self.exit_scope()
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            original_name = node.id
            if self.refactor_vars:
                base_name = self.refactor_name(original_name, self.target_convention)
                refactored_name = self.make_unique_name(base_name)
                node.id = refactored_name
                self.name_mappings[original_name] = refactored_name
                self.defined_variables.add(refactored_name)
                
                # Add to current scope
                if self.scope_stack:
                    self.scope_stack[-1].add(refactored_name)
                    
        elif isinstance(node.ctx, ast.Load):
            if node.id in self.name_mappings:
                node.id = self.name_mappings[node.id]
                
        return node

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