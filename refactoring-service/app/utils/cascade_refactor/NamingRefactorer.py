import ast


class CascadeNamingRefactorer(ast.NodeTransformer):
    """Second pass: Perform the actual refactoring with import aliasing"""
    def __init__(self, mappings, dep_list, definitions):
        self.mappings = mappings
        self.dep_list = dep_list
        self.defined_functions = definitions['functions']
        self.defined_classes = definitions['classes']
        self.defined_variables = definitions['variables']
        self.imported_names = definitions['imports']
        self.alias_mappings = {}  # Store aliases for conflicting names
        self.new_imports = []     # Store new import statements needed
        
    def is_name_defined_locally(self, name):
        """Check if a name is defined in the local scope"""
        return (name in self.defined_variables or 
                name in self.defined_classes or 
                name in self.defined_functions or 
                name in self.imported_names)
    
    def generate_unique_alias(self, original_name):
        """Generate a unique alias for a conflicting name"""
        base_name = f"{original_name}_external"
        counter = 1
        while base_name in self.defined_variables or base_name in self.defined_classes or \
              base_name in self.defined_functions or base_name in self.imported_names:
            base_name = f"{original_name}_external_{counter}"
            counter += 1
        return base_name

    def visit_ImportFrom(self, node):
        new_names = []
        for alias in node.names:  
            if alias.name in self.dep_list:
                mapped_name = self.mappings[alias.name]
                if (mapped_name in self.defined_variables or 
                    mapped_name in self.defined_classes or 
                    mapped_name in self.defined_functions):
                    # Generate unique alias for conflicting name
                    new_alias = self.generate_unique_alias(mapped_name)
                    self.alias_mappings[mapped_name] = new_alias
                    new_names.append(ast.alias(
                        name=mapped_name,
                        asname=new_alias
                    ))
                else:
                    # No conflict, just use mapped name
                    new_names.append(ast.alias(
                        name=mapped_name,
                        asname=None
                    ))
            else:
                # Name not in dep_list, keep original
                new_names.append(alias)
        
        node.names = new_names
        return node
    