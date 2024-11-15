import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Your To-Do List")
        self.setGeometry(100, 100, 400, 300)

        self.tasks = []

        self.layout = QVBoxLayout()

        self.input_field = QLineEdit()
        self.add_button = QPushButton("Add Task")
        self.task_list = QListWidget()

        self.input_field.setPlaceholderText("Your new task")

        widgets = [self.input_field, self.add_button, self.task_list]

        for widget in widgets:
            self.layout.addWidget(widget)

        self.add_button.clicked.connect(self.add_task)

        self.setLayout(self.layout)

    def add_task(self):
        task = self.input_field.text()

        if task:
            self.tasks.append(task)
            self.task_list.addItem(task)
            self.input_field.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set global font
    app.setFont(QFont("SF Mono", 14))
    window = ToDoApp()

    window.show()
    sys.exit(app.exec())
