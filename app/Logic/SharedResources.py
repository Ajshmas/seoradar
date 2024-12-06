# app/Logic/SharedResources.py

from PySide6.QtCore import QMutex, QWaitCondition


class SharedResources:
    def __init__(self, logic_thread, mutex, wait_condition, log_function):
        self.logic_thread = logic_thread
        self.mutex = mutex
        self.wait_condition = wait_condition
        self.log_function = log_function  # Функция для логирования сообщений
