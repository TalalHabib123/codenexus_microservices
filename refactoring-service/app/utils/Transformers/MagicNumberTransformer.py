import ast 

class MagicNumberTransformer(ast.NodeTransformer):
    def __init__(self, magic_numbers_to_refactor):
        self.magic_numbers_to_refactor = set(magic_numbers_to_refactor)
        self.magic_numbers = {}  # Maps numbers to their corresponding variable names
        self.counter = 0  # Counter to create unique variable names
        self.declarations = []  # List to hold variable declarations
    def create_var_name(self, number):
        """
        Generates a unique variable name for a given number.
        """
        var_name = f"magic_number_{self.counter}"
        self.counter += 1
        return var_name
    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)) and node.value in self.magic_numbers_to_refactor:
            if node.value not in self.magic_numbers:
                # Generate a variable name and create an assignment node
                var_name = self.create_var_name(node.value)
                self.magic_numbers[node.value] = var_name
                assign_node = ast.Assign(
                    targets=[ast.Name(id=var_name, ctx=ast.Store())],
                    value=ast.Constant(value=node.value),
                    lineno=0,  # No specific line
                    col_offset=0
                )
                self.declarations.append(assign_node)
            # Replace the constant with a variable reference
            return ast.Name(id=self.magic_numbers[node.value], ctx=ast.Load())
        return self.generic_visit(node)
