import ast
import re
from collections import defaultdict

class GlobalVariableVisitor(ast.NodeVisitor):
    def __init__(self, global_var_list):
        self.declared_globals = set(global_var_list) 
        self.used_globals = set()  

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in self.declared_globals:
                self.declared_globals.add(target.id)
        
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id in self.declared_globals:
                self.used_globals.add(node.id)
        
        self.generic_visit(node)

    def get_unused_globals(self):
        return self.declared_globals - self.used_globals
    
class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = {}  
        self.used_imports = set() 

    def visit_Import(self, node):
        for alias in node.names:
            module = alias.name
            asname = alias.asname if alias.asname else alias.name
            self.imports[asname] = {"original": module, "items": []}
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module
        if module:
            if module not in self.imports:
                self.imports[module] = {"original": module, "items": []}
            for alias in node.names:
                item = alias.name
                asname = alias.asname if alias.asname else alias.name
                self.imports[module]["items"].append({"alias": asname, "original": item})
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id in self.imports: 
                self.used_imports.add(node.id)
            else:
                for module, data in self.imports.items():
                    for item in data["items"]:
                        if node.id == item["alias"]:
                            self.used_imports.add((module, item["alias"]))
        self.generic_visit(node)

    def get_dead_imports(self):
        dead_imports = []
        for module, data in self.imports.items():
            if not data["items"]: 
                if module not in self.used_imports:
                    dead_imports.append({
                        "alias": module,
                        "original": data["original"],
                        "items": []
                    })
            else:
                unused_items = [
                    {"alias": item["alias"], "original": item["original"]}
                    for item in data["items"]
                    if (module, item["alias"]) not in self.used_imports
                ]
                if unused_items:
                    dead_imports.append({
                        "alias": module,
                        "original": data["original"],
                        "items": unused_items
                    })
        return dead_imports

    def get_used_imports(self):
        used_imports = []
        for module, data in self.imports.items():
            if not data["items"]:  
                if module in self.used_imports:
                    used_imports.append({
                        "alias": module,
                        "original": data["original"],
                        "items": []
                    })
            else:
                used_items = [
                    {"alias": item["alias"], "original": item["original"]}
                    for item in data["items"]
                    if (module, item["alias"]) in self.used_imports
                ]
                if used_items:
                    used_imports.append({
                        "alias": module,
                        "original": data["original"],
                        "items": used_items
                    })
        return used_imports

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
            elif isinstance(subbody_item, ast.Assign):
                for target in body_item.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        var_name = target.attr
                        class_variables.add(var_name)
                        self.defined_variables.add(f"P{class_name}.{var_name}")  

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

    
    

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.defined_functions = set()
        self.used_functions = set()
        self.function_arguments = defaultdict(list)
        self.def_vars = defaultdict(list)
        self.used_vars = defaultdict(list)
    
    def visit_FunctionDef(self, node):
        self.defined_functions.add(node.name)
        self.function_arguments[node.name]=len(node.args.args)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.used_functions.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            full_func_name = self.get_full_name(node.func)
            self.used_functions.add(full_func_name)

        self.generic_visit(node)
    
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.def_vars[node.lineno].append(target.id)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_vars[node.lineno].append(node.id)
        self.generic_visit(node)

    def get_full_name(self, node):
        if isinstance(node, ast.Attribute):
            return self.get_full_name(node.value) + '.' + node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return ''
    
    def get_arguments(self, node):
        return [ast.dump(arg) for arg in node.args]

    def get_function_arguments(self):
        return self.function_arguments
    
    def get_unused_variables(self):
        unused_vars = {}

        # Combine all used variables from all lines into a set
        all_used_vars = set()
        for vars in self.used_vars.values():
            all_used_vars.update(vars)

        # Check if a variable defined on a line is not in the set of all used variables
        for lineno, vars in self.def_vars.items():
            for var in vars:
                if var not in all_used_vars:
                    if lineno not in unused_vars:
                        unused_vars[lineno] = []
                    unused_vars[lineno].append(var)

        return unused_vars


    
class GlobalVisitor(ast.NodeVisitor):
    def __init__(self):
        self.magic_numbers = {}
        self.code_snippets = defaultdict(int)  
        self.line_numbers = defaultdict(list)  
        self.naming_conventions = defaultdict(list)  

    def identify_constant(self, node):
        if isinstance(node.value, (int, float)):
            self.magic_numbers[node.value] = self.magic_numbers.get(node.value, 0) + 1
        self.generic_visit(node)  
        
    def get_magic_numbers(self, node):
        self.visit(node)
        return self.magic_numbers #[num for num, count in self.magic_numbers.items() if count >= 0]

    def get_duplicated_code(self, node):
        self.visit(node)
        duplicated_lines = {code: lines for code, lines in self.line_numbers.items() if len(lines) > 1}
        return duplicated_lines

    def get_naming_convention(self, node):
        self.visit(node)
        return self.naming_conventions
    
    def check_func_convention(self, node):
        convention = self.check_convention(node.name)
        self.naming_conventions[convention].append(f"Function: {node.name}")

    def check_class_convention(self, node):
        convention = self.check_convention(node.name)
        self.naming_conventions[convention].append(f"Class: {node.name}")
    
    def check_var_convention(self, node):
        convention = self.check_convention(node.id)
        self.naming_conventions[convention].append(f"Variable: {node.id}")


    def check_convention(self, name):
        if re.match(r'^[a-z_]+$', name):
            return 'snake_case'
        elif re.match(r'^[a-z]+[A-Za-z0-9]*$', name):
            return 'camelCase'
        elif re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
            return 'PascalCase'
        else:
            return 'UNKNOWN'

    def visit(self, node):
        node_code = ast.dump(node).strip()  # Dump the AST node to code string
        line_number = getattr(node, 'lineno', None)  # Get the line number of the node
        self.code_snippets[node_code] += 1  # Count occurrences of this snippet
        if line_number:
            self.line_numbers[node_code].append(line_number)  # Track line numbers
        self.generic_visit(node)  # Always visit children nodes

        if isinstance(node, ast.FunctionDef):
            self.check_func_convention(node)
        elif isinstance(node, ast.ClassDef):
            self.check_class_convention(node)
        elif isinstance(node, ast.Name):
            self.check_var_convention(node)
        elif isinstance(node, ast.Constant):
            self.identify_constant(node)          