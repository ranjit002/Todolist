from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog,
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


class Task:
    """
    Represents a task with attributes such as title, deadline, location, and URL.
    Encapsulates task data and exposes methods to interact with it.
    By default, only the title is required, and other fields are optional.
    """

    def __init__(
        self,
        title: str,
        deadline: datetime = None,
        location: str = None,
        url: str = None,
    ):
        self._title = title
        self._deadline = deadline
        self._location = location
        self._url = url

    # Encapsulation: Use getters to access private attributes
    @property
    def title(self):
        return self._title

    @property
    def deadline(self):
        return self._deadline

    @property
    def location(self):
        return self._location

    @property
    def url(self):
        return self._url

    def __str__(self):
        """
        Returns a string representation of the task, including title and optional details.
        """
        details = [self.title]
        if self.deadline:
            details.append(f"Deadline: {self.deadline.strftime('%Y-%m-%d %H:%M')}")
        if self.location:
            details.append(f"Location: {self.location}")
        if self.url:
            details.append(f"URL: {self.url}")
        return " | ".join(details)

    def set_deadline(self, deadline: datetime):
        """Encapsulation: Set a deadline with validation"""
        if isinstance(deadline, datetime):
            self._deadline = deadline
        else:
            raise ValueError("Invalid deadline format")

    def set_location(self, location: str):
        """Encapsulation: Set a location"""
        self._location = location

    def set_url(self, url: str):
        """Encapsulation: Set a URL"""
        self._url = url


class TaskWidget(QWidget):
    """
    Represents a single task widget with UI elements to display and interact with the task.
    """

    def __init__(self, task: Task, delete_callback):
        super().__init__()
        self._task = task
        self._delete_callback = delete_callback

        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()
        self.task_label = QLabel(str(self._task))  # Display task details
        self.delete_button = QPushButton("🗑️")
        self.delete_button.setFixedSize(30, 30)

        layout.addWidget(self.task_label)
        layout.addWidget(self.delete_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.delete_button.clicked.connect(self._handle_delete)

    def _handle_delete(self):
        self._delete_callback(self._task)


class TaskManager:
    """
    Manages task operations, including loading, saving, and deleting tasks from the database.
    """

    def __init__(self, db_path: str):
        self._conn = database.get_conn(db_path)

    def load_tasks(self):
        tasks = database.get_all_tasks(self._conn)
        return [
            Task(
                title=task["title"],
                deadline=task.get("deadline"),
                location=task.get("location"),
                url=task.get("url"),
            )
            for task in tasks
        ]

    def save_task(self, task: Task):
        database.save_task(
            self._conn, task.title, task.deadline, task.location, task.url
        )

    def delete_task(self, task: Task):
        database.delete_task(self._conn, task.title)

    def close(self):
        database.close_connection(self._conn)


class TaskListWidget(QListWidget):
    """
    Displays the list of tasks in the UI, allowing users to add or remove tasks.
    """

    def __init__(self):
        super().__init__()

    def add_task(self, task: Task, delete_callback):
        task_item = QListWidgetItem()
        task_widget = TaskWidget(task, delete_callback)
        task_item.setSizeHint(task_widget.sizeHint())
        self.addItem(task_item)
        self.setItemWidget(task_item, task_widget)

    def remove_task(self, task: Task):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget and widget._task.title == task.title:
                self.takeItem(i)
                break


class TaskDetailsWindow(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Details for: {task.title}")

        self.layout = QVBoxLayout()

        # Display the task details
        self.task_title_label = QLabel(f"Title: {task.title}")
        self.deadline_label = QLabel(
            f"Deadline: {task.deadline if task.deadline else 'Not Set'}"
        )
        self.location_label = QLabel(
            f"Location: {task.location if task.location else 'Not Set'}"
        )
        self.url_label = QLabel(f"URL: {task.url if task.url else 'Not Set'}")

        self.layout.addWidget(self.task_title_label)
        self.layout.addWidget(self.deadline_label)
        self.layout.addWidget(self.location_label)
        self.layout.addWidget(self.url_label)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Your To-Do List")
        self.setGeometry(300, 300, 300, 400)

        # Initialize TaskManager
        self._task_manager = TaskManager("data/tasks.db")

        # Load tasks from the database
        self.tasks = self._task_manager.load_tasks()

        self.layout = QVBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Your new task")

        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self._add_task)

        self.task_list = QListWidget()
        self.task_list.itemClicked.connect(self._show_task_details)

        # Add widgets to the layout
        widgets = [self.input_field, self.add_button, self.task_list]
        for widget in widgets:
            self.layout.addWidget(widget)

        self.setLayout(self.layout)
        self._load_tasks()

    def _load_tasks(self):
        self.task_list.clear()  # Clear the existing items before loading the tasks
        for task in self.tasks:
            item = QListWidgetItem(task.title)  # Only show title in the list
            self.task_list.addItem(item)

    def _add_task(self):
        task_title = self.input_field.text()
        if task_title:
            new_task = Task(task_title)
            self._task_manager.save_task(new_task)
            self.tasks.append(new_task)
            self._load_tasks()
            self.input_field.clear()

    def _show_task_details(self, item):
        task_name = item.text()  # Get the clicked task's title
        task = self._get_task_by_title(
            task_name
        )  # Fetch full task details from the list
        if task:
            # Open a new window to show task details
            self._open_task_details_window(task)

    def _get_task_by_title(self, title):
        for task in self.tasks:
            if task.title == title:
                return task
        return None

    def _open_task_details_window(self, task):
        details_window = TaskDetailsWindow(task)
        details_window.exec()
