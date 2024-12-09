from utils.system_prompts.detection.long_function import LONG_FUNCTION
from utils.system_prompts.detection.god_object import GOD_OBJECT
from utils.system_prompts.detection.feature_envy import FEATURE_ENVY  
from utils.system_prompts.detection.inappropriate_intimacy import INAPPROPRIATE_INTIMACY
from utils.system_prompts.detection.middle_man import MIDDLE_MAN
from utils.system_prompts.detection.switch_statement import SWITCH_STATEMENT
from utils.system_prompts.detection.excessive_flag import EXCESSIVE_FLAGS


system_detection_prompts = {
    "long_function": LONG_FUNCTION,
    "god_object": GOD_OBJECT,
    "feature_envy": FEATURE_ENVY,
    "inappropriate_intimacy": INAPPROPRIATE_INTIMACY,
    "middle_man": MIDDLE_MAN,
    "switch_statement_abuser": SWITCH_STATEMENT,
    "excessive_flags": EXCESSIVE_FLAGS
}