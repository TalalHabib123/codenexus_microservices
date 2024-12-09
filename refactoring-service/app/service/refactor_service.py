from app.utils.Analysis.inconsistent_naming_refactor import inconsistent_naming_refactor
from app.utils.Analysis.magic_number_refactor import magic_numbers_refactor
from app.utils.Analysis.unreachable_code_refactor import unreachable_code_refactor
from app.utils.Analysis.unused_variables_refactor import unused_variables_refactor
from app.utils.Analysis.dead_code_refactor import dead_code_refactor


def refactor_inconsistent_naming(code, target_convention):
    try: 
        return {
            "refactored_code": inconsistent_naming_refactor(code, target_convention),
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def refactor_magic_numbers(code, magic_numbers):
    try:
        return {
            "refactored_code": magic_numbers_refactor(magic_numbers, code),
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def refactor_unreachable_code(unreachable, code):
    try:
        return {
            "refactored_code": unreachable_code_refactor(code, unreachable),
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def refactor_unused_variables(unused_variables, code):
    try:
        return {
            "refactored_code": unused_variables_refactor(unused_variables, code),
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
        
def refactor_dead_code(entity_name, entity_type, code):
    try:
        return {
            "refactored_code": dead_code_refactor(entity_name, entity_type, code),
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }