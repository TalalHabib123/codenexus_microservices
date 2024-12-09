from utils.helpers.function_extractor import extract_functions_from_code
from utils.helpers.class_extractor import extract_classes_from_code
from logger_config import get_logger

logger = get_logger(__name__)

extractor_type ={
    "functions": extract_functions_from_code,
    "classes": extract_classes_from_code
}

def process_data(task_data, type, job):
    processed_data = {}
    for file_path, content in task_data.items():
        try:
            processed_data[file_path] = extractor_type[type](content)
        except Exception as e:
            logger.error(f"Error extracting {type} from file: {file_path} for job: {job}")
            logger.error(e)
    
    return processed_data
        
