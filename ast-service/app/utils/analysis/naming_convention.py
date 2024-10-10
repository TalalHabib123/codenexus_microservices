import json
from app.utils.visitors.global_visitor import GlobalVisitor


def get_naming_convention(parsed_ast:str):
    visitor = GlobalVisitor()
    conventions = visitor.get_naming_convention(parsed_ast)
    print(conventions)
    total = 0
    snake_case = conventions['snake_case']
    camel_case = conventions['camel_case']
    pascal_case = conventions['pascal_case']
    for key in conventions:
        total += len(conventions[key])

    return json.dumps({
        'snake_case': len(snake_case),
        'camel_case': len(camel_case),
        'pascal_case': len(pascal_case),
        'unknown': total - (len(snake_case) + len(camel_case) + len(pascal_case))
    })