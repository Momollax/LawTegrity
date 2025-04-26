import logging
import os

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger("legifrance_logger")
    logger.setLevel(logging.DEBUG)

    # Fichier de log
    file_handler = logging.FileHandler("logs/logs.txt", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()