from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect
import httpx
import json
import uuid
import asyncio
import boto3
from contextlib import asynccontextmanager
from botocore.exceptions import ClientError
from app.service.endpoints_url import (
    BOTO_CLIENT_URL, 
    BOTO_CLIENT_REGION, 
    DETECTION_SERVICE_URL,
    AWS_ACCESS_KEY,
    AWS_SECRET_ACCESS_KEY,
    REFACTOR_SERVICE_URL
)

from app.service.refactor_mapping_keys import MAPPING_KEYS

websocket_gateway_router = APIRouter()

# SQS client configuration (Using LocalStack)
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

response_queue_url = get_or_create_queue('LLMResponseQueue')

# Store WebSocket connections mapped by correlation IDs
ws_connections = {}
refactoring_tasks = {}

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
            data = await websocket.receive_text()
            message = json.loads(data)
            
            task_data = message.get("data")
            task_type = message.get("task")
            task_job = message.get("job")

            if not isinstance(task_data, dict):
                await websocket.send_text(json.dumps({
                    "status": "task_failed",
                    "error": "Invalid task data format. Expected a dictionary with file paths as keys and code as values."
                }))
                continue

            correlation_id = str(uuid.uuid4())

            ws_connections[correlation_id] = websocket

            task_started = await send_task_to_llm(correlation_id, task_type, task_job, task_data)

            if task_started:
                await websocket.send_text(json.dumps({
                    "task_status": "task_started",
                    "correlation_id": correlation_id
                }))
            else:
                await websocket.send_text(json.dumps({
                    "task_status": "task_failed",
                    "correlation_id": correlation_id,
                    "error": "Task failed to start"
                }))

    except WebSocketDisconnect:
        print(f"Client disconnected: {websocket.client}")

async def send_task_to_llm(correlation_id: str, task_type: str, task_job: str, task_data: dict) -> bool:
    task_message = {
        'correlation_id': correlation_id,
        'task_type': task_type,
        'task_data': task_data, 
        'task_job': task_job
    }
    
    if task_type == 'detection':
        return await forward_task_to_service(DETECTION_SERVICE_URL + "/forward-task", task_message)
    elif task_type == 'refactoring':
        refactoring_tasks[correlation_id] = task_data
        return await forward_task_to_service(REFACTOR_SERVICE_URL + "/forward-task", task_message)
    else:
        return False

async def forward_task_to_service(service_url: str, task_message: dict) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(service_url, json=task_message)
            if response.status_code == 200:
                return True
            else:
                print(f"Failed to forward task: {response.text}")
                return False
    except Exception as e:
        print(f"Exception during forwarding task: {e}")
        return False
    
async def process_detection_response(message_body: dict):
    correlation_id = message_body['correlation_id']
    processed_data = message_body['processed_data']
    task_status = message_body['task_status']
    task_type = message_body['task_type']
    task_job = message_body['task_job']
    
    print("Processing detection response")
    websocket = ws_connections.get(correlation_id)
    print(f"Websocket: {websocket}")
    if websocket:
        print("Sending response to client")
        await websocket.send_text(json.dumps({
            "task_status": task_status,
            "correlation_id": correlation_id,
            "processed_data": processed_data,
            "task_type": task_type,
            "task_job": task_job
        }))
        del ws_connections[correlation_id]
        await websocket.close(code=1000)
        
async def process_refactoring_response(message_body: dict):
    correlation_id = message_body['correlation_id']
    processed_data = message_body['processed_data']
    task_status = message_body['task_status']
    task_type = message_body['task_type']
    task_job = message_body['task_job']
    

    websocket = ws_connections.get(correlation_id)
    print(f"Websocket: {websocket}")
    refactoring_job = refactoring_tasks.get(correlation_id)
    print(f"Refactoring Job: {refactoring_job}")
    print(f"task_job: {task_job}")  
    task_message = MAPPING_KEYS[task_job](refactoring_job, processed_data)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"Task Message: {task_message}")
    if websocket:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        final_data = {
            "file_path": processed_data['file_path'],
        }
        print("Processing refactoring response")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{REFACTOR_SERVICE_URL}/mapping/{task_job}", json=task_message)
                if response.status_code == 200:
                    final_data['code_snippet'] = response.json()['refactored_code']
                    processed_data = final_data
                else:
                    final_data['code_snippet'] = refactoring_job['code_snippet']
                    processed_data = final_data
                    task_status = "failed"
        except Exception as e:
            final_data['code_snippet'] = refactoring_job['code_snippet']
            processed_data = final_data
            task_status = "failed"
        print("Sending Task Response for Response")
        await websocket.send_text(json.dumps({
            "task_status": task_status,
            "correlation_id": correlation_id,
            "processed_data": processed_data,
            "task_type": task_type,
            "task_job": task_job
        }))
        del ws_connections[correlation_id]
        await websocket.close(code=1000)

async def consume_response_queue():
    while True:
        response = sqs.receive_message(QueueUrl=response_queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=10)
        messages = response.get('Messages', [])
        
        if messages:
            message_body = json.loads(messages[0]['Body'])
            print(f"Received message: {message_body}")
            if message_body['task_type'] == 'detection':
                await process_detection_response(message_body)
            
            elif message_body['task_type'] == 'refactoring':
                await process_refactoring_response(message_body)

            sqs.delete_message(QueueUrl=response_queue_url, ReceiptHandle=messages[0]['ReceiptHandle'])

        await asyncio.sleep(1) 