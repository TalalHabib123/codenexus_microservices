from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import uuid
import asyncio
import boto3
from contextlib import asynccontextmanager

websocket_gateway_router = FastAPI()

# SQS client configuration (Using LocalStack)
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

# Store WebSocket connections mapped by correlation IDs
ws_connections = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start consuming the response queue
    consume_task = asyncio.create_task(consume_response_queue())

    # Yield control back to the main application
    yield

    # Cleanup before shutdown
    consume_task.cancel()

@websocket_gateway_router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"Client connected: {websocket.client}")

    try:
        while True:
            # Wait for messages from the WebSocket client
            data = await websocket.receive_text()
            message = json.loads(data)
            task_data = message.get("data")
            task_type = message.get("task")

            # Generate a unique correlation ID for the task
            correlation_id = str(uuid.uuid4())

            # Store WebSocket connection for the correlation ID
            ws_connections[correlation_id] = websocket

            # Send acknowledgment to the client
            await websocket.send_text(json.dumps({
                "status": "task_started",
                "correlation_id": correlation_id
            }))

            # Send task to the LLM task queue via SQS
            await send_task_to_llm(correlation_id, task_type, task_data)

    except WebSocketDisconnect:
        print(f"Client disconnected: {websocket.client}")


async def send_task_to_llm(correlation_id: str, task_type: str, task_data: str):
    # Prepare message for the task queue
    task_message = {
        'correlation_id': correlation_id,
        'task_type': task_type,
        'task_data': task_data
    }
    
    # Send the message to the LLM task queue
    sqs.send_message(QueueUrl=task_queue_url, MessageBody=json.dumps(task_message))

# This function will constantly poll the response queue to send results back to the WebSocket client
async def consume_response_queue():
    while True:
        # Poll the response queue for processed results
        response = sqs.receive_message(QueueUrl=response_queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=10)
        messages = response.get('Messages', [])
        
        if messages:
            message_body = json.loads(messages[0]['Body'])
            correlation_id = message_body['correlation_id']
            processed_data = message_body['processed_data']

            # Retrieve the WebSocket connection using the correlation ID
            websocket = ws_connections.get(correlation_id)
            if websocket:
                # Send the processed result back to the WebSocket client
                await websocket.send_text(json.dumps({
                    "status": "task_completed",
                    "correlation_id": correlation_id,
                    "processed_data": processed_data
                }))
                # Clean up connection once message is sent
                del ws_connections[correlation_id]

            # Delete the processed message from the response queue
            sqs.delete_message(QueueUrl=response_queue_url, ReceiptHandle=messages[0]['ReceiptHandle'])

        await asyncio.sleep(1)  # Small delay to avoid busy-waiting 