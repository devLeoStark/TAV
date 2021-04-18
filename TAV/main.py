
from PyQt5 import QtWidgets, uic
import sys

class Dashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("views/dashboard.ui", self)  # Press Ctrl+F8 to toggle the breakpoint.

app = QtWidgets.QApplication([])
win = Dashboard()
win.show()
sys.exit(app.exec())
