from PySide6.QtCore import QThread, Signal
import time


class LogicThread(QThread):
    log_signal = Signal(str, str)
    status_signal = Signal(str)

    def __init__(self, thread_count, tasks, task_manager):
        super().__init__()
        self.thread_count = thread_count
        self.tasks = tasks
        self.task_manager = task_manager

    def run(self):
        self.status_signal.emit("Работает")

        # Запуск всех потоков внутри QThread
        for i in range(self.thread_count):
            self.execute_tasks(i + 1)

        self.status_signal.emit("Ожидание")
        self.log_signal.emit("Все задачи выполнены.", "INFO")

    def execute_tasks(self, thread_id):
        """
        Каждому потоку передаются все задачи для выполнения.
        """
        self.log_signal.emit(f"Поток {thread_id} начинает выполнение.", "INFO")

        for task in self.tasks:
            self.log_signal.emit(
                f"Поток {thread_id} выполняет задачу: {task}", "INFO")
            self.msleep(1000)  # Используем msleep для ожидания между задачами

        self.log_signal.emit(f"Поток {thread_id} завершил выполнение.", "INFO")
