import ast
import json
from typing import List
from app.utils.ast_encoder import ASTEncoder

from app.utils.ast_analysis import (
    get_magic_numbers,
    get_parameter_list,
    get_duplicated_code,
    get_unused_variables,
    get_naming_convention
)

from app.utils.ast_process import (
    get_function_names_from_ast,
    get_class_details_from_ast,
    get_global_variables_from_ast,
    check_main_block_in_ast,
    get_imports_from_ast,
    check_standalone_file
)

from app.utils.analysis.dead_code import (
    get_unutilized_functions,
    get_unutilized_classes,
    get_unutilized_global_variables,
    get_imports_data_from_ast,
    get_class_utiliztion_details
)

from app.utils.analysis.global_conflict import global_variable_conflicts

from app.utils.analysis.conditionals import analyze_condition_complexity

from app.utils.analysis.unreachable import unreachable_code_analysis

def unreachable_code_check(code: str) -> dict:
    try:
        return {
            'unreachable_code': unreachable_code_analysis(code),
            'success': True
        }
    except Exception as e:
        return {
            'unreachable_code': [],
            'success': False,
            'error': str(e)
        }

def overly_complex_conditionals_analysis(code: str) -> dict:
    try:
        return {
            'conditionals': analyze_condition_complexity(code),
            'success': True
        }
    except Exception as e:
        return {
            'conditionals': [],
            'success': False,
            'error': str(e)
        }

def global_variable_analysis(code: str, global_variables: list) -> dict:
    try:
        parsed_ast = ast.parse(code)
        return {
            'conflicts_report': global_variable_conflicts(parsed_ast, global_variables),
            'success': True
        }
    except Exception as e:
        return {
            'conflicts_report': [],
            'success': False,
            'error': str(e)
        }

def dead_class_analysis(code: str, class_name: str) -> dict:
    try:
        parsed_ast = ast.parse(code)
        return {
            'class_details': get_class_utiliztion_details(parsed_ast, class_name),
            'success': True
        }
    except Exception as e:
        return {
            'class_details': [],
            'success': False,
            'error': str(e)
        }

def deadcode_analysis(code: str, 
                      function_names: List[str], 
                      global_variables: list) -> dict:
    try:
        parsed_ast = ast.parse(code)
        return {
            'function_names': get_unutilized_functions(parsed_ast, function_names),
            'class_details': get_unutilized_classes(parsed_ast),
            'global_variables': get_unutilized_global_variables(parsed_ast, global_variables),
            'imports':get_imports_data_from_ast(parsed_ast),
            'success': True
        }
    except Exception as e:
        return {
            'function_names': [],
            'class_details': [],
            'global_variables': [],
            'imports': {"dead_imports": [], "unused_imports": []},
            'success': False,
            'error': str(e)
        }
    
    
def magic_num_analysis(code: str):
    try:
        parsed_ast = ast.parse(code)
        magic_nums = get_magic_numbers(parsed_ast)
        return {
            'data': magic_nums,
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def unused_variables_analysis(code: str):
    try:
        parsed_ast = ast.parse(code)
        unused_variables = get_unused_variables(parsed_ast)
        return {
            'data': unused_variables,
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def naming_convention_analysis(code: str):
    try:
        parsed_ast = ast.parse(code)
        naming_convention = get_naming_convention(parsed_ast)
        return {
            'data': naming_convention,
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def duplicated_code_analysis(code: str):
    try:
        parsed_ast = ast.parse(code)
        duplicated_code = get_duplicated_code(code)
        return {
            'data': duplicated_code,
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def parameter_list_analysis(code: str):
    try:
        parsed_ast = ast.parse(code)
        parameter_list = get_parameter_list(parsed_ast)
        return {
            'type': 'long-parameter',
            'data': parameter_list,
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
    