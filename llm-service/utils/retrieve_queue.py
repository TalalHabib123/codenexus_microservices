from logger_config import get_logger
from botocore.exceptions import ClientError

logger = get_logger(__name__)

def get_or_create_queue(sqs, queue_name):
    try:
        # Try to get the queue URL if it already exists
        logger.info(f"Getting queue URL for queue: {queue_name}")
        response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
    except ClientError as e:
        # If the queue does not exist
        logger.info(f"Queue does not exist: {queue_name}")
        if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
            try:
                # Create the queue if it does not exist
                logger.info(f"Creating queue: {queue_name}")
                response = sqs.create_queue(QueueName=queue_name)
                queue_url = response['QueueUrl']
                logger.info(f"Queue created: {queue_name}")
            except ClientError as e:
                # If there is an error creating the queue, raise it
                logger.error(f"Error creating queue: {queue_name}")
                logger.error(e)
                exit(1)
        else:
            # If there is another error, raise it
            logger.error(f"Error creating queue: {queue_name}")
            logger.error(e)
            exit(1)
    return queue_url