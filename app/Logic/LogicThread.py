# Logic/LogicThread.py

from PySide6.QtCore import QThread, Signal
import logging
from multiprocessing import Process
from app.Logic.run_tasks_process import execute_tasks_process


class LogicThread(QThread):
    log_signal = Signal(str, str)  # message, log_type
    status_signal = Signal(str)
    all_executions_completed = Signal()

    def __init__(self, thread_count, tasks, task_manager, mode, execution_count, tasks_directory, log_queue):
        super().__init__()
        self.thread_count = thread_count  # Максимальное количество процессов
        self.tasks = tasks  # Список задач для выполнения каждым процессом
        self.task_manager = task_manager
        self.mode = mode  # "Ограничение" или "Бесконечный"
        self.execution_count = execution_count  # Общее количество запусков процессов
        self.tasks_directory = tasks_directory
        self.processes = []
        self._is_running = True
        self._is_paused = False
        self.total_executions = 0  # Счётчик запусков процессов
        self.available_process_numbers = list(
            range(1, self.thread_count + 1))  # [1,2,3,4]
        self.process_number_map = {}  # pid -> process_number
        self.log_queue = log_queue

    def run(self):
        try:
            while self._is_running:
                # Проверка на паузу
                if self._is_paused:
                    self.msleep(100)
                    continue

                # Очистка завершённых процессов
                for process in self.processes[:]:
                    if not process.is_alive():
                        process.join()
                        self.processes.remove(process)
                        process_number = self.process_number_map.pop(
                            process.pid, None)
                        if process_number:
                            self.available_process_numbers.append(
                                process_number)
                            # Сортируем для назначения наименьшего номера
                            self.available_process_numbers.sort()
                            logging.info(self.format_process_message(
                                process_number, "завершён."))

                # Проверка условий для запуска новых процессов
                can_launch = False
                if self.mode == "Бесконечный":
                    can_launch = True
                elif self.mode == "Ограничение" and self.total_executions < self.execution_count:
                    can_launch = True

                if can_launch and len(self.processes) < self.thread_count and self.available_process_numbers:
                    # Запуск нового процесса
                    process_number = self.available_process_numbers.pop(
                        0)  # Назначаем наименьший доступный номер
                    self.total_executions += 1
                    p = Process(target=execute_tasks_process, args=(
                        self.tasks, process_number, self.log_queue))
                    p.start()
                    self.processes.append(p)
                    self.process_number_map[p.pid] = process_number
                    message = self.format_process_message(
                        process_number, "запущен для выполнения задач.")
                    logging.info(message)

                # Проверка завершения всех процессов при режиме "Ограничение"
                if self.mode == "Ограничение" and self.total_executions >= self.execution_count and not self.processes:
                    logging.info(
                        "Достигнут лимит выполнений. LogicThread завершает работу.")
                    break

                self.msleep(100)  # Небольшая пауза перед следующей проверкой

            # После выхода из цикла, завершаем все процессы
            self.terminate_all_processes()

        except Exception as e:

            logging.error(f"LogicThread: Произошла ошибка: {e}")
        finally:
            logging.info("LogicThread завершил работу.")
            self.all_executions_completed.emit()

    def should_launch_processes(self):
        # Логика для проверки условий запуска процессов
        if self.mode == "Бесконечный":
            return True
        elif self.mode == "Ограничение" and self.total_executions < self.execution_count:
            return True
        return False

    def execute_task_process(self, tasks, process_number, log_queue):
        for task in tasks:
            # Вызываем выполнение задачи
            logging.info(self.format_process_message(
                process_number, f"запустил задачу '{task}'."))
            execute_tasks_process(task, process_number, log_queue)

    def stop(self):
        self._is_running = False
        self.resume()  # В случае паузы, чтобы выйти из цикла

        # Принудительно завершить все дочерние процессы
        self.terminate_all_processes()

    def pause(self):
        self._is_paused = True
        self.status_signal.emit("Пауза")

    def resume(self):
        if self._is_paused:
            self._is_paused = False
            self.status_signal.emit("Работает")

    def terminate_all_processes(self):
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()
                process_number = self.process_number_map.pop(process.pid, None)
                if process_number:
                    self.available_process_numbers.append(process_number)
                    self.available_process_numbers.sort()
                    logging.info(self.format_process_message(
                        process_number, "принудительно завершён."))

        self.processes.clear()

    def format_process_message(self, process_number, action):
        """Форматирует сообщение о действии процесса."""
        return f"Процесс {process_number}: {action}"
