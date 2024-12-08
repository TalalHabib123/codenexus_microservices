import logging
from logging.handlers import RotatingFileHandler
import os

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
try:
    os.makedirs(log_dir, exist_ok=True)
    print(f"Successfully created or verified the directory: {log_dir}")
except Exception as e:
    print(f"Error creating directory: {e}")

log_file_path = os.path.join(log_dir, "app.log")

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,  # Use INFO as the default level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file_path, maxBytes=5_000_000, backupCount=3),
        logging.StreamHandler()
    ]
)

# Reduce logging level for noisy external libraries
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Function to get the logger
def get_logger(name=__name__):
    return logging.getLogger(name)
