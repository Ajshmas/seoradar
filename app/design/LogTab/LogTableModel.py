# app/design/LogTab/LogTableModel.py

from PySide6.QtCore import Qt, QAbstractTableModel
import datetime


class LogTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.logs = []

    def rowCount(self, parent=None):
        return len(self.logs)

    def columnCount(self, parent=None):
        return 3  # timestamp, log_type, message

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        log = self.logs[index.row()]
        column = index.column()

        if column == 0:
            return log['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        elif column == 1:
            return log['log_type']
        elif column == 2:
            return log['message']
        else:
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == 0:
                return "Время"
            elif section == 1:
                return "Тип"
            elif section == 2:
                return "Сообщение"
        return None

    def update_logs(self, logs):
        self.beginResetModel()
        self.logs = logs
        self.endResetModel()

    def clear_logs(self):
        self.beginResetModel()
        self.logs.clear()
        self.endResetModel()
