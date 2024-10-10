import json
from app.utils.visitors.global_visitor import GlobalVisitor

def get_magic_numbers(parsed_ast: str):
    visitor = GlobalVisitor()
    # visitor.visit(parsed_ast)
    return json.dumps(dict(visitor.get_magic_numbers(parsed_ast)))