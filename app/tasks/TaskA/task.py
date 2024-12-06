# tasks/TaskA/task.py

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

        # Симуляция выполнения задачи
        time.sleep(10)
