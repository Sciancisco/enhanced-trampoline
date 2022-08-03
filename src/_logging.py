import logging
import sys


LEVEL = logging.DEBUG


def get_console_logger(name, level=LEVEL):
    logger = logging.getLogger(__name__)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    
    return logger
