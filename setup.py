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

database_list = [[None for _ in range(2)] for j in range(18)]
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
        self.ui.btn_manual_device.clicked.connect(self.deviceMode)
        self.ui.btn_auto_device.clicked.connect(self.deviceMode)

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
        self.setButton(self.ui.btn_next, function=self.stackConveyorPort, text='مرحله بعد', icon='images/icon/next.png', show=True)
        self.ui.Stack.setCurrentWidget(self.ui.pageBottleRecognizeMode)

    #def stackpageCameraPort(self):
    #    self.setButton(self.ui.btn_previous,function=self.stackBottleRecognizeMode, text='مرحله قبل', icon='images/icon/back.png',  show=True)
    #    self.setButton(self.ui.btn_next, function=self.stackConveyorPort, text='مرحله بعد', icon='images/icon/next.png', show=True)
    #    self.ui.Stack.setCurrentWidget(self.ui.pageCameraPort)

    def stackConveyorPort(self):
        self.setButton(self.ui.btn_previous, function=self.stackBottleRecognizeMode, text='مرحله قبل', icon='images/icon/back.png', show=True)
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

    def deviceMode(self):
        if self.ui.btn_manual_device.isChecked():
            database_list[1][1] = 'manual'
        elif self.ui.btn_auto_device.isChecked():
            database_list[1][1] = 'auto'

    def createDataBase(self):

        database_list[0][0] = 'system_id'
        database_list[1][0] = 'bottle_recognize_mode'

        database_list[2][0] = 'conveyor_motor_forward_port'
        database_list[3][0] = 'conveyor_motor_backward_port'
        database_list[4][0] = 'conveyor_motor_timer'

        database_list[5][0] = 'press_motor_forward_port'
        database_list[6][0] = 'press_motor_backward_port'
        database_list[7][0] = 'press_motor_timer'

        database_list[8][0] = 'separation_motor_forward_port'
        database_list[9][0] = 'separation_motor_backward_port'
        database_list[10][0] = 'separation_motor_timer'

        database_list[11][0] = 'sensor1_depth_threshold'
        database_list[12][0] = 'sensor1_trig_port'
        database_list[13][0] = 'sensor1_echo_port'

        database_list[14][0] = 'sensor2_depth_threshold'
        database_list[15][0] = 'sensor2_trig_port'
        database_list[16][0] = 'sensor2_echo_port'

        database_list[17][0] = 'app_version'


        database_list[0][1] = self.ui.tb_system_id.text()

        database_list[2][1] = self.ui.tb_conveyor_motor_forward_port.text()
        database_list[3][1] = self.ui.tb_conveyor_motor_backward_port.text()
        database_list[4][1] = self.ui.tb_conveyor_motor_timer.text()

        database_list[5][1] = self.ui.tb_press_motor_forward_port.text()
        database_list[6][1] = self.ui.tb_press_motor_backward_port.text()
        database_list[7][1] = self.ui.tb_press_motor_timer.text()

        database_list[8][1] = self.ui.tb_separation_motor_forward_port.text()
        database_list[9][1] = self.ui.tb_separation_motor_backward_port.text()
        database_list[10][1] = self.ui.tb_separation_motor_timer.text()

        database_list[11][1] = self.ui.tb_sensor1_depth_threshold.text()
        database_list[12][1] = self.ui.tb_sensor1_trig_port.text()
        database_list[13][1] = self.ui.tb_sensor1_echo_port.text()

        database_list[14][1] = self.ui.tb_sensor2_depth_threshold.text()
        database_list[15][1] = self.ui.tb_sensor2_trig_port.text()
        database_list[16][1] = self.ui.tb_sensor2_echo_port.text()

        database_list[17][1] = self.ui.tb_app_version.text()

        print(database_list)
        DataBase.createTable("CREATE TABLE IF NOT EXISTS information (name VARCHAR(255) NOT NULL, value VARCHAR(255) NOT NULL);")
        for item in database_list:
            DataBase.insert(item)

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
