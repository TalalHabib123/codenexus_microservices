import ast

def parse_code_smell_output(input_str, task_data):
    lines = input_str.strip().split('\n')

    result = {}
    current_file = None
    current_detected = None
    current_issue = None

    # Helper function to strip braces if present
    def strip_braces(value):
        value = value.strip()
        if value.startswith('{') and value.endswith('}'):
            return value[1:-1].strip()
        return value

    for line in lines:
        line = line.strip()
        if line.startswith("File:"):
            # If we have a complete set from previous iteration, store it
            if current_file and current_detected and current_issue:
                if current_file not in result:
                    result[current_file] = []
                result[current_file].append({"Detected": current_detected, "Issue": current_issue})

            # Reset for new entry
            current_detected = None
            current_issue = None

            filename_part = line.split("File:", 1)[1].strip()
            current_file = strip_braces(filename_part)

        elif line.startswith("Detected:"):
            # If we have a previous complete set, store it
            if current_file and current_detected and current_issue:
                if current_file not in result:
                    result[current_file] = []
                result[current_file].append({"Detected": current_detected, "Issue": current_issue})
            
            detected_part = line.split("Detected:", 1)[1].strip()
            current_detected = strip_braces(detected_part)
            current_issue = None

        elif line.startswith("Issue:"):
            issue_part = line.split("Issue:", 1)[1].strip()
            current_issue = issue_part

    # After finishing all lines, if we ended with a complete set, store it
    if current_file and current_detected and current_issue:
        if current_file not in result:
            result[current_file] = []
        result[current_file].append({"Detected": current_detected, "Issue": current_issue})

    # Eliminate duplicates and combine issues
    cleaned_result = {}
    for file_name, entries in result.items():
        detected_map = {}
        for entry in entries:
            det = entry["Detected"]
            iss = entry["Issue"]
            if det not in detected_map:
                detected_map[det] = [iss]
            else:
                if iss not in detected_map[det]:
                    detected_map[det].append(iss)

        cleaned_entries = []
        for det, issues in detected_map.items():
            if len(issues) > 1:
                combined_issue = '. '.join(issues)
            else:
                combined_issue = issues[0]
            cleaned_entries.append({"Detected": det, "Issue": combined_issue})
        cleaned_result[file_name] = cleaned_entries

    # Use AST to find line numbers
    def find_line_numbers_for_file(code):
        # Parse the code and find classes and functions
        # top_level_functions: {func_name: lineno}
        # classes: {class_name: {'lineno': ..., 'methods': {method_name: lineno}}}
        tree = ast.parse(code)
        top_level_functions = {}
        classes = {}

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                # Top-level function
                top_level_functions[node.name] = node.lineno
            elif isinstance(node, ast.ClassDef):
                # Class
                class_info = {
                    "lineno": node.lineno,
                    "methods": {}
                }
                for subnode in node.body:
                    if isinstance(subnode, ast.FunctionDef):
                        class_info["methods"][subnode.name] = subnode.lineno
                classes[node.name] = class_info

        return top_level_functions, classes

    def find_line_number(file_name, detected):
        code = task_data.get(file_name, "")
        if not code:
            return None

        top_level_funcs, classes = find_line_numbers_for_file(code)

        if '.' in detected:
            # ClassName.MethodName
            class_name, method_name = detected.split('.', 1)
            if class_name in classes:
                class_methods = classes[class_name]["methods"]
                # If method found
                if method_name in class_methods:
                    return class_methods[method_name]
                else:
                    return None
            else:
                return None
        else:
            # Could be top-level function or a class
            # Check top-level function first
            if detected in top_level_funcs:
                return top_level_funcs[detected]
            # If not a top-level function, maybe it's a class
            if detected in classes:
                return classes[detected]["lineno"]
            return None

    # Add LineNumber to each entry
    for file_name, entries in cleaned_result.items():
        for entry in entries:
            line_num = find_line_number(file_name, entry["Detected"])
            entry["LineNumber"] = line_num

    return cleaned_result

if __name__ == "__main__":
# Example usage
    input_str = """
    File: OrderProcessor.py
    Detected: OrderProcessor.process_order_direct_access
    Issue: The method directly accesses private attribute `_stock` of the `Inventory` class, bypassing its public interface and tightly coupling the two classes.

    File: CustomerAndNotification.py
    Detected: NotificationService.send_direct_access
    Issue: The method directly accesses private attributes `name` and `email` of the `Customer` class, but in Python these attributes are public, which changes the risk.

    Upon reevaluation based on your parameters the revised answer is:

    File: OrderProcessor.py
    Detected: OrderProcessor.process_order_direct_access
    Issue: The method directly accesses private attribute `_stock` of the `Inventory` class, bypassing its public interface and tightly coupling the two classes.

    File: {PaymentProcessor.py}
    Detected: {PaymentProcessor.PaymentProcessor.process_payment}
    Issue: Tightly coupled logic handling multiple distinct payment types, leading to a large conditional structure with four cases, making it hard to extend or maintain.

    File: {PaymentProcessor.py}
    Detected: {process_refund}
    Issue: Overly complex function with four distinct refund cases, each performing non-encapsulated tasks, resulting in a heavy reliance on conditionals and difficulties in testing or extending the function.

    File: {OrderHandler.py}
    Detected: {OrderHandler.OrderHandler.handle_order}
    Issue: Function handling multiple order types with tightly coupled logic across three distinct cases, making it challenging to maintain, extend, or test due to its complexity.

    File: {OrderHandler.py}
    Detected: {process_shipping}
    Issue: Excessive use of conditionals to differentiate between shipping types, leading to a function with three distinct but non-modularized cases, resulting in tightly coupled logic.
    """

    task_data = {
        "OrderProcessor.py": "class Inventory: def __init__(self): self._stock = {} def add_stock(self, item_id, qty): self._stock[item_id] = qty def has_stock(self, items): return all(self._stock.get(i['id'],0)>=i['quantity'] for i in items) class OrderProcessor: def process_order_direct_access(self, order, inventory): if not inventory._stock.get(order['items'][0]['id'], 0) >= order['items'][0]['quantity']: return 'Failed' inventory._stock[order['items'][0]['id']] -= order['items'][0]['quantity'] return 'Success'",
        "CustomerAndNotification.py": "class Customer: def __init__(self, name, email): self.name = name self.email = email class NotificationService: def send_direct_access(self, customer, message): print(f'Sending message to {customer.name} at {customer.email}: {message}')",
        "PaymentProcessor.py": "class PaymentProcessor: def process_payment(self, payment_type, amount): if payment_type == 'credit_card': print('Credit card') elif payment_type == 'paypal': print('Paypal') elif payment_type == 'bank_transfer': print('Bank Transfer') elif payment_type == 'crypto': print('Crypto') def process_refund(payment_type, amount): if payment_type == 'credit_card': print('Refund CC') elif payment_type == 'paypal': print('Refund PayPal') elif payment_type == 'bank_transfer': print('Refund Bank') elif payment_type == 'crypto': print('Refund Crypto')",
        "OrderHandler.py": "class OrderHandler: def handle_order(self, order_type, details): if order_type == 'online': print('Online') elif order_type == 'instore': print('Instore') elif order_type == 'pickup': print('Pickup') def process_shipping(order_type, details): if order_type == 'standard': print('Standard') elif order_type == 'express': print('Express') elif order_type == 'overnight': print('Overnight')"
    }


    parsed = parse_code_smell_output(input_str, task_data)
    print(parsed)
