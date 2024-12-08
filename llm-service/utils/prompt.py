from utils.system_prompts.long_function import LONG_FUNCTION
from utils.system_prompts.god_object import GOD_OBJECT

from utils.content_prompt.long_function_content import create_long_function_prompt
from utils.content_prompt.god_object_content import create_god_object_prompt

def create_system_prompt(task_type, task_job):
    if task_type == "detection":
        if task_job == "god_object":
            return GOD_OBJECT
                
        elif task_job == "long_function":
            return LONG_FUNCTION


def create_detection_prompt(task_job, task_data, knowledge_base_detection, nn_model):
    content_prompt = {}
    system_prompt = {}
    processed_data = task_data
    if task_job == "long_function":
        content_prompt, processed_data = create_long_function_prompt(task_data, knowledge_base_detection, nn_model)
        system_prompt = create_system_prompt("detection", task_job)
        
    elif task_job == "god_object":
        content_prompt, processed_data = create_god_object_prompt(task_data, knowledge_base_detection, nn_model)
        system_prompt = create_system_prompt("detection", task_job)
        
    prompt = [
        system_prompt,
        content_prompt
    ]
    return prompt, processed_data


def create_prompt(task_type, task_data, task_job, knowledge_base_detection, nn_model):
    if task_type == "detection":
        return create_detection_prompt(task_job, task_data, knowledge_base_detection, nn_model)