from utils.string_parser import parse_code_smell_output
from utils.file_hasher import create_mapped_task_data, revert_task_data_keys
from utils.prompt import create_prompt, update_prompt, final_prompt
from llm_processor import process_with_llm
from logger_config import get_logger
import time

logger = get_logger(__name__)

def process_detection_job(message_body, model_pipeline, knowledge_base_detection, nn_model, INFERENCING_API):
    correlation_id = message_body['correlation_id']
    task_type = message_body['task_type']
    task_data = message_body['task_data']
    task_job = message_body['task_job']
    
    modified_task_data, name_to_path_mapping = create_mapped_task_data(task_data)
    final_result = {}
    task_status = "success"

    try:
        logger.info(f"Processing task message with correlation ID: {correlation_id}")
        logger.info(f"Task type: {task_type}")
        logger.info(f"Task job: {task_job}")

        messages_prompt, secondary_message_prompt, processed_data = create_prompt(
            task_type, modified_task_data, task_job, knowledge_base_detection, nn_model
        )

        processed_result, secondary_result = generate_responses(
            model_pipeline, messages_prompt, secondary_message_prompt, INFERENCING_API, correlation_id
        )

        if processed_result == "None" and secondary_result == "None":
            return final_result, task_status

        final_result = handle_detection(
            processed_result, secondary_result, modified_task_data, messages_prompt, 
            secondary_message_prompt, model_pipeline, INFERENCING_API, name_to_path_mapping, task_job
        )

    except Exception as e:
        logger.error(f"Error processing task message with correlation ID: {correlation_id}")
        logger.error(e)
        task_status = e

    return final_result, task_status

def generate_responses(model_pipeline, messages_prompt, secondary_message_prompt, INFERENCING_API, correlation_id):
    try:
        logger.info(f"Generating response for task message with correlation ID: {correlation_id}")
        processed_result = process_with_llm(model_pipeline, messages_prompt, use_inference_api=INFERENCING_API) #meta-llama/Llama-3.3-70B-Instruct
        time.sleep(1)
        secondary_result = process_with_llm(model_pipeline, secondary_message_prompt, use_inference_api=INFERENCING_API) #meta-llama/Llama-3.3-70B-Instruct
        return processed_result, secondary_result
    except Exception as e:
        logger.error(f"Error generating response for task message with correlation ID: {correlation_id}")
        logger.error(e)
        raise e
    
def generate_cleaned_result(model_pipeline, updated_result, INFERENCING_API, task_job):
    cleaning_prompt = final_prompt(updated_result, "detection", task_job)
    return process_with_llm(model_pipeline, cleaning_prompt, use_inference_api=INFERENCING_API) 

def handle_detection(processed_result, secondary_result, modified_task_data, messages_prompt, 
                     secondary_message_prompt, model_pipeline, INFERENCING_API, name_to_path_mapping, task_job):
    updated_prompt = update_prompt(messages_prompt, processed_result, secondary_message_prompt, secondary_result)

    final_processed_data = process_with_llm(model_pipeline, updated_prompt, use_inference_api=INFERENCING_API) #meta-llama/Llama-3.3-70B-Instruct
    # import pdb; pdb.set_trace()
    time.sleep(1)
    processed_data = generate_cleaned_result(model_pipeline, final_processed_data, INFERENCING_API, task_job)
    final_processed_result = parse_code_smell_output(processed_data, modified_task_data)

    return revert_task_data_keys(final_processed_result, name_to_path_mapping)