from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import my_todo_app.database as database


class TaskWidget(QWidget):
    def __init__(self, task_text, delete_callback):
        super().__init__()
        self.task_text = task_text
        self.delete_callback = delete_callback

        layout = QHBoxLayout()
        self.task_label = QLabel(task_text)
        self.delete_button = QPushButton("🗑️")
        self.delete_button.setFixedSize(30, 30)

        layout.addWidget(self.task_label)
        layout.addWidget(self.delete_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.delete_button.clicked.connect(self.handle_delete)

    def handle_delete(self):
        self.delete_callback(self.task_text)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Your To-Do List")
        self.setGeometry(300, 300, 300, 400)

        # Load tasks from the database
        self.conn = database.get_conn("data/tasks.db")
        self.tasks = self.tasks_from_db(self.conn)

        self.layout = QVBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Your new task")

        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)

        self.task_list = QListWidget()

        widgets = [self.input_field, self.add_button, self.task_list]

        for widget in widgets:
            self.layout.addWidget(widget)

        self.setLayout(self.layout)
        self.view_tasks(self.tasks)

    def tasks_from_db(self, conn):
        tasks = database.get_all_tasks(conn)
        return tasks

    def add_task_to_ui(self, task_text):
        task_item = QListWidgetItem()
        task_widget = TaskWidget(task_text, self.delete_task)
        task_item.setSizeHint(task_widget.sizeHint())
        self.task_list.addItem(task_item)
        self.task_list.setItemWidget(task_item, task_widget)

    def view_tasks(self, tasks):
        for task in tasks:
            self.task_list.addItem(task)

    def add_task(self):
        task = self.input_field.text()

        if task:
            database.save_task(self.conn, task)
            self.tasks.append(task)
            self.task_list.addItem(task)
            self.input_field.clear()
            self.add_task_to_ui(task)

    def delete_task(self, task_text):
        database.delete_task(self.conn, task_text)

        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if widget and widget.task_text == task_text:
                self.task_list.takeItem(i)

    def closeEvent(self, event):
        database.close_connection(self.conn)
