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

GLOBAL = {
    "file_path": "car.py",
    "code_snippet": """
global_config = {
    "mode": "development",
    "version": 1.0,
}

config = {
    "mode": "production",
    "debug": True,
}

# A global counter used in various parts of the script
global_counter = 0

def update_config(mode, debug_flag):
    global global_config, config
    # Update the global configuration inconsistently
    global_config["mode"] = mode
    config["debug"] = debug_flag
    print("Updated global_config:", global_config)
    print("Updated config:", config)

def increment_counter():
    global global_counter
    global_counter += 1
    print("Global counter incremented to:", global_counter)

def process_data(data):
    global processed_data  # 'processed_data' is not defined elsewhere
    processed_data = []   # Initialize within the function (conflict with global state)
    for item in data:
        processed_data.append(item * 2)
    print("Processed data:", processed_data)

def conflicting_function():
    global global_counter, config
    # Reassign the entire 'config' dictionary unexpectedly
    config = {"mode": "testing", "debug": False}
    # Use the new config value to adjust the counter
    if config["debug"]:
        global_counter += 10
    else:
        global_counter -= 5
    print("After conflicting_function, global_counter:", global_counter)
    print("After conflicting_function, config:", config)

def main():
    print("Initial global_config:", global_config)
    print("Initial config:", config)
    
    update_config("staging", False)
    increment_counter()
    process_data([1, 2, 3, 4])
    conflicting_function()
    increment_counter()
    
    print("\nFinal state of globals:")
    print("global_config:", global_config)
    print("config:", config)
    print("global_counter:", global_counter)
    print("processed_data:", processed_data)

if __name__ == "__main__":
    main()

    """,
}

message = { 
    'correlation_id': '1234',
    'task_type': 'refactoring',
    'task_data': GLOBAL,
    'task_job': 'global_conflict'
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