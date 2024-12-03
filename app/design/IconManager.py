# app/design/IconManager.py

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import QStyle, QApplication


class IconManager:
    @staticmethod
    def create_icon(icon_type, color, size=(32, 32)):
        """
        Создаёт иконку с заданным цветом.

        :param icon_type: Тип иконки (например, QStyle.StandardPixmap).
        :param color: QColor объект, который нужно применить к иконке.
        :param size: Размер иконки.
        :return: QIcon с заданным цветом.
        """
        # Получаем стандартную иконку по типу
        style = QApplication.instance().style()
        # Используем QStyle.StandardPixmap
        icon = style.standardIcon(icon_type)

        # Преобразуем иконку в pixmap
        pixmap = icon.pixmap(*size)

        # Создаём QPainter для рисования на pixmap
        painter = QPainter(pixmap)
        # Устанавливаем режим для изменения цвета
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        # Закрашиваем иконку нужным цветом
        painter.fillRect(pixmap.rect(), color)
        painter.end()

        return QIcon(pixmap)  # Возвращаем результат в виде QIcon
