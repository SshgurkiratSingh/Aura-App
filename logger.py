import logging
import os
from datetime import datetime

# Create logs directory
LOGS_DIR = "./logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Create log filename with timestamp
log_filename = os.path.join(LOGS_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """Get logger instance for a module."""
    return logging.getLogger(name)
