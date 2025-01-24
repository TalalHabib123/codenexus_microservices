import boto3
from botocore.exceptions import ClientError

def get_or_create_queue(sqs, queue_name):
    try:
        # Try to get the queue URL if it already exists
        response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
    except ClientError as e:
        # If the queue does not exist
        if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
            try:
                # Create the queue if it does not exist
                response = sqs.create_queue(QueueName=queue_name)
                queue_url = response['QueueUrl']
            except ClientError as e:
                exit(1)
        else:
            exit(1)
    return queue_url