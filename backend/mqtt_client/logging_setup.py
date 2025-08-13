import logging
import os

def setup_logging(log_level=logging.INFO, log_dir="logs"):
    """
    Basic logging setup: logs to both console and file.
    - log_level: logging.DEBUG, logging.INFO, etc.
    - log_dir: where to store log files
    """
    os.makedirs(log_dir, exist_ok=True)  # create logs/ if not exits

    # get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # catch all the levels

    # if logger exists then stop
    if logger.handlers:
        return

    # console output (only level above warning)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # write log in file
    file_handler = logging.FileHandler(f"{log_dir}/service.log", encoding="utf-8")
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # add handler
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
