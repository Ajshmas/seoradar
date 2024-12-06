# app/design/LogTab/LogTabLogic.py

from PySide6.QtCore import Qt, QDateTime, QTimer, QModelIndex
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu
from PySide6.QtGui import QKeySequence, QClipboard, QAction

import datetime
import logging

from .LogFilters import filter_logs


class LogTabLogic:
    def __init__(self, parent):
        self.parent = parent

        # Хранение всех логов
        self.all_logs = []  # Инициализация списка всех логов
        self.pending_logs = []  # Инициализация буфера новых логов

        # Флаг для отслеживания прокрутки пользователя
        self.user_scrolled_up = False

        # Настройка таймера для обработки буфера логов
        self.log_timer = QTimer(self.parent)
        self.log_timer.setInterval(100)  # 100 миллисекунд
        self.log_timer.timeout.connect(self.process_pending_logs)
        self.log_timer.start()

        # Таймер для дебаунса вызовов apply_filters
        self.apply_filters_timer = QTimer()
        self.apply_filters_timer.setSingleShot(True)
        self.apply_filters_timer.timeout.connect(self._apply_filters)

    def toggle_time_filter(self):
        """
        Переключает состояние фильтра по времени.
        """
        is_checked = self.parent.time_filter_button.isChecked()
        # Обновляем стили и доступность виджетов
        color = "white" if is_checked else "gray"
        self.parent.time_filter_label.setStyleSheet(f"color: {color};")
        self.parent.to_label.setStyleSheet(f"color: {color};")
        self.parent.start_datetime.setEnabled(is_checked)
        self.parent.end_datetime.setEnabled(is_checked)
        self.parent.start_datetime.setStyleSheet(f"color: {color};")
        self.parent.end_datetime.setStyleSheet(f"color: {color};")
        # Применяем фильтры
        self.apply_filters()

    def on_filter_changed(self):
        """
        Обработчик изменений фильтров. Используется для дебаунса вызовов apply_filters.
        """
        self.apply_filters_timer.start(100)  # Задержка 100 мс

    def on_scrollbar_value_changed(self, value):
        """
        Отслеживает, когда пользователь прокручивает таблицу вверх.
        """
        max_value = self.parent.vertical_scrollbar.maximum()
        self.user_scrolled_up = value < max_value

    def add_log(self, log_message, log_type="INFO"):
        """
        Добавляет новый лог в буфер для последующей обработки.
        """
        timestamp = datetime.datetime.now()  # Храним datetime объект
        log_entry = {'timestamp': timestamp,
                     'log_type': log_type, 'message': log_message}
        self.pending_logs.append(log_entry)

    def process_pending_logs(self):
        """
        Обрабатывает все логи, добавленные в буфер, и обновляет отображение.
        """
        if self.pending_logs:
            self.all_logs.extend(self.pending_logs)
            self.pending_logs.clear()

            # Ограничение количества логов
            if len(self.all_logs) > self.parent.MAX_LOGS:
                excess_logs = len(self.all_logs) - self.parent.MAX_LOGS
                del self.all_logs[:excess_logs]

            self.apply_filters()

    def apply_filters(self):
        """
        Запускает таймер для применения фильтров с дебаунсом.
        """
        self.apply_filters_timer.start(100)  # Задержка 100 мс

    def _apply_filters(self):
        """
        Применяет фильтры и обновляет отображение логов.
        """
        selected_filter = self.parent.filter_combobox.currentText()
        search_text = self.parent.search_input.text().lower()

        # Фильтрация временных интервалов
        if self.parent.time_filter_button.isChecked():
            start_time = self.parent.start_datetime.dateTime().toPython()
            end_time = self.parent.end_datetime.dateTime().toPython()

            # Проверка временных интервалов
            if start_time > end_time:
                self.add_log(
                    "Некорректные временные интервалы: Начало позже конца.", log_type="ERROR")
                return
        else:
            # Если фильтр по времени отключён, установим start_time и end_time так, чтобы охватить все возможные логи
            start_time = datetime.datetime.min
            end_time = datetime.datetime.max

        # Фильтрация логов
        filtered_logs = filter_logs(
            self.all_logs, selected_filter, search_text, start_time, end_time)

        # Обновление модели данных
        self.parent.model.update_logs(filtered_logs)

        # Используем QTimer.singleShot, чтобы прокрутка произошла после обновления интерфейса
        def adjust_scrollbar():
            if not self.user_scrolled_up:
                self.parent.table_view.scrollToBottom()

        QTimer.singleShot(0, adjust_scrollbar)

    def save_logs(self):
        """
        Сохраняет текущие логи в файл.
        """
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent, "Сохранить логи", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    for log in self.all_logs:
                        timestamp_str = log['timestamp'].strftime(
                            "%Y-%m-%d %H:%M:%S")
                        file.write(
                            f"{timestamp_str} [{log['log_type']}] {log['message']}\n")
                self.add_log("Логи успешно сохранены.", log_type="INFO")
        except Exception as e:
            self.add_log(f"Ошибка сохранения логов: {
                         str(e)}", log_type="ERROR")

    def clear_logs(self):
        """
        Очищает все логи.
        """
        self.all_logs.clear()
        self.pending_logs.clear()
        self.parent.model.clear_logs()
        self.add_log("Логи очищены.", log_type="INFO")

    def keyPressEvent(self, event):
        """
        Обрабатывает нажатия клавиш для копирования выбранных строк.
        """
        if event.matches(QKeySequence.Copy):
            self.copy_selected_rows()
        else:
            super(self.parent.__class__, self.parent).keyPressEvent(event)

    def copy_selected_rows(self):
        """
        Копирует выбранные строки в буфер обмена.
        """
        indexes = self.parent.table_view.selectionModel().selectedRows()
        if indexes:
            indexes = sorted(indexes, key=lambda x: x.row())
            copied_text = ""
            # Добавляем заголовки столбцов
            headers = [self.parent.model.headerData(i, Qt.Horizontal)
                       for i in range(self.parent.model.columnCount())]
            copied_text += ','.join(headers) + '\n'
            for index in indexes:
                row_data = []
                for column in range(self.parent.model.columnCount()):
                    data = self.parent.model.data(
                        self.parent.model.index(index.row(), column))
                    # Экранируем запятые и кавычки
                    data = str(data).replace('"', '""')
                    row_data.append(f'"{data}"')
                copied_text += ','.join(row_data) + '\n'
            # Устанавливаем текст в буфер обмена
            clipboard = QApplication.clipboard()
            clipboard.setText(copied_text.strip())
        else:
            # Если ничего не выбрано, копируем все данные
            copied_text = ""
            headers = [self.parent.model.headerData(i, Qt.Horizontal)
                       for i in range(self.parent.model.columnCount())]
            copied_text += ','.join(headers) + '\n'
            for row in range(self.parent.model.rowCount()):
                row_data = []
                for column in range(self.parent.model.columnCount()):
                    data = self.parent.model.data(
                        self.parent.model.index(row, column))
                    data = str(data).replace('"', '""')
                    row_data.append(f'"{data}"')
                copied_text += ','.join(row_data) + '\n'
            clipboard = QApplication.clipboard()
            clipboard.setText(copied_text.strip())

    def show_context_menu(self, position):
        """
        Отображает контекстное меню для копирования выбранных строк.
        """
        menu = QMenu()
        copy_action = QAction("Копировать", self.parent)
        copy_action.triggered.connect(self.copy_selected_rows)
        menu.addAction(copy_action)
        menu.exec(self.parent.table_view.viewport().mapToGlobal(position))
