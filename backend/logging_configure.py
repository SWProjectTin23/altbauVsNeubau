import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def configure_logging(
    service_name: str = "app",
    default_level: str = None,
):
    """
    Central logging config for all backends (API, MQTT).
    Controlled via env:
      LOG_LEVEL=INFO|DEBUG|...
      CONSOLE_LEVEL=INFO|WARNING|ERROR (overrides console handler)
      LOG_TO_FILE=true|false
      LOG_FILE=logs/service.log
      LOG_FILE_LEVEL=INFO|DEBUG|...
      LOG_FILE_MAX_BYTES=5242880
      LOG_FILE_BACKUP=5
    """

    root = logging.getLogger()
    if root.handlers:
        return  # prevent duplicate handlers in reloads
    level = (default_level or os.getenv("LOG_LEVEL", "INFO")).upper()

    # Base formatter
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Root logger level
    root.setLevel(level)

    # Console handler
    console_level = os.getenv("CONSOLE_LEVEL", level).upper()
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(console_level)
    console.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    root.addHandler(console)

    # Optional rotating file handler
    if os.getenv("LOG_TO_FILE", "false").lower() == "true":
        log_file = os.getenv("LOG_FILE", f"logs/{service_name}.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_level = os.getenv("LOG_FILE_LEVEL", level).upper()
        max_bytes = int(os.getenv("LOG_FILE_MAX_BYTES", 5_242_880))
        backup_count = int(os.getenv("LOG_FILE_BACKUP", 5))
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
        root.addHandler(file_handler)

    # Tame noisy third-party loggers
    logging.getLogger("werkzeug").setLevel(os.getenv("WERKZEUG_LOG_LEVEL", "WARNING"))
    logging.getLogger("urllib3").setLevel(os.getenv("URLLIB3_LOG_LEVEL", "WARNING"))