from app.utils.visitors.function_visitor import FunctionVisitor

def get_unused_variables(parsed_ast:str):
    visitor = FunctionVisitor()
    visitor.visit(parsed_ast)
    return visitor.get_unused_variables()
