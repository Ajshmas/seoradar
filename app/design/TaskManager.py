# design/TaskManager.py

import os
import importlib.util
import logging
import yaml  # Импортируем PyYAML


class TaskManager:
    def __init__(self, tasks_directory, log_helper=None):
        self.tasks_directory = tasks_directory
        self.log_helper = log_helper
        self.available_tasks = self.load_available_tasks()
        logging.debug(f"TaskManager инициализирован с задачами: {
                      self.available_tasks}")

    def load_available_tasks(self):
        """
        Загружает доступные задачи из директории tasks_directory, включая их настройки из config.yaml.
        """
        task_names = []
        self.task_configs = {}  # Словарь для хранения конфигураций задач
        for task_dir in os.listdir(self.tasks_directory):
            task_path = os.path.join(self.tasks_directory, task_dir, 'task.py')
            config_path = os.path.join(
                self.tasks_directory, task_dir, 'config.yaml')
            if os.path.isfile(task_path):
                spec = importlib.util.spec_from_file_location(
                    "task", task_path)
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    task_class = getattr(module, "Task", None)
                    if task_class:
                        # Инициализируем экземпляр задачи без аргументов
                        task_instance = task_class(
                            shared_resources=None, process_number=None, log_queue=None)
                        task_name = task_instance.get_task_name()
                        task_names.append(task_name)
                        logging.debug(
                            f"Задача '{task_name}' успешно загружена.")

                        # Загрузка конфигурации, если файл существует
                        if os.path.isfile(config_path):
                            with open(config_path, 'r', encoding='utf-8') as config_file:
                                try:
                                    config = yaml.safe_load(config_file)
                                    self.task_configs[task_name] = config
                                    logging.debug(f"Конфигурация для задачи '{
                                                  task_name}' загружена.")
                                except yaml.YAMLError as e:
                                    logging.error(f"Ошибка при загрузке config.yaml для задачи '{
                                                  task_name}': {e}")
                except Exception as e:
                    logging.error(f"Не удалось загрузить задачу из {
                                  task_path}: {e}")
        return task_names

    def get_task_names(self):
        """
        Возвращает список доступных задач.
        """
        return self.available_tasks

    def get_task_class(self, task_name):
        """
        Возвращает класс задачи по её имени.
        """
        for task_dir in os.listdir(self.tasks_directory):
            task_path = os.path.join(self.tasks_directory, task_dir, 'task.py')
            if os.path.isfile(task_path):
                spec = importlib.util.spec_from_file_location(
                    "task", task_path)
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    task_class = getattr(module, "Task", None)
                    if task_class:
                        task_instance = task_class(
                            shared_resources=None, process_number=None, log_queue=None)
                        if task_instance.get_task_name() == task_name:
                            return task_class
                except Exception as e:
                    logging.error(f"Не удалось загрузить задачу '{
                                  task_name}' из {task_path}: {e}")
        raise ValueError(f"Задача с именем '{task_name}' не найдена.")

    def get_task_config(self, task_name):
        """
        Возвращает конфигурацию задачи по её имени.
        """
        return self.task_configs.get(task_name, {})

    def execute_task(self, localized_task_name, shared_resources, thread_number=None, settings=None):
        """
        Выполняет задачу по имени с переданными настройками.

        :param localized_task_name: Локализованное имя задачи.
        :param shared_resources: Общие ресурсы (если нужны).
        :param thread_number: Номер процесса (для логирования).
        :param settings: Настройки задачи, полученные из config.yaml.
        """
        try:
            # Получение класса задачи по имени
            task_class = self.get_task_class(localized_task_name)
            task_instance = task_class(
                shared_resources=shared_resources,
                process_number=thread_number,  # Передаём process_number
                log_queue=None,  # Убираем, если не используете внутри Task
                log_helper=self.log_helper,
                settings=settings  # Передаём настройки
            )

            task_instance.run()
        except Exception as e:
            logging.error(f"TaskManager: Ошибка при выполнении задачи '{
                          localized_task_name}': {e}")
            raise
