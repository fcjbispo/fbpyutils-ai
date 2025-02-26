import logging
import sys
from typing import Optional

def configure_logging(
    level: int = logging.INFO,
    format: str = '%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
    stream: Optional[logging.StreamHandler] = None
) -> None:
    """Configura o sistema de logging global."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not stream:
        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(logging.Formatter(format))

    if not root_logger.hasHandlers():
        root_logger.addHandler(stream)

# Configure logging on module import
configure_logging()
