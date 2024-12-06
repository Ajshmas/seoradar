# app/design/QTextEditLogger.py

import logging
import re


class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        try:
            msg = self.format(record)
            # Предполагаем, что сообщение содержит "Процесс {номер}: сообщение"
            # Если нет, то пытаемся его извлечь из полного сообщения
            # Пример полного сообщения: "Задача А: Процесс 1 начал выполнение."

            # Используем регулярное выражение для извлечения номера процесса и сообщения
            pattern = r'Процесс\s+(\d+)\s+(.*)'
            match = re.search(pattern, msg)
            if match:
                process_number = match.group(1)
                process_message = match.group(2)
                formatted_message = f"Процесс {
                    process_number}: {process_message}"
                self.text_edit.append(formatted_message)
            else:
                # Если сообщение не соответствует ожидаемому формату, не выводим его
                pass
        except Exception:
            self.handleError(record)
