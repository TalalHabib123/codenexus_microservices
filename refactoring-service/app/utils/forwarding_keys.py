from app.utils import (
    class_extractor,
    function_extractor,
)

def return_function_extractor(task_data: dict):
    try:
        return {
            "file_path": task_data["file_path"],        
            "code_snippet": function_extractor.extract_function_snippet(task_data["code_snippet"], task_data["name"])
        }
    except Exception as e:
        return {}

def return_class_extractor(task_data: dict):
    try:
        return {
            "file_path": task_data["file_path"],
            "code_snippet": class_extractor.extract_class_snippet(task_data["code_snippet"], task_data["name"])
        }
    except Exception as e:
        return {}

def return_orginal_code(task_data: dict):
    return {
        "file_path": task_data["file_path"],
        "code_snippet": task_data["code_snippet"]
    }

FORWARDING_KEYS = {
    "god_object": return_class_extractor,
    "long_function": return_function_extractor,
    "temporary_field": return_orginal_code,
    "feature_envy": return_function_extractor,
    "inappropriate_intimacy": return_class_extractor,
    "switch_statement_abuser": return_function_extractor,
    "excessive_flags": return_function_extractor,
    "middle_man": return_class_extractor,
    "duplicate_code": return_orginal_code,
    "conditionals": return_orginal_code,
    "global_conflict": return_orginal_code,
    "long_parameter_list": return_function_extractor,
}