from utils.system_prompts.detection import (
    long_function as long_function_detection,
    god_object as god_object_detection,
    feature_envy as feature_envy_detection,
    inappropriate_intimacy as inappropriate_intimacy_detection,
    middle_man as middle_man_detection,
    switch_statement as switch_statement_detection,
    excessive_flag as excessive_flag_detection
)

from utils.system_prompts.refactoring import (
    god_object as god_object_refactoring,
    long_function as long_function_refactoring,
    feature_envy as feature_envy_refactoring,
    inappropriate_intimacy as inappropriate_intimacy_refactoring,
    switch_statement as switch_statement_refactoring,
    excessive_flags as excessive_flag_refactoring,
    middle_man as middle_flag_refactoring,
    temporary_field as temporary_field_refactoring,
    duplicate_code as duplicate_code_refactoring,
    conditionals as conditionals_refactoring,
    global_conflict as global_conflict_refactoring,
    long_parameter as long_parameter_refactoring
)

system_detection_prompts = {
    "long_function": long_function_detection.LONG_FUNCTION_DETECTION,
    "god_object": god_object_detection.GOD_OBJECT_DETECTION,
    "feature_envy": feature_envy_detection.FEATURE_ENVY_DETECTION,
    "inappropriate_intimacy": inappropriate_intimacy_detection.INAPPROPRIATE_INTIMACY_DETECTION,
    "middle_man": middle_man_detection.MIDDLE_MAN_DETECTION,
    "switch_statement_abuser": switch_statement_detection.SWITCH_STATEMENT_DETECTION,
    "excessive_flags": excessive_flag_detection.EXCESSIVE_FLAGS_DETECTION
}

system_refactoring_prompts = {
    "god_object": god_object_refactoring.GOD_OBJECT_REFACTORING,
    "long_function": long_function_refactoring.LONG_FUNCTION_REFACTORING,
    "temporary_field": temporary_field_refactoring.TEMPORARY_FIELDS_REFACTORING,
    "feature_envy": feature_envy_refactoring.FEATURE_ENVY_REFACTORING,
    "inappropriate_intimacy": inappropriate_intimacy_refactoring.INAPPROPRIATE_INTIMACY_REFACTORING,
    "switch_statement_abuser": switch_statement_refactoring.SWITCH_STATEMENT_ABUSER_REFACTORING,
    "excessive_flags": excessive_flag_refactoring.EXCESSIVE_FLAGS_REFACTORING,
    "middle_man": middle_flag_refactoring.MIDDLE_MAN_REFACTORING,
    "duplicate_code": duplicate_code_refactoring.DUPLICATE_CODE_REFACTORING,
    "conditionals": conditionals_refactoring.OVERLY_COMPLEX_CONDITIONALS_REFACTORING,
    "global_conflict": global_conflict_refactoring.GLOBAL_VARIABLE_CONFLICT_REFACTORING,
    "long_parameter_list": long_parameter_refactoring.LONG_PARAMETER_LIST_REFACTORING
}