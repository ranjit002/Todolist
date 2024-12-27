from datetime import datetime

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


class MainWindow(QWidget):
    """
    Main application window integrates task management, UI components, and user interaction.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Your To-Do List")
        self.setGeometry(300, 300, 400, 500)

        self._task_manager = TaskManager("data/tasks.db")
        self._init_ui()
        self._load_tasks()

    def _init_ui(self):
        self.layout = QVBoxLayout()

        # Input fields for new tasks
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Task title")

        self.deadline_field = QLineEdit()
        self.deadline_field.setPlaceholderText("Deadline (YYYY-MM-DD HH:MM)")

        self.location_field = QLineEdit()
        self.location_field.setPlaceholderText("Location")

        self.url_field = QLineEdit()
        self.url_field.setPlaceholderText("URL")

        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self._add_task)

        self.task_list = TaskListWidget()

        # Add input fields to the layout
        for widget in [
            self.input_field,
            self.deadline_field,
            self.location_field,
            self.url_field,
            self.add_button,
            self.task_list,
        ]:
            self.layout.addWidget(widget)

        self.setLayout(self.layout)

    def _load_tasks(self):
        tasks = self._task_manager.load_tasks()
        for task in tasks:
            self.task_list.add_task(task, self._delete_task)

    def _add_task(self):
        title = self.input_field.text().strip()
        deadline_text = self.deadline_field.text().strip()
        location = self.location_field.text().strip()
        url = self.url_field.text().strip()

        if title:
            # Optional: Only parse deadline if it's provided
            deadline = None
            if deadline_text:
                try:
                    deadline = datetime.strptime(deadline_text, "%Y-%m-%d %H:%M")
                except ValueError:
                    print("Invalid deadline format")
                    return

            new_task = Task(title, deadline, location, url)
            self._task_manager.save_task(new_task)
            self.task_list.add_task(new_task, self._delete_task)

            # Clear input fields
            self.input_field.clear()
            self.deadline_field.clear()
            self.location_field.clear()
            self.url_field.clear()

    def _delete_task(self, task: Task):
        self._task_manager.delete_task(task)
        self.task_list.remove_task(task)

    def closeEvent(self, event):
        self._task_manager.close()
