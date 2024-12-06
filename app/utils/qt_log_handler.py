import logging
from datetime import datetime


class QtLogHandler(logging.Handler):
    def __init__(self, emitter):
        super().__init__()
        self.emitter = emitter

    def emit(self, record):
        # Получаем время логирования
        timestamp = datetime.fromtimestamp(
            record.created).strftime('%Y-%m-%d %H:%M:%S')

        # Получаем уровень логирования
        log_type = record.levelname

        # Получаем только само сообщение
        message = record.getMessage()

        # Передаём время, уровень и сообщение в эмиттер
        self.emitter.new_log.emit(timestamp, log_type, message)
