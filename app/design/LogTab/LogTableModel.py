# app/design/LogTab/LogTableModel.py

from PySide6.QtCore import QAbstractTableModel, Qt


class LogTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logs = []
        self.headers = ["Время", "Тип", "Сообщение"]

    def rowCount(self, parent=None):
        return len(self.logs)

    def columnCount(self, parent=None):
        return 3  # Время, Тип, Сообщение

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if index.row() >= len(self.logs) or index.row() < 0:
            return None
        log = self.logs[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return log['timestamp']
            elif index.column() == 1:
                return log['log_type']
            elif index.column() == 2:
                return log['message']
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section < len(self.headers):
                return self.headers[section]
        return None

    def update_logs(self, new_logs):
        self.beginResetModel()
        self.logs = new_logs
        self.endResetModel()

    def clear_logs(self):
        self.beginResetModel()
        self.logs = []
        self.endResetModel()
