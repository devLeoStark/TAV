import hashlib
import json
import os
import time

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox
import sys

from PyQt5.QtWidgets import QFileDialog

COLOR_BLACK = QColor(0, 0, 0)
COLOR_RED = QColor(255, 0, 0)
COLOR_GREEN = QColor(0, 120, 0)


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
        self.isScanning(False)
        self.btnScan.clicked.connect(self.QuickScan)

    def QuickScan(self):
        self.ClearLog()
        if self.optionFullScan.isChecked():
            path = "C:/"
            self.FullScan(path)
        else:
            if self.folderPath.text() == "":
                QMessageBox.warning(self, 'Alert', "Please choose your folder", QMessageBox.Yes, QMessageBox.Yes)
            elif not self.checkPath(self.folderPath.text()):
                QMessageBox.warning(self, 'Alert', "Folder is invalid", QMessageBox.Yes, QMessageBox.Yes)
            else:
                path = self.folderPath.text()
                self.SpecificScan(path)

    def SpecificScan(self, path):
        count = 0
        isVirus = False
        scanned_size = 0
        total_size = self.TotalSizeDirectory(path)
        database = self.ReadJsonData("database/data.json")

        self.isScanning(True)
        self.logBrowser.append("Scanning: " + path)
        self.logBrowser.append(
            ".......................................................................................")
        scanPath = path.replace('/', '\\')
        for path, directories, files in os.walk(path):
            for file in files:
                if file.endswith("exe"):
                    filePath = os.path.join(path, file)
                    fileToMD5 = self.HashFileMD5(filePath)
                    scanned_size += os.path.getsize(filePath)
                    for data in database:
                        if fileToMD5 == data["md5"]:
                            isVirus = True
                    self.LoggingProcess(filePath, isVirus)
                    self.progressBarScan.setValue((int(scanned_size / total_size)) * 100)
        self.Finish()

    def Finish(self):
        self.logBrowser.setTextColor(COLOR_BLACK)
        self.logBrowser.append("FINISH")

    def TotalSizeDirectory(self, path):
        total_size = 0
        for path, directories, files in os.walk(path):
            filePath = ""
            for file in files:
                if file.endswith("exe"):
                    total_size += os.path.getsize(os.path.join(path, file))
        return total_size

    def LoggingProcess(self, path, isVirus):
        logLine = time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime()) + ": " + path
        if not isVirus:
            self.logBrowser.setTextColor(COLOR_GREEN)
            self.logBrowser.append(logLine)
        else:
            self.logBrowser.setTextColor(COLOR_RED)
            self.logBrowser.append(logLine)

    def ReadJsonData(self, dataPath):
        with open(dataPath) as json_file:
            jsonData = json.load(json_file)
            return jsonData

    def HashFileMD5(self, file):
        md5 = hashlib.md5()
        with open(file, 'rb') as file:
            buffer = file.read()
            md5.update(buffer)
        return md5.hexdigest()

    # def Progressing(self):

    def FullScan(self, path):
        self.isScanning(True)
        self.logBrowser.append("Full Scanning: " + path)

    def enableSpecificScan(self):
        self.isScanning(False)
        self.folderPath.setVisible(True)
        self.btnChooseFolder.setVisible(True)

    def disableSpecificScan(self):
        self.isScanning(False)
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

    def checkPath(self, path):
        return os.path.exists(path)

    def EnableLogToolBar(self, boolean):
        if boolean:
            self.btnCancel.setVisible(True)
            self.btnClearLog.setVisible(True)
            self.progressBarScan.setVisible(True)
            self.btnCancel.clicked.connect(self.CancelScan)
            self.btnClearLog.clicked.connect(self.ClearLog)
        else:
            self.btnCancel.setVisible(False)
            self.btnClearLog.setVisible(False)
            self.progressBarScan.setVisible(False)

    def isScanning(self, boolean):
        if boolean:
            self.EnableLogToolBar(True)
        else:
            self.EnableLogToolBar(False)

    def CancelScan(self):
        self.isScanning(False)
        self.logBrowser.setTextColor(COLOR_BLACK)
        self.logBrowser.append("CANCELED SCAN\n")

    def ClearLog(self):
        self.logBrowser.clear()


app = QtWidgets.QApplication(sys.argv)
win = Dashboard()
win.show()
sys.exit(app.exec())
