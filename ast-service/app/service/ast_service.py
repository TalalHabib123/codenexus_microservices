import ast
import json
from typing import List, Dict, Union
from app.models.ast_models import GlobalVariable, Import
from app.utils.ast_encoder import ASTEncoder
from app.utils.ast_process import (
    get_function_names_from_ast,
    get_class_details_from_ast,
    get_global_variables_from_ast,
    check_main_block_in_ast,
    get_imports_from_ast,
    check_standalone_file
)

from app.utils.ast_analysis import (
    get_unutilized_functions,
    get_unutilized_classes
)


def deadcode_analysis(code: str, 
                      function_names: List[str], 
                      class_details: List[Dict[str, Union[str, List[str]]]], 
                      global_variables: List[GlobalVariable], 
                      imports: Dict[str, List[Import]]) -> dict:
    try:
        parsed_ast = ast.parse(code)
        return {
            'function_names': get_unutilized_functions(parsed_ast, function_names),
            'class_details': get_unutilized_classes(parsed_ast, class_details),
            'global_variables': None,
            'imports': None,
            'success': True
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_ast(code: str) -> dict:
    try: 
        parsed_ast = ast.parse(code)
        ast_json = json.dumps(parsed_ast, cls=ASTEncoder, indent=4)
        return {
            'ast': ast_json,
            'function_names': get_function_names_from_ast(ast_json),
            'class_details': get_class_details_from_ast(ast_json),
            'global_variables': get_global_variables_from_ast(ast_json),
            'is_main_block_present': check_main_block_in_ast(ast_json),
            'imports': get_imports_from_ast(ast_json),
            'is_standalone_file': not check_standalone_file(ast_json),
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    