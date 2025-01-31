from utils.string_parser import parse_code_output
from utils.prompt import create_prompt, final_prompt
from llm_processor import process_with_llm
from logger_config import get_logger

logger = get_logger(__name__)

def process_refactoring_job(message_body, model_pipeline, knowledge_base_refactoring, nn_model, INFERENCING_API):
    correlation_id = message_body['correlation_id']
    task_type = message_body['task_type']
    task_data = message_body['task_data']
    task_job = message_body['task_job']
    
    final_data = {}
    task_status = "success"
    
    try:
        logger.info(f"Processing task message with correlation ID: {correlation_id}")
        logger.info(f"Task type: {task_type}")
        logger.info(f"Task job: {task_job}")
        
        file_path = task_data['file_path']
        
        messages_prompt = create_prompt(task_type, task_data, task_job, knowledge_base_refactoring, nn_model)
        
        processed_result = generate_responses(model_pipeline, messages_prompt, INFERENCING_API, correlation_id)
        
        if processed_result == "":
            raise Exception("Processed result is None")
        
        additional_prompt = final_prompt(processed_result, task_type, task_data)
        
        final_answer = generate_responses(model_pipeline, additional_prompt, INFERENCING_API, correlation_id) 
        
        if final_answer == "None":  
            final_result = parse_code_output(processed_result)
            
        else:
            final_result = parse_code_output(final_answer)
        
        final_data = {
            "file_path": file_path,
            "refactored_code": final_result[0]
        }
        
        if len(task_data.keys()) > 2:
            # If there additonal data process it here
            pass
        
    except Exception as e:
        logger.error(f"Error processing task message with correlation ID: {correlation_id}")
        logger.error(e)
        task_status = "failure"
        
    return final_data, task_status


def generate_responses(model_pipeline, messages_prompt, INFERENCING_API, correlation_id):
    try:
        logger.info(f"Generating response for task message with correlation ID: {correlation_id}")
        processed_result = process_with_llm(model_pipeline, messages_prompt, use_inference_api=INFERENCING_API)
        return processed_result
    except Exception as e:
        logger.error(f"Error generating response for task message with correlation ID: {correlation_id}")
        logger.error(e)
        raise e