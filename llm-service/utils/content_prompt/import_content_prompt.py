from utils.content_prompt.detection.long_function_content import create_long_function_prompt
from utils.content_prompt.detection.god_object_content import create_god_object_prompt
from utils.content_prompt.detection.feature_envy_content import create_feature_envy_prompt
from utils.content_prompt.detection.inappropriate_intimacy_content import create_inappropriate_intimacy_prompt
from utils.content_prompt.detection.middle_man_content import create_middle_man_prompt
from utils.content_prompt.detection.switch_statement_content import create_switch_statement_abuser_prompt
from utils.content_prompt.detection.excessive_flags_content import create_excessive_flags_prompt

content_detection_prompts = {
    "long_function": create_long_function_prompt,
    "god_object": create_god_object_prompt,
    "feature_envy": create_feature_envy_prompt,
    "inappropriate_intimacy": create_inappropriate_intimacy_prompt,
    "middle_man": create_middle_man_prompt,
    "switch_statement_abuser": create_switch_statement_abuser_prompt,
    "excessive_flags": create_excessive_flags_prompt
}
