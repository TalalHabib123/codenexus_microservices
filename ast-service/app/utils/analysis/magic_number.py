import json
from app.utils.visitors.global_visitor import MagicNumGlobalVisitor

def get_magic_numbers(parsed_ast: str):
    visitor = MagicNumGlobalVisitor()
    visitor.visit(parsed_ast)
    return visitor.get_magic_numbers(parsed_ast)