from app.utils.visitors.function_visitor import FunctionVisitor


def get_parameter_list(parsed_ast:str):
    visitor = FunctionVisitor()
    visitor.visit(parsed_ast)
    param_list = visitor.get_function_arguments()
    return param_list
