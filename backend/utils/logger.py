import logging
import os
import json
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        return json.dumps(log_record)


handler = RotatingFileHandler(
    f"{LOG_DIR}/intervux.log",
    maxBytes=5_000_000,
    backupCount=3
)

handler.setFormatter(JsonFormatter())

logging.basicConfig(level=logging.INFO, handlers=[handler])

def get_logger(name: str):
    return logging.getLogger(name)