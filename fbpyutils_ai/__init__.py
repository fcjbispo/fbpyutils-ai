import os
import logging
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from multiprocessing import Queue
from dotenv import load_dotenv

load_dotenv()

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
}
LOG_LEVEL = os.getenv('FBPY_LOG_LEVEL', 'INFO').upper()

log_dir = '.fbpyutils_ia_tools'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'fbpyutils_ai.log')

# Configuração do handler de arquivo rotativo
log_file_handler = RotatingFileHandler(
    log_file,
    maxBytes=256 * 1024,  # 256KB
    backupCount=5,
)
log_formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(module)s|%(funcName)s|%(lineno)d|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log_file_handler.setFormatter(log_formatter)

# Configuração da fila e listener para logs multitarefa
log_queue = Queue(-1)  # Tamanho da fila ilimitado
queue_handler = QueueHandler(log_queue)

# Logger raiz
logger = logging.getLogger()
logger.setLevel(LOG_LEVELS.get(LOG_LEVEL, logging.INFO))
logger.addHandler(queue_handler)

# Listener que processa os logs da fila e os envia para o handler de arquivo
listeners = [
    QueueListener(log_queue, log_file_handler)
]
for listener in listeners:
    listener.start()

def cleanup_logging():
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
