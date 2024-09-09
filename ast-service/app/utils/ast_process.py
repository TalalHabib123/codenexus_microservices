import json

def get_function_names_from_ast(ast_json):
    def traverse(node, current_function=None, in_class=False):
        if isinstance(node, dict):
            if node.get('_type') == 'FunctionDef' and not in_class:
                function_name = node['name']
                if current_function:
                    function_names.append(f"{current_function}.{function_name}")
                else:
                    function_names.append(function_name)
                current_function = function_name
            elif node.get('_type') == 'ClassDef':
                in_class = True
            for key, value in node.items():
                traverse(value, current_function, in_class)
        elif isinstance(node, list):
            for item in node:
                traverse(item, current_function, in_class)

    ast_dict = json.loads(ast_json)
    function_names = []
    traverse(ast_dict)
    return function_names

def get_class_details_from_ast(ast_json):
    def traverse(node, class_name=None):
        if isinstance(node, dict):
            if node.get('_type') == 'ClassDef':
                class_name = node['name']
                functions = []
                variables = []
                for item in node['body']:
                    # import pdb; pdb.set_trace()
                    if item.get('_type') == 'FunctionDef':
                        functions.append(item['name'])
                        for sub_item in item['body']:
                            if sub_item.get('_type') == 'Assign':
                                for target in sub_item['targets']:
                                    if isinstance(target, dict) and target.get('_type') == 'Attribute':
                                        if target['value'].get('_type') == 'Name' and target['value']['id'] == 'self':
                                            variables.append(target['attr'])
                class_details.append({
                    'class_name': class_name,
                    'functions': functions,
                    'variables': variables
                })
            for key, value in node.items():
                traverse(value, class_name)
        elif isinstance(node, list):
            for item in node:
                traverse(item, class_name)

    ast_dict = json.loads(ast_json)
    class_details = []
    traverse(ast_dict)
    return class_details

# def get_global_variables_from_ast(ast_json):
#     def traverse(node):
#         if isinstance(node, dict):
#             if node.get('_type') == 'Assign':
#                 for target in node['targets']:
#                     if isinstance(target, dict) and target.get('_type') == 'Name':
#                         var_name = target['id']
#                         var_type = get_type(node['value'])
#                         global_variables.append({
#                             'variable_name': var_name,
#                             'variable_type': var_type
#                         })
#             for key, value in node.items():
#                 traverse(value)
#         elif isinstance(node, list):
#             for item in node:
#                 traverse(item)

#     def get_type(value_node):
#         if isinstance(value_node, dict):
#             if value_node.get('_type') == 'Constant':
#                 return 'constant'
#             elif value_node.get('_type') == 'Call':
#                 func = value_node['func']
#                 if isinstance(func, dict) and func.get('_type') == 'Name':
#                     return func['id']
#             elif value_node.get('_type') == 'List':
#                 return 'list'
#             elif value_node.get('_type') == 'Dict':
#                 return 'dict'
#             return value_node.get('_type')
#         return 'unknown'

#     ast_dict = json.loads(ast_json)
#     global_variables = []
#     traverse(ast_dict)
#     return global_variables

def get_global_variables_from_ast(ast_json):
    def traverse(node, inside_function=False, inside_conditional=False, inside_class=False):
        if isinstance(node, dict):
            node_type = node.get('_type')

            # Track if we are inside a class definition
            if node_type == 'ClassDef':
                inside_class = True
            
            # Skip variables inside functions, conditionals, or classes
            if node_type in ['FunctionDef', 'If', 'While', 'For']:
                inside_function = True if node_type == 'FunctionDef' else inside_function
                inside_conditional = True if node_type in ['If', 'While', 'For'] else inside_conditional

            # Capture global variables not in functions, conditionals, or classes
            if node_type == 'Assign' and not inside_function and not inside_conditional and not inside_class:
                for target in node['targets']:
                    if isinstance(target, dict) and target.get('_type') == 'Name':
                        var_name = target['id']
                        var_type, class_or_func = get_type(node['value'])
                        global_variables.append({
                            'variable_name': var_name,
                            'variable_type': var_type,
                            'class_or_function': class_or_func
                        })
            
            for key, value in node.items():
                traverse(value, inside_function, inside_conditional, inside_class)
        elif isinstance(node, list):
            for item in node:
                traverse(item, inside_function, inside_conditional, inside_class)

    def get_type(value_node):
        if isinstance(value_node, dict):
            value_type = value_node.get('_type')

            if value_type == 'Constant':
                return 'constant', None
            elif value_type == 'Call':
                func = value_node['func']
                if isinstance(func, dict) and func.get('_type') == 'Name':
                    return 'function_call', func['id']
            elif value_type == 'List':
                return 'list', None
            elif value_type == 'Dict':
                return 'dict', None
            elif value_type == 'Name':
                return 'variable', value_node['id']  # For variable assignments
            elif value_type == 'ClassDef':
                return 'class_instance', value_node['name']

            return value_type, None
        return 'unknown', None

    ast_dict = json.loads(ast_json)
    global_variables = []
    traverse(ast_dict)
    return global_variables

def check_main_block_in_ast(ast_json):
    def traverse(node):
        if isinstance(node, dict):
            if node.get('_type') == 'If':
                test = node.get('test')
                if (isinstance(test, dict) and
                    test.get('_type') == 'Compare' and
                    test.get('left', {}).get('_type') == 'Name' and
                    test.get('left', {}).get('id') == '__name__' and
                    test.get('ops', [{}])[0].get('_type') == 'Eq' and
                    test.get('comparators', [{}])[0].get('_type') == 'Constant' and
                    test.get('comparators', [{}])[0].get('value') == '__main__'):
                    return True
            for key, value in node.items():
                if traverse(value):
                    return True
        elif isinstance(node, list):
            for item in node:
                if traverse(item):
                    return True
        return False

    ast_dict = json.loads(ast_json)
    return traverse(ast_dict)

def get_imports_from_ast(ast_json):
    def traverse(node):
        if isinstance(node, dict):
            if node.get('_type') == 'Import':
                for alias in node.get('names', []):
                    if isinstance(alias, dict) and alias.get('_type') == 'alias':
                        name = alias.get('name')
                        asname = alias.get('asname')
                        if asname:
                            imports["imports"].append({"name": name, "alias": asname, "type": "import"})
                        else:
                            imports['imports'].append({"name": name, "alias": None, "type": "import"})
            elif node.get('_type') == 'ImportFrom':
                module = node.get('module')
                level = node.get('level', 0)
                level_dots = '.' * level
                for alias in node.get('names', []):
                    if isinstance(alias, dict) and alias.get('_type') == 'alias':
                        name = alias.get('name')
                        asname = alias.get('asname')
                        if asname:
                            imports['from'].append({"name": name, "alias": asname, "type": "from", "module": level_dots + module})
                        else:
                            imports['from'].append({"name": name, "alias": None, "type": "from", "module": level_dots + module})
            for key, value in node.items():
                traverse(value)
        elif isinstance(node, list):
            for item in node:
                traverse(item)

    ast_dict = json.loads(ast_json)
    imports = {
        "imports": [],
        "from": []
    }
    traverse(ast_dict)
    return imports

def check_standalone_file(ast_json):
    def traverse(node):
        if isinstance(node, dict):
            node_type = node.get('_type')
            acceptable_node_types = (
                'FunctionDef', 'ClassDef', 'Import', 'ImportFrom',
                'Assign', 'AnnAssign', 'AugAssign',
                'Pass', 'Delete', 'Global', 'Nonlocal'
            )

            if node_type == 'Module':
                for stmt in node.get('body', []):
                    if traverse(stmt):
                        return True
                return False
            elif node_type in acceptable_node_types:
                return False
            else:
                return True
        elif isinstance(node, list):
            for item in node:
                if traverse(item):
                    return True
            return False
        else:
            return False

    ast_dict = json.loads(ast_json)
    return traverse(ast_dict)