# main.py

import sys
import logging
import multiprocessing
import signal
from PySide6.QtWidgets import QApplication
from logging.handlers import QueueHandler, QueueListener
from app.design.MainWindow import MainWindow


def main():
    multiprocessing.freeze_support()  # Необходимо для Windows

    # Создание очереди для логирования
    log_queue = multiprocessing.Queue()

    # Настройка обработчика для отправки логов в очередь
    queue_handler = QueueHandler(log_queue)
    logger = logging.getLogger()
    logger.addHandler(queue_handler)
    # Установите уровень логирования по необходимости
    logger.setLevel(logging.DEBUG)

    # Настройка слушателя очереди для записи логов в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    listener = QueueListener(log_queue, console_handler)
    listener.start()

    logging.info("Начало запуска приложения.")
    print("Начало запуска приложения.")

    # Создание QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Применение стиля Fusion ко всему приложению
    logging.info("QApplication создан с применённым стилем Fusion.")
    print("QApplication создан с применённым стилем Fusion.")

    # Создание и показ главного окна, передача log_queue
    main_window = MainWindow(log_queue)
    main_window.show()  # Убедитесь, что окно отображается
    logging.info("Главное окно показано.")
    print("Главное окно показано.")

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
