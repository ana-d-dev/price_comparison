# logger_config.py
from loguru import logger
import os

os.makedirs("logs", exist_ok=True)
logger.add(
    "logs/errors.log",
    rotation="1 MB",
    level="ERROR",
    format="{time} | {level} | {name}:{function}:{line} - {message}"
)
