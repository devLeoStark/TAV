import os

from PyQt5 import QtWidgets, uic
import sys

from PyQt5.QtWidgets import QFileDialog


class Dashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("views/dashboard.ui", self)
        self.btnQuickScan.clicked.connect(self.showQuickScan)

    def showQuickScan(self):
        uic.loadUi("views/quickscan.ui", self)
        self.btnChooseFolder.clicked.connect(self.chooseFolder)
        self.disableSpecificScan()
        self.optionSpecificScan.clicked.connect(self.enableSpecificScan)
        self.optionFullScan.clicked.connect(self.disableSpecificScan)

    def enableSpecificScan(self):
        self.folderPath.setVisible(True)
        self.btnChooseFolder.setVisible(True)

    def disableSpecificScan(self):
        self.folderPath.setVisible(False)
        self.btnChooseFolder.setVisible(False)

    def chooseFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose File", "", "All Files (*.*);; Python Files (*.py)",
                                                  options=options)

        if fileName:
            print(fileName)
            os.startfile(fileName)

    def chooseFolder(self):
        folderName = QFileDialog.getExistingDirectory(self, "Choose Folder")
        self.folderPath.setText(folderName)


app = QtWidgets.QApplication(sys.argv)
win = Dashboard()
win.show()
sys.exit(app.exec())
