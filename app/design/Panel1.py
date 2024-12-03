# app/design/Panel1.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import Qt


class Panel1(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(60, 60, 60);")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Поле для отображения логов
        self.log_tab = QTextEdit()
        self.log_tab.setReadOnly(True)
        self.log_tab.setStyleSheet("""
            QTextEdit {
                background-color: rgb(30, 30, 30);
                color: white;
                font-family: Consolas;
                font-size: 12px;
            }
        """)

        layout.addWidget(self.log_tab)
        self.setLayout(layout)

    def add_log(self, message, log_type="INFO"):
        """
        Добавляет сообщение в лог.

        :param message: Текст сообщения.
        :param log_type: Тип сообщения ("INFO", "ERROR").
        """
        if log_type == "INFO":
            formatted_message = f"<span style='color: lightgreen;'>[INFO] {
                message}</span>"
        elif log_type == "ERROR":
            formatted_message = f"<span style='color: red;'>[ERROR] {
                message}</span>"
        else:
            formatted_message = f"{message}"
        self.log_tab.append(formatted_message)
