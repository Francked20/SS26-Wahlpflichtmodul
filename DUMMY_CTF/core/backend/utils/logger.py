import logging
import sys
import os

__all__ = ["configure_logger"]

def configure_logger():
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()

    valid_levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    log_level = valid_levels.get(log_level_str)
    if log_level is None:
        print(f"[logger] Invalid LOG_LEVEL '{log_level_str}', defaulting to INFO")
        log_level = logging.INFO

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
