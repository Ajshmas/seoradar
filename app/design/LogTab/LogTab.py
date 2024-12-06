from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QFileDialog, QApplication
from PySide6.QtGui import QKeySequence
import logging

from .LogTabUI import LogTabUI
from .LogTabLogic import LogTabLogic
from .LogTableModel import LogTableModel  # Import the LogTableModel


class LogTab(QWidget):
    MAX_LOGS = 1000  # Максимальное количество логов

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(50, 50, 50);")

        # Initialize the data model
        self.model = LogTableModel()  # This will store and manage log data

        # Основной макет
        main_layout = QVBoxLayout()

        # Создаём логику
        self.logic = LogTabLogic(self)

        # Пробрасываем методы из логики (при необходимости)
        self.toggle_time_filter = self.logic.toggle_time_filter
        self.on_filter_changed = self.logic.on_filter_changed
        self.on_scrollbar_value_changed = self.logic.on_scrollbar_value_changed
        self.add_log = self.logic.add_log
        self.save_logs = self.logic.save_logs
        self.clear_logs = self.logic.clear_logs
        self.keyPressEvent = self.logic.keyPressEvent
        self.copy_selected_rows = self.logic.copy_selected_rows
        self.show_context_menu = self.logic.show_context_menu

        # Инициализируем UI
        self.ui = LogTabUI(self)
        self.ui.setup_ui(main_layout)

        # Устанавливаем основной макет
        self.setLayout(main_layout)

    def add_log(self, timestamp, log_type, message):
        """
        Добавляет новый лог в поле текстового вывода.
        """
        log_entry = f"{timestamp} [{log_type}] {message}"
        self.log_output.append(log_entry)

    def save_logs(self):
        """
        Сохраняет текущие логи в файл.
        """
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить логи", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.log_output.toPlainText())
                logging.info("Логи успешно сохранены.")
        except Exception as e:
            logging.error(f"Ошибка сохранения логов: {e}")

    def clear_logs(self):
        """
        Очищает все логи в текстовом поле.
        """
        self.log_output.clear()
        logging.info("Логи очищены.")

    def keyPressEvent(self, event):
        """
        Обрабатывает нажатия клавиш для копирования текста.
        """
        if event.matches(QKeySequence.Copy):
            self.copy_selected_rows()
        else:
            super(self.__class__, self).keyPressEvent(event)

    def copy_selected_rows(self):
        """
        Копирует выбранный текст в буфер обмена.
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_output.toPlainText())
