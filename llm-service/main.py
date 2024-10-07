import boto3
import json
import asyncio

# SQS client configuration (using LocalStack for local testing)
sqs = boto3.client(
    'sqs', 
    endpoint_url='http://localhost:4566', 
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key = 'test'
)

# Create or retrieve task and response queues
task_queue_url = sqs.create_queue(QueueName='LLMTaskQueue')['QueueUrl']
response_queue_url = sqs.create_queue(QueueName='LLMResponseQueue')['QueueUrl']

async def process_tasks_from_queue():
    while True:
        # Poll the task queue for messages
        response = sqs.receive_message(QueueUrl=task_queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=10)
        messages = response.get('Messages', [])
        
        if messages:
            # Extract message data
            message_body = json.loads(messages[0]['Body'])
            correlation_id = message_body['correlation_id']
            task_type = message_body['task_type']
            task_data = message_body['task_data']
            
            # Simulate processing the task (placeholder logic)
            processed_result = f"Processed {task_type}: {task_data}"

            # Send the processed result to the response queue with the same correlation ID
            response_message = {
                'correlation_id': correlation_id,
                'processed_data': processed_result
            }
            print(f"Processed task: {task_type} - {task_data}")
            sqs.send_message(QueueUrl=response_queue_url, MessageBody=json.dumps(response_message))

            # Delete the processed message from the task queue
            sqs.delete_message(QueueUrl=task_queue_url, ReceiptHandle=messages[0]['ReceiptHandle'])

        # Pause briefly to avoid busy-waiting
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Start the async task processing loop
    asyncio.run(process_tasks_from_queue())
