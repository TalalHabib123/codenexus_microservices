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

CONDITIONALS = {
    "file_path": "car.py",
    "code_snippet": """
import datetime
import random

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
        else:
            if day_of_week == "Friday":
                if coupon_code:
                    if coupon_code == "FRIDAYSALE":
                        discount = price * 0.10
                    else:
                        discount = price * 0.05
                else:
                    discount = price * 0.05
            else:
                if coupon_code:
                    if coupon_code == "SPECIAL":
                        discount = price * 0.07
                    else:
                        discount = price * 0.03
                else:
                    discount = 0
    elif customer_type == "premium":
        if is_member:
            if coupon_code:
                if day_of_week in ["Monday", "Tuesday"]:
                    discount = price * 0.30
                else:
                    if coupon_code.endswith("EXTRA"):
                        discount = price * 0.28
                    else:
                        discount = price * 0.25
            else:
                discount = price * 0.20
        else:
            if coupon_code:
                if coupon_code == "PREMIUM":
                    discount = price * 0.18
                else:
                    discount = price * 0.15
            else:
                discount = price * 0.15
    else:
        if coupon_code:
            if coupon_code.startswith("NEW"):
                discount = price * 0.05
            else:
                discount = price * 0.02
        else:
            discount = 0

    return discount

def process_order(order):
    # Extract order details
    price = order.get("price", 0)
    customer_type = order.get("customer_type", "regular")
    order_date = order.get("date", datetime.datetime.now())
    is_member = order.get("is_member", False)
    coupon_code = order.get("coupon_code", "")

    day_of_week = order_date.strftime("%A")

    # Calculate discount using the overly complex conditionals function
    discount = calculate_discount(price, customer_type, day_of_week, is_member, coupon_code)
    
    # Apply discount to get the final price
    final_price = price - discount

    # Additional well-structured code: simulate processing payment
    def process_payment(amount):
        print(f"Processing payment for amount: ${amount:.2f}")
        # Simulate payment success or failure
        if random.choice([True, False]):
            print("Payment processed successfully.")
            return True
        else:
            print("Payment failed.")
            return False

    payment_success = process_payment(final_price)

    # Log order details in a structured summary
    order_summary = {
        "original_price": price,
        "discount": discount,
        "final_price": final_price,
        "payment_success": payment_success,
        "processed_date": datetime.datetime.now().isoformat()
    }
    print("Order processed:", order_summary)
    return order_summary

def generate_sample_orders():
    return [
        {"price": 100, "customer_type": "regular", "date": datetime.datetime(2025, 3, 17), "is_member": True, "coupon_code": "VIP123"},
        {"price": 200, "customer_type": "premium", "date": datetime.datetime(2025, 3, 16), "is_member": True, "coupon_code": "DISCOUNTEXTRA"},
        {"price": 50, "customer_type": "regular", "date": datetime.datetime(2025, 3, 13), "is_member": False, "coupon_code": "FRIDAYSALE"},
        {"price": 75, "customer_type": "other", "date": datetime.datetime(2025, 3, 14), "is_member": False, "coupon_code": "NEWUSER"},
    ]

def main():
    orders = generate_sample_orders()
    for order in orders:
        print("\nProcessing new order:")
        process_order(order)

if __name__ == "__main__":
    main()
    """,
}

message = { 
    'correlation_id': '1234',
    'task_type': 'refactoring',
    'task_data': CONDITIONALS,
    'task_job': 'conditionals'
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