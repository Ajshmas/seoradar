# app/design/TasksTab.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QHBoxLayout,
    QLineEdit, QPushButton, QFileDialog, QSpinBox, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt
import logging
import yaml
import os
import copy


class TasksTab(QWidget):
    def __init__(self, parent=None, task_manager=None):
        super().__init__(parent)
        if task_manager is None:
            logging.error("TasksTab: task_manager не был передан.")
            raise ValueError("task_manager не может быть None.")
        self.task_manager = task_manager
        logging.debug("TasksTab: Инициализация.")
        self.task_settings = {}  # Хранение настроек для каждой задачи
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Первый раздел: Доступные задачи
        available_widget = QWidget()
        available_layout = QVBoxLayout(available_widget)
        available_label = QLabel("Доступные задачи")
        self.available_list_widget = QListWidget()
        self.available_list_widget.setSelectionMode(
            QListWidget.SingleSelection)
        self.available_list_widget.itemDoubleClicked.connect(
            self.add_task_via_double_click)
        available_layout.addWidget(available_label)
        available_layout.addWidget(self.available_list_widget)

        # Второй раздел: Выбранные задачи
        selected_widget = QWidget()
        selected_layout = QVBoxLayout(selected_widget)
        selected_label = QLabel("Выбранные задачи")
        self.selected_list_widget = QListWidget()
        self.selected_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.selected_list_widget.itemDoubleClicked.connect(
            self.remove_task_via_double_click)
        self.selected_list_widget.setDragEnabled(True)
        self.selected_list_widget.setAcceptDrops(True)
        self.selected_list_widget.setDragDropMode(QListWidget.InternalMove)
        self.selected_list_widget.setDefaultDropAction(Qt.MoveAction)
        selected_layout.addWidget(selected_label)
        selected_layout.addWidget(self.selected_list_widget)

        # Третий раздел: Настройки задач
        settings_widget = QWidget()
        self.settings_layout = QVBoxLayout(settings_widget)
        settings_label = QLabel("Настройки задач")
        self.settings_layout.addWidget(settings_label)
        self.settings_form = QVBoxLayout()  # Это основной слой для настроек
        self.settings_layout.addLayout(self.settings_form)
        self.settings_layout.addStretch()

        # Добавление разделов в основной макет
        main_layout.addWidget(available_widget)
        main_layout.addWidget(selected_widget)
        main_layout.addWidget(settings_widget)

        available_width = self.calculate_max_width(self.available_list_widget)
        selected_width = self.calculate_max_width(self.selected_list_widget)
        available_widget.setFixedWidth(available_width + 150)
        selected_widget.setFixedWidth(selected_width + 150)

        settings_widget.setSizePolicy(
            settings_widget.sizePolicy().horizontalPolicy(),
            settings_widget.sizePolicy().verticalPolicy()
        )

        self.setLayout(main_layout)

        # Заполнение доступных задач
        self.populate_available_tasks()

        # Подключение слота для изменения выбранных задач
        self.selected_list_widget.itemSelectionChanged.connect(
            self.on_selected_tasks_changed)

    def calculate_max_width(self, list_widget):
        max_width = 0
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            fm = list_widget.fontMetrics()
            text_width = fm.horizontalAdvance(item.text())
            if text_width > max_width:
                max_width = text_width
        return max_width

    def populate_available_tasks(self):
        try:
            available_tasks = self.task_manager.get_task_names()
            if not available_tasks:
                logging.warning(
                    "TasksTab: Нет доступных задач для отображения.")
            for task_name_localized in available_tasks:
                item = QListWidgetItem(task_name_localized)
                self.available_list_widget.addItem(item)
                logging.debug(
                    f"Задача '{task_name_localized}' добавлена в TasksTab.")
        except AttributeError as e:
            logging.error(f"Ошибка при получении списка задач: {e}")

    def add_task_via_double_click(self, item: QListWidgetItem):
        task_name = item.text()
        unique_task_name = f"{
            task_name} ({self.selected_list_widget.count() + 1})"
        new_item = QListWidgetItem(unique_task_name)

        # Генерация уникального идентификатора для задачи
        task_id = len(self.task_settings) + 1
        new_item.setData(Qt.UserRole, task_id)
        self.selected_list_widget.addItem(new_item)
        logging.debug(f"Задача '{unique_task_name}' добавлена в выбранные.")

        # Загружаем настройки для оригинального имени задачи и сохраняем их в словарь
        base_config = self.task_manager.get_task_config(task_name)
        # Сохраняем имя задачи в конфигурации, чтобы позже его использовать
        task_settings_with_name = {
            'task_name': task_name,
            **base_config
        }
        self.task_settings[task_id] = copy.deepcopy(task_settings_with_name)
        logging.debug(f"Создана запись настроек для задачи с id={
                      task_id}: {self.task_settings[task_id]}")

    def remove_task_via_double_click(self, item: QListWidgetItem):
        row = self.selected_list_widget.row(item)
        task_name = item.text()
        task_id = item.data(Qt.UserRole)

        self.selected_list_widget.takeItem(row)
        if task_id in self.task_settings:
            del self.task_settings[task_id]
            logging.debug(
                f"Задача '{task_name}' и ее настройки (id={task_id}) удалены.")

        self.clear_task_settings()

    def on_selected_tasks_changed(self):
        current_item = self.selected_list_widget.currentItem()
        if current_item is not None:
            task_id = current_item.data(Qt.UserRole)
            self.current_task_id = task_id
            logging.debug(f"Настройки текущей задачи (id={task_id}): {
                          self.task_settings[task_id]}")
            self.clear_task_settings()
            self.load_task_settings(task_id)

    def load_task_settings(self, task_id):
        task_config = self.task_settings.get(task_id, {})
        if not task_config:
            logging.info(f"TasksTab: Задача с id={task_id} не имеет настроек.")
            return

        widget_map = {}
        for key, params in task_config.items():
            if key == 'task_name':  # Пропускаем имя задачи, оно не должно быть виджетом
                continue
            widget = self.create_widget_for_param(key, params)
            if widget:
                widget_map[key] = widget
                self.settings_form.addLayout(widget)

        for key, widget in widget_map.items():
            param_type = task_config[key]['type']
            value = task_config[key].get('value')
            self.set_widget_value(widget, param_type, value)

    def get_selected_tasks(self):
        """Возвращает список выбранных задач."""
        selected_tasks = []
        for index in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(index)
            # Получаем id
            task_id = item.data(Qt.UserRole)
            # Также получаем имя задачи
            task_name = item.text().split(
                ' (')[0]  # Получаем оригинальное имя задачи
            # Теперь храним id и имя
            selected_tasks.append((task_id, task_name))
        return selected_tasks

    def reload_task_settings_with_ids(self):
        """Метод для перезагрузки выбранных задач с сохранением ID и имен."""
        self.selected_list_widget.clear()
        for task_id, task_config in self.task_settings.items():
            task_name = task_config.get('task_name', 'Неизвестная задача')
            unique_task_name = f"{task_name} ({task_id})"
            new_item = QListWidgetItem(unique_task_name)
            new_item.setData(Qt.UserRole, task_id)
            self.selected_list_widget.addItem(new_item)
        logging.info("Выбранные задачи перезагружены с сохранением ID.")

    def create_widget_for_param(self, key, params):
        layout = QHBoxLayout()
        label = QLabel(f"{key}:")
        label.setFixedWidth(150)
        layout.addWidget(label)

        param_type = params.get('type')

        if param_type == "string":
            line_edit = QLineEdit()
            line_edit.textChanged.connect(
                lambda value, k=key: self.update_task_setting_value(k, value))
            layout.addWidget(line_edit)
            return layout

        elif param_type == "number":
            spin_box = QSpinBox()
            spin_box.valueChanged.connect(
                lambda value, k=key: self.update_task_setting_value(k, value))
            layout.addWidget(spin_box)
            return layout

        elif param_type == "random_number":
            min_val = params.get('min', 0)
            max_val = params.get('max', 100)
            line_edit = QLineEdit()
            line_edit.setReadOnly(True)
            random_btn = QPushButton("Сгенерировать")
            random_btn.clicked.connect(lambda: self.generate_random_number(
                line_edit, min_val, max_val, key))
            layout.addWidget(line_edit)
            layout.addWidget(random_btn)
            return layout

        elif param_type == "file":
            file_layout = QHBoxLayout()
            line_edit = QLineEdit()
            line_edit.textChanged.connect(
                lambda value, k=key: self.update_task_setting_value(k, value))
            browse_btn = QPushButton("Обзор")
            browse_btn.clicked.connect(lambda: self.browse_file(line_edit))
            file_layout.addWidget(line_edit)
            file_layout.addWidget(browse_btn)
            layout.addLayout(file_layout)
            return layout

        elif param_type == "folder":
            folder_layout = QHBoxLayout()
            line_edit = QLineEdit()
            line_edit.textChanged.connect(
                lambda value, k=key: self.update_task_setting_value(k, value))
            browse_btn = QPushButton("Обзор")
            browse_btn.clicked.connect(lambda: self.browse_folder(line_edit))
            folder_layout.addWidget(line_edit)
            folder_layout.addWidget(browse_btn)
            layout.addLayout(folder_layout)
            return layout

        elif param_type == "list":
            combo_box = QComboBox()
            options = params.get('options', [])
            combo_box.addItems(options)
            combo_box.currentTextChanged.connect(
                lambda value, k=key: self.update_task_setting_value(k, value))
            layout.addWidget(combo_box)
            return layout

        elif param_type == "checkbox":
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(
                lambda state, k=key: self.update_task_setting_value(k, bool(state)))
            layout.addWidget(checkbox)
            return layout

        else:
            logging.warning(f"TasksTab: Неизвестный тип параметра '{
                            param_type}' для '{key}'.")
            return None

    def set_widget_value(self, widget_layout, param_type, value):
        widget = widget_layout.itemAt(1).widget()  # Получаем виджет
        if param_type == "string" and isinstance(widget, QLineEdit):
            widget.setText(value if value else "")
        elif param_type == "number" and isinstance(widget, QSpinBox):
            widget.setValue(value if value else 0)
        elif param_type == "list" and isinstance(widget, QComboBox):
            # Устанавливаем выбранное значение, если оно есть
            if isinstance(value, list):
                # Берем первый элемент, если список не пустой
                value = value[0] if value else ""
            widget.setCurrentText(value)
        elif param_type == "checkbox" and isinstance(widget, QCheckBox):
            widget.setChecked(value.lower() == "true" if isinstance(
                value, str) else bool(value))

    def update_task_setting_value(self, key, value):
        if hasattr(self, 'current_task_id') and self.current_task_id in self.task_settings:
            self.task_settings[self.current_task_id][key]['value'] = value
            logging.debug(f"Обновлено значение для задачи с id={
                          self.current_task_id}: {key} = {value}")

    def generate_random_number(self, line_edit, min_val, max_val, key):
        import random
        rand_num = random.randint(min_val, max_val)
        line_edit.setText(str(rand_num))
        self.update_task_setting_value(key, rand_num)

    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", "All Files (*)")
        if file_path:
            line_edit.setText(file_path)

    def browse_folder(self, line_edit):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Выберите папку", "")
        if folder_path:
            line_edit.setText(folder_path)

    def clear_task_settings(self):
        logging.debug("Полная очистка настроек задач")
        while self.settings_form.count():
            item = self.settings_form.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        layout.deleteLater()
