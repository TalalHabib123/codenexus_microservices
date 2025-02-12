def message_with_name(refactoring_job, processed_data):
    if not (refactoring_job or processed_data or processed_data['refactored_code']):
        return {}

    return {
        "original_code": refactoring_job['code_snippet'],
        "refactored_code": processed_data['refactored_code'],
        "name": refactoring_job['name']
    }
    
def message_without_name(refactoring_job, processed_data):
    if not (refactoring_job or processed_data or processed_data['refactored_code']):
        return {}

    return {
        "original_code": refactoring_job['code_snippet'],
        "refactored_code": processed_data['refactored_code']
    }
    
MAPPING_KEYS = {
    "god_object": message_with_name,
    "long_function": message_with_name,
    "temporary_field": message_without_name,
    "feature_envy": message_with_name,
    "inappropriate_intimacy": message_with_name,
    "switch_statement_abuser": message_with_name,
    "excessive_flags": message_with_name,
    "middle_man": message_with_name,
    "duplicate_code": message_without_name,
    "conditionals": message_without_name,
    "global_conflict": message_without_name,
    "long_parameter_list": message_with_name,
}