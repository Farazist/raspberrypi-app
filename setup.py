from io import BytesIO
import os
import sys
from pygame import mixer
from functools import partial
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QGridLayout

from database import DataBase

__author__ = "Sara Zarei, Sajjad Aemmi"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__email__ = "sajjadaemmi@gmail.com"
__status__ = "Production"

SERVER_ERROR_MESSAGE = 'خطا در برقراری ارتباط با اینترنت'
SIGNIN_ERROR_MESSAGE = 'اطلاعات وارد شده درست نیست'
SUPPORT_ERROR_MESSAGE = 'لطفا با واحد پشتیبانی فرازیست تماس حاصل فرمایید'+ '\n' + '9165 689 0915'
RECYCLE_MESSAGE = 'پسماند دریافت شد'
PLEASE_WAIT_MESSAGE = 'لطفا منتظر بمانید...'
SETTING_SAVE_MESSAGE = 'تغییرات با موفقیت اعمال شد'
TRANSFER_ERROR_MESSAGE = 'خطا در تراکنش'
DEVICE_VERSION = 'ورژن {}'

stack_timer = 60000

BTN_PASS_RECOVERY_STYLE = 'font: 18pt "IRANSans";color: rgb(121, 121, 121);border: none; outline-style: none;'

class MainWindow(QWidget):
   
    def __init__(self):
        super(MainWindow, self).__init__()

        loader = QUiLoader()
        self.ui = loader.load('setup.ui', None)

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ui.btn_exit.setSizePolicy(sp_retain)
        self.ui.lbl_empty.setSizePolicy(sp_retain)
        self.ui.btn_previous.setSizePolicy(sp_retain)
        self.ui.btn_next.setSizePolicy(sp_retain)

        #signals
        self.ui.btn_exit.clicked.connect(self.exitProgram)

        self.ui.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog)
        self.ui.showMaximized()

        self.stackSystemId()

    def setButton(self, button, function=None, show=True):
        try:
            button.clicked.disconnect()
        except:
            pass
        finally:
            if function:
                button.clicked.connect(function)
        if show:
            button.show()
        else:
            button.hide()

    def stackSystemId(self):
        self.setButton(self.ui.btn_previous, show=False)
        self.setButton(self.ui.btn_next, function=self.stackBottleRecognizeMode, show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageSystemId)

    def stackBottleRecognizeMode(self):
        self.setButton(self.ui.btn_previous, function=self.stackSystemId, show=True)
        self.setButton(self.ui.btn_next, function=self.stackpageCameraPort, show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageBottleRecognizeMode)

    def stackpageCameraPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackBottleRecognizeMode, show=True)
        self.setButton(self.ui.btn_next, function=self.stackConveyorPort, show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageCameraPort)

    def stackConveyorPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackpageCameraPort, show=True)
        self.setButton(self.ui.btn_next, function=self.stackMotorPort, show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageConveyorPort)

    def stackMotorPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackConveyorPort, show=True)
        self.setButton(self.ui.btn_next, function=self.stackSensorDepthThreshold, show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageMotorPort)
    
    def stackSensorDepthThreshold(self):
        self.setButton(self.ui.btn_previous, function=self.stackMotorPort, show=True)
        self.setButton(self.ui.btn_next, function=self.stackSensorTrigPort, show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageSensorDepthThreshold)
    
    def stackSensorTrigPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackSensorDepthThreshold, show=True)
        self.setButton(self.ui.btn_next, function=self.stackSensorEchoPort, show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageSensorTrigPort)
    
    def stackSensorEchoPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackSensorTrigPort, show=True)
        self.setButton(self.ui.btn_next, function=self.stackAppVersion, show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageSensorEchoPort)
    
    def stackAppVersion(self):
        self.setButton(self.ui.btn_previous, function=self.stackSensorEchoPort, show=True)
        self.setButton(self.ui.btn_next, show=False)
        self.ui.Stack.setCurrentWidget(self.ui.pageAppVersion)

    def exitProgram(self):
        self.close()
        QApplication.quit()

if __name__ == '__main__':
    os.environ["QT_QPA_FB_FORCE_FULLSCREEN"] = "0"
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    os.environ["QT_QPA_FONTDIR"] = "fonlts"
    # os.environ["QT_QPA_PLATFORM"] = "minimalegl"
    # os.environ["ESCPOS_CAPABILITIES_FILE"] = "/usr/python-escpos/capabilities.json"

    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
