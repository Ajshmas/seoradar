from PySide6.QtCore import QThread, Signal
import time


class WorkerThread(QThread):
    log_signal = Signal(str, str)  # (message, log_type)

    def __init__(self, tasks, thread_id, logic_thread):
        super().__init__()
        self.tasks = tasks  # Список задач
        self.thread_id = thread_id  # Идентификатор потока
        self.logic_thread = logic_thread  # Ссылка на LogicThread для управления паузой

    def run(self):
        """
        Метод, который выполняется в потоке.
        """
        try:
            self.log_signal.emit(
                f"Поток {self.thread_id}: Начинает выполнение всех задач.", "INFO")
            for task, status in self.tasks:
                # Проверяем, не приостановлено ли выполнение
                self.logic_thread.mutex.lock()
                while self.logic_thread.paused and self.logic_thread._is_running:
                    self.logic_thread.wait_condition.wait(
                        self.logic_thread.mutex)
                self.logic_thread.mutex.unlock()

                if not self.logic_thread._is_running:
                    self.log_signal.emit(
                        f"Поток {self.thread_id}: Выполнение задач остановлено.", "INFO")
                    return

                self.log_signal.emit(
                    f"Поток {self.thread_id}: Выполняет задачу: {task}", "DEBUG")
                time.sleep(1)  # Симуляция выполнения задачи (1 секунда)
                self.log_signal.emit(
                    f"Поток {self.thread_id}: Завершена задача: {task}", "INFO")
            self.log_signal.emit(
                f"Поток {self.thread_id}: Завершил выполнение всех задач.", "INFO")
        except Exception as e:
            self.log_signal.emit(
                f"Поток {self.thread_id}: Ошибка - {str(e)}", "ERROR")
