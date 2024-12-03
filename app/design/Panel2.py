from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QSpinBox, QLabel, QComboBox, QPushButton, QLineEdit, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from app.design.LogTab import LogTab  # Импортируем класс LogTab
from app.design.TaskManager import TaskManager


class Panel2(QWidget):
    def __init__(self, task_manager):
        super().__init__()
        self.task_manager = task_manager
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()
        # Позволяет пользователю менять местами вкладки
        self.tabs.setMovable(True)

        # Вкладка "Задачи"
        self.tasks_tab = TasksTab(self.task_manager)
        self.tabs.addTab(self.tasks_tab, "Задачи")

        # Вкладка "Настройки"
        self.settings_tab = SettingsTab()
        self.tabs.addTab(self.settings_tab, "Настройки")

        # Вкладка "Лог"
        self.log_tab = LogTab()  # Здесь используется LogTab для вывода логов
        self.tabs.addTab(self.log_tab, "Лог")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def get_tasks(self):
        return self.tasks_tab.get_selected_tasks()


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Настройка количества потоков
        threads_layout = QHBoxLayout()
        threads_label = QLabel("Количество потоков:")
        self.threads_input = QSpinBox()
        self.threads_input.setMinimum(1)
        self.threads_input.setMaximum(100)
        self.threads_input.setValue(5)
        threads_layout.addWidget(threads_label)
        threads_layout.addWidget(self.threads_input)

        layout.addLayout(threads_layout)
        self.setLayout(layout)


class TasksTab(QWidget):
    def __init__(self, task_manager):
        super().__init__()
        self.task_manager = task_manager
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # Левый экран: список существующих задач
        self.available_tasks_list = QListWidget()
        self.available_tasks_list.setStyleSheet("""
            QListWidget {
                background-color: rgb(50, 50, 50);
                color: white;
                font-family: Consolas;
                font-size: 12px;
            }
        """)
        self.populate_available_tasks()

        # Правый экран: список выбранных задач
        self.selected_tasks_list = QListWidget()
        self.selected_tasks_list.setStyleSheet("""
            QListWidget {
                background-color: rgb(50, 50, 50);
                color: white;
                font-family: Consolas;
                font-size: 12px;
            }
        """)

        # Подключение двойного клика для добавления задачи
        self.available_tasks_list.itemDoubleClicked.connect(
            self.add_task_to_selected)

        layout.addWidget(self.available_tasks_list)
        layout.addWidget(self.selected_tasks_list)

        self.setLayout(layout)

    def populate_available_tasks(self):
        self.available_tasks_list.clear()
        for task_name in self.task_manager.get_task_names():
            item = QListWidgetItem(task_name)
            self.available_tasks_list.addItem(item)

    def add_task_to_selected(self, item):
        task_name = item.text()
        selected_item = QListWidgetItem(task_name)
        self.selected_tasks_list.insertItem(
            0, selected_item)  # Добавление сверху

    def get_selected_tasks(self):
        tasks = []
        for index in range(self.selected_tasks_list.count()):
            item = self.selected_tasks_list.item(index)
            tasks.append(item.text())
        return tasks
