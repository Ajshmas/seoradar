# app/design/LogTab/LogTab.py

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer

from .LogTabUI import LogTabUI
from .LogTabLogic import LogTabLogic
from .LogTableModel import LogTableModel


class LogTab(QWidget):
    MAX_LOGS = 1000  # Максимальное количество логов

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(50, 50, 50);")

        # Основной макет
        main_layout = QVBoxLayout()

        # Создаём модель данных
        self.model = LogTableModel()

        # Инициализируем логику
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
