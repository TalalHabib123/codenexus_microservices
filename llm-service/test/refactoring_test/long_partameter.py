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

LONG_PARAMETER = {
    "file_path": "car.py",
    "code_snippet": """
def calculate_discount(price, customer_type, day_of_week, is_member, coupon_code):
    discount = 0
    if customer_type == "regular":
        if is_member:
            if day_of_week in ["Saturday", "Sunday"]:
                if coupon_code:
                    if coupon_code.startswith("VIP"):
                        discount = price * 0.25
                    else:
                        discount = price * 0.20
                else:
                    discount = price * 0.20
            else:
                if coupon_code:
                    if len(coupon_code) > 3:
                        discount = price * 0.15
                    else:
                        discount = price * 0.12
                else:
                    discount = price * 0.10
    """,
}

message = { 
    'correlation_id': '1234',
    'task_type': 'refactoring',
    'task_data': LONG_PARAMETER,
    'task_job': 'long_parameter_list'
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