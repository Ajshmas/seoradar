import logging
import logging.handlers
from multiprocessing import Queue
from PySide6.QtCore import QObject, Signal
from app.utils.qt_log_handler import QtLogHandler


class LogEmitter(QObject):
    new_log = Signal(str, str, str)  # timestamp, log_type, message


def setup_logging(log_queue: Queue, log_emitter: LogEmitter):
    """
    Настраивает систему логирования с использованием QueueHandler и QueueListener.

    :param log_queue: Очередь для передачи лог-записей.
    :param log_emitter: Объект-эмиттер для передачи логов в GUI.
    :return: Объект QueueListener.
    """
    # Создаём обработчик, который отправляет логи в очередь
    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_handler.setLevel(logging.DEBUG)

    # Создаём форматтер (он теперь не добавляет лишнюю информацию)
    formatter = logging.Formatter('%(message)s')
    queue_handler.setFormatter(formatter)

    # Получаем корневой логгер и добавляем QueueHandler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    # Создаём обработчики для QueueListener

    # Файловый обработчик с ротацией
    file_handler = logging.handlers.RotatingFileHandler(
        'app.log', maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Обработчик для LogTab через Qt сигналы
    qt_handler = QtLogHandler(log_emitter)
    qt_handler.setLevel(logging.INFO)
    qt_handler.setFormatter(formatter)

    # Создаём QueueListener
    listener = logging.handlers.QueueListener(
        log_queue, file_handler, qt_handler, respect_handler_level=True
    )
    listener.start()

    return listener
