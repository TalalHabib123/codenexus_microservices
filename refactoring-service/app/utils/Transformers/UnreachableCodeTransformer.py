import ast

class UnreachableLineRemover(ast.NodeTransformer):
    def __init__(self, unreachable_lines):
        self.unreachable_lines = set(unreachable_lines)  # Use a set for efficient lookup

    def generic_visit(self, node):
        """
        Visits all AST nodes, removing those marked as unreachable.
        Ensures structural integrity by adding `pass` or `continue` where necessary.
        """
        if hasattr(node, 'lineno') and node.lineno in self.unreachable_lines:
            return None  # Remove the node
        return super().generic_visit(node)

    def visit_If(self, node):
        """
        Handles if-statements by checking if the body or orelse becomes empty.
        Adds a `pass` statement if the body is empty.
        """
        node.body = [n for n in map(self.visit, node.body) if n is not None]
        node.orelse = [n for n in map(self.visit, node.orelse) if n is not None]

        if not node.body:
            node.body = [ast.Pass()]  # Add a pass statement if the body is empty
        return node

    def visit_FunctionDef(self, node):
        """
        Handles function definitions by checking if the body becomes empty.
        Adds a `pass` statement if the body is empty.
        """
        node.body = [n for n in map(self.visit, node.body) if n is not None]

        if not node.body:
            node.body = [ast.Pass()]  # Add a pass statement if the function body is empty
        return node

    def visit_For(self, node):
        """
        Handles for-loops by checking if the body or orelse becomes empty.
        Adds a `pass` or `continue` statement where necessary.
        """
        node.body = [n for n in map(self.visit, node.body) if n is not None]
        node.orelse = [n for n in map(self.visit, node.orelse) if n is not None]

        if not node.body:
            node.body = [ast.Continue()]  # Add a continue statement if the loop body is empty
        return node

    def visit_While(self, node):
        """
        Handles while-loops by checking if the body or orelse becomes empty.
        Adds a `pass` or `continue` statement where necessary.
        """
        node.body = [n for n in map(self.visit, node.body) if n is not None]
        node.orelse = [n for n in map(self.visit, node.orelse) if n is not None]

        if not node.body:
            node.body = [ast.Continue()]  # Add a continue statement if the loop body is empty
        return node

    def visit_Try(self, node):
        """
        Handles try-except blocks by checking if all bodies (try, except, else, final) become empty.
        Adds a `pass` statement where necessary.
        """
        node.body = [n for n in map(self.visit, node.body) if n is not None]
        for handler in node.handlers:
            handler.body = [n for n in map(self.visit, handler.body) if n is not None]
        node.orelse = [n for n in map(self.visit, node.orelse) if n is not None]
        node.finalbody = [n for n in map(self.visit, node.finalbody) if n is not None]

        if not node.body:
            node.body = [ast.Pass()]  # Add a pass statement if the try body is empty
        for handler in node.handlers:
            if not handler.body:
                handler.body = [ast.Pass()]  # Add a pass statement if an except body is empty
        if not node.orelse:
            node.orelse = [ast.Pass()]  # Add a pass statement if the else body is empty
        if not node.finalbody:
            node.finalbody = [ast.Pass()]  # Add a pass statement if the final body is empty
        return node

    def visit_With(self, node):
        """
        Handles with-statements by checking if the body becomes empty.
        Adds a `pass` statement if the body is empty.
        """
        node.body = [n for n in map(self.visit, node.body) if n is not None]

        if not node.body:
            node.body = [ast.Pass()]  # Add a pass statement if the with body is empty
        return node
