from typing import List, Dict, Union
from app.utils.visitors import (
    FunctionVisitor,
    ClassVisitor
)

def get_unutilized_functions(parsed_ast: str, function_names: list) -> list:
    visitor = FunctionVisitor()
    visitor.visit(parsed_ast)
    unutilized_functions = [fn for fn in function_names if all(fn != used_fn and not used_fn.startswith(fn + '.') for used_fn in visitor.used_functions)]
    return unutilized_functions

def get_unutilized_classes(parsed_ast: str, class_details: List[Dict[str, Union[str, List[str]]]]) -> List[Dict[str, Union[str, List[str]]]]:
    visitor = ClassVisitor()
    visitor.visit(parsed_ast)
    unutilized_classes = visitor.find_unutilized_members()
    return unutilized_classes