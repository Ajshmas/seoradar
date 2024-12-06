# app/design/SettingsTab.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QComboBox
from PySide6.QtCore import Qt
import logging


class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        logging.debug("SettingsTab: Инициализация.")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Настройки количества процессов
        processes_layout = QHBoxLayout()
        processes_label = QLabel("Количество процессов:")
        self.processes_input = QSpinBox()
        self.processes_input.setRange(1, 100)
        self.processes_input.setValue(5)
        processes_layout.addWidget(processes_label)
        processes_layout.addWidget(self.processes_input)
        processes_layout.addStretch()

        # Настройки режима выполнения
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Режим выполнения:")
        self.execution_mode_input = QComboBox()
        self.execution_mode_input.addItems(["Ограничение", "Бесконечный"])
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.execution_mode_input)
        mode_layout.addStretch()

        # Настройки количества выполнений (только для режима "Ограничение")
        execution_count_layout = QHBoxLayout()
        execution_count_label = QLabel("Количество выполнений:")
        self.execution_count_input = QSpinBox()
        self.execution_count_input.setRange(1, 1000)
        self.execution_count_input.setValue(10)
        execution_count_layout.addWidget(execution_count_label)
        execution_count_layout.addWidget(self.execution_count_input)
        execution_count_layout.addStretch()

        # Добавление всех настроек в макет
        layout.addLayout(processes_layout)
        layout.addLayout(mode_layout)
        layout.addLayout(execution_count_layout)

        # Добавление растяжки для выравнивания
        layout.addStretch()

        self.setLayout(layout)
        logging.debug("SettingsTab: Интерфейс инициализирован.")
