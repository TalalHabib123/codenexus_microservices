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

TEMPORARY = {
    "file_path": "car.py",
    "code_snippet": """
class Order:
    def __init__(self, order_id, items, customer):
        self.order_id = order_id
        self.items = items
        self.customer = customer
        self.total = sum(item.get('price', 0) for item in items)
        # Temporary field used only in apply_discount method (Temporary Field Code Smell)
        self.temp_discount_value = 0

    def apply_discount(self, discount_code):
        # Use the temporary field to store the discount value
        if discount_code == "SAVE10":
            self.temp_discount_value = self.total * 0.10
        elif discount_code == "SAVE20":
            self.temp_discount_value = self.total * 0.20
        else:
            self.temp_discount_value = 0

        # Apply the discount to the total
        self.total -= self.temp_discount_value

        # Capture the discount value for reporting
        discount_applied = self.temp_discount_value

        # Reset the temporary field immediately after use
        self.temp_discount_value = 0

        return discount_applied

    def add_item(self, item):
        self.items.append(item)
        self.total += item.get('price', 0)

    def get_order_summary(self):
        return {
            "order_id": self.order_id,
            "customer": self.customer,
            "total": self.total,
            "items_count": len(self.items)
        }

def process_orders(orders, discount_code):
    for order in orders:
        discount = order.apply_discount(discount_code)
        print(f"Order ID {order.order_id}: Applied discount of ${discount:.2f}")
        print("Order summary:", order.get_order_summary())

if __name__ == "__main__":
    # Create sample orders
    order1 = Order(order_id=101, items=[{"price": 120}, {"price": 80}], customer="Alice")
    order2 = Order(order_id=102, items=[{"price": 200}, {"price": 150}], customer="Bob")

    orders = [order1, order2]
    process_orders(orders, discount_code="SAVE10")
    """,
}

message = { 
    'correlation_id': '1234',
    'task_type': 'refactoring',
    'task_data': TEMPORARY,
    'task_job': 'temporary_field'
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