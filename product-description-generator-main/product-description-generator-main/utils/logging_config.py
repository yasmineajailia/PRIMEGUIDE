import os
import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'api.log'))  # Output to file
    ]
)

# Get logger
logger = logging.getLogger("product-ai-hub")

print("Logger configuration loaded. Logging is enabled to both console and file.")
