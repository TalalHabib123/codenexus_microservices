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
}