# app/Logic/log_config.py

import logging
import logging.handlers
from PySide6.QtCore import QObject, Signal


class LogEmitter(QObject):
    new_log = Signal(str, str)  # message, log_type


class QtLogHandler(logging.Handler):
    def __init__(self, emitter):
        super().__init__()
        self.emitter = emitter

    def emit(self, record):
        log_entry = self.format(record)
        self.emitter.new_log.emit(log_entry, record.levelname)


def setup_logging(log_queue, log_emitter):
    """
    Настраивает систему логирования с использованием QueueHandler и QueueListener.

    :param log_queue: Очередь для передачи лог-записей.
    :param log_emitter: Объект-эмиттер для передачи логов в GUI.
    :return: Объект QueueListener.
    """
    # Создаём обработчик, который отправляет логи в очередь
    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_handler.setLevel(logging.DEBUG)

    # Создаём форматтер
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    queue_handler.setFormatter(formatter)

    # Получаем корневой логгер и добавляем QueueHandler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    # Создаём обработчики для QueueListener

    # Файловый обработчик
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Обработчик для LogTab через Qt сигналы
    qt_handler = QtLogHandler(log_emitter)
    qt_handler.setLevel(logging.INFO)
    qt_handler.setFormatter(formatter)

    # Создаём QueueListener
    listener = logging.handlers.QueueListener(
        log_queue, file_handler, qt_handler)
    listener.start()

    return listener
