import logging
import sys

from config import LoggingConfig


GLOBAL_LEVEL = LoggingConfig["global_level"]
LOG_FILE = LoggingConfig["log_file"]


logging.basicConfig(filename=LOG_FILE)


def get_console_logger(name, level=GLOBAL_LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
