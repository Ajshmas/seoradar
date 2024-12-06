# app/utils/logger.py

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(message)s')


def log_task_start(task_name, process_number):
    """Логирует начало выполнения задачи процессом."""
    message = f"Процесс {process_number}: запустил {task_name}"
    logging.info(message)


def log_task_end(task_name, process_number):
    """Логирует завершение выполнения задачи процессом."""
    message = f"Процесс {
        process_number}: завершил выполнение задачи {task_name}"
    logging.info(message)


def log_task_error(task_name, process_number, error_message):
    """Логирует ошибку выполнения задачи процессом."""
    message = f"Процесс {process_number}: ошибка выполнения задачи {
        task_name}: {error_message}"
    logging.error(message)
