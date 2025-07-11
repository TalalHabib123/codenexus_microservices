import json
from app.utils.visitors.global_visitor import GlobalVisitor


def get_naming_convention(parsed_ast:str):
    visitor = GlobalVisitor()
    conventions = visitor.get_naming_convention(parsed_ast)
    total = 0
    for key in conventions:
        total += len(conventions[key])
        
    result = []
    result.append({"type":"snake_case", "total_count":total,"type_count":len(conventions['snake_case']), "vars": conventions['snake_case'] })
    result.append({"type":"camel_case", "total_count":total,"type_count":len(conventions['camelCase']), "vars": conventions['camelCase'] })
    result.append({"type":"pascal_case", "total_count":total,"type_count":len(conventions['PascalCase']), "vars": conventions['PascalCase'] })
    return result