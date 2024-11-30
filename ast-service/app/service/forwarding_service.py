# from app.service.end_point_urls import BOTO_CLIENT_URL, BOTO_CLIENT_REGION
# import boto3
# import json

# sqs = boto3.client(
#     'sqs', 
#     endpoint_url=BOTO_CLIENT_URL, 
#     region_name=BOTO_CLIENT_REGION,
#     aws_access_key_id='test',
#     aws_secret_access_key = 'test'
# )

# task_queue_url = sqs.create_queue(QueueName='LLMTaskQueue')['QueueUrl']

# async def send_task_to_llm(correlation_id: str, task_type: str, task_job: str, task_data: dict):
#     task_message = {
#         'correlation_id': correlation_id,
#         'task_type': task_type,
#         'task_data': task_data, 
#         'task_job': task_job
#     }

#     sqs.send_message(
#         QueueUrl=task_queue_url,
#         MessageBody=json.dumps(task_message)
#     )