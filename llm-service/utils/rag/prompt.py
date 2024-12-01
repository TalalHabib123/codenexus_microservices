from utils.function_extractor import extract_functions_from_code
from utils.class_extractor import extract_classes_from_code
from utils.system_prompts.long_function import LONG_FUNCTION
from utils.system_prompts.god_object import GOD_OBJECT

def system_prompt(task_type, task_job):
    if task_type == "detection":
        if task_job == "god_object":
            return GOD_OBJECT
                
        elif task_job == "long_function":
            return LONG_FUNCTION


def create_detection_prompt(task_job, task_data):
    processed_data = []
    if task_job == "long_function":
        processed_data = [{key: extract_functions_from_code(value)} for key, value in task_data.items()]
    elif task_job == "god_object":
        processed_data = [{key: extract_classes_from_code(value)} for key, value in task_data.items()]
    return processed_data
    
    

def create_prompt(task_type, task_data, task_job):
    pass