import ast


class NamingRefactorer(ast.NodeTransformer):
    def __init__(self, mappings, dep_list):
        self.mappings = mappings
        self.dep_list = dep_list
        self.defined_functions = set()
        self.defined_classes = set()
        self.defined_variables = set()
    def visit_FunctionDef(self, node):
        self.defined_functions.add(node.name)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.defined_classes.add(node.name)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if isinstance (node.ctx, ast.Store):
            self.defined_variables.add(node.id)

        if isinstance (node.ctx, ast.Load):
            if not node.id in self.defined_variables and not node.id in self.defined_classes and not node.id in self.defined_functions:
                if node.id in self.dep_list:
                    node.id = self.mappings[node.id]
        return node