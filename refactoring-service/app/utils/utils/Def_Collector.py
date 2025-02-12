import ast 


class DefinitionCollector(ast.NodeVisitor):
    """First pass: Collect all defined names in the AST"""
    def __init__(self):
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
        if isinstance(node.ctx, ast.Store):
            self.defined_variables.add(node.id)
        self.generic_visit(node)
        
    def get_definitions(self):
        return {
            'functions': self.defined_functions,
            'classes': self.defined_classes,
            'variables': self.defined_variables
        }
