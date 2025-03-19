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

GOD_Function = {
    "file_path": "car.py",
    "code_snippet": """
def simulate_long_function_code_smell(data):
    # Initialize accumulators and containers for various calculations
    total = 0
    count = 0
    even_sum = 0
    odd_sum = 0
    squares = []
    cubes = []
    factorials = {}
    processed_list = []

    # Loop over the data to perform several calculations
    for number in data:
        total += number
        count += 1
        if number % 2 == 0:
            even_sum += number
        else:
            odd_sum += number

        squares.append(number ** 2)
        cubes.append(number ** 3)
        
        # Compute factorial of the number
        fact = 1
        if number > 0:
            for i in range(1, number + 1):
                fact *= i
        factorials[number] = fact
        
        # Create a processed version of the number
        if number % 2 == 0:
            processed_list.append(number * 2)
        else:
            processed_list.append(number * 3)
    
    # Additional redundant nested loops for extra calculations
    extra_calculation = 0
    for i in range(10):
        for j in range(10):
            extra_calculation += i * j

    # Sum up the squares and cubes from earlier calculations
    sum_of_squares = 0
    for square in squares:
        sum_of_squares += square

    sum_of_cubes = 0
    for cube in cubes:
        sum_of_cubes += cube

    # Build a list of debug messages
    debug_messages = []
    for idx, val in enumerate(data):
        debug_messages.append(f"Index {idx}: Value {val}")

    # Calculate additional statistics
    average = total / count if count else 0
    min_value = min(data) if data else None
    max_value = max(data) if data else None
    data_range = (min_value, max_value)

    # Further nested loops to increase complexity
    nested_results = []
    for a in range(3):
        for b in range(3):
            for c in range(3):
                nested_results.append(a + b + c)

    # Generate Fibonacci sequence up to the maximum value found in data
    fibonacci_sequence = [0, 1]
    if max_value is not None and max_value > 1:
        while fibonacci_sequence[-1] < max_value:
            fibonacci_sequence.append(fibonacci_sequence[-1] + fibonacci_sequence[-2])

    # Multiply all numbers in the data to get a product (avoiding zero multiplication)
    product = 1
    for number in data:
        product *= (number if number != 0 else 1)

    # Create a dummy list with arbitrary operations
    dummy_list = []
    for i in range(20):
        dummy_list.append(i * 2)

    # An inner recursive function to further extend the function's length
    def recursive_sum(n):
        if n <= 0:
            return 0
        else:
            return n + recursive_sum(n - 1)
    recursion_result = recursive_sum(10)

    # Sum values at even and odd indices separately
    sum_even_indices = 0
    sum_odd_indices = 0
    for idx, number in enumerate(data):
        if idx % 2 == 0:
            sum_even_indices += number
        else:
            sum_odd_indices += number

    # Multiply processed list values to simulate additional processing
    multiplied_list = []
    for number in processed_list:
        multiplied_list.append(number * 5)

    # Combine pairs of data items in a nested loop
    combined = []
    for i in range(len(data)):
        for j in range(i, len(data)):
            combined.append(data[i] + data[j])

    # Temporary computations for further length
    temp_sum = sum(data) if data else 0
    temp_avg = temp_sum / len(data) if data else 0

    # Final aggregation of all computed values into a result dictionary
    result = {
        "total": total,
        "count": count,
        "average": average,
        "even_sum": even_sum,
        "odd_sum": odd_sum,
        "squares": squares,
        "cubes": cubes,
        "factorials": factorials,
        "processed_list": processed_list,
        "extra_calculation": extra_calculation,
        "sum_of_squares": sum_of_squares,
        "sum_of_cubes": sum_of_cubes,
        "debug_messages": debug_messages,
        "data_range": data_range,
        "nested_results": nested_results,
        "fibonacci_sequence": fibonacci_sequence,
        "product": product,
        "dummy_list": dummy_list,
        "recursion_result": recursion_result,
        "sum_even_indices": sum_even_indices,
        "sum_odd_indices": sum_odd_indices,
        "multiplied_list": multiplied_list,
        "combined": combined,
        "temp_sum": temp_sum,
        "temp_avg": temp_avg,
    }

    return result
    """,
}

message = { 
    'correlation_id': '1234',
    'task_type': 'refactoring',
    'task_data': GOD_Function,
    'task_job': 'long_function'
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