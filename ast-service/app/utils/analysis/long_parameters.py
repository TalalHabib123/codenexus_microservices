import json
import ast
from app.utils.visitors.function_visitor import FunctionVisitor


def get_parameter_list(parsed_ast:str):
    print(ast.dump(parsed_ast))
    visitor = FunctionVisitor()
    visitor.visit(parsed_ast)
    param_list = visitor.get_function_arguments()
    res = {key: True if len(value) > 3 else False for key, value in param_list.items()} # long param iff num of params is more than 3
    return json.dumps(dict(res))
