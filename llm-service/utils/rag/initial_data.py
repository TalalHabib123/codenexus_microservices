INITIAL_DATA_DETECTION = [
    ('Long Function', """
        def show_chapter(chapter, tutorial):
            if chapter["orderIndex"] == 1:
                self.redirect_to_root()
                return

            higher_chapters = [item for item in chapter["items"] if item.get("higher")]
            lower_tutorials = [item for item in chapter["items"] if not item.get("higher")]

            title = chapter["title"]
            description = chapter["description"]

            if chapter.get("lowerItem"):
                self.next_path = self.get_chapter_path(self.tutorial, chapter["lowerItem"])
                self.next_link = self.next_path
            elif not tutorial.get("pathId") and lower_tutorials:
                self.next_path = self.get_tutorial_path(lower_tutorials[0])
                self.next_link = self.next_path
            elif chapter.get("last") and tutorial.get("footLinks") and len(tutorial["footLinks"]) > 0:
                self.next_path = tutorial["footLinks"]["url"]
            else:
                self.next_path = None

            if len(higher_chapters) == 0:
                self.prev_link = self.get_chapter_path(tutorial, higher_chapters)
            elif not tutorial.get("pathId") and tutorial.get("higherItem"):
                higher_tutorial = tutorial["higherItem"]
                last_chapter = higher_tutorial["chapters"][-1]

                if last_chapter["orderIndex"] == 1:
                    self.prev_link = self.get_tutorial_path(higher_tutorial)
                else:
                    self.prev_link = self.get_chapter_path(higher_tutorial, higher_chapters)
            else:
                self.prev_link = None

            self.store_props = {
                "checkableType": "Chapter",
                "checkableId": chapter["id"],
                "checkboxes": current_user.get_checkboxes_for(chapter) if self.signed_in else [],
            }

            self.set_store()
            self.modal = self.get_modal_chapter(chapter) or self.get_modal_tutorial(tutorial)
     """),
    
    ('God Object', """
        class Car:
            def __init__(self, make, model, year, color):
                self.make = make
                self.model = model
                self.year = year
                self.color = color
                self.is_running = False
                self.is_parked = True

            def start(self):
                if self.is_parked:
                    self.is_running = True
                    self.is_parked = False
                    print("The car has started.")
                else:
                    print("You can't start the car while it's already running or not parked.")

            def stop(self):
                if self.is_running:
                    self.is_running = False
                    self.is_parked = True
                    print("The car has stopped.")
                else:
                    print("You can't stop the car while it's not running or already parked.")

            def accelerate(self, speed):
                if self.is_running and not self.is_parked:
                    print(f"The car is accelerating to {speed} mph.")
                else:
                    print("You can't accelerate while the car is not running or parked.")

            def brake(self):
                if self.is_running and not self.is_parked:
                    print("The car is braking.")
                else:
                    print("You can't brake while the car is not running or parked.")

            def paint(self, new_color):
                self.color = new_color
                print(f"The car has been painted {new_color}.")

            def tune_up(self):
                print("The car has had a tune-up.")

            def repair_engine(self):
                print("The engine has been repaired.")

            def replace_tires(self):
                print("The tires have been replaced.")
     """),
    
    ('Feature Envy', """
        class ShoppingItem:
            def __init__(self, name: str, price: float, tax: float, discount: float = 0):
                self.name = name
                self.price = price
                self.tax = tax
                self.discount = discount

            def calculate_tax(self) -> float:
                return self.price * self.tax

            def calculate_discounted_price(self) -> float:
                return self.price * (1 - self.discount)

            def calculate_final_price(self) -> float:
                return self.calculate_discounted_price() + self.calculate_tax()

        class Order:
            def get_bill_total(self, items: list[ShoppingItem]) -> float:
                # Feature Envy: Order calculates the final price using ShoppingItem's data
                return sum([item.price * (1 - item.discount) + item.price * item.tax for item in items])

            def get_receipt_string(self, items: list[ShoppingItem]) -> list[str]:
                # Feature Envy: Order relies on ShoppingItem's fields to format the receipt
                return [
                    f"{item.name}: Base Price: {item.price}$, Discounted Price: {item.price * (1 - item.discount)}$, "
                    f"Tax: {item.price * item.tax}$, Final Price: {item.price * (1 - item.discount) + item.price * item.tax}$"
                    for item in items
                ]

            def create_detailed_receipt(self, items: list[ShoppingItem]) -> str:
                # Feature Envy: Order loops through ShoppingItem details multiple times
                receipt_lines = []
                total_tax = sum([item.price * item.tax for item in items])
                total_discount = sum([item.price * item.discount for item in items])
                total_price = sum([item.price for item in items])
                final_total = sum([item.price * (1 - item.discount) + item.price * item.tax for item in items])

                for item in items:
                    receipt_lines.append(
                        f"Item: {item.name}\n"
                        f" - Base Price: {item.price}$\n"
                        f" - Discount: {item.discount * 100}%\n"
                        f" - Tax: {item.tax * 100}%\n"
                        f" - Final Price: {item.price * (1 - item.discount) + item.price * item.tax}$"
                    )

                receipt = "\n".join(receipt_lines)
                return (
                    f"Receipt:\n{receipt}\n"
                    f"-----------------\n"
                    f"Total Base Price: {total_price}$\n"
                    f"Total Discount: {total_discount}$\n"
                    f"Total Tax: {total_tax}$\n"
                    f"Final Total: {final_total}$"
                )

            def generate_summary(self, items: list[ShoppingItem]) -> dict:
                # Feature Envy: Order aggregates ShoppingItem data for its own purposes
                total_price = sum([item.price for item in items])
                total_tax = sum([item.price * item.tax for item in items])
                total_discount = sum([item.price * item.discount for item in items])
                final_total = sum([item.price * (1 - item.discount) + item.price * item.tax for item in items])

                return {
                    "Total Price": total_price,
                    "Total Tax": total_tax,
                    "Total Discount": total_discount,
                    "Final Total": final_total,
                }
     """),
    ("Inappropriate Intimacy", """
        class User:
            def __init__(self, name: str, email: str):
                self.name = name
                self.email = email
                self._password = None

            def set_password(self, password: str):
                self._password = password

            def check_password(self, password: str) -> bool:
                return self._password == password

            def get_password(self) -> str:
                return self._password

        class UserManager
            def __init__(self):
                self._users = {}

            def add_user(self, user: User):
                self._users[user.email] = user

            def remove_user(self, email: str):
                del self._users[email]

            def get_user(self, email: str) -> User:
                return self._users.get(email)

            def change_password(self, email: str, new_password: str):
                user = self.get_user(email)
                if user:
                    user.set_password(new_password)

            def check_password(self, email: str, password: str) -> bool:
                user = self.get_user(email)
                return user.check_password(password) if user else False

            def get_password(self, email: str) -> str:
                user = self.get_user(email)
                return user.get_password() if user else None
    """),
    ("Middle Man", """
        class Customer:
            def __init__(self, name: str, email: str, address: str):
                self.name = name
                self.email = email
                self.address = address

            def get_name(self) -> str:
                return self.name

            def get_email(self) -> str:
                return self.email

            def get_address(self) -> str:
                return self.address

            def update_address(self, new_address: str):
                self.address = new_address


        class CustomerService:
            def __init__(self, customer: Customer):
                self.customer = customer

            def get_customer_name(self) -> str:
                return self.customer.get_name()  # Delegates directly to Customer

            def get_customer_email(self) -> str:
                return self.customer.get_email()  # Delegates directly to Customer

            def get_customer_address(self) -> str:
                return self.customer.get_address()  # Delegates directly to Customer

            def update_customer_address(self, new_address: str):
                self.customer.update_address(new_address)  # Delegates directly to Customer
    """),
    ("Switch Statement Abusers", """
        class PaymentProcessor:
            def process_payment(self, payment_method: str, amount: float):
                if payment_method == "credit_card":
                    self.process_credit_card(amount)
                elif payment_method == "paypal":
                    self.process_paypal(amount)
                elif payment_method == "bank_transfer":
                    self.process_bank_transfer(amount)
                elif payment_method == "bitcoin":
                    self.process_bitcoin(amount)
                else:
                    raise ValueError(f"Unsupported payment method: {payment_method}")

            def process_credit_card(self, amount: float):
                print(f"Processing credit card payment of ${amount}")

            def process_paypal(self, amount: float):
                print(f"Processing PayPal payment of ${amount}")

            def process_bank_transfer(self, amount: float):
                print(f"Processing bank transfer of ${amount}")

            def process_bitcoin(self, amount: float):
                print(f"Processing Bitcoin payment of ${amount}")
     """),
    ("Excessive Use of Flags", """
        class OrderProcessor:
            def process_order(self, order, is_expedited: bool = False, is_gift: bool = False):
                if is_expedited:
                    print(f"Expediting order {order['id']}")
                    self.ship_order(order)
                else:
                    print(f"Processing standard order {order['id']}")
                
                if is_gift:
                    print(f"Wrapping order {order['id']} as a gift")
                    self.wrap_as_gift(order)

                print(f"Finalizing order {order['id']}")

            def ship_order(self, order):
                print(f"Shipping order {order['id']}")

            def wrap_as_gift(self, order):
                print(f"Order {order['id']} has been wrapped as a gift")
    """),
    ("Excessive Use of Flags", """
        def process_user_data(user_data, validate=False, format=False, export_csv=False, export_json=False):
            if validate:
                print("Validating user data...")
                if "name" not in user_data or not user_data["name"]:
                    raise ValueError("Validation failed: 'name' is required.")
                if "email" not in user_data or "@" not in user_data["email"]:
                    raise ValueError("Validation failed: 'email' is invalid.")
                print("Validation successful.")

            if format:
                print("Formatting user data...")
                user_data["name"] = user_data["name"].title()
                user_data["email"] = user_data["email"].lower()
                print("Formatting complete.")

            if export_csv:
                print("Exporting user data to CSV...")
                csv_data = f"{user_data['name']},{user_data['email']}\n"
                with open("user_data.csv", "w") as file:
                    file.write(csv_data)
                print("Exported to user_data.csv.")

            if export_json:
                print("Exporting user data to JSON...")
                import json
                with open("user_data.json", "w") as file:
                    json.dump(user_data, file)
                print("Exported to user_data.json.")

            if not (validate or format or export_csv or export_json):
                raise ValueError("At least one action must be specified.")
     """),
    # Add other code smells here
]