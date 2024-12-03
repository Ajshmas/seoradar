from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QComboBox, QFileDialog,
    QPushButton, QLineEdit, QLabel, QHBoxLayout, QDateTimeEdit, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QTextCursor
import datetime


class LogTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(50, 50, 50);")

        # Основной макет
        main_layout = QVBoxLayout()

        # Верхняя часть: Фильтры и Поиск
        filter_search_layout = QGridLayout()
        filter_search_layout.setSpacing(10)

        # Фильтр по типу логов
        self.filter_label = QLabel("Фильтр по типу:")
        self.filter_label.setStyleSheet("color: white;")
        self.filter_combobox = QComboBox()
        self.filter_combobox.addItems(["Все", "INFO", "ERROR", "DEBUG"])
        self.filter_combobox.setToolTip("Выберите тип логов для фильтрации.")
        self.filter_combobox.currentIndexChanged.connect(self.apply_filters)

        # Кнопка для включения/отключения фильтрации по времени
        self.time_filter_button = QPushButton("Фильтр по времени")
        self.time_filter_button.setCheckable(True)
        self.time_filter_button.setStyleSheet("""
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
        self.time_filter_button.setToolTip(
            "Включить или отключить фильтрацию логов по временным интервалам."
        )
        self.time_filter_button.clicked.connect(self.toggle_time_filter)

        # Фильтр по временным интервалам
        self.time_filter_label = QLabel("Время от:")
        self.time_filter_label.setStyleSheet(
            "color: gray;")  # Изначально серый цвет
        self.start_datetime = QDateTimeEdit(self)
        self.start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_datetime.setDateTime(
            QDateTime.currentDateTime().addDays(-1))
        self.start_datetime.setToolTip(
            "Начало временного интервала для фильтрации логов.")
        self.start_datetime.dateTimeChanged.connect(self.apply_filters)
        self.start_datetime.setEnabled(False)  # Изначально отключено
        self.start_datetime.setStyleSheet("color: gray;")
        self.start_datetime.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_datetime.setMinimumWidth(150)

        self.to_label = QLabel("до:")
        self.to_label.setStyleSheet("color: gray;")
        self.end_datetime = QDateTimeEdit(self)
        self.end_datetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_datetime.setDateTime(QDateTime.currentDateTime())
        self.end_datetime.setToolTip(
            "Конец временного интервала для фильтрации логов.")
        self.end_datetime.dateTimeChanged.connect(self.apply_filters)
        self.end_datetime.setEnabled(False)  # Изначально отключено
        self.end_datetime.setStyleSheet("color: gray;")
        self.end_datetime.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.end_datetime.setMinimumWidth(150)

        # Настройка выравнивания и отступов
        self.time_filter_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.to_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.time_filter_label.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.to_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Поле поиска по логам
        self.search_label = QLabel("Поиск:")
        self.search_label.setStyleSheet("color: white;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.setToolTip("Введите текст для поиска в логах.")
        self.search_input.textChanged.connect(self.apply_filters)

        # Создание макетов для меток и полей
        start_layout = QHBoxLayout()
        start_layout.setSpacing(5)
        start_layout.setContentsMargins(5, 0, 5, 0)
        start_layout.addWidget(self.time_filter_label)
        start_layout.addWidget(self.start_datetime)

        end_layout = QHBoxLayout()
        end_layout.setSpacing(5)
        end_layout.setContentsMargins(5, 0, 5, 0)
        end_layout.addWidget(self.to_label)
        end_layout.addWidget(self.end_datetime)

        # Горизонтальный макет для фильтра по времени
        time_filter_layout = QHBoxLayout()
        time_filter_layout.setSpacing(10)
        time_filter_layout.addWidget(self.time_filter_button)
        time_filter_layout.addLayout(start_layout)
        time_filter_layout.addLayout(end_layout)
        time_filter_layout.addStretch()

        # Добавляем виджеты в макет фильтров и поиска
        filter_search_layout.addWidget(self.filter_label, 0, 0)
        filter_search_layout.addWidget(self.filter_combobox, 0, 1, 1, 3)
        filter_search_layout.addLayout(time_filter_layout, 1, 0, 1, 4)
        filter_search_layout.addWidget(self.search_label, 2, 0)
        filter_search_layout.addWidget(self.search_input, 2, 1, 1, 3)

        main_layout.addLayout(filter_search_layout)

        # Отображение логов
        self.log_output = QTextEdit()
        self.log_output.setStyleSheet(
            "background-color: #232323; color: white;")
        self.log_output.setReadOnly(True)
        self.log_output.setToolTip("Отображение логов приложения.")
        main_layout.addWidget(self.log_output)

        # Нижняя часть: Кнопки сохранения и очистки логов
        save_layout = QHBoxLayout()
        self.save_log_button = QPushButton("Сохранить логи")
        self.save_log_button.setToolTip("Сохранить текущие логи в файл.")
        self.save_log_button.clicked.connect(self.save_logs)

        self.clear_log_button = QPushButton("Очистить логи")
        self.clear_log_button.setToolTip("Очистить все логи.")
        self.clear_log_button.clicked.connect(self.clear_logs)

        save_layout.addWidget(self.save_log_button)
        save_layout.addWidget(self.clear_log_button)
        save_layout.addStretch()

        main_layout.addLayout(save_layout)

        self.setLayout(main_layout)

        # Хранение всех логов
        self.all_logs = []

    def toggle_time_filter(self):
        """
        Включает или отключает фильтрацию по времени.
        """
        if self.time_filter_button.isChecked():
            # Активируем элементы фильтра по времени
            self.time_filter_label.setEnabled(True)
            self.start_datetime.setEnabled(True)
            self.to_label.setEnabled(True)
            self.end_datetime.setEnabled(True)

            # Меняем цвет текста на белый
            self.time_filter_button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(100, 100, 100);
                    color: white;
                    border: 2px solid rgb(150, 150, 150);
                    padding: 5px;
                }
            """)
            self.time_filter_label.setStyleSheet("color: white;")
            self.to_label.setStyleSheet("color: white;")
            self.start_datetime.setStyleSheet("color: white;")
            self.end_datetime.setStyleSheet("color: white;")
        else:
            # Деактивируем элементы фильтра по времени
            self.time_filter_label.setEnabled(False)
            self.start_datetime.setEnabled(False)
            self.to_label.setEnabled(False)
            self.end_datetime.setEnabled(False)

            # Меняем цвет текста на серый
            self.time_filter_button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(70, 70, 70);
                    color: gray;
                    border: 1px solid rgb(100, 100, 100);
                    padding: 5px;
                }
            """)
            self.time_filter_label.setStyleSheet("color: gray;")
            self.to_label.setStyleSheet("color: gray;")
            self.start_datetime.setStyleSheet("color: gray;")
            self.end_datetime.setStyleSheet("color: gray;")
        self.apply_filters()

    def add_log(self, log_message, log_type="INFO"):
        """
        Добавляет новый лог и обновляет отображение.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_log = f"[{timestamp}] [{log_type}] {log_message}"
        self.all_logs.append((formatted_log, log_type))
        self.apply_filters()

    def apply_filters(self):
        """
        Применяет фильтры и обновляет отображение логов.
        """
        selected_filter = self.filter_combobox.currentText()
        search_text = self.search_input.text().lower()

        # Проверка временных интервалов только если фильтр включён
        if self.time_filter_button.isChecked():
            start_time = self.start_datetime.dateTime().toPython()
            end_time = self.end_datetime.dateTime().toPython()

            # Проверка временных интервалов
            if start_time > end_time:
                print("LogTab: Некорректные временные интервалы. Начало позже конца.")
                return
        else:
            # Если фильтр по времени отключён, установим start_time и end_time так, чтобы охватить все возможные логи
            start_time = datetime.datetime.min
            end_time = datetime.datetime.max

        # Очистка поля вывода логов
        self.log_output.clear()

        for log, log_type in self.all_logs:
            # Парсинг временной метки
            try:
                timestamp_str, type_str, message = self.parse_log(log)
                log_time = datetime.datetime.strptime(
                    timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Если формат лога некорректен, пропускаем его
                continue

            # Применение фильтра по типу лога (без учёта регистра)
            if selected_filter != "Все" and log_type.upper() != selected_filter.upper():
                continue

            # Применение фильтра по временным интервалам
            if not (start_time <= log_time <= end_time):
                continue

            # Применение фильтра по тексту поиска
            if search_text and search_text not in log.lower():
                continue

            # Добавление логов с цветовой кодировкой
            color = self.get_color_for_log_type(log_type)
            colored_log = f"<span style='color:{color};'>{log}</span>"
            self.log_output.append(colored_log)
            # Прокрутка до последнего добавленного лога
            self.log_output.moveCursor(QTextCursor.End)

    def parse_log(self, log):
        """
        Парсит логовое сообщение на компоненты.

        :param log: Строка логового сообщения.
        :return: Tuple (timestamp_str, log_type, message)
        """
        try:
            timestamp_end = log.index(']')
            timestamp_str = log[1:timestamp_end]
            type_start = log.index('[', timestamp_end) + 1
            type_end = log.index(']', type_start)
            log_type = log[type_start:type_end]
            message = log[type_end + 2:]
            return timestamp_str, log_type, message
        except (ValueError, IndexError):
            # Если парсинг не удался, возвращаем пустые строки
            return "", "", ""

    def get_color_for_log_type(self, log_type):
        """
        Возвращает цвет для данного типа лога.

        :param log_type: Тип лога (например, INFO, ERROR, DEBUG).
        :return: Цвет в формате HEX.
        """
        colors = {
            "INFO": "#FFFFFF",    # Белый
            "ERROR": "#FFA500",   # Оранжевый
            "DEBUG": "#D3D3D3",   # Светло-серый
        }
        return colors.get(log_type.upper(), "#FFFFFF")  # Белый по умолчанию

    def save_logs(self):
        """
        Сохраняет текущие логи в файл.
        """
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить логи", "", "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    for log, _ in self.all_logs:
                        file.write(f"{log}\n")
                self.add_log("Логи успешно сохранены.", log_type="INFO")
        except Exception as e:
            self.add_log(f"Ошибка сохранения логов: {
                         str(e)}", log_type="ERROR")

    def clear_logs(self):
        """
        Очищает все логи.
        """
        self.all_logs.clear()
        self.apply_filters()
        self.add_log("Логи очищены.", log_type="INFO")
