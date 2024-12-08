import ast

class UnreachableLineRemover(ast.NodeTransformer):
    def __init__(self, unreachable_lines):
        self.unreachable_lines = set(unreachable_lines)  # Use a set for efficient lookup
    def generic_visit(self, node):
        # Check if the node's line number is in the unreachable list
        if hasattr(node, 'lineno') and node.lineno in self.unreachable_lines:
            return None  # Remove the node
        return super().generic_visit(node)