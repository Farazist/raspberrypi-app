import io
import os
import sys
import qrcode
from PIL.ImageQt import ImageQt
from time import sleep, time
from threading import Thread
from functools import partial
from escpos.printer import Usb
from gpiozero import LightSensor, LED
from gpiozero.pins.native import NativeFactory
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QTimer, QDate, QTime, QSize
from PySide2.QtGui import QMovie, QPixmap, QFont, QIcon, QImage
from PySide2.QtWidgets import QApplication, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QGridLayout

from server import Server
from database import DataBase
# from image_classifier import ImageClassifier

__author__ = "Sara Zarei, Sajjad Aemmi"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.1.0"
__email__ = "sajjadaemmi@gmail.com"
__status__ = "Production"

SERVER_ERROR_MESSAGE = 'خطا در برقراری ارتباط با سرور'
SIGNIN_ERROR_MESSAGE = 'شناسه کاربری یا گذر واژه درست نیست'
SUPPORT_ERROR_MESSAGE = 'لطفا با واحد پشتیبانی فرازیست تماس حاصل فرمایید'+ '\n' + '9165 689 0915'
RECYCLE_MESSAGE = 'پسماند دریافت شد'

class MainWindow(QWidget):
   
    def __init__(self):
        super(MainWindow, self).__init__()

        loader = QUiLoader()
        self.ui = loader.load('main.ui', None)

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ui.btnLeft.setSizePolicy(sp_retain)
        self.ui.btnRight.setSizePolicy(sp_retain) 
        self.ui.lblDeviceInfo.setSizePolicy(sp_retain)
        self.ui.btnSetting.setSizePolicy(sp_retain)

        # signals
        self.ui.btnSetting.clicked.connect(self.stackSignInOwner)
        self.ui.btnHere.clicked.connect(self.stackSignInUserMethods)
        self.ui.btnSignInUserMobileNumber.clicked.connect(self.stackSignInUserMobileNumber)
        self.ui.btnSignInUserQrCode.clicked.connect(self.stackSignInUserQRcode)
        self.ui.btnUserLogin.clicked.connect(self.signInUser)
        self.ui.btnMainMenu_1.clicked.connect(self.checkDeviceMode)
        self.ui.btnMainMenu_2.clicked.connect(self.stackWallet)
        #self.ui.btnMainMenu_3.clicked.connect(self.stackFastCharging)
        self.ui.btnOwnerLogin.clicked.connect(self.signInOwner)
        self.ui.btnOwnerPassRecovery.clicked.connect(self.ownerRecovery)
        self.ui.btnPrintReceiptNo.clicked.connect(self.stackMainMenu)
        self.ui.btnPrintReceiptYes.clicked.connect(self.printReceipt)
        self.ui.btnNExitApp.clicked.connect(self.stackSetting)
        self.ui.btnYExitApp.clicked.connect(self.exit_program)
        self.ui.btnSettingStart.clicked.connect(self.stackStart)
        self.ui.btnSetting1.clicked.connect(self.stackDeviceMode)
        self.ui.btnSetting5.clicked.connect(self.stackConveyorPort)
        self.ui.btnSetting2.clicked.connect(self.stackMotorPort)
        self.ui.btnSetting3.clicked.connect(self.stackSensorPort)
        self.ui.btnSetting6.clicked.connect(self.stackExitApp)

        self.ui.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog)
        self.ui.showMaximized()

        self.system_id = DataBase.select('system_id')
        self.system = Server.getSystem(self.system_id)
        self.owner = None

        self.deviceInfo = self.system['name'] + '\n' + self.system['owner']['name'] + ' ' + self.system['owner']['mobile_number']

        self.device_mode = DataBase.select('bottle_recognize_mode')
        self.categories = Server.getCategories()
        # self.image_classifier = ImageClassifier()
        
        print('Startup Intormation:')
        print('Device Mode:', self.device_mode)
        print('System ID:', self.system['id'])

        self.stackSignInOwner()

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

    def showNotification(self, text):
        self.ui.lblNotification.setText(text)
        self.ui.lblNotification.show()

    def stackSignInOwner(self):
        if self.owner == None:
            self.setButton(self.ui.btnLeft, show=False)
        else:
            self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.tbOwnerUsername.setText('')
        self.ui.tbOwnerPassword.setText('')
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInOwner)
    
    def signInOwner(self):
        self.owner = Server.signInUser(self.ui.tbOwnerUsername.text(), self.ui.tbOwnerPassword.text())
        if self.owner != None and self.owner['id'] == self.system['owner']['id']:
            self.stackSetting()
        else:
            print("mobile number or password is incurrect")
            self.showNotification(SIGNIN_ERROR_MESSAGE)
#        if DataBase.select('username') == self.ui.tbOwnerUsername.text() and DataBase.select('password') == self.ui.tbOwnerPassword.text():
#            self.stackSetting()
#        else:
#            self.ui.lblErrorOwner.setText('نام کاربری یا رمز عبور صحیح نیست')
    
    def signInUser(self):
        self.user = Server.signInUser(self.ui.tbUserId.text(), self.ui.tbUserPassword.text())
        if self.user != None:
            self.stackMainMenu()
        else:
            print("mobile number or password is incurrect")
            
    def signOutUser(self):
        self.user = None
        self.stackStart()

    def ownerRecovery(self):
        self.showNotification(SUPPORT_ERROR_MESSAGE)

    def detectItem(self): 
        try:
            # import picamera
            with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera: 
                camera.start_preview()
                try:
                    stream = io.BytesIO()
                    for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                        stream.seek(0)
                        results = self.image_classifier(stream)
                        label_id, prob = results[0]
                        stream.seek(0)
                        stream.truncate()
                finally:
                    camera.stop_preview()
        except Exception as e:
                print("error:", e)

    def stackStart(self):
        self.setButton(self.ui.btnLeft, show=False)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblNotification.hide()
        self.ui.lblDeviceInfo.setText(self.deviceInfo)
        self.ui.tbOwnerUsername.setText('')
        self.ui.tbOwnerPassword.setText('')
        gif_start = QMovie("animations/return.gif")
        self.ui.lblGifStart.setMovie(gif_start)
        # self.ui.btnGifStart.setMovie(gif_start)
        gif_start.start()
        self.ui.Stack.setCurrentWidget(self.ui.pageStart)

    def stackSignInUserMethods(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.qrcode_flag = False
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserMethods)

    def stackSignInUserMobileNumber(self):
        self.setButton(self.ui.btnLeft, function=self.stackSignInUserMethods, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.tbUserId.setText('')
        self.ui.tbUserPassword.setText('')
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserMobileNumber)

    def makeQRcode(self):
        gif_loading = QMovie("animations/Rolling.gif")
        self.ui.lblPixmapQr.setMovie(gif_loading)
        gif_loading.start()
        while self.qrcode_flag:
            try:
                qrcode_signin_token = Server.makeQRcodeSignInToken(self.system['id'])
                qrcode_img = qrcode.make(qrcode_signin_token)
                self.ui.lblPixmapQr.setPixmap(QPixmap.fromImage(ImageQt(qrcode_img)).scaled(256, 256))
            except:
                self.showNotification(SERVER_ERROR_MESSAGE)

            time_end = time() + 32
            while time() < time_end:
                self.user = Server.checkQRcodeSignInToken(qrcode_signin_token)
                if self.user:
                    self.qrcode_flag = False
                    break
                sleep(5)
        if self.user:
            self.stackMainMenu()

    def stackSignInUserQRcode(self):
        self.setButton(self.ui.btnLeft, function=self.stackSignInUserMethods, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblNotification.hide()
        self.qrcode_flag = True
        self.qrcode_thread = Thread(target=self.makeQRcode)
        self.qrcode_thread.start()
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserQRcode)

    def stackMainMenu(self):
        self.setButton(self.ui.btnLeft, function=self.signOutUser, text='خروج', icon='images/icon/log-out.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblNotification.hide()
        self.ui.lblDeviceInfo.setText(self.user['name'] + '\nخوش آمدید')
        self.ui.Stack.setCurrentWidget(self.ui.pageMainMenu)

    def stackWallet(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblNotification.hide()
        gif_wallet = QMovie("animations/wallet.gif")
        gif_wallet.setScaledSize(QSize().scaled(256, 256, Qt.KeepAspectRatio))
        self.ui.lblGifWallet.setMovie(gif_wallet)
        gif_wallet.start()
        self.ui.lblWallet.setText(str(self.user['wallet']))
        self.ui.Stack.setCurrentWidget(self.ui.pageWallet)

    def stackDeliveryItems(self):
        self.ui.btnLeft.hide()
        self.ui.btnRight.hide()
        self.ui.lblNotification.hide()
        self.ui.lblPixmapCategory1.setPixmap(QPixmap("images/item/category1.png").scaledToHeight(128))
        self.ui.lblPixmapCategory2.setPixmap(QPixmap("images/item/category2.png").scaledToHeight(128))
        self.ui.lblPixmapCategory3.setPixmap(QPixmap("images/item/category3.png").scaledToHeight(128))
        self.ui.lblPixmapCategory4.setPixmap(QPixmap("images/item/category4.png").scaledToHeight(128))   
        # self.detect_thread = Thread(target=self.detectItem)
        # self.detect_thread.start()
        self.ui.Stack.setCurrentWidget(self.ui.pageDeliveryItems)

    def SelectItem(self, item):
        self.selected_item = item
        self.selected_item['name'] = item['name']
        self.ui.lblUnit.setText(str(self.selected_item['price']))
        self.ui.lblSelectedItemCount.setText(str(self.selected_item['count']))
        
    def recycleItem(self):
        self.showNotification(RECYCLE_MESSAGE)
        self.ui.btnRight.show()
        self.selected_item['count'] += 1
        self.ui.lblSelectedItemCount.setText(str(self.selected_item['count']))
        for user_item in self.user_items:
            if self.selected_item['id'] == user_item['id']:
                break
        else:
            self.user_items.append(self.selected_item)
        self.total_price = sum(user_item['price'] * user_item['count'] for user_item in self.user_items)
        self.ui.lblTotal.setText(str(self.total_price))

    def hideRecycleItem(self):
        self.ui.datetime.setText(QDate.currentDate().toString(Qt.DefaultLocaleLongDate) + '\n' + QTime.currentTime().toString(Qt.DefaultLocaleLongDate))
        self.ui.lblNotification.hide()

    def sensorTest(self):
        try:
            while True:
                self.sensor.wait_for_light()
                print("bottle detected!")
                self.sensor.wait_for_dark()
                sleep(1)
        except Exception as e:
            print("error:", e)

    def stackManualDeliveryItems(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, function=self.stackAfterDelivery, text='پایان', icon='images/icon/tick.png', show=False)
        self.setButton(self.ui.btnRecycleItem, function=self.recycleItem)
        self.ui.lblTotal.setText("0")
        self.ui.lblRecycledDone.hide()
        self.items = Server.getItems(self.owner['id'])
        self.user_items = []
        self.layout_FArea = QGridLayout()
        i = 0
        row = 0
        while row < len(self.items) // 2:
            for col in range(2):
                btn = QPushButton()
                self.items[i]['count'] = 0
                btn.setText(self.items[i]['name'])
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setMinimumSize(250, 100)
                btn.setStyleSheet('QPushButton:pressed { background-color: #9caf9f } QPushButton{ background-color: #ffffff} QPushButton{ border: 2px solid #28a745} QPushButton{ border-radius: 10px} QPushButton{ font: 24pt "IRANSans"} QPushButton{ font: 24pt "IRANSansFaNum"} QPushButton{ color: #000000}')
                btn.clicked.connect(partial(self.SelectItem, self.items[i]))
                self.layout_FArea.addWidget(btn, row, col)
                i += 1
                if i >= len(self.items):
                    break
            row += 1
        self.SelectItem(self.items[0])
        self.ui.scrollAreaWidgetDelivery.setLayout(self.layout_FArea)
        self.ui.Stack.setCurrentWidget(self.ui.pageManualDeliveryItems)
        try:
            self.motor_port = int(DataBase.select('motor_port'))
            self.sensor_port = int(DataBase.select('sensor_port'))
            self.conveyor_port = int(DataBase.select('conveyor_port'))
            self.motor = LED(self.motor_port, pin_factory=factory)
            self.sensor = LightSensor(self.sensor_port, pin_factory=factory)
            print('motor on')
            self.motor.on()
        except Exception as e:
            print("error:", e)
        self.sensorTest_thread = Thread(target=self.sensorTest)
        self.sensorTest_thread.start()

    def stackSetting(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, function=self.saveSetting, text='ذخیره', icon='images/icon/save.png', show=True)
        self.ui.lblNotification.hide()
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingEmpty)
        self.ui.Stack.setCurrentWidget(self.ui.pageSetting)

    def stackDisableDevice(self):
        self.ui.btnLeft.hide()
        self.ui.btnRight.hide()
        self.ui.lblNotification.hide()
        self.ui.Stack.setCurrentWidget(self.ui.pageDisableDevice)

    def checkDeviceMode(self):
        if self.device_mode == 'manual':
            self.stackManualDeliveryItems()
        elif self.device_mode == 'auto':
            self.stackDeliveryItems()
    
    def stackDeviceMode(self):
        result = DataBase.select('bottle_recognize_mode')
        if result == 'manual':
            self.ui.btnManualDevice.setChecked(True)
        elif result == 'auto':
            self.ui.btnAutoDevice.setChecked(True)
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingDeviceMode)

    def stackExitApp(self):
        self.ui.lblNotification.hide()
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingExit)

    def stackMotorPort(self):
        self.ui.lblNotification.hide()
        self.ui.tbMotorPort.setText(str(DataBase.select('motor_port')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingMotorPort)

    def stackSensorPort(self):
        self.ui.lblNotification.hide()
        self.ui.tbSensorPort.setText(str(DataBase.select('sensor_port')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingSensorPort)

    def stackConveyorPort(self):
        self.ui.lblNotification.hide()
        self.ui.tbConveyorPort.setText(str(DataBase.select('conveyor_port')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingConveyorPort)

    def printReceipt(self):
        try:
            print("printing...")
            printer = Usb(idVendor=0x0416, idProduct=0x5011, timeout=0, in_ep=0x81, out_ep=0x03)
            printer.image("images/logo-small.png")
            printer.set(align=u'center')
            printer.text("Farazist\n")
            printer.text(str(self.total_price) + " Rial")
            # printer.barcode('1324354657687', 'EAN13', 64, 2, '', '')
            # printer.qr('content', ec=0, size=3, model=2, native=False, center=False, impl=u'bitImageRaster')
            printer.text(self.system['owner']['mobile_number'])
            printer.text("farazist.ir\n")
            printer.cut()
        except Exception as e:
                print("error:", e)
        self.stackMainMenu()

    def stackAfterDelivery(self):
        #self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnLeft, show=False)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblNotification.hide()
        self.total_price = sum(user_item['price'] * user_item['count'] for user_item in self.user_items) 
        self.ui.lblTotalPrice.setText(str(self.total_price))
        # self.delivery_items_flag = False
        Server.addNewDelivery(self.user, self.system['id'], self.user_items)
        Server.transfer(self.owner, self.user, self.total_price)
        self.user['wallet'] += self.total_price
        try:
            self.motor.off()
        except Exception as e:
            print("error:", e)
        self.ui.Stack.setCurrentWidget(self.ui.pageAfterDelivery)

    def stackCharity(self):
        self.ui.Stack.setCurrentWidget(self.ui.pageCharity)

    def stackProtectionOfEnvironment(self):
        self.ui.Stack.setCurrentWidget(self.ui.pageProtectionOfEnvironment)

    def stackFastCharging(self):
        self.ui.Stack.setCurrentWidget(self.ui.pageBuildingCharge)

    def changePredictItemFlag(self, value):
        self.predict_item_flag = value
        self.ui.lblDeliveryItems.clear()

    def saveSetting(self):
        if self.ui.btnManualDevice.isChecked() == True:
            result = DataBase.update('bottle_recognize_mode', 'manual')
        if self.ui.btnAutoDevice.isChecked() == True:
            result = DataBase.update('bottle_recognize_mode', 'auto')
        self.device_mode = DataBase.select('bottle_recognize_mode')
        if self.ui.tbSensorPort.text() != '':
            result = DataBase.update('sensor_port', self.ui.tbSensorPort.text())
        if self.ui.tbMotorPort.text() != '':
            result = DataBase.update('motor_port', self.ui.tbMotorPort.text())
        if self.ui.tbConveyorPort.text() != '':
            result = DataBase.update('conveyor_port', self.ui.tbConveyorPort.text())

    def exit_program(self):
        self.delivery_items_flag = False
        self.close()
        QApplication.quit()

if __name__ == '__main__':
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    try:
        factory = NativeFactory()
    except Exception as e:
        print("error:", e)

    app = QApplication(sys.argv)
    window = MainWindow()
    timer = QTimer()
    timer.timeout.connect(window.hideRecycleItem)
    timer.start(1000) #it's aboat 1 seconds
    sys.exit(app.exec_())
