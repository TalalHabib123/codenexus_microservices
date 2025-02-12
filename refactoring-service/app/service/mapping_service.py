from app.utils.Mappers import (
    class_mapper,
    function_mapper
)
from app.utils.code_validator import is_valid_python_code

def map_class(orginal_code, class_name, refactor_snippet):
    try:    
        code = class_mapper.replace_class_in_code(orginal_code, class_name, refactor_snippet)
        if not is_valid_python_code(code):
            raise Exception("Invalid Python code")
        
        return {
            "refactored_code": code,
            "success": True
        }  
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }   
        
def map_function(orginal_code, function_name, refactor_snippet):
    try:
        code = function_mapper.replace_function_in_code(orginal_code, function_name, refactor_snippet)
        if not is_valid_python_code(code):
            raise Exception("Invalid Python code")
        return {
            "refactored_code": code,
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 
        
def map_orginal_code(orginal_code):
    if not is_valid_python_code(orginal_code):
        return {
            "success": False,
            "error": "Invalid Python code"
        }
    return {
        "refactored_code": orginal_code,
        "success": True
    }    