import ast
from collections import defaultdict

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.defined_functions = set()
        self.used_functions = set()
        self.function_arguments = defaultdict(list)
        self.def_vars = defaultdict(list)
        self.used_vars = defaultdict(list)
    
    def visit_FunctionDef(self, node):
        function_name = node.name
        parameters = [arg.arg for arg in node.args.args]
        param_count = len(parameters)
        long_parameter = param_count > 3
        self.function_arguments[function_name] = {
            "function_name": function_name,
            "parameters": parameters,
            "long_parameter_count": param_count,
            "long_parameter": long_parameter,
            "line_number": node.lineno 
        }
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
        return [
            {
                "function_name": details["function_name"],
                "parameters": details["parameters"],
                "long_parameter_count": details["long_parameter_count"],
                "long_parameter": details["long_parameter"],
                "line_number": details["line_number"]
            }
            for details in self.function_arguments.values()
        ]
    def get_unused_variables(self):
        unused_vars = {}
        all_used_vars = set()

        # Collect all used variables from all lines into a set
        for vars in self.used_vars.values():
            all_used_vars.update(vars)

        # Check if a variable defined on a line is not in the set of all used variables
        for lineno, vars in self.def_vars.items():
            for var in vars:
                if var not in all_used_vars:
                    if lineno not in unused_vars:
                        unused_vars[lineno] = []
                    unused_vars[lineno].append({"variable": var, "line_number": lineno})

        # Return list of unused variables, flattened from the dictionary
        return [
            {"variable_name": var_info["variable"], "line_number": var_info["line_number"]}
            for var_list in unused_vars.values() for var_info in var_list
        ]
