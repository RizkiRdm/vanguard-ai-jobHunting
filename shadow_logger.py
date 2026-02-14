import logging
import sys
import os
from datetime import datetime


def setup_logging():
    """
    Configuring the global logging system for Vanguard AI.
    This includes logging to the terminal (Console) and to files (File Logging).
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Format log
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Handler for Console (Terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    # 2. Handler for File (save daily log)
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(f"logs/vanguard_{current_date}.log")
    file_handler.setFormatter(log_format)

    # Root Logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # delete built-in handler if any for avoiding duplication
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logging.info(
        "Logging system initialized. Output directed to console and local file."
    )
