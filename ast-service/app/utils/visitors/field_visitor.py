import ast
from collections import defaultdict

class TemporaryFieldAnalyzer(ast.NodeVisitor):
    def __init__(self):
        # Track field declarations and usages
        self.fields = defaultdict(lambda: {
            'declared_lines': set(),
            'used_lines': set(),
            'declared_in_methods': set(),
            'used_in_methods': set(),
            'conditionally_declared_lines': set()
        })
        self.current_method = None
        self.in_conditional = False

    def visit_ClassDef(self, node):
        """Visit each class and analyze its fields and methods."""
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Track the current method being analyzed."""
        prev_method = self.current_method
        self.current_method = node.name
        self.generic_visit(node)
        self.current_method = prev_method

    def visit_If(self, node):
        """Track conditional declarations of fields."""
        prev_conditional = self.in_conditional
        self.in_conditional = True
        self.generic_visit(node)
        self.in_conditional = prev_conditional

    def visit_Assign(self, node):
        """Track field declarations (e.g., self.field)."""
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                attr = target
                if isinstance(attr.value, ast.Name) and attr.value.id == 'self':
                    field_name = attr.attr
                    self.fields[field_name]['declared_lines'].add(node.lineno)
                    self.fields[field_name]['declared_in_methods'].add(self.current_method)
                    if self.in_conditional:
                        self.fields[field_name]['conditionally_declared_lines'].add(node.lineno)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Track field usages (e.g., self.field)."""
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            field_name = node.attr
            lineno = getattr(node, 'lineno', None) or getattr(node.value, 'lineno', None)
            if lineno is None:
                # Try to find the line number from parent nodes
                lineno = self.get_parent_lineno(node)
            if lineno:
                self.fields[field_name]['used_lines'].add(lineno)
            self.fields[field_name]['used_in_methods'].add(self.current_method)
        self.generic_visit(node)

    def get_parent_lineno(self, node):
        """Recursively get line number from parent nodes."""
        parent = getattr(node, 'parent', None)
        while parent:
            lineno = getattr(parent, 'lineno', None)
            if lineno is not None:
                return lineno
            parent = getattr(parent, 'parent', None)
        return None

    def generic_visit(self, node):
        """Override generic_visit to set parent nodes."""
        for child in ast.iter_child_nodes(node):
            child.parent = node
            self.visit(child)

    def analyze(self):
        """Analyze the tracked fields to detect temporary fields."""
        results = []
        for field_name, info in self.fields.items():
            declared_lines = info['declared_lines']
            used_lines = info['used_lines']
            declared_methods = info['declared_in_methods']
            used_methods = info['used_in_methods']
            conditional_lines = info['conditionally_declared_lines']

            # Field declared but never used
            if not used_lines:
                results.append(
                    f"Field '{field_name}' declared at lines {sorted(declared_lines)} is never used."
                )

            # Field declared and used only in the same method
            elif declared_methods == used_methods and len(used_methods) == 1:
                method = next(iter(used_methods))
                results.append(
                    f"Field '{field_name}' is declared and used only in method '{method}'. "
                    f"Consider making it a local variable. Declared at {sorted(declared_lines)}, used at {sorted(used_lines)}."
                )

            # Field declared in __init__ but only used in one other method
            elif '__init__' in declared_methods and len(used_methods - {'__init__'}) == 1:
                method = next(iter(used_methods - {'__init__'}))
                results.append(
                    f"Field '{field_name}' is declared in __init__ but only used in method '{method}'. "
                    f"Consider passing it as a parameter to '{method}'. Declared at {sorted(declared_lines)}, used at {sorted(used_lines)}."
                )

            # Field used only once across the class
            elif len(used_lines) == 1:
                results.append(
                    f"Field '{field_name}' is used only once at line {next(iter(used_lines))}. Consider whether it is needed."
                )

            # Field conditionally declared but not widely used
            elif conditional_lines and len(used_lines) < len(declared_lines) * 2:
                results.append(
                    f"Field '{field_name}' is conditionally declared at lines {sorted(conditional_lines)} and used infrequently."
                )

        return results