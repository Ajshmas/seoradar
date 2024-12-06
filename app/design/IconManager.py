# app/design/IconManager.py

from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, Qt
from PySide6.QtCore import QSize


class IconManager:
    @staticmethod
    def create_icon(style_pixmap, color):
        """
        Создает иконку с заданным стилем и цветом.

        :param style_pixmap: Стандартный QStyle.StandardPixmap.
        :param color: QColor для окраски иконки.
        :return: QIcon.
        """
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)

        # Рисуем стандартный значок
        icon = QIcon.fromTheme(str(style_pixmap))
        if not icon.isNull():
            icon.paint(painter, pixmap.rect())
        else:
            # Если значок не найден, рисуем простой круг
            painter.drawEllipse(pixmap.rect())

        painter.end()
        return QIcon(pixmap)
