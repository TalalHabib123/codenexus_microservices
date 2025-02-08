import ast
import re
from collections import defaultdict
from app.models.ast_models import MagicNumbersDetails

class GlobalVariableConflictAnalyzer(ast.NodeVisitor):
    def __init__(self, global_vars_list):
        self.global_vars = {var: {"declared": [], "assignments": [], "usages": []} for var in global_vars_list}
        self.local_assignments = defaultdict(list)
        self.local_uses = defaultdict(list)
        self.function_scopes = []
        self.current_function = None
        self.global_declarations = defaultdict(list)
        self.local_variable_names = defaultdict(set)
        self.module_level_assignments = set()

    def visit_FunctionDef(self, node):
        self.function_scopes.append(node.name)
        self.current_function = node.name

        for arg in node.args.args:
            self.local_variable_names[node.name].add(arg.arg)

        self.generic_visit(node)

        self.function_scopes.pop()
        if self.function_scopes:
            self.current_function = self.function_scopes[-1]
        else:
            self.current_function = None

    def visit_Global(self, node):
        if self.current_function:
            for name in node.names:
                self.global_declarations[name].append(self.current_function)
                if name not in self.global_vars:
                    self.global_vars[name] = {
                        "declared": [(self.current_function, node.lineno)],
                        "assignments": [],
                        "usages": []
                    }

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            
            if self.current_function is None:
                self.module_level_assignments.add(var_name)

            if self.current_function:
                self.local_variable_names[self.current_function].add(var_name)
                
            if var_name in self.global_vars:
                if self.current_function is None:  # Assignment at module level
                    self.global_vars[var_name]["assignments"].append(("module", node.lineno))
                elif var_name in self.global_declarations and self.current_function in self.global_declarations[var_name]:
                    self.global_vars[var_name]["assignments"].append((self.current_function, node.lineno))
                else:
                    self.local_assignments[var_name].append((self.current_function, node.lineno))
        self.generic_visit(node)

    def visit_Name(self, node):
        var_name = node.id
        if var_name in self.global_vars and self.current_function:
            if var_name not in self.local_variable_names[self.current_function]:
                self.global_vars[var_name]["usages"].append((self.current_function, node.lineno))
        self.generic_visit(node)

    def analyze_conflicts(self):
        conflicts_report = []

        for var, data in self.global_vars.items():
            conflict_details = {
                "variable": var,
                "assignments": data.get("assignments", []),
                "local_assignments": self.local_assignments.get(var, []),
                "usages": data.get("usages", []),
                "conflicts": [],
                "warnings": []
            }

            # Conflict detection: Multiple assignments
            all_assignments = data["assignments"] + self.local_assignments.get(var, [])
            if len(all_assignments) > 1:
                conflict_details["conflicts"].append(
                    f"Multiple assignments to '{var}' detected. Potential conflict!"
                )

            # Conflict detection: Usage without assignment
            if not data["assignments"] and var in self.global_vars and data.get("usages", []):
                conflict_details["warnings"].append(
                    f"Variable '{var}' used without assignment."
                )
            
            # Check for potential conflicts due to missing 'global' declaration in usage
            for usage in data.get("usages", []):
                function_name, line = usage
                if function_name not in self.global_declarations[var]:
                    conflict_details["conflicts"].append(
                        f"Potential conflict in function '{function_name}' at line {line}: '{var}' is used without a 'global' declaration."
                    )

            # Check for potential shadowing of global variable by a local variable
            for func_name, locals_in_func in self.local_variable_names.items():
                if (
                    var in locals_in_func 
                    and func_name not in self.global_declarations[var] 
                    and var in self.module_level_assignments
                ):
                    conflict_details["conflicts"].append(
                        f"Shadowing issue in function '{func_name}': Local variable '{var}' may shadow the global variable."
                    )

            conflicts_report.append(conflict_details)
        
        return conflicts_report
    
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
  
class GlobalVisitor(ast.NodeVisitor):
    def __init__(self):
        self.magic_numbers = {}  
        self.code_snippets = defaultdict(int)  
        self.line_numbers = defaultdict(list)  
        self.naming_conventions = defaultdict(list)  

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            self.magic_numbers[node.value] = self.magic_numbers.get(node.value, 0) + 1
        self.generic_visit(node)  
        
    def get_magic_numbers(self, node):
        self.visit(node)
        return [num for num, count in self.magic_numbers.items() if count >= 0]

    def get_duplicated_code(self, node):
        self.visit(node)
        duplicated_code = [code for code, count in self.code_snippets.items() if count > 1]
        duplicated_lines = {code: lines for code, lines in self.line_numbers.items() if len(lines) > 1}
        return duplicated_code, duplicated_lines

    def get_naming_convention(self, node):
        self.visit(node)
        return self.naming_conventions
    
    def check_func_convention(self, node):
        convention = self.check_convention(node.name)
        self.naming_conventions[convention].append({"variable": node.name, "line_number": node.lineno})

    def check_class_convention(self, node):
        convention = self.check_convention(node.name)
        self.naming_conventions[convention].append({"variable": node.name, "line_number": node.lineno})
    
    def check_var_convention(self, node):
        convention = self.check_convention(node.id)
        self.naming_conventions[convention].append({"variable": node.id, "line_number": node.lineno})


    def check_convention(self, name):
        # Helper method to check naming conventions
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
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            self.check_var_convention(node)


class MagicNumGlobalVisitor(ast.NodeVisitor):
    def __init__(self):
        self.magic_numbers = {}  

    def generic_visit(self, node: ast.AST):
        # Assign parent attribute to child nodes
        for child in ast.iter_child_nodes(node):
            child.parent = node
        super().generic_visit(node)

    def visit_Constant(self, node):
        # Check if the constant is a numeric value (int or float, but not bool)
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            # Exclude numbers in lists, tuples, or assignments
            if not isinstance(getattr(node, 'parent', None), (ast.List, ast.Tuple, ast.Assign)):
                if node.value in self.magic_numbers:
                    self.magic_numbers[node.value]['count'] += 1
                else:
                    self.magic_numbers[node.value] = {
                        'count': 1,
                        'line_number': node.lineno
                    }
        
        # Continue traversing the AST
        self.generic_visit(node)

    def get_magic_numbers(self):
        # Return magic numbers that appear more than twice
        return [
            {'magic_number': num, 'line_number': details['line_number']} 
            for num, details in self.magic_numbers.items() 
            if details['count'] > 2
        ]

