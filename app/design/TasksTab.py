from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit


class TasksTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Заголовок
        self.header_label = QLabel("Список задач")
        self.header_label.setStyleSheet(
            "color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(self.header_label)

        # Таблица для отображения задач
        self.tasks_table = QTableWidget(self)
        # Два столбца: название задачи, статус
        self.tasks_table.setColumnCount(2)
        self.tasks_table.setHorizontalHeaderLabels(["Задача", "Статус"])
        self.tasks_table.setRowCount(0)  # Начинаем с нулевой строки
        layout.addWidget(self.tasks_table)

        # Поле для добавления новой задачи
        add_task_layout = QHBoxLayout()
        self.new_task_input = QLineEdit()
        self.new_task_input.setPlaceholderText("Введите название задачи...")
        self.add_task_button = QPushButton("Добавить задачу")
        self.add_task_button.setStyleSheet(
            "background-color: #4CAF50; color: white;")
        self.add_task_button.clicked.connect(self.add_task)
        add_task_layout.addWidget(self.new_task_input)
        add_task_layout.addWidget(self.add_task_button)
        layout.addLayout(add_task_layout)

        self.setLayout(layout)

    def add_task(self):
        """
        Добавляет новую задачу в таблицу.
        """
        task_name = self.new_task_input.text().strip()
        if task_name:
            row_position = self.tasks_table.rowCount()
            self.tasks_table.insertRow(row_position)
            self.tasks_table.setItem(
                row_position, 0, QTableWidgetItem(task_name))
            self.tasks_table.setItem(
                row_position, 1, QTableWidgetItem("Ожидание"))
            self.new_task_input.clear()

    def get_tasks(self):
        """
        Возвращает список задач из таблицы.
        """
        tasks = []
        for row in range(self.tasks_table.rowCount()):
            task_name = self.tasks_table.item(row, 0).text()
            task_status = self.tasks_table.item(row, 1).text()
            tasks.append((task_name, task_status))
        return tasks
