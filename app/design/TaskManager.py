# app/design/TaskManager.py

import os
import importlib
from PySide6.QtCore import QObject, QMutex
from PySide6.QtCore import QMutexLocker


class SharedResources(QObject):
    def __init__(self):
        super().__init__()
        self.lock = QMutex()
        self.counter = 0
        # Добавьте другие глобальные переменные и ресурсы здесь


class TaskManager:
    def __init__(self, tasks_directory):
        self.tasks_directory = tasks_directory
        self.tasks = {}
        self.shared_resources = SharedResources()
        self.load_tasks()

    def load_tasks(self):
        for task_name in os.listdir(self.tasks_directory):
            task_path = os.path.join(self.tasks_directory, task_name)
            if os.path.isdir(task_path) and os.path.exists(os.path.join(task_path, "__init__.py")):
                try:
                    # Предполагается, что главный модуль называется task_a.py
                    module_name = f"app.tasks.{task_name}.task_a"
                    module = importlib.import_module(module_name)
                    # Предполагается, что класс называется как задача
                    task_class = getattr(module, task_name)
                    self.tasks[task_name] = task_class
                except Exception as e:
                    print(f"Не удалось загрузить задачу {task_name}: {e}")

    def get_task_names(self):
        return list(self.tasks.keys())

    def instantiate_task(self, task_name):
        if task_name in self.tasks:
            return self.tasks[task_name](self.shared_resources)
        else:
            raise ValueError(f"Задача {task_name} не найдена.")
