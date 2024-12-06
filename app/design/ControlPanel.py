# app/design/ControlPanel.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
import logging


class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.debug("ControlPanel: Инициализация.")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Создание кнопок
        self.start_button = QPushButton("Старт")
        self.stop_button = QPushButton("Стоп")
        self.pause_button = QPushButton("Пауза")
        self.resume_button = QPushButton("Возобновить")

        # Настройка размера кнопок
        self.start_button.setFixedHeight(30)
        self.stop_button.setFixedHeight(30)
        self.pause_button.setFixedHeight(30)
        self.resume_button.setFixedHeight(30)

        # Добавление кнопок в макет
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.resume_button)

        # Добавление разделителя
        layout.addStretch()

        # Добавление QLabel для отображения статуса
        self.status_label = QLabel("Статус: Остановлено")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        logging.debug("ControlPanel: Интерфейс инициализирован.")

    def update_buttons_on_start(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        self.resume_button.setEnabled(False)
        logging.debug("ControlPanel: Кнопки обновлены после запуска.")

    def update_buttons_on_stop(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        logging.debug("ControlPanel: Кнопки обновлены после остановки.")

    def update_buttons_on_pause(self):
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(True)
        logging.debug("ControlPanel: Кнопки обновлены после паузы.")

    def update_buttons_on_resume(self):
        self.pause_button.setEnabled(True)
        self.resume_button.setEnabled(False)
        logging.debug("ControlPanel: Кнопки обновлены после возобновления.")

    def update_buttons_on_completed(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        logging.debug(
            "ControlPanel: Кнопки обновлены после завершения всех процессов.")

    def update_status(self, status_message):
        """
        Обновляет текст статуса.
        """
        self.status_label.setText(f"Статус: {status_message}")
        logging.debug(f"ControlPanel: Статус обновлён на '{status_message}'.")
