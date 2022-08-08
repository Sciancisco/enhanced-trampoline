import logging
import sys

from config import LoggingConfig


GLOBAL_LEVEL = LoggingConfig["global_level"]
LOG_FILE = LoggingConfig["log_file"]


def get_console_logger(name, log_file=LOG_FILE, level=GLOBAL_LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if log_file:
        handler = logging.FileHandler(log_file)
        handler.setLevel(level)
        logger.addHandler(handler)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
