import json
import os.path
import sys
import time
from time import sleep
from winreg import ConnectRegistry, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, HKEY_CLASSES_ROOT, HKEY_USERS, \
    HKEY_CURRENT_CONFIG, OpenKey, QueryValueEx, KEY_ALL_ACCESS, DeleteValue

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QAbstractScrollArea, QHeaderView, QMessageBox

from views.dashboard import Ui_DashboardLayout
from views.deepscan import Ui_DeepScanLayout
from views.history import Ui_HistoryLayout
from views.quickscan import Ui_QuickScanLayout, readJsonData

PRIMARY_COLOR = V_COLOR = '#c82032'
K_COLOR = '#f7961e'
U_COLOR = '#374f8a'


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_DashboardLayout()
        self.ui.setupUi(self)
        self.ui.btnQuickScan.clicked.connect(self.displayQuickScanLayout)
        self.ui.btnDeepScan.clicked.connect(self.displayDeepScanProgress)
        self.ui.btnHistory.clicked.connect(self.displayHistoryDialog)

    def displayQuickScanLayout(self):
        self.main = QuickScan()
        self.main.show()
        self.close()

    def displayDeepScanProgress(self):
        self.main = DeepScan()
        self.main.show()
        self.close()

    def displayHistoryDialog(self):
        self.history = History()
        self.history.show()
        self.close()


class QuickScan(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_QuickScanLayout()
        self.ui.setupUi(self)
        self.ui.btnHome.clicked.connect(self.backDashboard)

    def backDashboard(self):
        self.main = Main()
        self.main.show()
        self.close()


class DeepScan(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_DeepScanLayout()
        self.ui.setupUi(self)
        self.progressing(0)
        self.ui.btnHome.clicked.connect(self.backDashboard)
        self.ui.btnCancel.clicked.connect(self.cancelDeepScan)
        self.ui.btnPause.clicked.connect(self.controlDeepScan)
        self.deepScanThread = DeepScanThread()
        self.deepScanThread.start()
        self.deepScanThread.progressValue.connect(self.progressing)
        self.deepScanThread.amount_detect.connect(self.showAmountDetected)
        self.deepScanThread.done.connect(self.finishDeepScanning)

    def showAmountDetected(self, amount):
        self.ui.lbDetected.setText("Detected: " + str(amount))

    def cancelDeepScan(self):
        self.deepScanThread.killed = True
        self.ui.lbScanning.setText('Cancelled')

    def controlDeepScan(self):
        if self.ui.btnPause.isChecked():
            self.deepScanThread.pause = True
            self.ui.btnPause.setText('Resume')
            self.ui.lbScanning.setText('Pausing...')
        else:
            self.deepScanThread.pause = False
            self.ui.btnPause.setText('Pause')
            self.ui.lbScanning.setText('Scanning...')

    def backDashboard(self):
        self.main = Main()
        self.main.show()
        self.close()

    def progressing(self, value):
        try:
            percentHtml = """<html><head/><body><p>{VALUE}<span style=" font-size:58pt; vertical-align:super;">%</span></p></body></html>"""
            percent = percentHtml.replace("{VALUE}", str(value))
            self.ui.lbPercentage.setText(percent)
            # PROGRESSBAR STYLESHEET BASE
            styleSheet = """
                            QFrame{
                            	border-radius: 150px;
                            	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgb(247, 193, 131), stop:{STOP_2} #f7961e);
                            }
                            """
            progress = (100 - value) / 100.0
            stop_1 = str(progress - 0.001)
            stop_2 = str(progress)

            # SET VALUES TO NEW STYLESHEET
            newStylesheet = styleSheet.replace(
                "{STOP_1}", stop_1).replace("{STOP_2}", stop_2)

            # APPLY STYLESHEET WITH NEW VALUES
            self.ui.circularProgress.setStyleSheet(newStylesheet)
        except Exception as e:
            print(e)

    def finishDeepScanning(self, done):
        if done:
            self.ui.btnPause.setDisabled(True)
            self.ui.btnCancel.setDisabled(True)
            self.ui.lbScanning.setText('Finished')
        else:
            self.ui.btnPause.setEnabled(True)
            self.ui.btnCancel.setEnabled(True)


def checkFileExist(filePath):
    return os.path.isfile(filePath)


def checkRegisreyExist(registryPath):
    try:
        registry = None
        first = registryPath.find('\\')
        rootPath = registryPath[:first]
        registryPath = registryPath[(first + 1):]

        last = registryPath.rfind('\\')
        key = registryPath[(last + 1):]
        registryPath = registryPath[:last]

        if rootPath == 'HKEY_LOCAL_MACHINE':
            registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        elif rootPath == 'HKEY_CURRENT_USER':
            registry = ConnectRegistry(None, HKEY_CURRENT_USER)
        elif rootPath == 'HKEY_CLASSES_ROOT':
            registry = ConnectRegistry(None, HKEY_CLASSES_ROOT)
        elif rootPath == 'HKEY_USERS':
            registry = ConnectRegistry(None, HKEY_USERS)
        else:
            registry = ConnectRegistry(None, HKEY_CURRENT_CONFIG)

        k = OpenKey(registry, registryPath)
        value = QueryValueEx(k, key)
        print("Registry Value: " + str(value))
        return True
    except Exception as e:
        # print(e)
        return False


def deleteRegistry(registryPath):
    try:
        first = registryPath.find('\\')
        rootPath = registryPath[:first]
        registryPath = registryPath[(first + 1):]

        last = registryPath.rfind('\\')
        key = registryPath[(last + 1):]
        registryPath = registryPath[:last]

        if rootPath == 'HKEY_LOCAL_MACHINE':
            hkey = OpenKey(HKEY_LOCAL_MACHINE, registryPath, 0, KEY_ALL_ACCESS)
        elif rootPath == 'HKEY_CURRENT_USER':
            hkey = OpenKey(HKEY_CURRENT_USER, registryPath, 0, KEY_ALL_ACCESS)
        elif rootPath == 'HKEY_CLASSES_ROOT':
            hkey = OpenKey(HKEY_CLASSES_ROOT, registryPath, 0, KEY_ALL_ACCESS)
        elif rootPath == 'HKEY_USERS':
            hkey = OpenKey(HKEY_USERS, registryPath, 0, KEY_ALL_ACCESS)
        else:
            hkey = OpenKey(HKEY_CURRENT_CONFIG,
                           registryPath, 0, KEY_ALL_ACCESS)

        DeleteValue(hkey, key)
    except Exception as e:
        print(e)


def deleteFile(filePath):
    os.remove(filePath)


def writeHistory(newData):
    try:
        with open("database/history.json", "r+") as file:
            historyLog = json.load(file)
            if time.strftime("%Y%m%d", time.localtime()) in historyLog[len(historyLog) - 1]:
                for item in newData:
                    historyLog[len(
                        historyLog) - 1][time.strftime("%Y%m%d", time.localtime())].append(item)
            else:
                todayData = json.loads(json.dumps(
                    {time.strftime("%Y%m%d", time.localtime()): newData}))
                historyLog.append(todayData)
            file.seek(0)
            json.dump(historyLog, file, indent=4)
            file.close()
    except Exception as e:
        print(e)


class DeepScanThread(QtCore.QThread):
    progressValue = QtCore.pyqtSignal(int)
    amount_detect = QtCore.pyqtSignal(int)
    done = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super(DeepScanThread, self).__init__(parent)
        self.pause = False
        self.killed = False

    def run(self):
        count = 0
        fileDetected = 0
        registryDetected = 0
        detectItem = []
        database = readJsonData("database/data.json")
        for data in database:
            count += 1
            guess = 0
            fileDetectedList = []
            registryDetectedList = []
            for fileName in data['file_created']:
                if checkFileExist(fileName):
                    fileDetected += 1
                    fileDetectedList.append(fileName)
                    # deleteFile(fileName)
                    guess += 1

            for registryPath in data['hkey_created']:
                if checkRegisreyExist(registryPath):
                    registryDetected += 1
                    registryDetectedList.append(registryPath)
                    # deleteRegistry(registryPath)
                    guess += 1
            if guess > 0:
                detectItem += [{
                    'virusName': data['name'],
                    'fileDetected': fileDetectedList,
                    'registryDetected': registryDetectedList
                }]

            self.progressValue.emit(int((count / len(database)) * 100))
            self.amount_detect.emit(fileDetected)

            if count == len(database):
                self.done.emit(True)
            else:
                self.done.emit(False)

            sleep(1)

            if self.pause:
                while self.pause:
                    continue
            elif self.killed:
                return
            else:
                continue

        if fileDetected > 0 or registryDetected > 0:
            writeHistory(detectItem)


class History(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.main = Main()
        self.ui = Ui_HistoryLayout()
        self.ui.setupUi(self)
        self.ui.tableAll.setColumnWidth(0, 150)
        self.ui.tableAll.setColumnWidth(1, 330)
        self.ui.tableAll.setColumnWidth(2, 330)
        self.ui.tableAll.setSortingEnabled(True)
        self.detected = 0

        self.ui.btnHome.clicked.connect(self.backDashboard)
        self.setTableAllData()

    def backDashboard(self):
        self.main.show()
        self.close()

    def setTableAllData(self):
        try:
            with open("database/history.json", "r+") as file:
                historyLog = json.load(file)
                self.lastDayObject = historyLog[-1]
                self.lastDayHistory = self.lastDayObject[list(
                    self.lastDayObject.keys())[0]]
                print(self.lastDayHistory)
                row = 0
                self.ui.tableAll.setRowCount(len(self.lastDayHistory))
                self.ui.tableAll.cellClicked.connect(self.detail)
                fileDetectedData = ''
                registryDetectedData = ''
                for model in self.lastDayHistory:
                    for file in model['fileDetected']:
                        fileDetectedData += (str(file).replace('\\',
                                             '/') + '\n')
                        self.detected += 1
                    for registry in model['registryDetected']:
                        registryDetectedData += (
                            str(registry).replace('\\', '/') + '\n')
                    self.ui.tableAll.setItem(
                        row, 0, QtWidgets.QTableWidgetItem(model['virusName']))
                    self.ui.tableAll.setItem(
                        row, 1, QtWidgets.QTableWidgetItem(fileDetectedData))
                    self.ui.tableAll.setItem(
                        row, 2, QtWidgets.QTableWidgetItem(registryDetectedData))
                    row += 1
            self.ui.lbAmountDetected.setText(str(self.detected))
            self.ui.lbAmountDeleted.setText(str(self.detected))
            for history in historyLog:
                self.ui.cbDate.addItem(list(history.keys())[0])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def detail(self, row, column):
        try:
            messages = ''
            if column == 1:
                for item in self.lastDayHistory[row]['fileDetected']:
                    messages += '- ' + str(item).replace('\\', '/') + '\n'
            elif column == 2:
                for item in self.lastDayHistory[row]['registryDetected']:
                    messages += '- ' + str(item).replace('\\', '/') + '\n'
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Details")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("views/icons/tav_logo.png"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
            msgBox.setWindowIcon(icon)
            msgBox.setText(messages)
            msgBox.exec()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec())
