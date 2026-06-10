import logging
import os
from .config import settings

logger = logging.getLogger('Fraud-Model')

logger.setLevel(settings.LOG_LEVEL)

os.makedirs(
    "app/logs",
    exist_ok=True
)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('app/logs/app.log')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)