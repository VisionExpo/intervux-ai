import logging
import os
import sys
from logging.handlers import RotatingFileHandler
try:
    from pythonjsonlogger import jsonlogger  # pythonjsonlogger < 3
except ImportError:
    from pythonjsonlogger import json as jsonlogger  # pythonjsonlogger >= 3


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Standardize format via pythonjsonlogger
log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
formatter = jsonlogger.JsonFormatter(log_format)

# Stdout handler
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)

# Configure handlers
handlers = [stdout_handler]

# Only use RotatingFileHandler in production (not in tests) to avoid Windows file locks
is_testing = os.getenv("ENV") == "test"
if not is_testing:
    try:
        # File handler
        file_handler = RotatingFileHandler(
            f"{LOG_DIR}/intervux.log",
            maxBytes=5_000_000,
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    except (PermissionError, OSError) as e:
        # Fallback to stdout only if logs directory is read-only (common in Docker bind mounts)
        print(f"CRITICAL: Failed to initialize log file handler: {e}. Logging to stdout only.", file=sys.stderr)

# Configure the root logger idempotently
root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)

def get_logger(name: str):
    return logging.getLogger(name)