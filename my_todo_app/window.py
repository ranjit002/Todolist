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
    """
    Represents a single task widget with a label and delete button.
    """

    def __init__(self, task_text: str, delete_callback):
        super().__init__()
        self.task_text = task_text
        self.delete_callback = delete_callback

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        self.task_label = QLabel(self.task_text)
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


class TaskManager:
    """
    Handles task-related operations such as loading, saving, and deleting tasks from the database.
    """

    def __init__(self, db_path: str):
        self.conn = database.get_conn(db_path)

    def load_tasks(self):
        return database.get_all_tasks(self.conn)

    def save_task(self, task_text: str):
        database.save_task(self.conn, task_text)

    def delete_task(self, task_text: str):
        database.delete_task(self.conn, task_text)

    def close(self):
        database.close_connection(self.conn)


class TaskListWidget(QListWidget):
    """
    Manages the list of tasks displayed in the UI.
    """

    def __init__(self):
        super().__init__()

    def add_task(self, task_text: str, delete_callback):
        task_item = QListWidgetItem()
        task_widget = TaskWidget(task_text, delete_callback)
        task_item.setSizeHint(task_widget.sizeHint())
        self.addItem(task_item)
        self.setItemWidget(task_item, task_widget)

    def remove_task(self, task_text: str):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget and widget.task_text == task_text:
                self.takeItem(i)
                break


class MainWindow(QWidget):
    """
    Main application window that integrates the task manager and UI components.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Your To-Do List")
        self.setGeometry(300, 300, 300, 400)

        self.task_manager = TaskManager("data/tasks.db")
        self.init_ui()
        self.load_tasks()

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Input field for new tasks
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Your new task")
        self.layout.addWidget(self.input_field)

        # Add task button
        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)

        # Task list widget
        self.task_list = TaskListWidget()
        self.layout.addWidget(self.task_list)

        self.setLayout(self.layout)

    def load_tasks(self):
        tasks = self.task_manager.load_tasks()
        for task in tasks:
            self.task_list.add_task(task, self.delete_task)

    def add_task(self):
        task_text = self.input_field.text().strip()
        if task_text:
            self.task_manager.save_task(task_text)
            self.task_list.add_task(task_text, self.delete_task)
            self.input_field.clear()

    def delete_task(self, task_text: str):
        self.task_manager.delete_task(task_text)
        self.task_list.remove_task(task_text)

    def closeEvent(self, event):
        self.task_manager.close()
