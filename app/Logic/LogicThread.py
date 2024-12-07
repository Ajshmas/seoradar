# Logic/LogicThread.py

from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
import logging
from multiprocessing import Process
from app.Logic.run_tasks_process import execute_tasks_process
import heapq  # Для эффективного управления доступными номерами


class LogicThread(QThread):
    log_signal = Signal(str, str)  # message, log_type
    status_signal = Signal(str)
    all_executions_completed = Signal()

    def __init__(self, thread_count, tasks, task_manager, mode, execution_count, tasks_directory, log_queue):
        super().__init__()
        self.thread_count = thread_count  # Максимальное количество параллельных процессов
        self.tasks = tasks  # Список всех выбранных задач
        self.task_manager = task_manager
        self.mode = mode  # "Ограничение" или "Бесконечный"
        self.execution_count = execution_count  # Общее количество запусков процессов
        self.tasks_directory = tasks_directory
        self.log_queue = log_queue
        self.processes = {}  # Ключ: Process, Значение: process_number
        self._is_running = True
        self.executions_started = 0  # Количество запущенных процессов
        # Изначально все номера свободны
        self.available_numbers = list(range(1, self.thread_count + 1))
        # Превращаем список в мин-кучу для эффективного получения наименьшего номера
        heapq.heapify(self.available_numbers)

        # Добавляем механизмы паузы
        self.pause_mutex = QMutex()
        self.pause_condition = QWaitCondition()
        self.paused = False

    def run(self):
        try:
            logging.debug(f"LogicThread запущен с thread_count={
                          self.thread_count}, execution_count={self.execution_count}, mode={self.mode}")
            self.status_signal.emit("Запущен")

            while self._is_running and (self.mode == "Бесконечный" or self.executions_started < self.execution_count):
                # Проверка состояния паузы
                self.pause_mutex.lock()
                while self.paused and self._is_running:
                    self.status_signal.emit("Пауза")
                    self.pause_condition.wait(self.pause_mutex)
                    if not self.paused:
                        self.status_signal.emit("Запущен")
                self.pause_mutex.unlock()

                # Запуск новых дочерних процессов, если есть свободные номера и не достигнут лимит запусков
                while self._is_running and self.available_numbers and (self.mode != "Ограничение" or self.executions_started < self.execution_count):
                    # Назначение порядкового номера
                    process_number = heapq.heappop(self.available_numbers)

                    # Создание и запуск дочернего процесса
                    p = Process(target=execute_tasks_process, args=(
                        self.tasks.copy(), process_number, self.log_queue))
                    p.start()
                    logging.info(f"Запущен дочерний процесс {
                                 process_number} с задачами: {self.tasks.copy()}")

                    # Сохранение процесса и его номера
                    self.processes[p] = process_number
                    self.executions_started += 1
                    self.status_signal.emit(f"Запущено процессов: {
                                            len(self.processes)}")

                # Проверка завершения процессов
                for p in list(self.processes.keys()):
                    if not p.is_alive():
                        p.join()
                        finished_number = self.processes.pop(p)
                        logging.info(f"Дочерний процесс завершился: PID {
                                     p.pid}, номер процесса: {finished_number}")

                        # Освобождение номера процесса
                        heapq.heappush(self.available_numbers, finished_number)
                        self.status_signal.emit(f"Запущено процессов: {
                                                len(self.processes)}")

                        # Если достигнут лимит запусков, и нет активных процессов, завершить работу
                        if self.mode == "Ограничение" and self.executions_started >= self.execution_count and not self.processes:
                            logging.info(
                                "Достигнут лимит выполнений. LogicThread завершает работу.")
                            self.status_signal.emit("Завершено")
                            self._is_running = False
                            break

                self.msleep(100)  # Пауза перед следующей проверкой

            # Ожидание завершения всех процессов перед выходом
            for p, number in self.processes.items():
                p.join()
                logging.info(f"Дочерний процесс завершился: PID {
                             p.pid}, номер процесса: {number}")
                heapq.heappush(self.available_numbers, number)
            self.processes.clear()

        except Exception as e:
            logging.error(f"LogicThread: Произошла ошибка: {e}")
            self.status_signal.emit("Ошибка")
        finally:
            # Принудительно завершить все процессы при остановке
            for p, number in self.processes.items():
                if p.is_alive():
                    p.terminate()
                    p.join()
                    logging.info(f"Дочерний процесс принудительно завершен: PID {
                                 p.pid}, номер процесса: {number}")
            self.processes.clear()
            logging.info("LogicThread завершил работу.")
            self.status_signal.emit("Остановлено")
            self.all_executions_completed.emit()

    def stop(self):
        self._is_running = False
        self.pause_mutex.lock()
        self.paused = False  # Убираем паузу, чтобы поток мог выйти из wait
        self.pause_condition.wakeAll()
        self.pause_mutex.unlock()
        self.status_signal.emit("Останавливается")

        # Принудительно завершить все процессы
        for p, number in self.processes.items():
            if p.is_alive():
                p.terminate()
                p.join()
                logging.info(f"Дочерний процесс принудительно завершен: PID {
                             p.pid}, номер процесса: {number}")
        self.processes.clear()

    def pause(self):
        self.pause_mutex.lock()
        self.paused = True
        self.pause_mutex.unlock()
        self.status_signal.emit("Пауза")
        logging.info("LogicThread приостановлен.")

    def resume(self):
        self.pause_mutex.lock()
        if self.paused:
            self.paused = False
            self.pause_condition.wakeAll()
            self.status_signal.emit("Запущен")
            logging.info("LogicThread возобновлён.")
        self.pause_mutex.unlock()
