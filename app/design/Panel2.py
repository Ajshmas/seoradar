# app/design/Panel2.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
import logging
from app.design.LogTab.LogTab import LogTab
from app.design.SettingsTab import SettingsTab
from app.design.TasksTab import TasksTab  # Убедитесь, что импорт правильный


class Panel2(QWidget):
    def __init__(self, tasks_directory, task_manager):
        super().__init__()
        logging.debug("Инициализация Panel2.")
        self.tasks_directory = tasks_directory
        self.task_manager = task_manager

        layout = QVBoxLayout(self)

        # Создание вкладок
        self.tabs = QTabWidget()
        self.log_tab = LogTab()
        self.settings_tab = SettingsTab()
        self.tasks_tab = TasksTab(parent=self, task_manager=self.task_manager)
        # Добавьте другие вкладки по необходимости

        # Добавление вкладок в QTabWidget
        self.tabs.addTab(self.log_tab, "Логи")
        self.tabs.addTab(self.settings_tab, "Настройки")
        self.tabs.addTab(self.tasks_tab, "Задачи")
        # Добавьте другие вкладки по необходимости

        layout.addWidget(self.tabs)
        self.setLayout(layout)
        logging.debug("Panel2 инициализирован с вкладками.")

    def update_log_output(self, message, log_type):
        """
        Метод для обновления логов во вкладке LogTab.
        """
        self.log_tab.add_log(message, log_type)
        # Также можно добавить логирование в консоль или другие места
