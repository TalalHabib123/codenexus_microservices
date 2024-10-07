import ast
from collections import defaultdict

def track_object_usage(code_ast: str, class_name: str):
    # Parse the code into an AST
    tree = code_ast
    
    # To track objects of the specified class and their method and variable calls
    objects = {}
    method_calls = set()
    variable_accesses = set()

    class ObjectTracker(ast.NodeVisitor):
        def visit_Assign(self, node):
            # Check if the assigned value is an instantiation of the target class
            if isinstance(node.value, ast.Call):
                # Check if the instantiation is a simple name (e.g., "Test") or an attribute (e.g., "MyClassFile.Test")
                if (isinstance(node.value.func, ast.Name) and node.value.func.id == class_name) or \
                   (isinstance(node.value.func, ast.Attribute) and node.value.func.attr == class_name):
                    # Track variable names that are instances of the class
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            objects[target.id] = class_name
            self.generic_visit(node)

        def visit_Attribute(self, node):
            # Check if the attribute is called on a tracked object
            if isinstance(node.value, ast.Name) and node.value.id in objects:
                if isinstance(node.ctx, ast.Load):
                    variable_accesses.add(node.attr)
            self.generic_visit(node)
        
        def visit_Call(self, node):
            # Check if the call is on an attribute of a tracked object
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id in objects:
                    method_calls.add(node.func.attr)
            self.generic_visit(node)

    tracker = ObjectTracker()
    tracker.visit(tree)

    # Remove variable accesses that are actually method calls
    variable_accesses -= method_calls

    return {
        "methods": sorted(method_calls),
        "variables": sorted(variable_accesses)
    }
    
class ClassVisitor(ast.NodeVisitor):
    def __init__(self):
        self.class_details = []
        self.defined_functions = set()
        self.used_functions = set()
        self.defined_variables = set()
        self.used_variables_count = defaultdict(int) 
        self.class_instances = {}  

    def visit_ClassDef(self, node):
        class_name = node.name
        class_functions = set()
        class_variables = set()

        for body_item in node.body:
            if isinstance(body_item, ast.FunctionDef):
                class_functions.add(body_item.name)
                self.defined_functions.add(f"{class_name}.{body_item.name}") 
                
                # Iterate over the body of the function
                for subbody_item in body_item.body:
                    if isinstance(subbody_item, ast.Call):
                        if isinstance(subbody_item.func, ast.Attribute):
                            full_func_name = self.get_full_name(subbody_item.func)
                            self.used_functions.add(full_func_name)
                        elif isinstance(subbody_item.func, ast.Name):
                            self.used_functions.add(subbody_item.func.id)
                    elif isinstance(subbody_item, ast.Assign):
                        for target in subbody_item.targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                var_name = target.attr
                                class_variables.add(var_name)
                                self.defined_variables.add(f"{class_name}.{var_name}") 

            elif isinstance(body_item, ast.Assign):
                for target in body_item.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        var_name = target.attr
                        class_variables.add(var_name)
                        self.defined_variables.add(f"{class_name}.{var_name}")

        self.class_details.append({
            'class_name': class_name,
            'functions': list(class_functions),
            'variables': list(class_variables)
        })

        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            full_func_name = self.get_full_name(node.func)
            if isinstance(node.func.value, ast.Name) and node.func.value.id in self.class_instances:
                class_name = self.class_instances[node.func.value.id]
                self.used_functions.add(f"{class_name}.{node.func.attr}")
            else:
                self.used_functions.add(full_func_name)
        elif isinstance(node.func, ast.Name):
            self.used_functions.add(node.func.id)

        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            var_name = node.id
            if var_name in self.class_instances:
                self.used_variables_count[var_name] += 1

        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            var_name = node.attr
            for class_detail in self.class_details:
                if var_name in class_detail['variables']:
                    qualified_var = f"{class_detail['class_name']}.{var_name}"
                    self.used_variables_count[qualified_var] += 1
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            class_name = node.value.func.id
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.class_instances[target.id] = class_name

        self.generic_visit(node)

    def get_full_name(self, node):
        if isinstance(node, ast.Attribute):
            return self.get_full_name(node.value) + '.' + node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return ''

    def find_unutilized_members(self):
        unutilized_details = []

        for class_detail in self.class_details:
            class_name = class_detail['class_name']
            class_functions = class_detail['functions']
            class_variables = class_detail['variables']

            unutilized_functions = [
                fn for fn in class_functions 
                if not (fn.startswith('__') and fn.endswith('__'))  
                and all(f"{class_name}.{fn}" != used_fn and not used_fn.startswith(f"{class_name}.{fn}") for used_fn in self.used_functions)
            ]

            unutilized_variables = [
                var for var in class_variables if self.used_variables_count[f"{class_name}.{var}"] < 2
            ]

            unutilized_details.append({
                'class_name': class_name,
                'unutilized_functions': unutilized_functions,
                'unutilized_variables': unutilized_variables
            })

        return unutilized_details
