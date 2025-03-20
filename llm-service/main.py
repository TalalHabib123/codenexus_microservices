import os
import boto3
import json
import asyncio
from llm_processor import load_model_pipeline
from utils.rag.retrieval import initialize_knowledge_base_detection
from logger_config import get_logger
from dotenv import load_dotenv
from utils.retrieve_queue import get_or_create_queue
from job.detection_job import process_detection_job
from job.refactoring_job import process_refactoring_job

from huggingface_hub import login

login("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", True)

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

task_queue_url = get_or_create_queue(sqs, os.getenv('TASK_QUEUE_NAME'))
response_queue_url = get_or_create_queue(sqs, os.getenv('RESPONSE_QUEUE_NAME'))

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
            response_message = {}
            final_result = {}
            task_status = "success"
            
            try:
                if message_body['task_type'] == "detection":
                    final_result, task_status = process_detection_job(
                        message_body, 
                        model_pipeline, 
                        knowledge_base_detection, 
                        nn_model, 
                        INFERENCING_API)
                    
                if message_body['task_type'] == "refactoring":
                    final_result, task_status = process_refactoring_job(
                        message_body, 
                        model_pipeline, 
                        knowledge_base_detection, 
                        nn_model, 
                        INFERENCING_API)
        
            except Exception as e:
                logger.error(f"Error processing task message with correlation ID: {message_body['correlation_id']}")
                logger.error(e)
                task_status = e
                final_result = {} if message_body['task_type'] == "detection" else ""
            
            # Send the processed result to the response queue with the same correlation ID
            response_message = {
                'correlation_id': message_body['correlation_id'],
                'processed_data': final_result,
                'task_status': task_status,
                'task_type': message_body['task_type'],
                'task_job': message_body['task_job']
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
