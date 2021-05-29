import os.path
import sys
from time import sleep
from winreg import ConnectRegistry, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, HKEY_CLASSES_ROOT, HKEY_USERS, \
    HKEY_CURRENT_CONFIG, OpenKey, QueryValueEx

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from views.dashboard import Ui_DashboardLayout
from views.deepscan import Ui_DeepScanLayout
from views.quickscan import Ui_QuickScanLayout, readJsonData


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_DashboardLayout()
        self.ui.setupUi(self)
        self.ui.btnQuickScan.clicked.connect(self.displayQuickScanLayout)
        self.ui.btnDeepScan.clicked.connect(self.displayDeepScanProgress)

    def displayQuickScanLayout(self):
        self.main = QuickScan()
        self.main.show()
        self.close()

    def displayDeepScanProgress(self):
        self.main = DeepScan()
        self.main.show()
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
        self.main = Main()
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
                            	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgb(247, 193, 131), stop:{STOP_2} rgb(247, 147, 30));
                            }
                            """
            progress = (100 - value) / 100.0
            stop_1 = str(progress - 0.001)
            stop_2 = str(progress)

            # SET VALUES TO NEW STYLESHEET
            newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)

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
        return True
    except Exception as e:
        print(e)
        return False


class DeepScanThread(QtCore.QThread):
    progressValue = QtCore.pyqtSignal(int)
    amount_detect = QtCore.pyqtSignal(int)
    done = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super(DeepScanThread, self).__init__(parent)
        self.guess = 0
        self.pause = False
        self.killed = False

    def run(self):
        count = 0
        detect = 0
        database = readJsonData("database/data.json")
        for data in database:
            count += 1
            for fileName in data['file_created']:
                if checkFileExist(fileName):
                    self.guess += 1

            for registryPath in data['hkey_created']:
                if checkRegisreyExist(registryPath):
                    self.guess += 1

            if self.guess > 0:
                detect += 1

            self.progressValue.emit(int((count / len(database)) * 100))
            self.amount_detect.emit(detect)

            if count == len(database):
                self.done.emit(True)
            else:
                self.done.emit(False)

            sleep(1)

            if self.pause:
                while self.pause: continue
            elif self.killed:
                return
            else:
                continue


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec())
