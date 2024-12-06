from PySide6.QtWidgets import (
    QVBoxLayout, QGridLayout, QLabel, QComboBox, QPushButton, QDateTimeEdit,
    QSizePolicy, QHBoxLayout, QLineEdit, QTextEdit, QMenu, QFileDialog
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QKeySequence, QAction

import datetime


class LogTabUI:
    def __init__(self, parent):
        self.parent = parent

    def setup_ui(self, main_layout):
        # Верхняя часть: Фильтры и Поиск
        filter_search_layout = self.create_filter_search_layout()
        main_layout.addLayout(filter_search_layout)

        # Отображение логов (используем QTextEdit вместо QTableView)
        self.parent.text_edit = self.create_text_edit()
        main_layout.addWidget(self.parent.text_edit)

        # Убедитесь, что сохраняются только кнопки для сохранения и очистки логов.
        save_layout = self.create_save_layout()  # Без лишнего поля
        main_layout.addLayout(save_layout)

    def create_filter_search_layout(self):
        """
        Создаёт макет для фильтров и поиска.
        """
        filter_search_layout = QGridLayout()
        filter_search_layout.setSpacing(10)

        # Фильтр по типу логов
        self.parent.filter_label = QLabel("Фильтр по типу:")
        self.parent.filter_label.setStyleSheet("color: white;")
        self.parent.filter_combobox = QComboBox()
        self.parent.filter_combobox.addItems(
            ["Все", "INFO", "ERROR", "DEBUG", "CRITICAL"])
        self.parent.filter_combobox.setToolTip(
            "Выберите тип логов для фильтрации.")
        self.parent.filter_combobox.currentIndexChanged.connect(
            self.parent.on_filter_changed)

        # Кнопка для включения/отключения фильтрации по времени
        self.parent.time_filter_button = QPushButton("Фильтр по времени")
        self.parent.time_filter_button.setCheckable(True)
        self.parent.time_filter_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(70, 70, 70);
                color: gray;
                border: 1px solid rgb(100, 100, 100);
                padding: 5px;
            }
            QPushButton:checked {
                background-color: rgb(100, 100, 100);
                color: white;
                border: 2px solid rgb(150, 150, 150);
            }
        """)
        self.parent.time_filter_button.setToolTip(
            "Включить или отключить фильтрацию логов по временным интервалам."
        )
        self.parent.time_filter_button.clicked.connect(
            self.parent.toggle_time_filter)

        # Фильтр по временным интервалам
        self.parent.time_filter_label = QLabel("Время от:")
        self.parent.time_filter_label.setStyleSheet(
            "color: gray;")  # Изначально серый цвет
        self.parent.start_datetime = QDateTimeEdit(self.parent)
        self.parent.start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.parent.start_datetime.setDateTime(
            QDateTime.currentDateTime().addDays(-1))
        self.parent.start_datetime.setToolTip(
            "Начало временного интервала для фильтрации логов.")
        self.parent.start_datetime.dateTimeChanged.connect(
            self.parent.on_filter_changed)
        self.parent.start_datetime.setEnabled(False)  # Изначально отключено
        self.parent.start_datetime.setStyleSheet("color: gray;")
        self.parent.start_datetime.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.parent.start_datetime.setMinimumWidth(150)

        self.parent.to_label = QLabel("до:")
        self.parent.to_label.setStyleSheet("color: gray;")
        self.parent.end_datetime = QDateTimeEdit(self.parent)
        self.parent.end_datetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.parent.end_datetime.setDateTime(QDateTime.currentDateTime())
        self.parent.end_datetime.setToolTip(
            "Конец временного интервала для фильтрации логов.")
        self.parent.end_datetime.dateTimeChanged.connect(
            self.parent.on_filter_changed)
        self.parent.end_datetime.setEnabled(False)  # Изначально отключено
        self.parent.end_datetime.setStyleSheet("color: gray;")
        self.parent.end_datetime.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.parent.end_datetime.setMinimumWidth(150)

        # Настройка выравнивания и отступов
        self.parent.time_filter_label.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter)
        self.parent.to_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.parent.time_filter_label.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.parent.to_label.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Поле поиска по логам
        self.parent.search_label = QLabel("Поиск:")
        self.parent.search_label.setStyleSheet("color: white;")
        self.parent.search_input = QLineEdit()
        self.parent.search_input.setPlaceholderText(
            "Введите текст для поиска...")
        self.parent.search_input.setToolTip(
            "Введите текст для поиска в логах.")
        self.parent.search_input.textChanged.connect(
            self.parent.on_filter_changed)

        # Создание макетов для меток и полей
        start_layout = QHBoxLayout()
        start_layout.setSpacing(5)
        start_layout.setContentsMargins(5, 0, 5, 0)
        start_layout.addWidget(self.parent.time_filter_label)
        start_layout.addWidget(self.parent.start_datetime)

        end_layout = QHBoxLayout()
        end_layout.setSpacing(5)
        end_layout.setContentsMargins(5, 0, 5, 0)
        end_layout.addWidget(self.parent.to_label)
        end_layout.addWidget(self.parent.end_datetime)

        # Горизонтальный макет для фильтра по времени
        time_filter_layout = QHBoxLayout()
        time_filter_layout.setSpacing(10)
        time_filter_layout.addWidget(self.parent.time_filter_button)
        time_filter_layout.addLayout(start_layout)
        time_filter_layout.addLayout(end_layout)
        time_filter_layout.addStretch()

        # Добавляем виджеты в макет фильтров и поиска
        filter_search_layout.addWidget(self.parent.filter_label, 0, 0)
        filter_search_layout.addWidget(self.parent.filter_combobox, 0, 1, 1, 3)
        filter_search_layout.addLayout(time_filter_layout, 1, 0, 1, 4)
        filter_search_layout.addWidget(self.parent.search_label, 2, 0)
        filter_search_layout.addWidget(self.parent.search_input, 2, 1, 1, 3)

        return filter_search_layout  # Возвращаем макет

    def create_text_edit(self):
        """
        Создаёт QTextEdit для отображения логов.
        """
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)  # Отключаем редактирование
        text_edit.setLineWrapMode(QTextEdit.NoWrap)  # Отключаем перенос строк
        text_edit.setMinimumHeight(200)

        return text_edit

    def create_save_layout(self):
        """
        Создаёт макет для кнопок сохранения и очистки логов.
        """
        save_layout = QHBoxLayout()
        self.parent.save_log_button = QPushButton("Сохранить логи")
        self.parent.save_log_button.setToolTip(
            "Сохранить текущие логи в файл.")
        self.parent.save_log_button.clicked.connect(self.parent.save_logs)

        self.parent.clear_log_button = QPushButton("Очистить логи")
        self.parent.clear_log_button.setToolTip("Очистить все логи.")
        self.parent.clear_log_button.clicked.connect(self.parent.clear_logs)

        save_layout.addWidget(self.parent.save_log_button)
        save_layout.addWidget(self.parent.clear_log_button)
        save_layout.addStretch()

        return save_layout  # Возвращаем макет
