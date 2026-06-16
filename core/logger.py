# core/logger.py
import os
import sys
import logging
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Always — console logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Only if not on HuggingFace — file logging
    is_huggingface = os.getenv("SPACE_ID") is not None

    if not is_huggingface:
        try:
            os.makedirs("logs", exist_ok=True)
            file_handler = logging.FileHandler(
                f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError):
            pass

    logger.propagate = False
    return logger