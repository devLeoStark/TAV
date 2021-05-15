import hashlib
import json
import os
import sys
import time
from threading import Thread

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox

COLOR_BLACK = QColor(0, 0, 0)
COLOR_RED = QColor(255, 0, 0)
COLOR_GREEN = QColor(0, 120, 0)

MD5 = SHA256 = 1
SAFE = 1
VIRUS = 3


def HashFileMD5(file):
    md5 = hashlib.md5()
    with open(file, 'rb') as file:
        buffer = file.read()
        md5.update(buffer)
    return md5.hexdigest()


def HashFileSHA256(file):
    sha256 = hashlib.sha256()
    with open(file, 'rb') as file:
        buffer = file.read()
        sha256.update(buffer)
    return sha256.hexdigest()


class Dashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("views/dashboard.ui", self)
        self.btnQuickScan.clicked.connect(self.showQuickScan)

    def backToDashboard(self):
        try:
            uic.loadUi("views/dashboard.ui", self)
        except Exception as e:
            print(str(e))

    def showQuickScan(self):
        uic.loadUi("views/quickscan.ui", self)
        self.btnHome.clicked.connect(self.backToDashboard)
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
        guess = SAFE
        scanned = 0
        total = self.getNumberOfFile(path)
        self.isScanning(True)
        self.logBrowser.append("Scanning: " + path)
        self.logBrowser.append("-----------------------*****-----------------------")
        scanPath = path.replace('/', '\\')
        for path, directories, files in os.walk(scanPath):
            for file in files:
                filePath = os.path.join(path, file)
                scanned += 1
                if self.DatabaseChecking(filePath) > 0:
                    guess = VIRUS
                self.LoggingProcess(filePath, guess)
                self.progressBarScan.setValue((int(scanned / total)) * 100)
        self.Finish()

    def DatabaseChecking(self, filePath):
        level = 0
        fileToMD5 = HashFileMD5(filePath)
        fileToSHA256 = HashFileSHA256(filePath)
        database = self.ReadJsonData("database/data.json")
        for data in database:
            if fileToMD5 == data["md5"]:
                level += MD5
            if fileToSHA256 == data["sha256"]:
                level += SHA256
        return level

    def Finish(self):
        self.logBrowser.setTextColor(COLOR_BLACK)
        self.logBrowser.append("FINISH")

    def getNumberOfFile(self, path):
        amount = 0
        for path, directories, files in os.walk(path):
            for file in files:
                amount += 1
        return amount

    def LoggingProcess(self, path, guess):
        logLine = time.strftime("%Y/%m/%d - %H:%M:%S", time.localtime()) + ":  " + path
        if guess == VIRUS:
            self.logBrowser.setTextColor(COLOR_RED)
        else:
            self.logBrowser.setTextColor(COLOR_GREEN)
        self.logBrowser.append(logLine)

    def ReadJsonData(self, dataPath):
        with open(dataPath) as json_file:
            jsonData = json.load(json_file)
            return jsonData

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
        folderName = QFileDialog.getExistingDirectory(self, "Choose Folder", "C:/")
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
        self.logBrowser.append("CANCELED SCAN")

    def ClearLog(self):
        self.logBrowser.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Dashboard()
    win.show()
    sys.exit(app.exec())
