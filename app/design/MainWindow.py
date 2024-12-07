from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox, QFileDialog, QMenuBar
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
import logging
import os
from datetime import datetime
import yaml

from app.design.ControlPanel import ControlPanel
from app.design.TaskManager import TaskManager
from app.design.Panel2 import Panel2
from app.Logic.LogicThread import LogicThread


class MainWindow(QWidget):
    def __init__(self, log_queue, log_emitter):
        super().__init__()
        try:
            logging.debug("Инициализация MainWindow начата.")
            self.log_queue = log_queue
            self.log_emitter = log_emitter

            self.setWindowTitle("SEORADAR")
            self.setGeometry(100, 100, 1000, 700)

            # Инициализация интерфейса
            layout = QVBoxLayout(self)

            # Добавление меню
            self.menu_bar = QMenuBar(self)
            file_menu = self.menu_bar.addMenu("Файл")

            save_config_action = QAction("Сохранить конфиг", self)
            save_config_action.triggered.connect(self.save_config)
            file_menu.addAction(save_config_action)

            save_config_as_action = QAction("Сохранить конфиг как", self)
            save_config_as_action.triggered.connect(self.save_config_as)
            file_menu.addAction(save_config_as_action)

            load_config_action = QAction("Сменить конфиг", self)
            load_config_action.triggered.connect(self.load_config)
            file_menu.addAction(load_config_action)

            reset_config_action = QAction("Сбросить конфиг", self)
            reset_config_action.triggered.connect(self.reset_config)
            file_menu.addAction(reset_config_action)

            layout.setMenuBar(self.menu_bar)

            # Добавляем ControlPanel в самом верху
            self.control_panel = ControlPanel()
            layout.addWidget(self.control_panel)
            logging.debug("ControlPanel добавлен в MainWindow.")

            # Инициализация TaskManager
            self.task_manager = TaskManager(
                tasks_directory="app/tasks", log_helper=None)
            logging.debug("TaskManager инициализирован.")

            # Создание Panel2, которая содержит вкладки
            self.panel2 = Panel2(
                tasks_directory="app/tasks",
                task_manager=self.task_manager,
                log_emitter=self.log_emitter
            )
            logging.debug("Panel2 инициализирован.")

            # Добавление Panel2 в основной макет
            layout.addWidget(self.panel2)
            logging.debug("Panel2 добавлен в MainWindow.")

            # Убедимся, что папка Configs существует
            self.configs_dir = os.path.join(os.getcwd(), 'Configs')
            if not os.path.exists(self.configs_dir):
                os.makedirs(self.configs_dir)
                logging.info(f"Создана папка конфигураций: {self.configs_dir}")

            # Инициализация LogicThread как None
            self.logic_thread = None

            # Подключение кнопок управления
            self.control_panel.start_button.clicked.connect(
                self.start_logic_thread)
            self.control_panel.stop_button.clicked.connect(
                self.stop_logic_thread)
            self.control_panel.pause_button.clicked.connect(
                self.pause_logic_thread)
            self.control_panel.resume_button.clicked.connect(
                self.resume_logic_thread)

            logging.debug("MainWindow успешно инициализировано.")

            # Загрузка конфигурации, если есть
            self.load_actual_config()

            # Подключение сигналов логирования через LogEmitter
            self.log_emitter.new_log.connect(self.panel2.update_log_output)

            # Добавляем флаг для отслеживания состояния закрытия
            self.is_closing = False

        except Exception as e:
            logging.error(f"Ошибка при инициализации MainWindow: {e}")
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при инициализации MainWindow: {e}")

    def start_logic_thread(self):
        if self.logic_thread and self.logic_thread.isRunning():
            QMessageBox.warning(self, "Предупреждение",
                                "LogicThread уже запущен.")
            logging.warning(
                "Попытка запустить LogicThread, но он уже запущен.")
            return

        selected_tasks = self.get_selected_tasks()
        if not selected_tasks:
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите хотя бы одну задачу для запуска.")
            logging.warning(
                "Попытка запустить LogicThread без выбранных задач.")
            return

        # Сохраняем текущие настройки в конфиг перед запуском
        self.save_config()  # Сохраняем настройки в файл Actual.yaml

        # Извлекаем только имена задач
        task_names = [task[1]
                      for task in selected_tasks]  # берем только имя задачи

        # Получаем настройки из SettingsTab через Panel2
        try:
            settings_tab = self.panel2.settings_tab
            thread_count = settings_tab.processes_input.value()
            mode = settings_tab.execution_mode_input.currentText()
            if mode == "Ограничение":
                execution_count = settings_tab.execution_count_input.value()
            else:
                execution_count = float('inf')  # Для бесконечного режима
        except AttributeError as e:
            thread_count = 5
            mode = "Ограничение"
            execution_count = 10
            logging.warning(
                f"Не удалось получить настройки из Panel2. Используются значения по умолчанию. Ошибка: {e}")

        logging.debug(f"Запуск LogicThread с thread_count={thread_count}, mode={
                      mode}, execution_count={execution_count}")

        # Создаём и запускаем LogicThread
        self.logic_thread = LogicThread(
            thread_count=thread_count,
            tasks=task_names,  # Передаем список задач
            task_manager=self.task_manager,
            mode=mode,
            execution_count=execution_count,
            tasks_directory="app/tasks",
            log_queue=self.log_queue  # Передаём очередь
        )
        self.logic_thread.log_signal.connect(self.update_log_output)
        self.logic_thread.status_signal.connect(
            self.control_panel.update_status)
        self.logic_thread.all_executions_completed.connect(
            self.on_all_executions_completed)
        self.logic_thread.finished.connect(self.on_logic_thread_finished)
        self.logic_thread.start()

        # Обновляем состояние кнопок
        self.control_panel.update_buttons_on_start()

        logging.debug("LogicThread запущен из MainWindow.")

    def on_logic_thread_finished(self):
        """
        Слот, вызываемый при завершении LogicThread.
        """
        self.logic_thread = None
        logging.debug("LogicThread завершился и был очищен из MainWindow.")

    def on_all_executions_completed(self):
        if not self.is_closing:
            self.control_panel.update_buttons_on_completed()
            # Добавляем текущий timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.update_log_output(
                timestamp,
                "INFO",
                "Все выполнения достигли лимита и завершены."
            )
            logging.info("Слот on_all_executions_completed вызван.")
            QMessageBox.information(
                self, "Завершено", "Все выполнения достигли лимита и завершены.")
        # Устанавливаем logic_thread в None
        self.logic_thread = None

    def cleanup(self):
        self.is_closing = True  # Устанавливаем флаг перед началом очистки
        if self.logic_thread and self.logic_thread.isRunning():
            self.logic_thread.stop()
            self.logic_thread.wait(5000)  # Ждем максимум 5 секунд
            if self.logic_thread.isRunning():
                logging.warning(
                    "LogicThread не завершился вовремя при очистке.")
            else:
                logging.debug(
                    "LogicThread успешно завершился во время очистки.")

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

    def stop_logic_thread(self):
        if self.logic_thread and self.logic_thread.isRunning():
            self.logic_thread.stop()
            self.control_panel.update_buttons_on_stop()
            logging.debug("LogicThread остановлен из MainWindow.")
        else:
            QMessageBox.information(
                self, "Информация", "LogicThread не запущен.")
            logging.info("Попытка остановить LogicThread, но он не запущен.")

    def pause_logic_thread(self):
        if self.logic_thread and self.logic_thread.isRunning():
            self.logic_thread.pause()
            self.control_panel.update_buttons_on_pause()
            logging.debug("LogicThread приостановлен из MainWindow.")
        else:
            QMessageBox.information(
                self, "Информация", "LogicThread не запущен.")
            logging.info(
                "Попытка приостановить LogicThread, но он не запущен.")

    def resume_logic_thread(self):
        if self.logic_thread and self.logic_thread.isRunning():
            self.logic_thread.resume()
            self.control_panel.update_buttons_on_resume()
            logging.debug("LogicThread возобновлён из MainWindow.")
        else:
            QMessageBox.information(
                self, "Информация", "LogicThread не запущен.")
            logging.info("Попытка возобновить LogicThread, но он не запущен.")

    def get_selected_tasks(self):
        """Возвращает список выбранных задач."""
        try:
            tasks_tab = self.panel2.tasks_tab
            return tasks_tab.get_selected_tasks()
        except IndexError:
            logging.error("TasksTab не найден в Panel2.")
            return []
        except AttributeError:
            logging.error("TasksTab не имеет метода get_selected_tasks.")
            return []

    def update_log_output(self, timestamp, log_type, message):
        """
        Обрабатывает входящие лог-сообщения, отображает их в интерфейсе.
        """
        # Добавляем лог-сообщение в LogTab через Panel2
        self.panel2.update_log_output(timestamp, log_type, message)

    def save_config(self):
        config_data = self.get_current_config()
        config_file_path = os.path.join(self.configs_dir, 'Actual.yaml')
        self.save_config_to_file(config_data, config_file_path)

    def save_config_as(self):
        config_data = self.get_current_config()
        file_dialog = QFileDialog(self)
        # Устанавливаем начальный каталог на папку Configs
        file_path, _ = file_dialog.getSaveFileName(
            self, "Сохранить конфиг как", self.configs_dir, "YAML files (*.yaml);;All files (*)")
        if file_path:
            self.save_config_to_file(config_data, file_path)

    def save_config_to_file(self, config_data, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(config_data, file,
                          default_flow_style=False, allow_unicode=True)
            logging.info(f"Конфигурация сохранена в файл: {file_path}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении конфигурации в файл: {e}")
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при сохранении конфигурации в файл: {e}")

    def load_config(self):
        file_dialog = QFileDialog(self)
        # Устанавливаем начальный каталог на папку Configs
        config_file_path, _ = file_dialog.getOpenFileName(
            self, "Выбрать конфиг", self.configs_dir, "YAML files (*.yaml);;All files (*)")
        if config_file_path:
            self._load_config_from_file(config_file_path)

    def reset_config(self):
        default_config = {
            "general_settings": {
                "thread_count": 5,
                "execution_mode": "Ограничение",
                "execution_count": 10
            },
            "tasks_settings": {}
        }
        actual_config_path = os.path.join(self.configs_dir, 'Actual.yaml')
        self.save_config_to_file(default_config, actual_config_path)
        self._load_config_from_file(actual_config_path)

    def load_actual_config(self):
        config_path = os.path.join(self.configs_dir, 'Actual.yaml')
        if os.path.exists(config_path):
            self._load_config_from_file(config_path)
        else:
            logging.info(
                "Файл конфигурации не найден, используется стандартная конфигурация.")

    def _load_config_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)

            general_settings = config_data.get("general_settings", {})
            settings_tab = self.panel2.settings_tab
            settings_tab.processes_input.setValue(
                general_settings.get("thread_count", 5))
            settings_tab.execution_mode_input.setCurrentText(
                general_settings.get("execution_mode", "Ограничение"))
            settings_tab.execution_count_input.setValue(
                general_settings.get("execution_count", 10))

            tasks_settings = config_data.get("tasks_settings", {})
            tasks_tab = self.panel2.tasks_tab
            tasks_tab.task_settings = tasks_settings
            tasks_tab.reload_task_settings_with_ids()

            logging.info(f"Конфигурация загружена из файла: {file_path}")
        except Exception as e:
            logging.error(f"Ошибка при загрузке настроек из файла: {e}")
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при загрузке настроек из файла: {e}")

    def get_current_config(self):
        settings_tab = self.panel2.settings_tab
        tasks_tab = self.panel2.tasks_tab

        general_settings = {
            "thread_count": settings_tab.processes_input.value(),
            "execution_mode": settings_tab.execution_mode_input.currentText(),
            "execution_count": settings_tab.execution_count_input.value()
        }

        tasks_settings = tasks_tab.task_settings

        return {
            "general_settings": general_settings,
            "tasks_settings": tasks_settings
        }

    def cleanup(self):
        self.is_closing = True  # Устанавливаем флаг перед началом очистки
        if self.logic_thread and self.logic_thread.isRunning():
            self.logic_thread.stop()
            self.logic_thread.wait(5000)  # Ждем максимум 5 секунд
            if self.logic_thread.isRunning():
                logging.warning(
                    "LogicThread не завершился вовремя при очистке.")
            else:
                logging.debug(
                    "LogicThread успешно завершился во время очистки.")

    def closeEvent(self, event):
        self.cleanup()
        event.accept()
