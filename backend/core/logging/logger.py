import logging
import os
import re
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


# ---------------------------------------------------------------------------
# Secret redaction
# The interview WebSocket carries the JWT in its query string, and uvicorn's
# access log prints the full path. Scrub credentials from every log line.
# ---------------------------------------------------------------------------
_REDACTIONS = (
    (re.compile(r"eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}"), "[REDACTED_JWT]"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"), r"\1[REDACTED]"),
    (
        re.compile(r"(?i)\b(token|access_token|refresh_token|password|api_key|secret)=([^&\s\"']+)"),
        r"\1=[REDACTED]",
    ),
)


def redact_secrets(text: str) -> str:
    for pattern, replacement in _REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


class RedactSecretsFilter(logging.Filter):
    """Rewrites a record's message with credentials removed (never drops records)."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:
            return True
        redacted = redact_secrets(message)
        if redacted != message:
            record.msg = redacted
            record.args = None
        return True


_redact_filter = RedactSecretsFilter()

# Stdout handler
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
stdout_handler.addFilter(_redact_filter)

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
        file_handler.addFilter(_redact_filter)
        handlers.append(file_handler)
    except (PermissionError, OSError) as e:
        # Fallback to stdout only if logs directory is read-only (common in Docker bind mounts)
        print(f"CRITICAL: Failed to initialize log file handler: {e}. Logging to stdout only.", file=sys.stderr)

# Configure the root logger idempotently
root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)

# Handlers installed by others (uvicorn, pytest) do not carry our filter, so
# also filter at the logger level for the root logger and uvicorn's loggers.
for _name in ("", "uvicorn", "uvicorn.access", "uvicorn.error"):
    _logger = logging.getLogger(_name)
    if _redact_filter not in _logger.filters:
        _logger.addFilter(_redact_filter)

def get_logger(name: str):
    return logging.getLogger(name)