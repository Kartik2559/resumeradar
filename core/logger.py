import logging
import sys
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S") #Date Time used in ISO 8601
    consol_handler = logging.StreamHandler(sys.stdout)
    consol_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler.setFormatter(formatter)

    logger.addHandler(consol_handler)
    logger.addHandler(file_handler)
    logger.propogate = False

    return logger