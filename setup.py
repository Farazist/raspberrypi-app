from io import BytesIO
import os
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QWidget, QSizePolicy

from database import DataBase

__author__ = "Sara Zarei, Sajjad Aemmi"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__email__ = "sajjadaemmi@gmail.com"
__status__ = "Production"

database_list = ['0' for _ in range(9)]
print(database_list)

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

    def setButton(self, button, function=None, text=None, icon=None, show=True):
        try:
            button.clicked.disconnect()
        except:
            pass
        finally:
            if function:
                button.clicked.connect(function)
        if text:
            button.setText(text)
        if icon:
            button.setIcon(QIcon(icon))
        if show:
            button.show()
        else:
            button.hide()

    def stackSystemId(self):
        self.setButton(self.ui.btn_previous, show=False)
        self.setButton(self.ui.btn_next, function=self.stackBottleRecognizeMode, text='مرحله بعد', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageSystemId)

    def stackBottleRecognizeMode(self):
        self.setButton(self.ui.btn_previous, function=self.stackSystemId, text='مرحله قبل', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_next, function=self.stackpageCameraPort, text='مرحله بعد', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageBottleRecognizeMode)

    def stackpageCameraPort(self):
        self.setButton(self.ui.btn_previous,function=self.stackBottleRecognizeMode, text='مرحله قبل', icon='images/icon/back.png',  show=True)
        self.setButton(self.ui.btn_next, function=self.stackConveyorPort, text='مرحله بعد', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageCameraPort)

    def stackConveyorPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackpageCameraPort, text='مرحله قبل', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_next, function=self.stackMotorPort, text='مرحله بعد', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageConveyorPort)

    def stackMotorPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackConveyorPort, text='مرحله قبل', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_next, function=self.stackSensorDepthThreshold, text='مرحله بعد', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageMotorPort)
    
    def stackSensorDepthThreshold(self):
        self.setButton(self.ui.btn_previous, function=self.stackMotorPort, text='مرحله قبل', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_next, function=self.stackSensorTrigPort, text='مرحله بعد', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageSensorDepthThreshold)
    
    def stackSensorTrigPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackSensorDepthThreshold, text='مرحله قبل', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_next, function=self.stackSensorEchoPort, text='مرحله بعد', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageSensorTrigPort)
    
    def stackSensorEchoPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackSensorTrigPort, text='مرحله قبل', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_next, function=self.stackAppVersion, text='مرحله بعد', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageSensorEchoPort)
    
    def stackAppVersion(self):
        self.setButton(self.ui.btn_previous, function=self.stackSensorEchoPort, text='مرحله قبل', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_next, function=self.createDataBase, text='پایان', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageAppVersion)

    def createDataBase(self):
        database_list[0] = self.ui.tb_system_id.text()
        database_list[2] = self.ui.tb_camera_port.text()
        database_list[3] = self.ui.tb_conveyor_port.text()
        database_list[4] = self.ui.tb_motor_port.text()
        database_list[5] = self.ui.tb_sensor_depth_threshold.text()
        database_list[6] = self.ui.tb_sensor_trig_port.text()
        database_list[7] = self.ui.tb_sensor_echo_port.text()
        database_list[8] = self.ui.tb_app_version.text()
        print(database_list)

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
