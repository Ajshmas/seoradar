# app/tasks/TaskA/task.py

import time
import logging


class Task:
    def __init__(self, shared_resources, process_number, log_queue, log_helper=None, settings=None):
        self.shared_resources = shared_resources
        self.process_number = process_number
        self.log_queue = log_queue
        self.log_helper = log_helper

    def get_task_name(self):
        return "Задача А"

    def run(self):
        logging.info(f"Задача А: Процесс {
                     self.process_number} начал выполнение.")
        print(f"Задача А: Процесс {self.process_number} начал выполнение.")
        # Симуляция выполнения задачи
        time.sleep(10)
        logging.info(f"Задача А: Процесс {
                     self.process_number} завершил выполнение.")
        print(f"Задача А: Процесс {self.process_number} завершил выполнение.")
