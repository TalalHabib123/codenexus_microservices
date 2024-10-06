import json
from app.utils.visitors.function_visitor import FunctionVisitor
from app.utils.visitors.global_visitor import GlobalVisitor

# extract magic numbers from the ast 
def get_magic_numbers(parsed_ast: str):
    visitor = GlobalVisitor()
    return json.dumps(visitor.get_magic_numbers(parsed_ast))

# extract number of paramenters
def get_parameter_list(parsed_ast:str):
    visitor = FunctionVisitor()
    visitor.visit(parsed_ast)
    return json.dumps(dict(visitor.get_function_arguments()))

# extract duplicated code
def get_duplicated_code(parsed_ast:str):
    visitor = GlobalVisitor()
    return json.dumps(visitor.get_duplicated_code(parsed_ast))

# Extract unused variables
def get_unused_variables(parsed_ast:str):
    visitor = FunctionVisitor()
    visitor.visit(parsed_ast)
    return json.dumps(visitor.get_unused_variables())

# naming convention
def get_naming_convention(parsed_ast:str):
    visitor = GlobalVisitor()
    conventions = visitor.get_naming_convention(parsed_ast)
    total = 0
    snake_case = conventions['snake_case']
    camel_case = conventions['camel_case']
    pascal_case = conventions['pascal_case']
    for key in conventions:
        total += len(conventions[key])
    snake_percent = (len(snake_case)/total) * 100
    camel_percent = (len(camel_case)/total) * 100
    pascal_percent = (len(pascal_case)/total) * 100
    unknown = 100 - (snake_percent + camel_percent + pascal_percent)
    return json.dumps({
        'snake_case': snake_percent,
        'camel_case': camel_percent,
        'pascal_case': pascal_percent,
        'unknown': unknown
    })