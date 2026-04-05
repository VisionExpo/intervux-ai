import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Standardize format via pythonjsonlogger
log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
formatter = jsonlogger.JsonFormatter(log_format)

# File handler
file_handler = RotatingFileHandler(
    f"{LOG_DIR}/intervux.log",
    maxBytes=5_000_000,
    backupCount=3
)
file_handler.setFormatter(formatter)

# Stdout handler
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)

# Configure the root logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, stdout_handler])

def get_logger(name: str):
    return logging.getLogger(name)