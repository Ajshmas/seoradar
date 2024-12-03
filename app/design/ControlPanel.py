from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QStyle
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter, QColor
from app.design.IconManager import IconManager  # Убедитесь, что путь корректен


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(50, 50, 50);")

        layout = QHBoxLayout()
        layout.setSpacing(10)
        # Прижимаем все элементы к левому краю
        layout.setAlignment(Qt.AlignLeft)

        style = self.style()

        # Создаём иконки с цветами через IconManager
        self.start_icon = IconManager.create_icon(
            QStyle.SP_MediaPlay, QColor("green"))
        self.stop_icon = IconManager.create_icon(
            QStyle.SP_MediaStop, QColor("darkred"))
        self.pause_icon = IconManager.create_icon(
            QStyle.SP_MediaPause, QColor("orange"))
        self.resume_icon = IconManager.create_icon(
            QStyle.SP_MediaPlay, QColor("green"))
        self.status_icon = IconManager.create_icon(
            QStyle.SP_MediaStop, QColor("gray"))
        self.error_icon = IconManager.create_icon(
            QStyle.SP_MediaStop, QColor("darkred"))

        # Кнопка "Запуск" с иконкой "Play"
        self.start_button = QPushButton()
        self.start_button.setIcon(self.start_icon)
        self.start_button.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.start_button.setToolTip("Запустить выполнение задач.")

        # Кнопка "Стоп" с иконкой "Stop"
        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.stop_icon)
        self.stop_button.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Остановить выполнение задач.")

        # Кнопка "Пауза" с иконкой "Pause"
        self.pause_button = QPushButton()
        self.pause_button.setIcon(self.pause_icon)
        self.pause_button.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.pause_button.setEnabled(False)
        self.pause_button.setToolTip("Приостановить выполнение задач.")

        # Кнопка "Возобновить" с иконкой "Play"
        self.resume_button = QPushButton()
        self.resume_button.setIcon(self.resume_icon)
        self.resume_button.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.resume_button.setEnabled(False)
        self.resume_button.setToolTip("Возобновить выполнение задач.")

        # Добавляем пустое пространство между кнопками и статусом
        spacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Кнопка "Статус" с иконкой (по умолчанию Статус ожидания - Стоп)
        self.status_button = QPushButton()
        self.status_button.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed)
        # Отключаем возможность клика по кнопке
        # self.status_button.setEnabled(False)
        self.status_button.setIcon(self.status_icon)
        self.status_button.setToolTip("Текущий статус выполнения задач.")

        # Добавляем кнопки в макет
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.resume_button)
        layout.addSpacerItem(spacer)  # Добавляем отступ
        layout.addWidget(self.status_button)

        self.setLayout(layout)

    def update_status(self, status):
        """
        Обновляет иконку кнопки статуса в зависимости от текущего статуса.
        Также управляет состоянием кнопок "Пауза" и "Возобновить".
        """
        if status == "Работает":
            self.status_button.setIcon(self.start_icon)
            self.status_button.setToolTip("Задачи выполняются")
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)
        elif status == "На паузе":
            self.status_button.setIcon(self.pause_icon)
            self.status_button.setToolTip("Задачи на паузе")
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)
        elif status == "Ожидание":
            self.status_button.setIcon(self.stop_icon)
            self.status_button.setToolTip("Ожидает выполнения")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(False)
        elif status == "Ошибка":
            self.status_button.setIcon(self.error_icon)
            self.status_button.setToolTip("Произошла ошибка")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(False)
        else:
            self.status_button.setIcon(self.status_icon)
            self.status_button.setToolTip("Ожидает выполнения")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(False)
