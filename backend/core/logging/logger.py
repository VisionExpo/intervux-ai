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

# Configure handlers
handlers = [stdout_handler]

# Only use RotatingFileHandler in production (not in tests) to avoid Windows file locks
is_testing = "PYTEST_CURRENT_TEST" in os.environ
if not is_testing:
    handlers.append(file_handler)

# Configure the root logger
logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)

def get_logger(name: str):
    return logging.getLogger(name)