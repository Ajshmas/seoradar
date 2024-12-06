from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu
from PySide6.QtGui import QKeySequence, QClipboard, QAction

from datetime import datetime
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
        Отслеживает, когда пользователь прокручивает текстовое поле.
        """
        max_value = self.parent.text_edit.verticalScrollBar().maximum()
        self.user_scrolled_up = value < max_value

    def add_log(self, timestamp, log_type, message):
        """
        Добавляет новый лог в буфер для последующей обработки.
        """
        log_entry = {
            'timestamp': timestamp,
            'log_type': log_type,
            'message': message
        }
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
            start_time = datetime.strptime(
                self.parent.start_datetime.dateTime().toString("yyyy-MM-dd HH:mm:ss"), "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(
                self.parent.end_datetime.dateTime().toString("yyyy-MM-dd HH:mm:ss"), "%Y-%m-%d %H:%M:%S")

            # Проверка временных интервалов
            if start_time > end_time:
                logging.error(
                    "Некорректные временные интервалы: Начало позже конца.")
                return
        else:
            # Если фильтр по времени отключён, установим start_time и end_time так, чтобы охватить все возможные логи
            start_time = datetime.min
            end_time = datetime.max

        # Фильтрация логов
        filtered_logs = filter_logs(
            self.all_logs, selected_filter, search_text, start_time, end_time)

        # Обновление отображения в QTextEdit
        self.parent.text_edit.clear()
        for log in filtered_logs:
            log_entry = f"[{log['timestamp']}] [{
                log['log_type']}] {log['message']}\n"
            self.parent.text_edit.append(log_entry)

        # Используем QTimer.singleShot, чтобы прокрутка произошла после обновления интерфейса
        def adjust_scrollbar():
            if not self.user_scrolled_up:
                self.parent.text_edit.verticalScrollBar().setValue(
                    self.parent.text_edit.verticalScrollBar().maximum())

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
                        timestamp_str = log['timestamp']
                        log_type = log['log_type']
                        message = log['message']
                        file.write(
                            f'"{timestamp_str}","{log_type}","{message}"\n')
                # Добавляем лог о сохранении
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logging.info("Логи успешно сохранены.")
        except Exception as e:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.error(f"Ошибка сохранения логов: {e}")

    def clear_logs(self):
        """
        Очищает все логи.
        """
        self.all_logs.clear()
        self.pending_logs.clear()
        self.parent.text_edit.clear()  # Очистка текста в QTextEdit
        # Добавляем лог о очистке
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info("Логи очищены.")

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
        clipboard = QApplication.clipboard()
        text = self.parent.text_edit.toPlainText()  # Получаем весь текст
        clipboard.setText(text)  # Копируем в буфер обмена

    def show_context_menu(self, position):
        """
        Отображает контекстное меню для копирования всех логов.
        """
        menu = QMenu()
        copy_action = QAction("Копировать все логи", self.parent)
        copy_action.triggered.connect(self.copy_selected_rows)
        menu.addAction(copy_action)
        menu.exec(self.parent.text_edit.viewport().mapToGlobal(position))
