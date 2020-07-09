from io import BytesIO
import os
import sys
import qrcode
from pygame import mixer
from time import sleep, time
from threading import Thread, Timer, Event
from functools import partial
# from escpos.printer import Usb
from gpiozero import DistanceSensor, Motor
from gpiozero.pins.native import NativeFactory
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QTimer, QDate, QTime, QSize, QThread, Signal
from PySide2.QtGui import QMovie, QPixmap, QFont, QIcon
from PySide2.QtWidgets import QApplication, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QGridLayout, QLabel
from PIL.ImageQt import ImageQt
from scipy import stats
#from mfrc522 import SimpleMFRC522

from server import Server
from database import DataBase
from custombutton import CustomButton
from image_classifier import ImageClassifier

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
DEPOSITE_TO_RFID_MESSAGE = 'انتقال به کارت با موفقیت انجام شد'
MONEY_ERROR_MESSAGE = 'موجودی شما برای انجام این تراکنش کافی نمی باشد'
DEVICE_VERSION = 'ورژن {}'

stack_timer = 240000
motor_timer = 2.0
camera_timer = 3.0
separation_motor_timer = 1.0
predict_item_threshold = 0.1

BTN_PASS_RECOVERY_STYLE = 'font: 18pt "IRANSans";color: rgb(121, 121, 121);border: none; outline-style: none;'

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

class QRCodeThread(QThread):
    scan_successfully_signal = Signal()
    show_qrcode_signal = Signal(str)

    def __init__(self):
        QThread.__init__(self)
        self.event = Event()
    
    def stop(self):
        self.event.set()

    def run(self):
        self.event = Event()
        while not self.event.isSet():
            print('make QRcode SignIn Token')
            try:
                qrcode_signin_token = Server.makeQRcodeSignInToken(window.system['id'])
                print(qrcode_signin_token)
                self.show_qrcode_signal.emit(qrcode_signin_token)
                counter = 0
                while not self.event.wait(4) and counter < 4:
                    counter += 1
                    print('check QRcode SignIn Token')
                    window.user = Server.checkQRcodeSignInToken(qrcode_signin_token)
                    if window.user:
                        self.stop()
            except:
                window.showNotification(SERVER_ERROR_MESSAGE)
        
        if hasattr(window, 'user') and window.user:
            print('scan successfully')
            window.playSound('audio2')
            self.scan_successfully_signal.emit()


class SigninOwnerThread(QThread):
    success_signal = Signal()
    
    def __init__(self):
        QThread.__init__(self)
    
    def run(self):
        try:
            window.owner = Server.signInUser(int(window.ui.tbOwnerUsername.text()), int(window.ui.tbOwnerPassword.text()))
            self.success_signal.emit()
        except:
            window.showNotification(SERVER_ERROR_MESSAGE)


class SigninUserThread(QThread):
    success_signal = Signal()
    
    def __init__(self):
        QThread.__init__(self)
    
    def run(self):
        try:
            window.user = Server.signInUser(int(window.ui.tbUserId.text()), int(window.ui.tbUserPasswordID.text()))
            self.success_signal.emit()
        except:
            window.showNotification(SERVER_ERROR_MESSAGE)


class SigninUserMobileThread(QThread):
    success_signal = Signal()
    
    def __init__(self):
        QThread.__init__(self)
    
    def run(self):
        try:
            window.user = Server.signInUser(int(window.ui.tbUserId.text()), int(window.ui.tbUserPasswordID.text()))
            self.success_signal.emit()
        except:
            window.showNotification(SERVER_ERROR_MESSAGE)


class LoadingThread(QThread):
    success_signal = Signal()
    
    def __init__(self):
        QThread.__init__(self)
    
    def run(self):
        try:
            window.system = Server.getSystem(window.system_id)
            window.deviceInfo = window.system['name'] + '\n' + window.system['owner']['name'] + ' ' + window.system['owner']['mobile_number']
            
            print('Startup Intormation:')
            print('Device Mode:', window.device_mode)
            print('System ID:', window.system['id'])

            self.success_signal.emit()
        except:
            window.showNotification(SERVER_ERROR_MESSAGE)


class AutoDeliveryItemsThread(QThread):
    success_signal = Signal()

    def __init__(self):
        QThread.__init__(self)
    
    def stop(self):
        self.delivery_item_flag = False

    def run(self):
        self.delivery_item_flag = True
        try:
            import picamera
            with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
                # camera.start_preview()
                stream = BytesIO()
                for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                    if self.delivery_item_flag:
                        stream.seek(0)
                        results = window.image_classifier(stream)
                        label_id, prob = results[0]
                        if prob > predict_item_threshold:
                            window.predicted_items.append(label_id)
                            print(label_id, prob)
                        stream.seek(0)
                        stream.truncate()
                    else:
                        break
        except Exception as e:
            print("error:", e)
     
            # category_index = self.items[most_probability_item]['category_id'] - 1
            # categories_count[category_index] += 1
            # for i in range(len(categories_count)):
            #     window.grid_widget_s4[i].setText(str(categories_count[i]))
        

class AfterDeliveryThread(QThread):
    success_signal = Signal()
    
    def __init__(self):
        QThread.__init__(self)
    
    def run(self):
        try:
            window.total_price = sum(user_item['price'] * user_item['count'] for user_item in window.user_items) 
   
            Server.addNewDelivery(window.user, window.system['id'], window.user_items)
            if Server.transfer(window.owner, window.user, window.total_price) == "1":
                window.user['wallet'] += window.total_price
                self.success_signal.emit()
            else:
                window.showNotification(TRANSFER_ERROR_MESSAGE)
        except:
            window.showNotification(SERVER_ERROR_MESSAGE)


class MainWindow(QWidget):
   
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.system_id = DataBase.select('system_id')
        self.device_version = DataBase.select('app_version')
        self.device_mode = DataBase.select('bottle_recognize_mode')
        self.initHardwares()

        loader = QUiLoader()
        self.ui = loader.load('main.ui', None)

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ui.btnLeft.setSizePolicy(sp_retain)
        self.ui.btnRight.setSizePolicy(sp_retain) 
        self.ui.lblDeviceInfo.setSizePolicy(sp_retain)
        self.ui.btnSetting.setSizePolicy(sp_retain)

        self.btnOwnerLogin = CustomButton()
        self.btnOwnerLogin.setGif("animations/Rolling-white.gif")
        self.btnOwnerPassRecovery = QPushButton('بازیابی رمز عبور')
        self.btnOwnerPassRecovery.setStyleSheet(BTN_PASS_RECOVERY_STYLE)
        self.ui.vLayoutSignInOwner.addWidget(self.btnOwnerLogin)
        self.ui.vLayoutSignInOwner.addWidget(self.btnOwnerPassRecovery)
        self.ui.vLayoutSignInOwner.setAlignment(Qt.AlignHCenter)

        self.btnUserLoginID = CustomButton()
        self.btnUserLoginID.setGif("animations/Rolling-white.gif")
        self.lbl = QLabel(None)
        self.lbl.setStyleSheet(BTN_PASS_RECOVERY_STYLE)
        self.ui.vLayoutSignInUser.addWidget(self.btnUserLoginID)
        self.ui.vLayoutSignInUser.addWidget(self.lbl)
        self.ui.vLayoutSignInUser.setAlignment(Qt.AlignHCenter)

        self.btnUserLoginMobile = CustomButton()
        self.btnUserLoginMobile.setGif("animations/Rolling-white.gif")
        self.lbl = QLabel(None)
        self.lbl.setStyleSheet(BTN_PASS_RECOVERY_STYLE)
        self.ui.vLayoutSignInUserMobile.addWidget(self.btnUserLoginMobile)
        self.ui.vLayoutSignInUserMobile.addWidget(self.lbl)
        self.ui.vLayoutSignInUserMobile.setAlignment(Qt.AlignHCenter)

        # Threads
        self.qrcode_thread = QRCodeThread()
        self.qrcode_thread.show_qrcode_signal.connect(self.showQrcode)
        self.qrcode_thread.scan_successfully_signal.connect(self.stackMainMenu)

        self.signin_owner_thread = SigninOwnerThread()
        self.signin_owner_thread.success_signal.connect(self.afterSignInOwner)

        self.signin_user_thread = SigninUserThread()
        self.signin_user_thread.success_signal.connect(self.afterSignInUser)

        self.signin_user_mobile_thread = SigninUserMobileThread()
        self.signin_user_mobile_thread.success_signal.connect(self.afterSignInUserMobile)

        self.loading_thread = LoadingThread()
        self.loading_thread.success_signal.connect(self.stackSignInOwner)
        #self.loading_thread.success_signal.connect(self.stackMainMenu)
        #self.user = Server.signInUser(105, 1234)
        #self.owner = Server.signInUser(104, 1234)

        self.auto_delivery_items_thread = AutoDeliveryItemsThread()
    
        self.after_delivery_thread = AfterDeliveryThread()
        self.after_delivery_thread.success_signal.connect(self.stackAfterDelivery)

        # signals
        self.ui.btnRefresh.clicked.connect(self.refresh)
        self.ui.btnSetting.clicked.connect(self.stackSignInOwner)
        self.ui.btnHere.clicked.connect(self.stackSignInUserMethods)
        self.ui.btnSignInUserIDNumber.clicked.connect(self.stackSignInUserIDNumber)
        self.ui.btnSignInUserMobileNumber.clicked.connect(self.stackSignInUserMobileNumber)
        self.btnUserLoginID.clicked.connect(self.signInUser)
        self.btnUserLoginMobile.clicked.connect(self.signInUserMobile)
        self.ui.btnMainMenu_1.clicked.connect(self.checkDeviceMode)
        self.ui.btnMainMenu_2.clicked.connect(self.stackWallet)
        self.ui.btnMainMenu_3.clicked.connect(self.stackFastCharging)
        self.ui.btnMainMenu_4.clicked.connect(self.stackWalletServices)
        self.btnOwnerLogin.clicked.connect(self.signInOwner)
        self.btnOwnerPassRecovery.clicked.connect(self.ownerRecovery)
        self.ui.btnPrintReceiptNo.clicked.connect(self.stackMainMenu)
        self.ui.btnPrintReceiptYes.clicked.connect(self.printReceipt)
        self.ui.btnNExitApp.clicked.connect(self.stackSetting)
        self.ui.btnYExitApp.clicked.connect(self.exitProgram)
        self.ui.btnSettingStart.clicked.connect(self.stackStart)
        self.ui.btnSetting1.clicked.connect(self.stackDeviceMode)
        self.ui.btnSetting5.clicked.connect(self.stackConveyorPort)
        self.ui.btnSetting2.clicked.connect(self.stackPressMotor)
        self.ui.btnSetting10.clicked.connect(self.stackSeparationMotor)
        self.ui.btnSetting3.clicked.connect(self.stackSensor1Ports)
        self.ui.btnSetting9.clicked.connect(self.stackSensor2Ports)
        self.ui.btnSetting6.clicked.connect(self.stackExitApp)
        self.ui.btnSetting4.clicked.connect(self.stackAddOpetator)
        self.ui.btnSetting7.clicked.connect(self.stackHelp)
        self.ui.btnSetting8.clicked.connect(self.stackLicense)
        self.ui.btnWalletServices_1.clicked.connect(self.stackChargingResidentialUnit)
        self.ui.btnWalletServices_2.clicked.connect(self.stackRFID)
        self.ui.btnWalletServices_3.clicked.connect(self.stackCharity)
        self.ui.btnWalletServices_4.clicked.connect(self.stackEnvirnmentalProtection)
        self.ui.btnPlus_charity.clicked.connect(self.plusCharity)
        self.ui.btnMinus_charity.clicked.connect(self.minusCharity)
        self.ui.btnPlus_envirnmentalProtection.clicked.connect(self.plusEnvirnment)
        self.ui.btnMinus_envirnmentalProtection.clicked.connect(self.minusEnvirnment)
        self.ui.btnPlus_RFID.clicked.connect(self.plusRFID)
        self.ui.btnMinus_RFID.clicked.connect(self.minusRFID)
        self.ui.btn_confirm_deposit_to_RFIDcard.clicked.connect(self.depositToRFIDcard)

        self.ui.btnCharity_1.clicked.connect(lambda: self.ui.lblSelectedCharity.setText(self.ui.lblCharity_1.text()))
        self.ui.btnCharity_2.clicked.connect(lambda: self.ui.lblSelectedCharity.setText(self.ui.lblCharity_2.text()))
        self.ui.btnCharity_3.clicked.connect(lambda: self.ui.lblSelectedCharity.setText(self.ui.lblCharity_3.text()))
        self.ui.btnCharity_4.clicked.connect(lambda: self.ui.lblSelectedCharity.setText(self.ui.lblCharity_4.text()))
        
        self.ui.btnEnvirnmentalProtection_1.clicked.connect(lambda: self.ui.lblSelectedEnvirnmentalProtection.setText(self.ui.lblEnvirnmentalProtection_1.text()))
        self.ui.btnEnvirnmentalProtection_2.clicked.connect(lambda: self.ui.lblSelectedEnvirnmentalProtection.setText(self.ui.lblEnvirnmentalProtection_2.text()))
        self.ui.btnEnvirnmentalProtection_3.clicked.connect(lambda: self.ui.lblSelectedEnvirnmentalProtection.setText(self.ui.lblEnvirnmentalProtection_3.text()))
        self.ui.btnEnvirnmentalProtection_4.clicked.connect(lambda: self.ui.lblSelectedEnvirnmentalProtection.setText(self.ui.lblEnvirnmentalProtection_4.text()))

        self.ui.tbOwnerUsername.textChanged.connect(self.hideNotification)
        self.ui.tbOwnerPassword.textChanged.connect(self.hideNotification)
        self.ui.tbUserId.textChanged.connect(self.hideNotification)
        self.ui.tbUserPasswordID.textChanged.connect(self.hideNotification)
        try:
            self.ui.btn_press_motor_forward_on.clicked.connect(self.motor.on)
            self.ui.btn_press_motor_off.clicked.connect(self.motor.off)
            self.ui.btn_conveyor_motor_forward_on.clicked.connect(self.conveyor.on)
            self.ui.btn_conveyor_motor_off.clicked.connect(self.conveyor.off)
        except Exception as e:
            print("error:", e)

        self.ui.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog)
        self.ui.showMaximized()
    
        self.flag_system_startup_now = True
        self.delivery_items_flag = False

        # self.categories = Server.getCategories()
        self.image_classifier = ImageClassifier()

        self.stackLoading()
        self.playSound('audio2')
        self.refresh()

    def initHardwares(self):
        try:
            if hasattr(self, 'press_motor'):
                self.press_motor.close()
                print("press motor close")
            self.press_motor_forward_port = int(DataBase.select('press_motor_forward_port'))
            self.press_motor_backward_port = int(DataBase.select('press_motor_backward_port'))
            self.press_motor = Motor(forward=self.press_motor_forward_port, backward=self.press_motor_backward_port, pin_factory=factory)
            print('press motor ready')
        except Exception as e:
            print("error:", e)

        try:
            if hasattr(self, 'separation_motor'):
                self.separation_motor.close()
                print("separation motor close")
            self.separation_motor_forward_port = int(DataBase.select('separation_motor_forward_port'))
            self.separation_motor_backward_port = int(DataBase.select('separation_motor_backward_port'))
            self.separation_motor = Motor(forward=self.separation_motor_forward_port, backward=self.separation_motor_backward_port, pin_factory=factory)
            print('separation motor ready')
        except Exception as e:
            print("error:", e)

        try:
            if hasattr(self, 'conveyor_motor'):
                self.conveyor.close()
                print("conveyor motor close")
            self.conveyor_motor_forward_port = int(DataBase.select('conveyor_motor_forward_port'))
            self.conveyor_motor_backward_port = int(DataBase.select('conveyor_motor_backward_port'))
            self.conveyor_motor = Motor(forward=self.conveyor_motor_forward_port, backward=self.conveyor_motor_backward_port, pin_factory=factory)
            print('conveyor motor ready')
        except Exception as e:
            print("error:", e)
        
        try:
            if hasattr(self, 'distance_sensor1'):
                self.distance_sensor1.close()
                print("distance sensor 1 close")
            distance_sensor1_trig_port = int(DataBase.select('distance_sensor1_trig_port'))
            distance_sensor1_echo_port = int(DataBase.select('distance_sensor1_echo_port'))
            distance_sensor1_depth_threshold = float(DataBase.select('distance_sensor1_depth_threshold'))
            self.distance_sensor1 = DistanceSensor(distance_sensor1_trig_port, distance_sensor1_echo_port, max_distance=1, threshold_distance=distance_sensor1_depth_threshold/100, pin_factory=factory)
            self.distance_sensor1.when_in_range = self.startRecycleItem
            print('distance sensor 1 ready')
        except Exception as e:
            print("error:", e)

        try:
            if hasattr(self, 'distance_sensor2'):
                self.distance_sensor2.close()
                print("distance sensor 2 close")
            distance_sensor2_trig_port = int(DataBase.select('distance_sensor2_trig_port'))
            distance_sensor2_echo_port = int(DataBase.select('distance_sensor2_echo_port'))
            distance_sensor2_depth_threshold = float(DataBase.select('distance_sensor2_depth_threshold'))
            self.distance_sensor2 = DistanceSensor(distance_sensor2_trig_port, distance_sensor2_echo_port, max_distance=1, threshold_distance=distance_sensor2_depth_threshold/100, pin_factory=factory)
            self.distance_sensor2.when_in_range = self.endRecycleItem
            print('distance sensor 2 ready')
        except Exception as e:
            print("error:", e)

        try:
            if not hasattr(self, 'rfid_sensor'):
                self.rfid_sensor = SimpleMFRC522()
                print('RFID sensor ready')
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

    def hideNotification(self):
        self.ui.lblNotification.hide()

    def playSound(self, path):
        try:
            path = os.path.join('sounds', path+'.mp3')
            if os.path.isfile(path):
                mixer.music.load(path)
                mixer.music.play()
        except Exception as e:
            print("error:", e)

    def stopSound(self):
        try:
                mixer.music.stop()
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

    def refresh(self):
        self.showNotification(PLEASE_WAIT_MESSAGE)
        self.loading_thread.start()            

    def stackLoading(self):
        self.ui.lblLogo.hide()
        self.setButton(self.ui.btnLeft, show=False)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.Stack.setCurrentWidget(self.ui.pageLoading)

    def stackSignInOwner(self):
        self.ui.lblLogo.show()
        self.qrcode_thread.stop()
        self.ui.lblNotification.hide()
        if self.flag_system_startup_now:
            self.setButton(self.ui.btnLeft, show=False)
        else:
            if hasattr(self, 'user') == True:
                self.user = None
            self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
            self.ui.lblDeviceInfo.setText(self.deviceInfo)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.tbOwnerUsername.setText('')
        self.ui.tbOwnerPassword.setText('')
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInOwner)
    
    def signInOwner(self):
        self.showNotification(PLEASE_WAIT_MESSAGE)
        self.playSound('audio8')
        self.signin_owner_thread.start()                  

    def afterSignInOwner(self):
        if self.owner != 0 and self.owner['id'] == self.system['owner']['id']: 
            try:
                if self.flag_system_startup_now:
                    if self.device_mode == 'manual':
                        self.items = Server.getItems(self.owner['id'])
                    elif self.device_mode == 'auto':
                        self.items = Server.getItems(0)

                    # Server.turnOnSystemSMS(self.owner, self.system)
                    self.flag_system_startup_now = False
                self.stackSetting()
                self.playSound('audio2')
                self.hideNotification()
            except:
                self.showNotification(SERVER_ERROR_MESSAGE)
        else:
            print("mobile number or password is incurrect")
            self.showNotification(SIGNIN_ERROR_MESSAGE)    

    def signInUser(self):
        self.showNotification(PLEASE_WAIT_MESSAGE)
        self.playSound('audio8')
        self.signin_user_thread.start()

    def afterSignInUser(self):
        if self.user != 0:
            self.ui.lblDeviceInfo.setText(self.user['name'] + '\nخوش آمدید')
            self.stackMainMenu()
            self.playSound('audio2')
        else:
            print("mobile number or password is incurrect")
            self.showNotification(SIGNIN_ERROR_MESSAGE)

    def signInUserMobile(self):
        self.showNotification(PLEASE_WAIT_MESSAGE)
        self.playSound('audio8')
        self.signin_user_mobile_thread.start()

    def afterSignInUserMobile(self):
        if self.user != 0:
            self.ui.lblDeviceInfo.setText(self.user['name'] + '\nخوش آمدید')
            self.stackMainMenu()
            self.playSound('audio2')
        else:
            print("mobile number or password is incurrect")
            self.showNotification(SIGNIN_ERROR_MESSAGE)

    def signOutUser(self):
        print('user log out')
        self.user = None
        self.stackStart()

    def ownerRecovery(self):
        self.showNotification(SUPPORT_ERROR_MESSAGE)

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
        self.qrcode_thread.stop()
        self.ui.Stack.setCurrentWidget(self.ui.pageStart)

    def stackSignInUserIDNumber(self):
        self.setButton(self.ui.btnLeft, function=self.stackSignInUserMethods, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.stopSound()
        self.ui.tbUserId.setText('')
        self.ui.tbUserPasswordID.setText('')
        self.qrcode_thread.stop()
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserIDNumber)

    def stackSignInUserMobileNumber(self):
        self.setButton(self.ui.btnLeft, function=self.stackSignInUserMethods, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.stopSound()
        self.ui.tbUserMobile.setText('')
        self.ui.tbUserPasswordMobile.setText('')
        self.qrcode_thread.stop()
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserMobileNumber)

    def stackSignInUserMethods(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.playSound('audio10')
        self.ui.lblNotification.hide()

        gif_loading = QMovie("animations/Rolling.gif")
        self.ui.lblPixmapQr.setMovie(gif_loading)
        gif_loading.start()

        self.qrcode_thread.start()
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserMethods)

    def showQrcode(self, qrcode_signin_token):
        qr.clear()
        qr.add_data(qrcode_signin_token)
        qr.make(fit=True)
        qrcode_img = qr.make_image(fill_color="black", back_color="white")
        self.ui.lblPixmapQr.setPixmap(QPixmap.fromImage(ImageQt(qrcode_img)).scaled(300, 300))
        self.ui.lblNotification.hide()

    def stackMainMenu(self):
        self.setButton(self.ui.btnLeft, function=self.signOutUser, text='خروج', icon='images/icon/log-out.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblNotification.hide()
        self.stopSound()

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

    def stackWalletServices(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblNotification.hide()
        self.ui.Stack.setCurrentWidget(self.ui.pageWalletServices)

    def stackAutoDeliveryItems(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, function=self.afterDelivery, text='پایان', icon='images/icon/tick.png', show=False)
        self.ui.lblNotification.hide()
        # self.ui.listAutoDeliveryItems.clear()
        self.ui.lblPixmapCategory1.setPixmap(QPixmap("images/item/category1.png").scaledToHeight(128))
        self.ui.lblPixmapCategory2.setPixmap(QPixmap("images/item/category2.png").scaledToHeight(128))
        self.ui.lblPixmapCategory3.setPixmap(QPixmap("images/item/category3.png").scaledToHeight(128))
        self.ui.lblPixmapCategory4.setPixmap(QPixmap("images/item/category4.png").scaledToHeight(128))   
        
        self.setButton(self.ui.btnAutoDeliveryRecycleItem, function=self.startRecycleItem)
        
        self.delivery_items_flag = True
        self.user_items = []
        for item in self.items:
            item['count'] = 0

        self.ui.Stack.setCurrentWidget(self.ui.pageAutoDeliveryItems)

        
    def startRecycleItem(self):
        print('startRecycleItem')
        try:
            if self.delivery_items_flag == True:
                self.detect_item_flag = True

                if self.device_mode == 'auto':
                    self.predicted_items = []
                    self.auto_delivery_items_thread.start()
                    # self.auto_delivery_items_thread_stop_timer = Timer(camera_timer, self.auto_delivery_items_thread.stop)
                    # self.auto_delivery_items_thread_stop_timer.start()
                    # pass

                if hasattr(self, 'press_motor_stop_timer'):
                    self.press_motor_stop_timer.cancel()
                try:
                    self.press_motor.forward()
                    print('press motor on')
                    self.press_motor_stop_timer = Timer(motor_timer, self.press_motor.stop)
                    self.press_motor_stop_timer.start()
                except Exception as e:
                    print("error:", e)

                if hasattr(self, 'conveyor_motor_stop_timer'):
                    self.conveyor_motor_stop_timer.cancel()
                try:
                    self.conveyor_motor.on()
                    print('conveyor motor on')
                    self.conveyor_motor_stop_timer = Timer(motor_timer, self.conveyor_motor.stop)
                    self.conveyor_motor_stop_timer.start()
                except Exception as e:
                    print("error:", e)
        except Exception as e:
            print("error:", e)


    def endRecycleItem(self):
        print('endRecycleItem')
        try:
            if hasattr(self, 'detect_item_flag') and self.detect_item_flag == True:
                self.detect_item_flag = False
                if self.device_mode == 'auto':
                    self.auto_delivery_items_thread.stop()

                    if len(self.predicted_items) > 0:
                        most_probability_item = stats.mode(self.predicted_items).mode[0]
                        self.selected_item = self.items[most_probability_item]
                        print('most probability item:', window.selected_item['name'])

                        self.ui.listAutoDeliveryItems.addItems([self.selected_item['name']])

                        if self.selected_item['category_id'] == 1:
                            self.ui.lblNumCategory1.setText(str(int(self.ui.lblNumCategory1.text()) + 1))
                        elif self.selected_item['category_id'] == 2:
                            self.ui.lblNumCategory2.setText(str(int(self.ui.lblNumCategory2.text()) + 1))
                        elif self.selected_item['category_id'] == 3:
                            self.ui.lblNumCategory3.setText(str(int(self.ui.lblNumCategory3.text()) + 1))
                        elif self.selected_item['category_id'] == 4:
                            self.ui.lblNumCategory4.setText(str(int(self.ui.lblNumCategory4.text()) + 1))

                if hasattr(self, 'separation_motor_stop_timer'):
                    self.separation_motor_stop_timer.cancel()
                try:
                    if self.selected_item['category_id'] == 1:
                        self.separation_motor.forward()
                    else:
                        self.separation_motor.backward()
                    print('separation motor on')
                    self.separation_motor_stop_timer = Timer(separation_motor_timer, self.separation_motor.stop)
                    self.separation_motor_stop_timer.start()
                except Exception as e:
                    print("error:", e)

                self.playSound('audio3')
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
             
        except Exception as e:
            print("error:", e)


    def SelectItem(self, item, this_btn):
        self.selected_item = item
        self.selected_item['name'] = item['name']
        self.ui.lblSelectedItem.setText(self.selected_item['name'])
        self.ui.lblUnit.setText(str(self.selected_item['price']))
        self.ui.lblSelectedItemCount.setText(str(self.selected_item['count']))
        # for btn in self.layout_FArea.findChildren(QPushButton):
        #     btn.setStyleSheet('background-color: #ffffff; border: 2px solid #28a745; border-radius: 10px; outline-style: none; font: 24pt "IRANSansFaNum"')

        # this_btn.setStyleSheet('background-color: #28a745; color:#ffffff; border-radius: 10px; outline-style: none; font: 24pt "IRANSansFaNum"')
        
    def manualDeliveryRecycleItem(self):
        self.startRecycleItem()
        self.endRecycleItem()


    def stackManualDeliveryItems(self):
        self.delivery_items_flag = True
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, function=self.afterDelivery, text='پایان', icon='images/icon/tick.png', show=False)
        self.setButton(self.ui.btnManualDeliveryRecycleItem, function=self.manualDeliveryRecycleItem)
        self.playSound('audio7')
        self.ui.lblTotal.setText("0")
        self.ui.lblRecycledDone.hide()
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
        self.ui.scrollWidgetManualDelivery.setLayout(self.layout_FArea)
        self.ui.Stack.setCurrentWidget(self.ui.pageManualDeliveryItems)
        
    def printReceipt(self):
        self.playSound('audio4')
        # printer = Usb(idVendor=0x0416, idProduct=0x5011, timeout=0, in_ep=0x81, out_ep=0x03)
        os.system('sudo python3 printer.py ' 
        + str(self.total_price)
        + ' --mobile_number ' + str(self.system['owner']['mobile_number'])
        + ' --datetime "' + QDate.currentDate().toString(Qt.DefaultLocaleShortDate) + '-' + QTime.currentTime().toString(Qt.DefaultLocaleShortDate) + '"')
        self.stackMainMenu()

    def afterDelivery(self):
        self.showNotification(PLEASE_WAIT_MESSAGE)
        self.after_delivery_thread.start()

    def stackAfterDelivery(self):
        try:
            self.delivery_items_flag = False

            self.ui.Stack.setCurrentWidget(self.ui.pageAfterDelivery)
            self.playSound('audio11')
            self.setButton(self.ui.btnLeft, show=False)
            self.setButton(self.ui.btnRight, show=False)
            self.ui.lblNotification.hide()
            gif_afterDelivery = QMovie("animations/earth.gif")
            self.ui.lblGifAfterDelivery.setMovie(gif_afterDelivery)
            gif_afterDelivery.start()
            self.ui.lblTotalPrice.setText(str(self.total_price))
        except:
            self.showNotification(SERVER_ERROR_MESSAGE)
    
        try:
            self.motor.off()
            self.conveyor.off()
        except Exception as e:
            print("error:", e)

    def fastChargingDeliveryRecycleItem(self):
        pass

    def stackFastCharging(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.setButton(self.ui.btnRecycleItem_FastCharging, function=self.fastChargingDeliveryRecycleItem)
        self.ui.lblRecycledDone_FastCharging.hide()
        self.ui.tbUnit_FastCharging.setText('')
        self.ui.tbWeight_FastCharging.setText('')


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
        self.ui.Stack.setCurrentWidget(self.ui.pageFastDelivery)

    def stackChargingResidentialUnit(self):
        self.setButton(self.ui.btnLeft, function=self.stackWalletServices, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.ui.lblUserAddress.setText(self.user['address'])
        print(self.user['address'])
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ui.tbUserNewAddress.setSizePolicy(sp_retain)
        self.ui.btnChangedUserAddress.setSizePolicy(sp_retain)
        self.ui.tbUserNewAddress.hide()
        self.ui.btnChangedUserAddress.hide()
        self.ui.btnEditUserAddress.clicked.connect(self.editUserAddress)
        self.ui.Stack.setCurrentWidget(self.ui.pageChargingResidentialUnit)

    def editUserAddress(self):
        self.ui.tbUserNewAddress.show()
        self.ui.btnChangedUserAddress.show()

    def depositToRFIDcard(self):
        try:
            print("Now place your tag to write")
            data = 'test'
            self.rfid_sensor.write(data)
            print("Written")
            self.showNotification(DEPOSITE_TO_RFID_MESSAGE)
        except Exception as e:
            print("error:", e)

        self.stackWalletServices()

    def plusRFID(self):
        if self.user_wallet < int(self.ui.lblPayment_RFID.text()):
            self.showNotification(MONEY_ERROR_MESSAGE)
        else:
            self.ui.lbl_deposit_to_RFID.setText(str(int(self.ui.lbl_deposit_to_RFID.text()) + self.money_RFID))
            self.user_wallet -= self.money_RFID
            self.ui.lbl_total_wallet_RFID.setText(str(self.user_wallet))

    def minusRFID(self):
        if int(self.ui.lbl_deposit_to_RFID.text()) > 0:
            self.ui.lbl_deposit_to_RFID.setText(str(int(self.ui.lbl_deposit_to_RFID.text()) - self.money_RFID))
            self.user_wallet += self.money_RFID
            self.ui.lbl_total_wallet_RFID.setText(str(self.user_wallet))
        else:
            print('End of minus operations')

    def stackRFID(self):
        self.setButton(self.ui.btnLeft, function=self.stackWalletServices, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.hideNotification()

        self.user_wallet = self.user['wallet']
        self.money_RFID = int(self.ui.lblPayment_RFID.text())

        self.ui.lbl_deposit_to_RFID.setText('0')
        self.ui.lbl_total_wallet_RFID.setText(str(self.user_wallet))
        self.ui.Stack.setCurrentWidget(self.ui.pageRFID)

    def plusCharity(self):
        if self.user_wallet < int(self.ui.lblPayment_charity.text()):
            self.showNotification(MONEY_ERROR_MESSAGE)
        else:
            self.ui.lbl_deposit_price_charity_organization.setText(str(int(self.ui.lbl_deposit_price_charity_organization.text()) + self.money_charity_organization))
            self.user_wallet -= self.money_charity_organization
            self.ui.lblTotalPrice_charity.setText(str("{:,.0f}".format(self.user_wallet)))

    def minusCharity(self):
        if int(self.ui.lbl_deposit_price_charity_organization.text()) > 0:
            self.ui.lbl_deposit_price_charity_organization.setText(str(int(self.ui.lbl_deposit_price_charity_organization.text()) - self.money_charity_organization))
            self.user_wallet += self.money_charity_organization
            self.ui.lblTotalPrice_charity.setText(str("{:,.0f}".format(self.user_wallet)))
        else:
            print('End of minus operations')

    def stackCharity(self):
        self.setButton(self.ui.btnLeft, function=self.stackWalletServices, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, text='تایید', icon='images/icon/tick.png', show=True)
        self.hideNotification()

        self.user_wallet = self.user['wallet']
        self.money_charity_organization = int(self.ui.lblPayment_charity.text())

        self.ui.lbl_deposit_price_charity_organization.setText('0')
        self.ui.lblTotalPrice_charity.setText(str("{:,.0f}".format(self.user_wallet)))
        self.ui.lblSelectedCharity.setText(self.ui.lblCharity_1.text())
        self.ui.Stack.setCurrentWidget(self.ui.pageCharity)

    def plusEnvirnment(self):
        if self.user_wallet < int(self.ui.lblPayment_envirnmentalProtection.text()):
            self.showNotification(MONEY_ERROR_MESSAGE)
        else:
            self.ui.lbl_deposit_price_environmental_organization.setText(str(int(self.ui.lbl_deposit_price_environmental_organization.text()) + self.money_envirnmental_organization))
            self.user_wallet -= self.money_envirnmental_organization
            self.ui.lblTotalPrice_envirnmentalProtection.setText(str("{:,.0f}".format(self.user_wallet)))

    def minusEnvirnment(self):
        if int(self.ui.lbl_deposit_price_environmental_organization.text()) > 0:
            self.ui.lbl_deposit_price_environmental_organization.setText(str(int(self.ui.lbl_deposit_price_environmental_organization.text()) - self.money_envirnmental_organization))
            self.user_wallet += self.money_envirnmental_organization
            self.ui.lblTotalPrice_envirnmentalProtection.setText(str("{:,.0f}".format(self.user_wallet)))
        else:
            print('End of minus operations')

    def stackEnvirnmentalProtection(self):
        self.setButton(self.ui.btnLeft, function=self.stackWalletServices, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, text='تایید', icon='images/icon/tick.png', show=True)
        self.hideNotification()

        self.user_wallet = self.user['wallet']
        self.money_envirnmental_organization = int(self.ui.lblPayment_envirnmentalProtection.text())

        self.ui.lbl_deposit_price_environmental_organization.setText('0')
        self.ui.lblTotalPrice_envirnmentalProtection.setText(str("{:,.0f}".format(self.user_wallet)))
        self.ui.lblSelectedEnvirnmentalProtection.setText(self.ui.lblEnvirnmentalProtection_1.text())

        self.ui.Stack.setCurrentWidget(self.ui.pageEnvirnmentalProtection)

    def stackSetting(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, function=self.saveSetting, text='ذخیره', icon='images/icon/save.png', show=True)
        self.qrcode_thread.stop()
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
            self.stackAutoDeliveryItems()
    
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

    def stackPressMotor(self):
        self.ui.lblNotification.hide()
        self.ui.tb_press_motor_forward_port.setText(str(DataBase.select('press_motor_forward_port')))
        self.ui.tb_press_motor_backward_port.setText(str(DataBase.select('press_motor_backward_port')))
        self.ui.tb_press_motor_timer.setText(str(DataBase.select('press_motor_timer')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingPressMotor)

    def stackSeparationMotor(self):
        self.ui.lblNotification.hide()
        self.ui.tb_separation_motor_forward_port.setText(str(DataBase.select('separation_motor_forward_port')))
        self.ui.tb_separation_motor_backward_port.setText(str(DataBase.select('separation_motor_backward_port')))
        self.ui.tb_separation_motor_timer.setText(str(DataBase.select('separation_motor_timer')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingSeparationMotor)

    def stackSensor1Ports(self):
        self.ui.lblNotification.hide()
        self.ui.tb_sensor1_trig_port.setText(str(DataBase.select('sensor1_trig_port')))
        self.ui.tb_sensor1_echo_port.setText(str(DataBase.select('sensor1_echo_port')))
        self.ui.tb_sensor1_depth_threshold.setText(str(DataBase.select('sensor1_depth_threshold')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingSensor1Ports)

    def stackSensor2Ports(self):
        self.ui.lblNotification.hide()
        self.ui.tb_sensor2_trig_port.setText(str(DataBase.select('sensor2_trig_port')))
        self.ui.tb_sensor2_echo_port.setText(str(DataBase.select('sensor2_echo_port')))
        self.ui.tb_sensor2_depth_threshold.setText(str(DataBase.select('sensor2_depth_threshold')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingSensor2Ports)

    def stackConveyorPort(self):
        self.ui.lblNotification.hide()
        self.ui.tb_conveyor_motor_forward_port.setText(str(DataBase.select('conveyor_motor_forward_port')))
        self.ui.tb_conveyor_motor_backward_port.setText(str(DataBase.select('conveyor_motor_backward_port')))
        self.ui.tb_conveyor_motor_timer.setText(str(DataBase.select('conveyor_motor_timer')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingConveyorMotor)

    def stackAddOpetator(self):
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingAddOperator)

    def stackHelp(self):
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingHelp)
        self.ui.lbl_version.setText(DEVICE_VERSION.format(self.device_version))
        self.ui.lbl_version.show()

    def stackLicense(self):
        self.ui.tbLicense.setText(str(DataBase.select('app_version')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingLicense)

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
        if self.ui.tb_sensor1_trig_port.text() != '':
            result = DataBase.update('sensor1_trig_port', self.ui.tb_sensor1_trig_port.text())
        if self.ui.tb_sensor1_echo_port.text() != '':
            result = DataBase.update('sensor1_echo_port', self.ui.tb_sensor1_echo_port.text())
        if self.ui.tb_sensor1_depth_threshold.text() != '':
            result = DataBase.update('sensor1_depth_threshold', self.ui.tb_sensor1_depth_threshold.text())

        if self.ui.tb_sensor2_trig_port.text() != '':
            result = DataBase.update('sensor2_trig_port', self.ui.tb_sensor2_trig_port.text())
        if self.ui.tb_sensor2_echo_port.text() != '':
            result = DataBase.update('sensor2_echo_port', self.ui.tb_sensor2_echo_port.text())
        if self.ui.tb_sensor2_depth_threshold.text() != '':
            result = DataBase.update('sensor2_depth_threshold', self.ui.tb_sensor2_depth_threshold.text())

        if self.ui.tb_press_motor_forward_port.text() != '':
            result = DataBase.update('press_motor_forward_port', self.ui.tb_press_motor_forward_port.text())

        if self.ui.tb_press_motor_backward_port.text() != '':
            result = DataBase.update('press_motor_backward_port', self.ui.tb_press_motor_backward_port.text())

        if self.ui.tb_separation_motor_forward_port.text() != '':
            result = DataBase.update('separation_motor_forward_port', self.ui.tb_separation_motor_forward_port.text())

        if self.ui.tb_separation_motor_backward_port.text() != '':
            result = DataBase.update('separation_motor_backward_port', self.ui.tb_separation_motor_backward_port.text())

        if self.ui.tb_conveyor_motor_forward_port.text() != '':
            result = DataBase.update('conveyor_motor_forward_port', self.ui.tb_conveyor_motor_forward_port.text())

        if self.ui.tb_conveyor_motor_backward_port.text() != '':
            result = DataBase.update('conveyor_motor_backward_port', self.ui.tb_conveyor_motor_backward_port.text())

        self.initHardwares()

    def exitProgram(self):
        Server.turnOffSystemSMS(self.owner, self.system)
        self.delivery_item_flag = False
        self.close()
        QApplication.quit()

if __name__ == '__main__':
    os.environ["QT_QPA_FB_FORCE_FULLSCREEN"] = "0"
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    os.environ["QT_QPA_FONTDIR"] = "fonts"
    # os.environ["QT_QPA_PLATFORM"] = "minimalegl"
    # os.environ["ESCPOS_CAPABILITIES_FILE"] = "/usr/python-escpos/capabilities.json"
    mixer.init()
    try:
        factory = NativeFactory()
    except Exception as e:
        print("error:", e)

    app = QApplication(sys.argv)
    window = MainWindow()
    #timer = QTimer()
    #timer.start(10000) #it's aboat 1 seconds
    app.exec_()
