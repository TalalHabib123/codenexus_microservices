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

SWITCH_STATEMENT = {
    "file_path": "car.py",
    "code_snippet": """
def process_event(event_type, data):
    if event_type == "CREATE":
        result = f"Created new record with data: {data}"
    elif event_type == "UPDATE":
        result = f"Updated record with data: {data}"
    elif event_type == "DELETE":
        result = f"Deleted record with ID: {data.get('id', 'unknown')}"
    elif event_type == "RETRIEVE":
        result = f"Retrieved record details: {data}"
    elif event_type == "ARCHIVE":
        result = f"Archived record with ID: {data.get('id', 'unknown')}"
    elif event_type == "RESTORE":
        result = f"Restored record with ID: {data.get('id', 'unknown')}"
    elif event_type == "VALIDATE":
        if data.get("is_valid"):
            result = "Validation successful."
        else:
            result = "Validation failed."
    elif event_type == "EXPORT":
        result = f"Exported data: {data}"
    elif event_type == "IMPORT":
        result = f"Imported data: {data}"
    elif event_type == "NOTIFY":
        result = f"Notification sent with message: {data.get('message', '')}"
    else:
        result = "Unknown event type."

    return result
    """,
}

message = { 
    'correlation_id': '1234',
    'task_type': 'refactoring',
    'task_data': SWITCH_STATEMENT,
    'task_job': 'switch_statement_abuser'
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