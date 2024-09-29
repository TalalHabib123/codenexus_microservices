from typing import List, Dict, Union, Any
from app.utils.visitors import (
    FunctionVisitor,
    ClassVisitor,
    GlobalVariableVisitor,
    ImportVisitor
)


def get_unutilized_functions(parsed_ast: str, function_names: list) -> list:
    try:
        visitor = FunctionVisitor()
        visitor.visit(parsed_ast)
        unutilized_functions = [fn for fn in function_names if all(fn != used_fn and not used_fn.startswith(fn + '.') for used_fn in visitor.used_functions)]
        return unutilized_functions
    except Exception as e:
        print(str(e))
        return []

def get_unutilized_classes(parsed_ast: str) -> List[Dict[str, Union[str, List[str]]]]:
    try:
        visitor = ClassVisitor()
        visitor.visit(parsed_ast)
        unutilized_classes = visitor.find_unutilized_members()
        return unutilized_classes
    except Exception as e:
        print(str(e))
        return []
    
def get_unutilized_global_variables(parsed_ast: str, global_variables: list) -> list:
    try:
        visitor = GlobalVariableVisitor(global_variables)
        visitor.visit(parsed_ast)
        return visitor.get_unused_globals()
    except Exception as e:
        print(str(e))
        return []

def get_imports_data_from_ast(parsed_ast: str) -> Dict[str, List[Dict[str, Any]]]:
    try:
        visitor = ImportVisitor()
        visitor.visit(parsed_ast)
        return {"dead_imports": visitor.get_dead_imports(), "unused_imports": visitor.get_used_imports()}
    except Exception as e:
        print(str(e))
        return {"dead_imports": [], "unused_imports": []}