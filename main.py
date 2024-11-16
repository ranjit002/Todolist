import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from my_todo_app.window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("SF Mono", 14))  # Set global font

    window = MainWindow()

    window.show()
    sys.exit(app.exec())
