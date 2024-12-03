import sys
from PySide6.QtWidgets import QApplication, QWidget, QSplitter, QVBoxLayout, QStyle
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor
from app.design.Panel1 import Panel1
from app.design.Panel2 import Panel2
from app.design.ControlPanel import ControlPanel
from app.design.IconManager import IconManager
from app.design.TaskManager import TaskManager
from Logic import LogicThread


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Интерфейс с разделителем")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout(self)

        # Инициализация TaskManager
        tasks_directory = "app/tasks"
        self.task_manager = TaskManager(tasks_directory)

        # Добавляем ControlPanel в самом верху
        self.control_panel = ControlPanel()
        layout.addWidget(self.control_panel)

        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: transparent;
                border: none;
                height: 10px;
            }
            QSplitter {
                background-color: rgb(40, 40, 40);
            }
        """)

        self.panel1 = Panel1()
        # Передаем TaskManager в Panel2
        self.panel2 = Panel2(self.task_manager)

        splitter.addWidget(self.panel1)
        splitter.addWidget(self.panel2)

        layout.addWidget(splitter)

        self.logic_thread = None
        self.control_panel.start_button.clicked.connect(
            self.start_logic_thread)
        self.control_panel.stop_button.clicked.connect(self.stop_logic_thread)
        self.control_panel.pause_button.clicked.connect(
            self.pause_logic_thread)
        self.control_panel.resume_button.clicked.connect(
            self.resume_logic_thread)

        self.setLayout(layout)

    def start_logic_thread(self):
        if not self.logic_thread or not self.logic_thread.isRunning():
            try:
                # Получаем количество потоков
                thread_count = self.panel2.settings_tab.threads_input.value()
                tasks = self.panel2.get_tasks()

                if not tasks:
                    self.panel2.log_tab.add_log(
                        "Нет задач для выполнения.", log_type="ERROR")
                    self.control_panel.update_status("Ошибка")
                    return

                # Создаем новый поток и передаем количество потоков и задачи
                self.logic_thread = LogicThread(
                    thread_count, tasks, self.task_manager)
                self.logic_thread.log_signal.connect(self.update_log_output)
                self.logic_thread.status_signal.connect(
                    self.control_panel.update_status)
                self.logic_thread.status_signal.connect(
                    self.update_window_icon)  # Обновление иконки
                self.logic_thread.start()

                # Обновление состояния кнопок
                self.control_panel.start_button.setEnabled(False)
                self.control_panel.stop_button.setEnabled(True)
                self.control_panel.pause_button.setEnabled(True)
                self.control_panel.resume_button.setEnabled(False)
                self.control_panel.update_status("Работает")
            except Exception as e:
                self.panel2.log_tab.add_log(f"Ошибка при запуске потоков: {
                                            str(e)}", log_type="ERROR")
                self.control_panel.update_status("Ошибка")
        else:
            self.panel2.log_tab.add_log(
                "Потоки уже запущены.", log_type="INFO")

    def stop_logic_thread(self):
        if self.logic_thread and self.logic_thread.isRunning():
            self.logic_thread.stop()
            self.logic_thread.wait()
            self.logic_thread = None

            # Обновление состояния кнопок
            self.control_panel.start_button.setEnabled(True)
            self.control_panel.stop_button.setEnabled(False)
            self.control_panel.pause_button.setEnabled(False)
            self.control_panel.resume_button.setEnabled(False)
            self.control_panel.update_status("Остановлен")
            self.panel2.log_tab.add_log("Потоки остановлены.", log_type="INFO")
        else:
            self.panel2.log_tab.add_log(
                "Нет активных потоков для остановки.", log_type="INFO")

    def pause_logic_thread(self):
        if self.logic_thread and self.logic_thread.isRunning():
            self.logic_thread.pause()
            self.control_panel.pause_button.setEnabled(False)
            self.control_panel.resume_button.setEnabled(True)
            self.panel2.log_tab.add_log(
                "Потоки приостановлены.", log_type="INFO")
        else:
            self.panel2.log_tab.add_log(
                "Нет активных потоков для паузы.", log_type="INFO")

    def resume_logic_thread(self):
        if self.logic_thread and self.logic_thread.isRunning():
            self.logic_thread.resume()
            self.control_panel.pause_button.setEnabled(True)
            self.control_panel.resume_button.setEnabled(False)
            self.panel2.log_tab.add_log(
                "Потоки возобновлены.", log_type="INFO")
        else:
            self.panel2.log_tab.add_log(
                "Нет активных потоков для возобновления.", log_type="INFO")

    def update_window_icon(self, status):
        icon = IconManager.create_icon(
            self.get_style_icon(status), self.get_color(status))
        self.setWindowIcon(icon)

    def get_style_icon(self, status):
        if status == "Работает":
            return QStyle.SP_MediaPlay
        elif status == "На паузе":
            return QStyle.SP_MediaPause
        elif status == "Ожидание":
            return QStyle.SP_MediaStop
        elif status == "Ошибка":
            return QStyle.SP_MessageBoxCritical
        else:
            return QStyle.SP_MediaStop

    def get_color(self, status):
        if status == "Работает":
            return QColor("green")
        elif status == "На паузе":
            return QColor("orange")
        elif status == "Ожидание":
            return QColor("darkred")
        elif status == "Ошибка":
            return QColor("darkred")
        else:
            return QColor("gray")

    def update_log_output(self, message, log_type):
        self.panel2.log_tab.add_log(message, log_type)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
