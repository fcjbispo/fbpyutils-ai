"""
Initialization module for the fbpyutils_ai package.

Sets up logging configuration using RotatingFileHandler and QueueListener
for multiprocessing environments. Loads environment variables using dotenv.
"""
import os
import logging
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from multiprocessing import Queue
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

LOG_LEVELS: Dict[str, int] = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
}
LOG_LEVEL: str = os.getenv('FBPY_LOG_LEVEL', 'INFO').upper()

log_dir: str = os.path.join(os.path.expanduser("~"), '.fbpyutils_ai')
os.makedirs(log_dir, exist_ok=True)
log_file: str = os.path.join(log_dir, 'fbpyutils_ai.log')

# Setup for rotating file handler
log_file_handler: RotatingFileHandler = RotatingFileHandler(
    log_file,
    maxBytes=256 * 1024,  # 256KB
    backupCount=5,
)
log_formatter: logging.Formatter = logging.Formatter(
    '%(asctime)s|%(levelname)s|%(module)s|%(funcName)s|%(lineno)d|%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log_file_handler.setFormatter(log_formatter)

# Setup queue and listener for multiprocessing logging
log_queue: Queue = Queue(-1)  # Unlimited queue size
queue_handler: QueueHandler = QueueHandler(log_queue)

# Root logger configuration
logger: logging.Logger = logging.getLogger()
logger.setLevel(LOG_LEVELS.get(LOG_LEVEL, logging.INFO))
logger.addHandler(queue_handler)

# Listener that processes logs from the queue and sends them to the file handler
listeners: List[QueueListener] = [
    QueueListener(log_queue, log_file_handler)
]
for listener in listeners:
    listener.start()

def cleanup_logging() -> None:
    """Stops all active queue listeners."""
    for listener in listeners:
        listener.stop()

# Certifique-se de parar os listeners ao encerrar a aplicação (exemplo em __main__ ou atexit)
# import atexit
# atexit.register(cleanup_logging)

# logging.basicConfig( # Removido basicConfig e movido para configuração manual
#     level=LOG_LEVELS.get(LOG_LEVEL, logging.INFO),
#     format='%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )  # Configuração básica de logging
