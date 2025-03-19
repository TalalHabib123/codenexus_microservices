import boto3
import os
import json
from dotenv import load_dotenv
from utils_helper import get_or_create_queue


load_dotenv()

sqs = boto3.client(
    'sqs', 
    endpoint_url=str(os.getenv('SQS_ENDPOINT_URL')), 
    region_name=str(os.getenv('REGION_NAME')),
    aws_access_key_id=str(os.getenv('AWS_ACCESS_KEY_ID')),
    aws_secret_access_key=str(os.getenv('AWS_SECRET_ACCESS_KEY'))
)

task_queue_url = get_or_create_queue(sqs, os.getenv('TASK_QUEUE_NAME'))
response_queue_url = get_or_create_queue(sqs, os.getenv('RESPONSE_QUEUE_NAME'))

EXCESSIVE_FLAG = {
    "file_path": "car.py",
    "code_snippet": """
def process_data_excessive_flags(
    data,
    clean=False,
    sort_data=False,
    filter_positive=False,
    normalize_data=False,
    square_data=False,
    aggregate_result=False,
    log_operations=False
):
    result = data.copy()
    if log_operations:
        print("Original data:", result)
    
    if clean:
        result = [x for x in result if x is not None]
        if log_operations:
            print("After cleaning:", result)
    
    if sort_data:
        result.sort()
        if log_operations:
            print("After sorting:", result)
    
    if filter_positive:
        result = [x for x in result if x > 0]
        if log_operations:
            print("After filtering positive numbers:", result)
    
    if normalize_data:
        total = sum(result)
        if total != 0:
            result = [x / total for x in result]
        if log_operations:
            print("After normalization:", result)
    
    if square_data:
        result = [x ** 2 for x in result]
        if log_operations:
            print("After squaring:", result)
    
    if aggregate_result:
        aggregated = sum(result)
        if log_operations:
            print("After aggregation:", aggregated)
        result = aggregated
    
    return result
    """,
}

message = { 
    'correlation_id': '1234',
    'task_type': 'refactoring',
    'task_data': EXCESSIVE_FLAG,
    'task_job': 'excessive_flags'
}

sqs.send_message(QueueUrl=task_queue_url, MessageBody=json.dumps(message))

while True:
    response = sqs.receive_message(QueueUrl=response_queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=5)
    messages = response.get('Messages', [])
    
    if messages:
        message_body = json.loads(messages[0]['Body'])
        correlation_id = message_body['correlation_id']
        processed_data = message_body['processed_data']
        task_status = message_body['task_status']
        
        if task_status == "success":
            print(f"Processed data for correlation ID {correlation_id}: {processed_data['refactored_code']}")
        else:
            print(f"Error processing data for correlation ID {correlation_id}")
        
        
        receipt_handle = messages[0]['ReceiptHandle']
        sqs.delete_message(QueueUrl=response_queue_url, ReceiptHandle=receipt_handle)
        
        break