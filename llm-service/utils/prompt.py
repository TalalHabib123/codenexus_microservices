from utils.system_prompts.import_system_prompt import system_detection_prompts
from utils.content_prompt.import_content_prompt import content_detection_prompts                


def create_detection_prompt(task_job, task_data, knowledge_base_detection, nn_model):
    content_prompt = {}
    system_prompt = {}
    processed_data = task_data
    
    content_prompt, processed_data = content_detection_prompts[task_job](task_data, knowledge_base_detection, nn_model)
    system_prompt = system_detection_prompts[task_job]
        
    prompt = [
        system_prompt,
        content_prompt
    ]
    return prompt, processed_data


def create_prompt(task_type, task_data, task_job, knowledge_base_detection, nn_model):
    if task_type == "detection":
        return create_detection_prompt(task_job, task_data, knowledge_base_detection, nn_model)