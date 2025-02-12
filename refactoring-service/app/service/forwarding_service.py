from app.service.end_point_urls import (
    BOTO_CLIENT_URL, 
    BOTO_CLIENT_REGION, 
    AWS_ACCESS_KEY, 
    AWS_SECRET_ACCESS_KEY
)
import boto3
import json
from botocore.exceptions import ClientError
from app.utils.forwarding_keys import FORWARDING_KEYS

sqs = boto3.client(
    'sqs', 
    endpoint_url=BOTO_CLIENT_URL, 
    region_name=BOTO_CLIENT_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY
)

def get_or_create_queue(queue_name):
    try:
        response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
    except ClientError as e:
        if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
            try:
                response = sqs.create_queue(QueueName=queue_name)
                queue_url = response['QueueUrl']
            except ClientError as e:
                exit(1)
        else:
            exit(1)
    return queue_url

# task_queue_url = sqs.create_queue(QueueName='LLMTaskQueue')['QueueUrl']
task_queue_url = get_or_create_queue('LLMTaskQueue')

async def send_task_to_llm(correlation_id: str, task_type: str, task_job: str, task_data: dict):
    data = FORWARDING_KEYS[task_job](task_data)
    if not data:
        raise Exception("Data extraction failed")
    
    task_message = {
        'correlation_id': correlation_id,
        'task_type': task_type,
        'task_data': data, 
        'task_job': task_job
    }

    sqs.send_message(
        QueueUrl=task_queue_url,
        MessageBody=json.dumps(task_message)
    )