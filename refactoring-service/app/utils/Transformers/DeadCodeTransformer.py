import ast 

class DeadObjectRemover(ast.NodeTransformer):
    def __init__(self, dead_object, entity_type):
        self.dead_object = dead_object
        self.entity_type = entity_type
        
    def visit_FunctionDef(self, node):
        # Remove the function if its name matches the dead object
        print(self.dead_object == node.name, self.dead_object, node.name, type(self.dead_object),type(node.name) )
        print(self.entity_type == "function")
        if self.entity_type.strip() == "function" and node.name.strip() == self.dead_object.strip():
            print("Removing function")
            return None
        # Process the function body
        node.body = [stmt for stmt in node.body if not self.is_dead_object(stmt)]
        if not node.body:  # If the body is empty, replace it with `pass`
            node.body = [ast.Pass()]
        return self.generic_visit(node)
    def visit_ClassDef(self, node):
        # Remove the class if its name matches the dead object
        if self.entity_type.strip() == "class" and node.name.strip() == self.dead_object.strip():
            return None
        # Process the class body
        node.body = [stmt for stmt in node.body if not self.is_dead_object(stmt)]
        if not node.body:  # If the body is empty, replace it with `pass`
            node.body = [ast.Pass()]
        return self.generic_visit(node)
    def visit_Assign(self, node):
        # Remove the variable assignment if it matches the dead object
        if self.entity_type == "variable":
            node.targets = [target for target in node.targets if not (
                isinstance(target, ast.Name) and target.id == self.dead_object)]
            if not node.targets:  # If no targets remain, remove the assignment
                return None
        return self.generic_visit(node)
    def is_dead_object(self, stmt):
        """Check if the statement corresponds to the dead object."""
        if self.entity_type == "function" and isinstance(stmt, ast.FunctionDef):
            return stmt.name == self.dead_object
        if self.entity_type == "class" and isinstance(stmt, ast.ClassDef):
            return stmt.name == self.dead_object
        if self.entity_type == "variable" and isinstance(stmt, ast.Assign):
            return any(isinstance(target, ast.Name) and target.id == self.dead_object for target in stmt.targets)
        return False
