import ast 


# class MagicNumberTransformer(ast.NodeTransformer):
#     def __init__(self, magic_numbers_details):
#         """
#         Initialize the transformer with the magic numbers details.
#         :param magic_numbers_details: List of dictionaries containing 'magic_number' and 'line_number'.
#         """
#         # Extract only the magic_number values into a set for fast lookup
#         self.magic_numbers_to_refactor = {detail.magic_number for detail in magic_numbers_details}
#         self.magic_numbers = {}  # Maps numbers to their corresponding variable names
#         self.counter = 0  # Counter to create unique variable names
#         self.declarations = []  # List to hold variable declarations

#     def create_var_name(self, number):
#         """
#         Generates a unique variable name for a given number.
#         """
#         var_name = f"magic_number_{self.counter}"
#         self.counter += 1
#         return var_name

#     def visit_Constant(self, node):
#         """
#         Visits constant nodes in the AST and replaces magic numbers with variable references.
#         """
#         if isinstance(node.value, (int, float)) and node.value in self.magic_numbers_to_refactor:
#             if node.value not in self.magic_numbers:
#                 # Generate a variable name and create an assignment node
#                 var_name = self.create_var_name(node.value)
#                 self.magic_numbers[node.value] = var_name
#                 assign_node = ast.Assign(
#                     targets=[ast.Name(id=var_name, ctx=ast.Store())],
#                     value=ast.Constant(value=node.value),
#                     lineno=0,  # No specific line
#                     col_offset=0
#                 )
#                 self.declarations.append(assign_node)
#             # Replace the constant with a variable reference
#             return ast.Name(id=self.magic_numbers[node.value], ctx=ast.Load())
#         return self.generic_visit(node)

class MagicNumberTransformer(ast.NodeTransformer):
     def __init__(self, magic_numbers):
         self.magic_numbers = set(magic_numbers)
         self.var_names = {}  # Map magic number value to variable name
         self.counter = 0
         self.assignments = {}  # Nested dict to track assignments by node
         self.current_function = None
     def visit_FunctionDef(self, node):
         # Track the current function being processed
         previous_function = self.current_function
         self.current_function = node
         # Process the function body
         self.generic_visit(node)
         # Reset the current function
         self.current_function = previous_function
         return node
     def visit_Constant(self, node):
         if isinstance(node.value, (int, float)) and node.value in self.magic_numbers:
             if node.value not in self.var_names:
                 # Create a unique variable name
                 var_name = f"magic_number_{self.counter}"
                 self.var_names[node.value] = var_name
                 self.counter += 1
             
             var_name = self.var_names[node.value]
             
             # Create assignment node
             assign_node = ast.Assign(
                 targets=[ast.Name(id=var_name, ctx=ast.Store())],
                 value=ast.Constant(value=node.value)
             )
             # Track assignments by function or module
             if self.current_function:
                 # For function-scoped magic numbers
                 if self.current_function not in self.assignments:
                     self.assignments[self.current_function] = {}
                 
                 # Add assignment to the function's first body statement
                 if node.value not in self.assignments[self.current_function]:
                     self.assignments[self.current_function][node.value] = assign_node
             else:
                 # For module-level magic numbers
                 if node.value not in self.assignments:
                     self.assignments[node.value] = assign_node
             # Replace constant with variable name
             new_node = ast.Name(id=var_name, ctx=ast.Load())
             ast.copy_location(new_node, node)
             return new_node
         return node

class AssignmentInserter(ast.NodeTransformer):
        def __init__(self, assignments):
            self.assignments = assignments

        def visit_Module(self, node):
            # Insert module-level assignments
            module_assignments = [
                assign for num, assign in self.assignments.items() 
                if not isinstance(assign, dict)
            ]
            node.body = module_assignments + node.body
            return self.generic_visit(node)

        def visit_FunctionDef(self, node):
            # Insert function-level assignments
            if node in self.assignments:
                function_assignments = [
                    assign for num, assign in self.assignments[node].items()
                ]
                node.body = function_assignments + node.body
            return self.generic_visit(node)