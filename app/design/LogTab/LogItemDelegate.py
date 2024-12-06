# app/design/LogTab/LogItemDelegate.py

from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtCore import QSize


class LogItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.row_height = 18  # Устанавливаем желаемую высоту строки

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(self.row_height)
        return size
