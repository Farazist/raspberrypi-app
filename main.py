from io import BytesIO
import os
import sys
import qrcode
from pygame import mixer
from time import sleep, time
from threading import Thread, Timer, Event
from functools import partial
# from escpos.printer import Usb
from gpiozero import DistanceSensor, LED
from gpiozero.pins.native import NativeFactory
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QTimer, QDate, QTime, QSize, QThread, Signal
from PySide2.QtGui import QMovie, QPixmap, QFont, QIcon
from PySide2.QtWidgets import QApplication, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QGridLayout
from PIL.ImageQt import ImageQt

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
SIGNIN_ERROR_MESSAGE = 'اطلاعات وارد شده درست نیست'
SUPPORT_ERROR_MESSAGE = 'لطفا با واحد پشتیبانی فرازیست تماس حاصل فرمایید'+ '\n' + '9165 689 0915'
RECYCLE_MESSAGE = 'پسماند دریافت شد'
RECYCLE_END_MESSAGE = 'لطفا منتظر بمانید'
SETTING_SAVE_MESSAGE = 'تغییرات با موفقیت اعمال شد'

class QRCodeThread(QThread):
    scan_successfully_signal = Signal()

    def __init__(self):
        QThread.__init__(self)
        self.event = Event()
    
    def stop(self):
        self.event.set()

    def run(self):
        self.event = Event()
        while not self.event.isSet():
            try:
                qrcode_signin_token = Server.makeQRcodeSignInToken(window.system['id'])
                print(qrcode_signin_token)
                qrcode_img = qrcode.make(qrcode_signin_token)
                window.ui.lblPixmapQr.setPixmap(QPixmap.fromImage(ImageQt(qrcode_img)).scaled(300, 300))

                counter = 0
                while not self.event.wait(4) and counter < 4:
                    counter += 1
                    print('server request')
                    window.user = Server.checkQRcodeSignInToken(qrcode_signin_token)
                    if window.user:
                        self.stop()
            except:
                window.showNotification(SERVER_ERROR_MESSAGE)
        
        if window.user:
            print('scan successfully')
            self.scan_successfully_signal.emit()

class MainWindow(QWidget):
   
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initHardwares()

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
        #self.ui.btnHere.clicked.connect(self.stackSignInUserMethods)
        self.ui.btnHere.clicked.connect(self.stackSignInUserQRcode)
        self.ui.btnSignInUserMobileNumber.clicked.connect(self.stackSignInUserMobileNumber)
        self.ui.btnSignInUserQrCode.clicked.connect(self.stackSignInUserQRcode)
        self.ui.btnUserLogin.clicked.connect(self.signInUser)
        self.ui.btnMainMenu_1.clicked.connect(self.checkDeviceMode)
        self.ui.btnMainMenu_2.clicked.connect(self.stackWallet)
        # self.ui.btnMainMenu_3.clicked.connect(self.stackFastCharging)
        self.ui.btnOwnerLogin.clicked.connect(self.signInOwner)
        self.ui.btnOwnerPassRecovery.clicked.connect(self.ownerRecovery)
        self.ui.btnPrintReceiptNo.clicked.connect(self.stackMainMenu)
        self.ui.btnPrintReceiptYes.clicked.connect(self.printReceipt)
        self.ui.btnNExitApp.clicked.connect(self.stackSetting)
        self.ui.btnYExitApp.clicked.connect(self.exitProgram)
        self.ui.btnSettingStart.clicked.connect(self.stackStart)
        self.ui.btnSetting1.clicked.connect(self.stackDeviceMode)
        self.ui.btnSetting5.clicked.connect(self.stackConveyorPort)
        self.ui.btnSetting2.clicked.connect(self.stackMotorPort)
        self.ui.btnSetting3.clicked.connect(self.stackSensorPort)
        self.ui.btnSetting6.clicked.connect(self.stackExitApp)
        self.ui.btnSetting4.clicked.connect(self.stackAddOpetator)
        try:
            self.ui.btnMotorOn.clicked.connect(self.motor.on)
            self.ui.btnMotorOff.clicked.connect(self.motor.off)
            self.ui.btnConveyorOn.clicked.connect(self.conveyor.on)
            self.ui.btnConveyorOff.clicked.connect(self.conveyor.off)
        except Exception as e:
            print("error:", e)

        self.ui.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog)
        self.ui.showMaximized()

        self.system_id = DataBase.select('system_id')
        self.system = Server.getSystem(self.system_id)
        self.owner = None
        self.system_startup_now = True

        self.deviceInfo = self.system['name'] + '\n' + self.system['owner']['name'] + ' ' + self.system['owner']['mobile_number']

        self.device_mode = DataBase.select('bottle_recognize_mode')
        # self.categories = Server.getCategories()
        # self.image_classifier = ImageClassifier()
        self.qrcode_thread = QRCodeThread()
        self.qrcode_thread.scan_successfully_signal.connect(self.stackMainMenu)

        print('Startup Intormation:')
        print('Device Mode:', self.device_mode)
        print('System ID:', self.system['id'])

        self.stackSignInOwner()
        self.playSound('audio2')

    def initHardwares(self):
        try:
            if hasattr(self, 'motor'):
                self.motor.close()
                print("motor close")
            self.motor_port = int(DataBase.select('motor_port'))
            self.motor = LED(self.motor_port, pin_factory=factory)
            print('motor ready')
        except Exception as e:
            print("error:", e)

        try:
            if hasattr(self, 'conveyor'):
                self.conveyor.close()
                print("conveyor close")
            self.conveyor_port = int(DataBase.select('conveyor_port'))
            self.conveyor = LED(self.conveyor_port, pin_factory=factory)
            print('conveyor ready')
        except Exception as e:
            print("error:", e)
        
        try:
            if hasattr(self, 'sensor'):
                self.sensor.close()
                print("sensor close")
            sensor_trig_port = int(DataBase.select('sensor_trig_port'))
            sensor_echo_port = int(DataBase.select('sensor_echo_port'))
            sensor_depth_threshold = float(DataBase.select('sensor_depth_threshold'))
            self.sensor = DistanceSensor(sensor_trig_port, sensor_echo_port, max_distance=1, threshold_distance=sensor_depth_threshold/100, pin_factory=factory)
            self.sensor.when_in_range = self.recycleItem
            print('sensor ready')
        except Exception as e:
            print("error:", e)

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

    def playSound(self, path):
        try:
            path = os.path.join('sounds', path+'.mp3')
            if os.path.isfile(path):
                mixer.music.load(path)
                mixer.music.play()
        except Exception as e:
            print("error:", e)

    def makeGif(self):
        pngdir = 'images/slider'
        images = []
        kargs = { 'duration': 5 }
        for file_name in os.listdir(pngdir):
            if file_name.endswith('.JPG'):
                file_path = os.path.join(pngdir, file_name)
        #         images.append(imageio.imread(file_path))
        # imageio.mimsave('animations/slider1.gif', images, 'GIF', **kargs)

    def stackSignInOwner(self):
        if self.system_startup_now:
            self.setButton(self.ui.btnLeft, show=False)
        else:
            if self.user != None:
                self.user = None
            self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
            self.ui.lblDeviceInfo.setText(self.deviceInfo)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.tbOwnerUsername.setText('')
        self.ui.tbOwnerPassword.setText('')
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInOwner)
    
    def signInOwner(self):
        self.owner = Server.signInUser(int(self.ui.tbOwnerUsername.text()), int(self.ui.tbOwnerPassword.text()))
        if self.owner != None and self.owner['id'] == self.system['owner']['id']:
            if self.system_startup_now:
                # Server.turnOnSystemSMS(self.owner, self.system)
                self.system_startup_now = False
            self.stackSetting()
            self.playSound('audio2')
        else:
            print("mobile number or password is incurrect")
            self.showNotification(SIGNIN_ERROR_MESSAGE)

    def signInUser(self):
        self.user = Server.signInUser(int(self.ui.tbUserId.text()), int(self.ui.tbUserPassword.text()))
        if self.user != None:
            self.stackMainMenu()
            self.playSound('audio2')
        else:
            print("mobile number or password is incurrect")
            self.showNotification(SIGNIN_ERROR_MESSAGE)
            
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
                    stream = BytesIO()
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
        gif_start = QMovie("animations/slider1.gif")
        self.ui.lblGifStart.setMovie(gif_start)
        gif_start.start()
        self.ui.Stack.setCurrentWidget(self.ui.pageStart)

    def stackSignInUserMethods(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblNotification.hide()
        self.qrcode_thread.stop()
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserMethods)

    def stackSignInUserMobileNumber(self):
        self.setButton(self.ui.btnLeft, function=self.stackSignInUserQRcode, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.tbUserId.setText('')
        self.ui.tbUserPassword.setText('')
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserMobileNumber)

    def stackSignInUserQRcode(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        #self.qrcode_thread.stop()
        self.playSound('audio8')
        self.ui.lblNotification.hide()
        
        gif_loading = QMovie("animations/Rolling.gif")
        self.ui.lblPixmapQr.setMovie(gif_loading)
        gif_loading.start()

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

    def SelectItem(self, item, this_btn):
        self.selected_item = item
        self.selected_item['name'] = item['name']
        self.ui.lblSelectedItem.setText(self.selected_item['name'])
        self.ui.lblUnit.setText(str(self.selected_item['price']))
        self.ui.lblSelectedItemCount.setText(str(self.selected_item['count']))

        # for btn in self.layout_FArea.findChildren(QPushButton):
        #     btn.setStyleSheet('background-color: #ffffff; border: 2px solid #28a745; border-radius: 10px; outline-style: none; font: 24pt "IRANSansFaNum"')

        # this_btn.setStyleSheet('background-color: #28a745; color:#ffffff; border-radius: 10px; outline-style: none; font: 24pt "IRANSansFaNum"')
        
    def recycleItem(self):
        if hasattr(self, 'motor_off_timer'):
            self.motor_off_timer.cancel()
        self.motorOn()
        self.motor_off_timer = Timer(10.0, self.motorOff)
        self.motor_off_timer.start()

        if hasattr(self, 'conveyor_off_timer'):
            self.conveyor_off_timer.cancel()
        self.conveyorOn()
        self.conveyor_off_timer = Timer(10.0, self.conveyorOff)
        self.conveyor_off_timer.start()

        self.playSound('audio3')
        #self.showNotification(RECYCLE_MESSAGE)
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
        self.ui.datetime.setText(QDate.currentDate().toString(Qt.DefaultLocaleShortDate) + '\n' + QTime.currentTime().toString(Qt.DefaultLocaleShortDate))
        # self.ui.lblNotification.hide()

    def motorOff(self):
        try:
            self.motor.off()
            print("motor off")
        except Exception as e:
            print("error:", e)

    def conveyorOff(self):
        try:
            self.conveyor.off()
            print("conveyor off")
        except Exception as e:
            print("error:", e)

    def motorOn(self):
        try:
            self.motor.on()
            print('motor on')
        except Exception as e:
            print("error:", e)
    
    def conveyorOn(self):
        try:
            self.conveyor.on()
            print('conveyor on')
        except Exception as e:
            print("error:", e)

    def stackManualDeliveryItems(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, function=self.stackAfterDelivery, text='پایان', icon='images/icon/tick.png', show=False)
        self.setButton(self.ui.btnRecycleItem, function=self.recycleItem)
        self.playSound('audio7')
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
                btn.setStyleSheet('QPushButton:pressed {background-color: #6fdc89;border-style: inset;} QPushButton{background-color: #ffffff; border: 2px solid #28a745; border-radius: 10px; outline-style: none; font: 22pt "IRANSansFaNum"}')
                btn.setMinimumSize(250, 100)
                btn.clicked.connect(partial(self.SelectItem, self.items[i], btn))
                self.layout_FArea.addWidget(btn, row, col)
                i += 1
                if i >= len(self.items):
                    break
            row += 1
        self.SelectItem(self.items[0], self.layout_FArea.itemAt(0))
        self.ui.scrollAreaWidgetDelivery.setLayout(self.layout_FArea)
        self.ui.Stack.setCurrentWidget(self.ui.pageManualDeliveryItems)
        
    def printReceipt(self):
        self.playSound('audio4')
        os.system('sudo python3 printer.py ' 
        + str(self.total_price)
        + ' --mobile_number ' + str(self.system['owner']['mobile_number'])
        + ' --datetime "' + QDate.currentDate().toString(Qt.DefaultLocaleShortDate) + '-' + QTime.currentTime().toString(Qt.DefaultLocaleShortDate) + '"')
        self.stackMainMenu()

    def stackAfterDelivery(self):
        self.playSound('audio5')
        self.setButton(self.ui.btnLeft, show=False)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblNotification.hide()
        gif_afterDelivery = QMovie("animations/earth.gif")
        self.ui.lblGifAfterDelivery.setMovie(gif_afterDelivery)
        gif_afterDelivery.start()

        self.total_price = sum(user_item['price'] * user_item['count'] for user_item in self.user_items) 
        self.ui.lblTotalPrice.setText(str(self.total_price))
        # self.delivery_items_flag = False
        Server.addNewDelivery(self.user, self.system['id'], self.user_items)
        if Server.transfer(self.owner, self.user, self.total_price) == "1":
            self.user['wallet'] += self.total_price
        else:
            print('not enough money in owner wallet')
        
        try:
            self.motor.off()
            self.conveyor.off()
        except Exception as e:
            print("error:", e)
        
        self.ui.Stack.setCurrentWidget(self.ui.pageAfterDelivery)

    def stackSetting(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, function=self.saveSetting, text='ذخیره', icon='images/icon/save.png', show=True)
        self.ui.lblNotification.hide()
        self.ui.lblDeviceInfo.setText(self.deviceInfo)
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
        self.ui.tb_sensor_trig_port.setText(str(DataBase.select('sensor_trig_port')))
        self.ui.tb_sensor_echo_port.setText(str(DataBase.select('sensor_echo_port')))
        self.ui.tb_sensor_depth_threshold.setText(str(DataBase.select('sensor_depth_threshold')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingSensorPort)

    def stackConveyorPort(self):
        self.ui.lblNotification.hide()
        self.ui.tbConveyorPort.setText(str(DataBase.select('conveyor_port')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingConveyorPort)

    def stackAddOpetator(self):
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingAddOperator)
    
    def stackCharity(self):
        self.ui.Stack.setCurrentWidget(self.ui.pageCharity)

    def stackProtectionOfEnvironment(self):
        self.ui.Stack.setCurrentWidget(self.ui.pageProtectionOfEnvironment)

    def stackFastCharging(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)

        self.layout_SArea_FastCharging = QGridLayout()
        for row in range(4):
            for col in range(2):
                btn = QPushButton()
                #self.items[i]['count'] = 0
                btn.setText('آهن')
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setMinimumSize(250, 100)
                btn.setStyleSheet('QPushButton:pressed { background-color: #9caf9f } QPushButton{ background-color: #ffffff} QPushButton{ border: 2px solid #28a745} QPushButton{ border-radius: 10px} QPushButton{ font: 24pt "IRANSans"} QPushButton{ font: 24pt "IRANSansFaNum"} QPushButton{ color: #000000}')
                #btn.clicked.connect(partial(self.SelectItem, self.items[i]))
                self.layout_SArea_FastCharging.addWidget(btn, row, col)
            #    i += 1
            #    if i >= len(self.items):
            #        break
            #row += 1
        #self.SelectItem(self.items[0])
        self.ui.scrollAreaWidgetFastCharging.setLayout(self.layout_SArea_FastCharging)
        self.ui.Stack.setCurrentWidget(self.ui.pageFastCharging)

    def changePredictItemFlag(self, value):
        self.predict_item_flag = value
        self.ui.lblDeliveryItems.clear()

    def saveSetting(self):
        self.showNotification(SETTING_SAVE_MESSAGE)
        if self.ui.btnManualDevice.isChecked() == True:
            result = DataBase.update('bottle_recognize_mode', 'manual')
        if self.ui.btnAutoDevice.isChecked() == True:
            result = DataBase.update('bottle_recognize_mode', 'auto')
        self.device_mode = DataBase.select('bottle_recognize_mode')
        if self.ui.tb_sensor_trig_port.text() != '':
            result = DataBase.update('sensor_trig_port', self.ui.tb_sensor_trig_port.text())
        if self.ui.tb_sensor_echo_port.text() != '':
            result = DataBase.update('sensor_echo_port', self.ui.tb_sensor_echo_port.text())
        if self.ui.tb_sensor_depth_threshold.text() != '':
            result = DataBase.update('sensor_depth_threshold', self.ui.tb_sensor_depth_threshold.text())
        if self.ui.tbMotorPort.text() != '':
            result = DataBase.update('motor_port', self.ui.tbMotorPort.text())
        if self.ui.tbConveyorPort.text() != '':
            result = DataBase.update('conveyor_port', self.ui.tbConveyorPort.text())

        self.initHardwares()

    def exitProgram(self):
        Server.turnOffSystemSMS(self.owner, self.system)
        self.delivery_items_flag = False
        self.close()
        QApplication.quit()

if __name__ == '__main__':
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    # os.environ["ESCPOS_CAPABILITIES_FILE"] = "/home/pi/Documents/capabilities.json"
    mixer.init()
    try:
        factory = NativeFactory()
    except Exception as e:
        print("error:", e)

    app = QApplication(sys.argv)
    window = MainWindow()
    timer = QTimer()
    timer.timeout.connect(window.hideRecycleItem)
    timer.start(1000) #it's aboat 1 seconds
    app.exec_()
