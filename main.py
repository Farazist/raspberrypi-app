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
from image_classifier import ImageClassifier

__author__ = "Sara Zarei, Sajjad Aemmi"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.1.0"
__email__ = "sajjadaemmi@gmail.com"
__status__ = "Production"

class MainWindow(QWidget):
   
    def __init__(self):
        super(MainWindow, self).__init__()

        loader = QUiLoader()
        self.ui = loader.load('main.ui', None)

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ui.btnLeft.setSizePolicy(sp_retain)
        self.ui.btnRight.setSizePolicy(sp_retain) 

        # signals
        self.ui.btnSetting.clicked.connect(self.stackAdminLogin)
        self.ui.btnHere.clicked.connect(self.stackSignInUserMethods)
        self.ui.btnSignInUserMobileNumber.clicked.connect(self.stackSignInUserMobileNumber)
        self.ui.btnSignInUserQrCode.clicked.connect(self.stackQRCode)
        self.ui.btnUserLogin.clicked.connect(self.signInUser)
        self.ui.btnMainMenu_1.clicked.connect(self.checkDeviceMode)
        self.ui.btnMainMenu_2.clicked.connect(self.stackWallet)
        self.ui.btnAdminLogin.clicked.connect(self.signInAdmin)
        self.ui.btnAdminPassRecovery.clicked.connect(self.adminRecovery)
        self.ui.btnPrintReceiptNo.clicked.connect(self.stackMainMenu)
        self.ui.btnPrintReceiptYes.clicked.connect(self.printReceipt)
        self.ui.btnNExitApp.clicked.connect(self.stackSetting)
        self.ui.btnYExitApp.clicked.connect(self.exit_program)
        self.ui.btnSetting1.clicked.connect(self.stackDeviceMode)
        self.ui.btnSetting5.clicked.connect(self.stackDisableDevice)
        self.ui.btnSetting2.clicked.connect(self.stackMotorPort)
        self.ui.btnSetting3.clicked.connect(self.stackSensorPort)
        self.ui.btnSetting6.clicked.connect(self.stackExitApp)

        self.ui.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog)
        self.ui.showMaximized()

        self.system_id = DataBase.select('system_id')
        self.system = Server.getSystem(self.system_id)

        self.deviceInfo = self.system['name'] + '\n' + self.system['owner']['name'] + ' ' + self.system['owner']['mobile_number']

        self.device_mode = DataBase.select('bottle_recognize_mode')
        self.categories = Server.getCategories()
        self.image_classifier = ImageClassifier()
        
        print('Startup Intormation:')
        print('Device Mode:', self.device_mode)
        print('System ID:', self.system_id)

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
        
    def signInUser(self):
        self.user = Server.signInUser(self.ui.tbUserId.text(), self.ui.tbUserPassword.text())

        if self.user != None:
            self.stackMainMenu()
        else:
            print("mobile number or password is incurrect")
            self.ui.lblErrorUser.show()

    def signOutUser(self):
        self.user = None
        self.stackStart()

    def signInAdmin(self):
        self.admin = Server.signInUser(self.ui.tbAdminUsername.text(), self.ui.tbAdminPassword.text())

        if self.admin != None:
            self.stackSetting()
        else:
            print("mobile number or password is incurrect")
            self.ui.lblErrorAdmin.setText('نام کاربری یا رمز عبور صحیح نیست')
#        if DataBase.select('username') == self.ui.tbAdminUsername.text() and DataBase.select('password') == self.ui.tbAdminPassword.text():
#            self.stackSetting()
#        else:
#            self.ui.lblErrorAdmin.setText('نام کاربری یا رمز عبور صحیح نیست')

    def adminRecovery(self):
        self.ui.lblErrorAdmin.setText('لطفا با واحد پشتیبانی فرازیست تماس حاصل فرمایید'+ '\n' + '9165 689 0915')

    def detectItem(self): 

        try:
            import picamera
            
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

        self.ui.lblDeviceInfo.setText(self.deviceInfo)
        self.ui.tbAdminUsername.setText('')
        self.ui.tbAdminPassword.setText('')
        self.ui.lblErrorAdmin.setText('')

        gif_start = QMovie("animations/return.gif")
        self.ui.lblGifStart.setMovie(gif_start)
        # self.ui.btnGifStart.setMovie(gif_start)
        gif_start.start()


        self.ui.StackSetting.setCurrentIndex(0)
        self.ui.Stack.setCurrentIndex(1)

    def stackSignInUserMethods(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)

        self.qrcode_flag = False

        self.ui.Stack.setCurrentIndex(12)

    def stackSignInUserMobileNumber(self):
        self.setButton(self.ui.btnLeft, function=self.stackSignInUserMethods, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)

        self.ui.tbUserId.setText('')
        self.ui.tbUserPassword.setText('')
        self.ui.lblErrorUser.hide()

        self.ui.Stack.setCurrentIndex(2)

    def makeQRCode(self):
        while self.qrcode_flag:
            qrcode_signin_token = Server.makeQrcodeSignInToken(self.system['id'])
            qrcode_img = qrcode.make(qrcode_signin_token)
            try:
                self.ui.lblPixmapQr.setPixmap(QPixmap.fromImage(ImageQt(qrcode_img)).scaled(256, 256))
            except:
                self.ui.lblPixmapQr.setText('خطا در برقراری ارتباط')
                self.ui.lblPixmapQr.setStyleSheet('font: 32pt "IRANSans"; color: rgb(204, 0, 0);')
        
            time_end = time() + 32
            while time() < time_end:
                self.user = Server.checkQrcodeSignInToken(qrcode_signin_token)
                if self.user:
                    self.qrcode_flag = False
                    break
                sleep(5)
        
        if self.user:
            self.stackMainMenu()

    def stackQRCode(self):
        self.setButton(self.ui.btnLeft, function=self.stackSignInUserMethods, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)

        self.qrcode_flag = True
        self.qrcode_thread = Thread(target=self.makeQRCode)
        self.qrcode_thread.start()
        
        self.ui.Stack.setCurrentIndex(8)

    def stackMainMenu(self):
        self.setButton(self.ui.btnLeft, function=self.signOutUser, text='خروج', icon='images/icon/log-out.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        
        self.ui.lblDeviceInfo.setText(self.user['name'])

        self.ui.Stack.setCurrentIndex(3)

    def stackAdminLogin(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        
        self.ui.tbAdminUsername.setText('')
        self.ui.tbAdminPassword.setText('')
        self.ui.lblErrorAdmin.setText('')

        self.ui.Stack.setCurrentIndex(4)

    def stackWallet(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)

        gif_wallet = QMovie("animations/wallet.gif")
        gif_wallet.setScaledSize(QSize().scaled(256, 256, Qt.KeepAspectRatio))
        self.ui.lblGifWallet.setMovie(gif_wallet)
        gif_wallet.start()

        self.ui.lblWallet.setText(str(self.user['wallet']))

        self.ui.Stack.setCurrentIndex(5)

    def stackDeliveryItems(self):
        self.ui.btnLeft.hide()
        self.ui.btnRight.hide()

        self.ui.lblPixmapCategory1.setPixmap(QPixmap("images/item/category1.png").scaledToHeight(128))
        self.ui.lblPixmapCategory2.setPixmap(QPixmap("images/item/category2.png").scaledToHeight(128))
        self.ui.lblPixmapCategory3.setPixmap(QPixmap("images/item/category3.png").scaledToHeight(128))
        self.ui.lblPixmapCategory4.setPixmap(QPixmap("images/item/category4.png").scaledToHeight(128))   

        # self.detect_thread = Thread(target=self.detectItem)
        # self.detect_thread.start()

        self.ui.Stack.setCurrentIndex(6)

    def SelectItem(self, item):
        self.selected_item = item
        self.selected_item['text'] = item['text'].replace('\n', ' ')
        self.ui.lblSelectedItemName.setText(self.selected_item['text'])
        self.ui.lblUnit.setText(str(self.selected_item['price']))
        self.ui.lblSelectedItemCount.setText(str(self.selected_item['count']))
        
    def recycleItem(self):
        self.ui.lblRecycledDone.show()
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
        self.ui.lblRecycledDone.hide()

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
        self.setButton(self.ui.btnRight, function=self.stackAfterDelivery, text='پایان', icon='images/icon/tick.png', show=True)
        self.setButton(self.ui.btnRecycleItem, function=self.recycleItem)
     
        self.ui.lblRecycledDone.hide()

        self.user_items = []

        self.deliveryButtons = [
                    [
                        {'text': 'بطری\nشیشه ای','function': self.SelectItem, 'price': 150},
                        {'text': 'بطری پت\nشفاف ۵۰۰','function': self.SelectItem, 'price': 300},
                        {'text': 'بطری پت\nشفاف ۱۵۰۰','function': self.SelectItem, 'price': 200}
                    ],
                    [
                        {'text': 'بطری\nآلومینومی ۲۳۰','function': self.SelectItem, 'price': 50},
                        {'text': 'بطری پت\nرنگی ۵۰۰','function': self.SelectItem, 'price': 250},
                        {'text': 'بطری پت\nرنگی ۱۵۰۰','function': self.SelectItem, 'price': 150}
                    ],
                    [
                        {'text': 'بطری\nفلزی','function': self.SelectItem, 'price': 450},
                        {'text': 'بطری پلی اتیلن\n۵۰۰','function': self.SelectItem, 'price': 550},
                        {'text': 'بطری پلی اتیلن\n۱۵۰۰','function': self.SelectItem, 'price': 350}
                    ]
                ]

        self.layout_FArea = QGridLayout()

        for i in range(3):
            for j in range(3):
                btn = QPushButton()
                self.deliveryButtons[i][j]['count'] = 0
                btn.setText(self.deliveryButtons[i][j]['text'])
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setFixedSize(230, 150)
                btn.setStyleSheet('QPushButton:pressed { background-color: #9caf9f } QPushButton{ background-color: #ffffff} QPushButton{ border: 3px solid #184d26} QPushButton{ border-radius: 30px} QPushButton{ font: 24pt "IRANSans"} QPushButton{ font: 24pt "IRANSansFaNum"} QPushButton{ color: #000000}')
                if self.deliveryButtons[i][j]['function']:
                    btn.clicked.connect(partial(self.deliveryButtons[i][j]['function'], self.deliveryButtons[i][j]))
                self.layout_FArea.addWidget(btn, i, j)

        self.SelectItem(self.deliveryButtons[0][0])
        
        self.ui.FrameDelivery.setLayout(self.layout_FArea)

        self.ui.Stack.setCurrentIndex(9)

        try:
            self.motor_port = int(DataBase.select('motor_port'))
            self.sensor_port = int(DataBase.select('sensor_port'))
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

        self.ui.Stack.setCurrentIndex(7)

    def stackDisableDevice(self):
        self.ui.btnLeft.hide()
        self.ui.btnRight.hide()

        self.ui.Stack.setCurrentIndex(10)

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

        self.ui.StackSetting.setCurrentIndex(1)

    def stackExitApp(self):
        self.ui.StackSetting.setCurrentIndex(2)

    def stackMotorPort(self):
        self.ui.tbMotorPort.setText(str(DataBase.select('motor_port')))
        self.ui.StackSetting.setCurrentIndex(3)

    def stackSensorPort(self):
        self.ui.tbSensorPort.setText(str(DataBase.select('sensor_port')))
        self.ui.StackSetting.setCurrentIndex(4)

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
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)

        self.total_price = sum(user_item['price'] * user_item['count'] for user_item in self.user_items) 
        self.ui.lblTotalPrice.setText(str(self.total_price))
        # self.delivery_items_flag = False
        
        Server.addNewDelivery(self.user, self.system['id'], self.user_items)
        Server.transferSecure(self.user, self.system['id'], self.total_price)
        self.user = Server.getUser(self.user)
       
        try:
            self.motor.off()
        except Exception as e:
            print("error:", e)
        
        self.ui.Stack.setCurrentIndex(11)

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
    window.stackStart()
    timer = QTimer()
    timer.timeout.connect(window.hideRecycleItem)
    timer.start(1000) #it's aboat 1 seconds
    sys.exit(app.exec_())
