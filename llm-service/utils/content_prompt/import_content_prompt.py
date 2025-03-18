from utils.content_prompt.detection import (
    long_function_content as long_function_detection,
    god_object_content as god_object_detection,
    feature_envy_content as feature_envy_detection,
    inappropriate_intimacy_content as inappropriate_intimacy_detection,
    middle_man_content as middle_man_detection,
    switch_statement_content as switch_statement_detection,
    excessive_flags_content as excessive_flags_detection
)

from utils.content_prompt.refactoring import (
    god_object_content as god_object_refactoring,
    large_fucntion_content as large_function_refactoring,
    temporary_field_content as temporary_field_refactoring,
    duplicate_code_content as duplicate_code_refactoring,
    complex_conditionals_content as complex_conditionals_refactoring,
    global_variable_content as global_variable_refactoring,
    excessive_flags_content as excessive_flags_refactoring,
    swtich_statement_content as swtich_statement_refactoring,
    long_parameter_content as long_parameter_refactoring
)

content_detection_prompts = {
    "long_function": long_function_detection.create_long_function_prompt,
    "god_object": god_object_detection.create_god_object_prompt,
    "feature_envy": feature_envy_detection.create_feature_envy_prompt,
    "inappropriate_intimacy": inappropriate_intimacy_detection.create_inappropriate_intimacy_prompt,
    "middle_man": middle_man_detection.create_middle_man_prompt,
    "switch_statement_abuser": switch_statement_detection.create_switch_statement_abuser_prompt,
    "excessive_flags": excessive_flags_detection.create_excessive_flags_prompt
}


content_refactoring_prompts = {
    "god_object": god_object_refactoring.create_god_object_content,
    "long_function": large_function_refactoring.create_long_function_content,
    "temporary_field": temporary_field_refactoring.create_temporary_field_content,
    "duplicate_code": duplicate_code_refactoring.create_duplicate_code_content,
    "conditionals": complex_conditionals_refactoring.create_overly_complex_conditionals_content,
    "global_conflict": global_variable_refactoring.create_global_variable_conflict_content,
    "excessive_flags": excessive_flags_refactoring.create_excessive_flags_content,
    "switch_statement_abuser": swtich_statement_refactoring.create_switch_statement_abuser_content,
    "long_parameter_list": long_parameter_refactoring.create_long_parameter_list_content
}
