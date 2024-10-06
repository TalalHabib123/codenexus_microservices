import ast

class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = {} 
        self.used_imports = set()  
        self.called_attributes = {}  

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

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and isinstance(node.ctx, ast.Load):
            var_name = node.value.id  
            attr_name = node.attr
            if var_name in self.imports:
                if attr_name not in self.called_attributes.get(var_name, []):
                    self.called_attributes[var_name] = self.called_attributes.get(var_name, []) + [attr_name]
            else:
                for module, data in self.imports.items():
                    for item in data["items"]:
                        if var_name == item["alias"]:
                            key = (module, item["alias"])
                            if attr_name not in self.called_attributes.get(key, []):
                                self.called_attributes[key] = self.called_attributes.get(key, []) + [attr_name]
        elif isinstance(node.value, ast.Call):
            self.visit_Call(node.value) 
            attr_name = node.attr 
            called_obj = node.value.func
            if isinstance(called_obj, ast.Name):
                func_name = called_obj.id
                for module, data in self.imports.items():
                    for item in data["items"]:
                        if func_name == item["alias"]:
                            key = (module, item["alias"])
                            if attr_name not in self.called_attributes.get(key, []):
                                self.called_attributes[key] = self.called_attributes.get(key, []) + [attr_name]
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            for module, data in self.imports.items():
                for item in data["items"]:
                    if func_name == item["alias"]:
                        self.used_imports.add((module, item["alias"]))
        elif isinstance(node.func, ast.Attribute): 
            self.visit_Attribute(node.func)  
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
                        "items": [],
                        "called_attributes": self.called_attributes.get(module, [])
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
                        "items": used_items,
                        "called_attributes": [
                            {"alias": item["alias"], "called": self.called_attributes.get((module, item["alias"]), [])}
                            for item in data["items"]
                            if (module, item["alias"]) in self.used_imports
                        ]
                    })
        return used_imports
   