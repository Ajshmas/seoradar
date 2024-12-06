# main.py

import sys
import logging
import multiprocessing
import signal
from PySide6.QtWidgets import QApplication
from logging.handlers import QueueHandler
from app.design.MainWindow import MainWindow
from app.utils.logger_config import setup_logging, LogEmitter


def main():
    multiprocessing.freeze_support()  # Необходимо для Windows

    # Создание очереди для логирования
    log_queue = multiprocessing.Queue()

    # Создание эмиттера для логов в GUI
    log_emitter = LogEmitter()

    # Настройка логирования через централизованный модуль
    listener = setup_logging(log_queue, log_emitter)

    logging.info("Начало запуска приложения.")

    # Создание QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Применение стиля Fusion ко всему приложению
    logging.info("QApplication создан с применённым стилем Fusion.")

    # Создание и показ главного окна, передача log_queue и log_emitter
    main_window = MainWindow(log_queue, log_emitter)
    main_window.show()  # Убедитесь, что окно отображается

    # Обработка сигналов завершения

    def handle_signal(signum, frame):
        logging.info(f"Получен сигнал завершения: {
                     signum}. Завершение приложения.")
        main_window.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)  # Обработка Ctrl+C
    signal.signal(signal.SIGTERM, handle_signal)  # Обработка SIGTERM

    # Запуск цикла приложения
    try:
        sys.exit(app.exec())
    finally:
        listener.stop()


if __name__ == '__main__':
    main()
