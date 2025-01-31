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

GOD_OBJECT = {
    "file_path": "car.py",
    "code_snippet": """
class Car:
    def __init__(self, make, model, year, color):
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.is_running = False
        self.is_parked = True

    def start(self):
        if self.is_parked:
            self.is_running = True
            self.is_parked = False
            print("The car has started.")
        else:
            print("You can't start the car while it's already running or not parked.")

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.is_parked = True
            print("The car has stopped.")
        else:
            print("You can't stop the car while it's not running or already parked.")

    def accelerate(self, speed):
        if self.is_running and not self.is_parked:
            print(f"The car is accelerating to {speed} mph.")
        else:
            print("You can't accelerate while the car is not running or parked.")

    def brake(self):
        if self.is_running and not self.is_parked:
            print("The car is braking.")
        else:
            print("You can't brake while the car is not running or parked.")

    def paint(self, new_color):
        self.color = new_color
        print(f"The car has been painted {new_color}.")

    def tune_up(self):
        print("The car has had a tune-up.")

    def repair_engine(self):
        print("The engine has been repaired.")

    def replace_tires(self):
        print("The tires have been replaced.")

    """,
}

message = { 
    'correlation_id': '1234',
    'task_type': 'refactoring',
    'task_data': GOD_OBJECT,
    'task_job': 'god_object'
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