import logging
import sys


GLOBAL_DEFAULT_LEVEL = logging.DEBUG


def get_console_logger(name, level=GLOBAL_DEFAULT_LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    
    return logger
