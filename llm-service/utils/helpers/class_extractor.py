import ast

def extract_classes_from_code(code_string):
    """
    Extracts all classes from a Python code string.

    Args:
        code_string (str): Python code as a string.

    Returns:
        list: A list of strings, where each string is the full code of a class.
    """
    try:
        # Parse the code into an abstract syntax tree (AST)
        tree = ast.parse(code_string)
        
        # List to store extracted class strings
        classes = []
        
        # Iterate through all top-level nodes in the AST
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):  # Check if the node is a class definition
                # Extract the start and end line numbers for the class
                start_lineno = node.lineno - 1  # Convert to zero-based index
                end_lineno = max(n.end_lineno for n in ast.walk(node) if hasattr(n, 'end_lineno'))
                
                # Extract the full class code as a string
                class_code = '\n'.join(code_string.splitlines()[start_lineno:end_lineno])
                classes.append(class_code)
        
        return classes
    except Exception as e:
        print(f"Error processing the code: {e}")
        return []

# Example usage
if __name__ == "__main__":
    python_code = """
class GodClass:
    def __init__(self, config_path: str, db_path: str):
        # Configuration
        self.config = self._load_config(config_path)

        # Database connection
        self.db_path = db_path
        self.conn = None

        # Data cache
        self.data_cache = []

        # Logging settings
        self.log_file = self.config.get("log_file", "app.log")
        self.log_level = self.config.get("log_level", "INFO")

        # State
        self.user_is_logged_in = False
        self.current_user = None

    def _load_config(self, config_path: str):
        # Load configuration from a JSON file
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {
                "log_file": "app.log",
                "log_level": "INFO",
                "default_admin": "admin",
                "default_password": "admin123"
            }
        return config

    def log(self, message: str, level: str = "INFO"):
        # Log a message to a file, ignoring log_level thresholds for simplicity
        with open(self.log_file, "a") as f:
            f.write(f"[{level}] {message}")

    def connect_db(self):
        # Connect to the database
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.log("Connected to the database.", "DEBUG")

    def create_tables(self):
        # Create tables if they don't exist
        self.connect_db()
        cursor = self.conn.cursor()
        self.conn.commit()
        self.log("Tables ensured in database.", "DEBUG")

    def add_user(self, username: str, password: str):
        # Add a user to the database
        self.connect_db()
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            self.log(f"User added: {username}", "INFO")
        except sqlite3.IntegrityError:
            self.log(f"User {username} already exists.", "ERROR")

    def login_user(self, username: str, password: str):
        # Login a user
        self.connect_db()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            self.user_is_logged_in = True
            self.current_user = username
            self.log(f"User {username} logged in.", "INFO")
            return True
        else:
            self.log(f"Failed login attempt for user {username}.", "WARNING")
            return False

    def add_item(self, name: str, value: int):
        # Add an item to the database
        if not self.user_is_logged_in:
            self.log("Attempted to add item without being logged in.", "ERROR")
            return

        self.connect_db()
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO items (name, value) VALUES (?, ?)", (name, value))
        self.conn.commit()
        self.log(f"Item added: {name} with value {value}", "INFO")

    def load_data_into_cache(self):
        # Load all items from the database into memory
        self.connect_db()
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, value FROM items")
        self.data_cache = cursor.fetchall()
        self.log("Data loaded into cache.", "DEBUG")

    def process_data(self):
        # Process data in memory (e.g., sorting by value)
        if not self.data_cache:
            self.log("Data cache is empty, cannot process.", "WARNING")
            return
        self.data_cache.sort(key=lambda x: x[1])
        self.log("Data processed (sorted by value).", "INFO")

    def user_interaction(self):
        # Simulate user interaction via input/output
        print("Welcome to the GodClass Application!")
        username = input("Enter username: ")
        password = input("Enter password: ")
        if self.login_user(username, password):
            print("Login successful.")
            action = input("Do you want to add an item? (y/n): ")
            if action.lower() == 'y':
                name = input("Item name: ")
                value = int(input("Item value: "))
                self.add_item(name, value)
                print("Item added successfully!")
            else:
                print("No action taken.")
        else:
            print("Login failed. Goodbye.")

    def close(self):
        # Close the database connection
        if self.conn:
            self.conn.close()
            self.log("Database connection closed.", "DEBUG")    
"""
    extracted_classes = extract_classes_from_code(python_code)
    print("Extracted Classes:")
    print(extracted_classes)
