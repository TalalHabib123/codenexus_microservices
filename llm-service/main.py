import os
import boto3
import json
import asyncio
from llm_processor import load_model_pipeline, process_with_llm
from utils.rag.retrieval import initialize_knowledge_base_detection
from utils.prompt import create_prompt
from logger_config import get_logger
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from utils.string_parser import parse_code_smell_output
from utils.file_hasher import create_mapped_task_data, revert_task_data_keys

INFERENCING_API = True

load_dotenv()

logger = get_logger(__name__)

sqs = boto3.client(
    'sqs', 
    endpoint_url=str(os.getenv('SQS_ENDPOINT_URL')), 
    region_name=str(os.getenv('REGION_NAME')),
    aws_access_key_id=str(os.getenv('AWS_ACCESS_KEY_ID')),
    aws_secret_access_key=str(os.getenv('AWS_SECRET_ACCESS_KEY'))
)

# Create or retrieve task and response queues
def get_or_create_queue(queue_name):
    try:
        # Try to get the queue URL if it already exists
        logger.info(f"Getting queue URL for queue: {queue_name}")
        response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
    except ClientError as e:
        # If the queue does not exist
        logger.info(f"Queue does not exist: {queue_name}")
        if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
            try:
                # Create the queue if it does not exist
                logger.info(f"Creating queue: {queue_name}")
                response = sqs.create_queue(QueueName=queue_name)
                queue_url = response['QueueUrl']
                logger.info(f"Queue created: {queue_name}")
            except ClientError as e:
                # If there is an error creating the queue, raise it
                logger.error(f"Error creating queue: {queue_name}")
                logger.error(e)
                exit(1)
        else:
            # If there is another error, raise it
            logger.error(f"Error creating queue: {queue_name}")
            logger.error(e)
            exit(1)
    return queue_url

# Get or create task and response queues
task_queue_url = get_or_create_queue(os.getenv('TASK_QUEUE_NAME'))
response_queue_url = get_or_create_queue(os.getenv('RESPONSE_QUEUE_NAME'))

# Load the LLM model pipeline
model_pipeline = load_model_pipeline(use_inference_api=INFERENCING_API)
try:
    logger.info("Initializing knowledge base for detection")
    knowledge_base_detection, nn_model, embeddings = initialize_knowledge_base_detection()
except Exception as e:
    logger.error("Error initializing knowledge base for detection")
    logger.error(e)
    exit(1)

async def process_tasks_from_queue():
    while True:
        # Poll the task queue for messages
        response = sqs.receive_message(QueueUrl=task_queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=5)
        messages = response.get('Messages', [])
        
        if messages:
            # Extract message data
            logger.info("Received task message")
            message_body = json.loads(messages[0]['Body'])
            correlation_id = message_body['correlation_id']
            task_type = message_body['task_type']
            task_data = message_body['task_data']
            modified_task_data, name_to_path_mapping = create_mapped_task_data(task_data)
            task_job = message_body['task_job'] 
            response_message = {}
            final_result = ""
            processed_result = {}
            task_status = "success"
            try:
                # Process the task message
                logger.info(f"Processing task message with correlation ID: {correlation_id}")
                logger.info(f"Task type: {task_type}")
                logger.info(f"Task job: {task_job}")
                messages_prompt, processed_data = create_prompt(task_type, modified_task_data, task_job,knowledge_base_detection, nn_model)  #knowledge_base_detection, nn_model
                try:
                    logger.info(f"Generating response for task message with correlation ID: {correlation_id}")
                    processed_result = process_with_llm(model_pipeline, messages_prompt, use_inference_api=INFERENCING_API)
                    if processed_result == "None":
                        continue
                    if task_type =="detection":
                        processed_data = parse_code_smell_output(processed_result, modified_task_data)
                        final_result = revert_task_data_keys(processed_data, name_to_path_mapping)
                except Exception as e:
                    logger.error(f"Error generating response for task message with correlation ID: {correlation_id}")
                    logger.error(e)
                    task_status = e
                    break
            except Exception as e:
                logger.error(f"Error processing task message with correlation ID: {correlation_id}")
                logger.error(e)
                task_status = e
                

            # Send the processed result to the response queue with the same correlation ID
            response_message = {
                'correlation_id': correlation_id,
                'processed_data': final_result,
                'task_status': task_status,
                'task_type': task_type,
                'task_job': task_job
            }
            
            sqs.send_message(QueueUrl=response_queue_url, MessageBody=json.dumps(response_message))

            # Delete the processed message from the task queue
            sqs.delete_message(QueueUrl=task_queue_url, ReceiptHandle=messages[0]['ReceiptHandle'])

        # Pause briefly to avoid busy-waiting
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Start the async task processing loop
    # Clean the queue before starting the process
    sqs.purge_queue(QueueUrl=task_queue_url)
    sqs.purge_queue(QueueUrl=response_queue_url)
    asyncio.run(process_tasks_from_queue())
