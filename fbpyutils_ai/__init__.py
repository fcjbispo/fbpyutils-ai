import os
import logging
from dotenv import load_dotenv

load_dotenv()

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,	
    'INFO': logging.INFO,		
    'WARNING': logging.WARNING,	
    'ERROR': logging.ERROR,
}
LOG_LEVEL = os.getenv('FBPY_LOG_LEVEL', 'INFO').upper()

logging.basicConfig(
    level=LOG_LEVELS.get(LOG_LEVEL, logging.INFO),
    format='%(asctime)s|%(levelname)s|%(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)  # Configuração básica de logging
