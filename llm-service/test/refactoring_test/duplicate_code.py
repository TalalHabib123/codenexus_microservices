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

DUPLICATE = {
    "file_path": "car.py",
    "code_snippet": """
import datetime

def process_online_order(order):
    print("Processing online order...")
    
    # Validate order details
    if "items" not in order or not order["items"]:
        print("Invalid order: No items found.")
        return None

    # Duplicate calculation block (calculating total, discount, and tax)
    total = 0
    discount = 0
    for item in order["items"]:
        price = item.get("price", 0)
        quantity = item.get("quantity", 1)
        total += price * quantity
        
        # Duplicate discount logic
        if item.get("on_sale", False):
            discount += price * quantity * 0.1

    tax = total * 0.08  # 8% tax
    final_total = total - discount + tax

    # Duplicate summary creation block
    summary = {
        "order_id": order.get("order_id"),
        "order_date": order.get("order_date", datetime.datetime.now().isoformat()),
        "total": total,
        "discount": discount,
        "tax": tax,
        "final_total": final_total,
        "items_count": len(order["items"]),
        "order_type": "Online"
    }
    print("Online Order Summary:", summary)
    return summary

def process_instore_order(order):
    print("Processing in-store order...")
    
    # Validate order details
    if "items" not in order or not order["items"]:
        print("Invalid order: No items found.")
        return None

    # Duplicate calculation block (calculating total, discount, and tax)
    total = 0
    discount = 0
    for item in order["items"]:
        price = item.get("price", 0)
        quantity = item.get("quantity", 1)
        total += price * quantity
        
        # Duplicated discount logic
        if item.get("on_sale", False):
            discount += price * quantity * 0.1

    tax = total * 0.08  # 8% tax
    final_total = total - discount + tax

    # Duplicate summary creation block
    summary = {
        "order_id": order.get("order_id"),
        "order_date": order.get("order_date", datetime.datetime.now().isoformat()),
        "total": total,
        "discount": discount,
        "tax": tax,
        "final_total": final_total,
        "items_count": len(order["items"]),
        "order_type": "In-Store"
    }
    print("In-Store Order Summary:", summary)
    return summary

def send_receipt(order_summary):
    print("\nSending receipt...")
    print("Receipt Details:")
    for key, value in order_summary.items():
        print(f"{key}: {value}")

def main():
    # Sample order for online purchase
    online_order = {
        "order_id": "ON12345",
        "order_date": "2025-03-18T10:00:00",
        "items": [
            {"name": "Laptop", "price": 1000, "quantity": 1, "on_sale": True},
            {"name": "Mouse", "price": 50, "quantity": 2, "on_sale": False}
        ]
    }

    # Sample order for in-store purchase
    instore_order = {
        "order_id": "IS54321",
        "order_date": "2025-03-18T11:30:00",
        "items": [
            {"name": "Smartphone", "price": 800, "quantity": 1, "on_sale": True},
            {"name": "Charger", "price": 25, "quantity": 3, "on_sale": False}
        ]
    }

    online_summary = process_online_order(online_order)
    instore_summary = process_instore_order(instore_order)

    if online_summary:
        send_receipt(online_summary)
    if instore_summary:
        send_receipt(instore_summary)

if __name__ == "__main__":
    main()
    
    """,
}

message = { 
    'correlation_id': '1234',
    'task_type': 'refactoring',
    'task_data': DUPLICATE,
    'task_job': 'duplicate_code'
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