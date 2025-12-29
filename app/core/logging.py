import logging
from .config import settings

def setup_logging():
    """
    Configure logging for the whole application.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def get_logger(name: str):
    """
    Get a named logger for a module
    """
    return logging.getLogger(name)