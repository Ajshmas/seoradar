# app/tasks/TaskA/task_a.py

from PySide6.QtCore import QMutexLocker


class TaskA:
    def __init__(self, shared_resources):
        self.shared_resources = shared_resources

    def run(self):
        # Попытка захватить блокировку с таймаутом
        if self.shared_resources.lock.tryLock(1000):  # 1000 мс
            try:
                self.shared_resources.counter += 1
                print(f"TaskA увеличил счетчик до {
                      self.shared_resources.counter}")
            finally:
                self.shared_resources.lock.unlock()
        else:
            print("TaskA не смог захватить блокировку на ресурс.")
            # Логика обработки случая, когда ресурс недоступен
