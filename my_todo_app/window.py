from PyQt6.QtWidgets import QLineEdit, QListWidget, QPushButton, QVBoxLayout, QWidget

import my_todo_app.database as database


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Your To-Do List")
        self.setGeometry(300, 300, 300, 400)

        # Load tasks from the database
        self.conn = database.get_conn("data/tasks.db")
        self.tasks = self.load_from_db(self.conn)

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

    def load_from_db(self, conn):
        tasks = database.get_all_tasks(conn)
        return tasks

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

    def closeEvent(self, event):
        database.close_connection(self.conn)
