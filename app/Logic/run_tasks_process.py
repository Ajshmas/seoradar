# Logic/run_tasks_process.py

import logging
from logging.handlers import QueueHandler
from app.design.TaskManager import TaskManager


def execute_tasks_process(tasks, process_number, log_queue):
    """
    Функция для выполнения списка задач в отдельном процессе.

    :param tasks: Список названий задач для выполнения.
    :param process_number: Номер процесса для логирования.
    :param log_queue: Очередь для логирования.
    """
    # Настройка логирования для дочернего процесса с использованием QueueHandler
    handler = QueueHandler(log_queue)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)  # Устанавливаем нужный уровень

    # Логируем начало выполнения задач
    logger.info(f"Процесс {process_number}: начал выполнение задач.")

    try:
        # Инициализация TaskManager внутри процесса
        task_manager = TaskManager(
            tasks_directory="app/tasks", log_helper=None)

        for task_name in tasks:
            # Логируем запуск каждой задачи
            logger.info(
                f"Процесс {process_number}: запустил задачу '{task_name}'.")

            # Выполнение задачи
            task_manager.execute_task(
                localized_task_name=task_name,
                shared_resources=None,
                thread_number=process_number,
                settings=None)

            # Логируем завершение каждой задачи
            logger.info(
                f"Процесс {process_number}: завершил выполнение задачи '{task_name}'.")

    except Exception as e:
        # Логируем ошибку, если задача не завершена
        logger.error(f"Процесс {process_number}: ошибка выполнения задач: {e}")

    finally:
        logger.info(f"Процесс {process_number}: все задачи завершены.")
