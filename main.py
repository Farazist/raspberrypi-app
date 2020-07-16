from io import BytesIO
import os
import sys
import qrcode
from pygame import mixer
from time import sleep, time
from threading import Thread, Timer, Event
from functools import partial
# from escpos.printer import Usb
from gpiozero import DistanceSensor
from gpiozero.pins.native import NativeFactory
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QTimer, QDate, QTime, QSize, QThread, Signal
from PySide2.QtGui import QMovie, QPixmap, QFont, QIcon
from PySide2.QtWidgets import QApplication, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QGridLayout, QLabel
from PIL.ImageQt import ImageQt
from scipy import stats
from mfrc522 import SimpleMFRC522

from utils.motor import Motor
from server import Server
from database import DataBase
from custombutton import CustomButton
from image_classifier import ImageClassifier
from error_log import ErrorLog

__author__ = "Sara Zarei, Sajjad Aemmi"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__email__ = "sajjadaemmi@gmail.com"
__status__ = "Production"

SERVER_ERROR_MESSAGE = 'خطا در برقراری ارتباط با اینترنت'
SIGNIN_ERROR_MESSAGE = 'اطلاعات وارد شده درست نیست'
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

log_file = ErrorLog.checkExistsFile()

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
                ErrorLog.writeToFile('Server Error Message In QRCodeThread')
        
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
            id = int(window.ui.tb_owner_id.text())
            password = int(window.ui.tb_owner_password.text())
            window.owner = Server.signInUser(id, password)
            self.success_signal.emit()
        except:
            window.showNotification(SERVER_ERROR_MESSAGE)
            ErrorLog.writeToFile('Server Error Message In SigninOwnerThread')
        


class SigninUserThread(QThread):
    success_signal = Signal()
    
    def __init__(self):
        QThread.__init__(self)
    
    def run(self):
        try:
            id = int(window.ui.tb_user_id_or_mobile_number.text())
            password = int(window.ui.tb_user_password.text())
            window.user = Server.signInUser(id, password)
            self.success_signal.emit()
        except:
            window.showNotification(SERVER_ERROR_MESSAGE)
            ErrorLog.writeToFile('Server Error Message In SigninUserThread')


class LoadingThread(QThread):
    success_signal = Signal()
    fail_signal = Signal()
    
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
            ErrorLog.writeToFile('Server Error Message In LoadingThread')
            self.fail_signal.emit()
            

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
            ErrorLog.writeToFile(str(e) + ' In AutoDeliveryItemsThread')
        

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
            ErrorLog.writeToFile('Server Error Message In AfterDeliveryThread')


class MainWindow(QWidget):
   
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.system_id = DataBase.select('system_id')
        self.device_version = DataBase.select('app_version')
        self.device_mode = DataBase.select('bottle_recognize_mode')
        

        loader = QUiLoader()
        self.ui = loader.load('main.ui', None)

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ui.btn_left.setSizePolicy(sp_retain)
        self.ui.btn_right.setSizePolicy(sp_retain) 
        self.ui.lbl_device_info.setSizePolicy(sp_retain)
        self.ui.btn_setting.setSizePolicy(sp_retain)

        self.btnOwnerLogin = CustomButton()
        self.btnOwnerLogin.setGif("animations/Rolling-white.gif")
        self.ui.vLayoutSignInOwner.addWidget(self.btnOwnerLogin)
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

        self.loading_thread = LoadingThread()
        self.loading_thread.success_signal.connect(self.stackSignInOwner)
        self.loading_thread.fail_signal.connect(self.ui.btn_refresh_loading.show)
        # self.loading_thread.success_signal.connect(self.stackMainMenu)
        # self.user = Server.signInUser(105, 1234)
        # self.owner = Server.signInUser(104, 1234)

        self.auto_delivery_items_thread = AutoDeliveryItemsThread()
    
        self.after_delivery_thread = AfterDeliveryThread()
        self.after_delivery_thread.success_signal.connect(self.stackAfterDelivery)

        # signals
        self.ui.btn_refresh_loading.clicked.connect(self.refresh)
        self.ui.btn_setting.clicked.connect(self.stackSignInOwner)
        self.ui.btn_start.clicked.connect(self.stackSignInUserMethods)
        self.ui.btn_sign_in_user_id_number.clicked.connect(self.stackSignInUserIDNumber)
        self.ui.btn_sign_in_user_mobile_number.clicked.connect(self.stackSignInUserMobileNumber)
        self.btnUserLoginID.clicked.connect(self.signInUser)
        self.btnUserLoginMobile.clicked.connect(self.signInUserMobile)
        self.ui.btn_main_menu_1.clicked.connect(self.checkDeviceMode)
        #self.ui.btn_main_menu_3.clicked.connect(self.stackFastCharging)
        self.ui.btn_main_menu_4.clicked.connect(self.stackWalletServices)
        self.btnOwnerLogin.clicked.connect(self.signInOwner)
        self.ui.btn_print_receipt_no.clicked.connect(self.stackMainMenu)
        self.ui.btn_print_receipt_yes.clicked.connect(self.printReceipt)
        self.ui.btn_no_exit_app_setting.clicked.connect(self.stackSetting)
        self.ui.btn_yes_exit_app_setting.clicked.connect(self.exitProgram)
        self.ui.btn_setting_start.clicked.connect(self.stackStart)
        self.ui.btn_setting_1.clicked.connect(self.stackDeviceMode)
        self.ui.btn_setting_5.clicked.connect(self.stackConveyorPort)
        self.ui.btn_setting_2.clicked.connect(self.stackPressMotor)
        self.ui.btn_setting_10.clicked.connect(self.stackSeparationMotor)
        self.ui.btn_setting_3.clicked.connect(self.stackSensor1Ports)
        self.ui.btn_setting_9.clicked.connect(self.stackSensor2Ports)
        self.ui.btn_setting_6.clicked.connect(self.stackExitApp)
        self.ui.btn_setting_4.clicked.connect(self.stackAddOpetator)
        self.ui.btn_setting_7.clicked.connect(self.stackHelp)
        self.ui.btn_setting_8.clicked.connect(self.stackLicense)
        self.ui.btn_wallet_services_1.clicked.connect(self.stackChargingResidentialUnit)
        self.ui.btn_wallet_services_2.clicked.connect(self.stackRFID)
        self.ui.btn_wallet_services_3.clicked.connect(self.stackCharity)
        self.ui.btn_wallet_services_4.clicked.connect(self.stackEnvirnmentalProtection)
        self.ui.btn_wallet_services_5.clicked.connect(self.stackWallet)
        self.ui.btn_plus_charity.clicked.connect(self.plusCharity)
        self.ui.btn_minus_charity.clicked.connect(self.minusCharity)
        self.ui.btn_plus_envirnmental_protection.clicked.connect(self.plusEnvirnment)
        self.ui.btn_minus_envirnmental_protection.clicked.connect(self.minusEnvirnment)
        self.ui.btn_plus_rfid.clicked.connect(self.plusRFID)
        self.ui.btn_minus_rfid.clicked.connect(self.minusRFID)
        self.ui.btn_confirm_deposit_to_RFIDcard.clicked.connect(self.depositToRFIDcard)

        self.ui.btn_charity_1.clicked.connect(lambda: self.ui.lbl_selected_charity.setText(self.ui.lbl_charity_1.text()))
        self.ui.btn_charity_2.clicked.connect(lambda: self.ui.lbl_selected_charity.setText(self.ui.lbl_charity_2.text()))
        self.ui.btn_charity_3.clicked.connect(lambda: self.ui.lbl_selected_charity.setText(self.ui.lbl_charity_3.text()))
        self.ui.btn_charity_4.clicked.connect(lambda: self.ui.lbl_selected_charity.setText(self.ui.lbl_charity_4.text()))
        
        self.ui.btn_envirnmental_protection_1.clicked.connect(lambda: self.ui.lbl_selected_envirnmental_protection.setText(self.ui.lbl_envirnmental_protection_1.text()))
        self.ui.btn_envirnmental_protection_2.clicked.connect(lambda: self.ui.lbl_selected_envirnmental_protection.setText(self.ui.lbl_envirnmental_protection_2.text()))
        self.ui.btn_envirnmental_protection_3.clicked.connect(lambda: self.ui.lbl_selected_envirnmental_protection.setText(self.ui.lbl_envirnmental_protection_3.text()))
        self.ui.btn_envirnmental_protection_4.clicked.connect(lambda: self.ui.lbl_selected_envirnmental_protection.setText(self.ui.lbl_envirnmental_protection_4.text()))

        self.ui.tb_owner_id.textChanged.connect(self.hideNotification)
        self.ui.tb_owner_password.textChanged.connect(self.hideNotification)
        self.ui.tb_user_id_or_mobile_number.textChanged.connect(self.hideNotification)
        self.ui.tb_user_password.textChanged.connect(self.hideNotification)
        
        self.ui.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog)
        self.ui.showMaximized()
    
        self.flag_system_startup_now = True
        self.delivery_items_flag = False
        self.detect_item_flag = False

        # self.categories = Server.getCategories()
        self.image_classifier = ImageClassifier()

        self.initHardwares()
        self.stackLoading()
        self.playSound('audio2')
        self.refresh()

    def initHardwares(self):
        try:
            if hasattr(self, 'press_motor'):
                self.press_motor.close()
                print("press motor close")
            press_motor_forward_port = int(DataBase.select('press_motor_forward_port'))
            press_motor_backward_port = int(DataBase.select('press_motor_backward_port'))
            self.press_motor = Motor(forward=press_motor_forward_port, backward=press_motor_backward_port, active_high=False, pin_factory=factory)
            
            self.ui.btn_press_motor_forward_on.clicked.connect(self.press_motor.forward)
            self.ui.btn_press_motor_backward_on.clicked.connect(self.press_motor.backward)
            self.ui.btn_press_motor_off.clicked.connect(self.press_motor.stop)
            print('press motor ready')
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In press_motor initHardwares Method')

        try:
            if hasattr(self, 'separation_motor'):
                self.separation_motor.close()
                print("separation motor close")
            separation_motor_forward_port = int(DataBase.select('separation_motor_forward_port'))
            separation_motor_backward_port = int(DataBase.select('separation_motor_backward_port'))
            self.separation_motor = Motor(forward=separation_motor_forward_port, backward=separation_motor_backward_port, active_high=False, pin_factory=factory)
        
            self.ui.btn_separation_motor_forward_on.clicked.connect(self.separation_motor.forward)
            self.ui.btn_separation_motor_backward_on.clicked.connect(self.separation_motor.backward)
            self.ui.btn_separation_motor_off.clicked.connect(self.separation_motor.stop)
            print('separation motor ready')
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In separation_motor initHardwares Method')

        try:
            if hasattr(self, 'conveyor_motor'):
                self.conveyor_motor.close()
                print("conveyor motor close")
            conveyor_motor_forward_port = int(DataBase.select('conveyor_motor_forward_port'))
            conveyor_motor_backward_port = int(DataBase.select('conveyor_motor_backward_port'))
            self.conveyor_motor = Motor(forward=conveyor_motor_forward_port, backward=conveyor_motor_backward_port, active_high=False, pin_factory=factory)
       
            self.ui.btn_conveyor_motor_forward_on.clicked.connect(self.conveyor_motor.forward)
            self.ui.btn_conveyor_motor_backward_on.clicked.connect(self.conveyor_motor.backward)
            self.ui.btn_conveyor_motor_off.clicked.connect(self.conveyor_motor.stop)
            print('conveyor motor ready')
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In conveyor_motor initHardwares Method')
        
        try:
            if hasattr(self, 'distance_sensor1'):
                self.distance_sensor1.close()
                print("distance sensor 1 close")
            distance_sensor1_trig_port = int(DataBase.select('distance_sensor1_trig_port'))
            distance_sensor1_echo_port = int(DataBase.select('distance_sensor1_echo_port'))
            distance_sensor1_depth_threshold = float(DataBase.select('distance_sensor1_depth_threshold'))
            self.distance_sensor1 = DistanceSensor(distance_sensor1_echo_port, distance_sensor1_trig_port, max_distance=1, threshold_distance=distance_sensor1_depth_threshold/100, pin_factory=factory)
            self.distance_sensor1.when_in_range = self.startRecycleItem
            print('distance sensor 1 ready')
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In distance_sensor1 initHardwares Method')

        try:
            if hasattr(self, 'distance_sensor2'):
                self.distance_sensor2.close()
                print("distance sensor 2 close")
            distance_sensor2_trig_port = int(DataBase.select('distance_sensor2_trig_port'))
            distance_sensor2_echo_port = int(DataBase.select('distance_sensor2_echo_port'))
            distance_sensor2_depth_threshold = float(DataBase.select('distance_sensor2_depth_threshold'))
            self.distance_sensor2 = DistanceSensor(distance_sensor2_echo_port, distance_sensor2_trig_port, max_distance=1, threshold_distance=distance_sensor2_depth_threshold/100, pin_factory=factory)
            self.distance_sensor2.when_in_range = self.endRecycleItem
            print('distance sensor 2 ready')
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In distance_sensor2 initHardwares Method')

        try:
            if not hasattr(self, 'rfid_sensor'):
                self.rfid_sensor = SimpleMFRC522()
                print('RFID sensor ready')
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In rfid_sensor initHardwares Method')

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
        self.ui.lbl_notification.setText(text)
        self.ui.lbl_notification.show()

    def hideNotification(self):
        self.ui.lbl_notification.hide()

    def playSound(self, path):
        try:
            path = os.path.join('sounds', path+'.mp3')
            if os.path.isfile(path):
                mixer.music.load(path)
                mixer.music.play()
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In playSound Method')

    def stopSound(self):
        try:
            mixer.music.stop()
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In stopSound Method')

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
        self.ui.lbl_logo.hide()
        self.setButton(self.ui.btn_left, show=False)
        self.setButton(self.ui.btn_right, show=False)
        self.ui.btn_refresh_loading.hide()
        self.ui.Stack.setCurrentWidget(self.ui.pageLoading)

    def stackSignInOwner(self):
        self.ui.lbl_logo.show()
        self.qrcode_thread.stop()
        self.ui.lbl_notification.hide()
        if self.flag_system_startup_now:
            self.setButton(self.ui.btn_left, show=False)
        else:
            if hasattr(self, 'user') == True:
                self.user = None
            self.setButton(self.ui.btn_left, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
            self.ui.lbl_device_info.setText(self.deviceInfo)
        self.setButton(self.ui.btn_right, show=False)
        self.ui.tb_owner_id.setText('')
        self.ui.tb_owner_password.setText('')
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
                ErrorLog.writeToFile('Server Error Message In stopSound Method')
        else:
            print("mobile number or password is incurrect")
            self.showNotification(SIGNIN_ERROR_MESSAGE)    

    def signInUser(self):
        self.showNotification(PLEASE_WAIT_MESSAGE)
        self.playSound('audio8')
        self.signin_user_thread.start()

    def afterSignInUser(self):
        if self.user != 0:
            self.ui.lbl_device_info.setText(self.user['name'] + '\nخوش آمدید')
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
            self.ui.lbl_device_info.setText(self.user['name'] + '\nخوش آمدید')
            self.stackMainMenu()
            self.playSound('audio2')
        else:
            print("mobile number or password is incurrect")
            self.showNotification(SIGNIN_ERROR_MESSAGE)

    def signOutUser(self):
        print('user log out')
        self.user = None
        self.stackStart()

    def stackStart(self):
        self.setButton(self.ui.btn_left, show=False)
        self.setButton(self.ui.btn_right, show=False)
        self.ui.lbl_notification.hide()
        self.ui.lbl_device_info.setText(self.deviceInfo)
        gif_start = QMovie("animations/slider1.gif")
        self.ui.lbl_slider_start.setMovie(gif_start)
        gif_start.start()
        self.qrcode_thread.stop()
        self.ui.Stack.setCurrentWidget(self.ui.pageStart)

    def stackSignInUserIDNumber(self):
        self.setButton(self.ui.btn_left, function=self.stackSignInUserMethods, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, show=False)
        self.stopSound()
        self.ui.tb_user_id_or_mobile_number.setText('')
        self.ui.tb_user_password.setText('')
        self.qrcode_thread.stop()
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserIDNumber)

    def stackSignInUserMobileNumber(self):
        self.setButton(self.ui.btn_left, function=self.stackSignInUserMethods, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, show=False)
        self.stopSound()
        self.ui.tbUserMobile.setText('')
        self.ui.tbUserPasswordMobile.setText('')
        self.qrcode_thread.stop()
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserMobileNumber)

    def stackSignInUserMethods(self):
        self.setButton(self.ui.btn_left, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, show=False)
        self.playSound('audio10')
        self.ui.lbl_notification.hide()

        gif_loading = QMovie("animations/Rolling.gif")
        self.ui.lbl_pixmap_qr.setMovie(gif_loading)
        gif_loading.start()

        self.qrcode_thread.start()
        self.ui.Stack.setCurrentWidget(self.ui.pageSignInUserMethods)

    def showQrcode(self, qrcode_signin_token):
        qr.clear()
        qr.add_data(qrcode_signin_token)
        qr.make(fit=True)
        qrcode_img = qr.make_image(fill_color="black", back_color="white")
        self.ui.lbl_pixmap_qr.setPixmap(QPixmap.fromImage(ImageQt(qrcode_img)).scaled(300, 300))
        self.ui.lbl_notification.hide()

    def stackMainMenu(self):
        self.setButton(self.ui.btn_left, function=self.signOutUser, text='خروج', icon='images/icon/log-out.png', show=True)
        self.setButton(self.ui.btn_right, show=False)
        self.ui.lbl_notification.hide()
        self.stopSound()

        self.ui.Stack.setCurrentWidget(self.ui.pageMainMenu)

    def stackWalletServices(self):
        self.setButton(self.ui.btn_left, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, show=False)
        self.ui.lbl_notification.hide()
        self.ui.Stack.setCurrentWidget(self.ui.pageWalletServices)

    def stackAutoDeliveryItems(self):
        self.setButton(self.ui.btn_left, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, function=self.afterDelivery, text='پایان', icon='images/icon/tick.png', show=False)
        self.ui.lbl_notification.hide()
        # self.ui.list_auto_delivery_items.clear()
        self.ui.lbl_pixmap_category_1.setPixmap(QPixmap("images/item/category1.png").scaledToHeight(128))
        self.ui.lbl_pixmap_category_2.setPixmap(QPixmap("images/item/category2.png").scaledToHeight(128))
        self.ui.lbl_pixmap_category_3.setPixmap(QPixmap("images/item/category3.png").scaledToHeight(128))
        self.ui.lbl_pixmap_category_4.setPixmap(QPixmap("images/item/category4.png").scaledToHeight(128))   
        
        self.setButton(self.ui.btn_recycle_auto_delivery_items, function=self.startRecycleItem)
        
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
                    ErrorLog.writeToFile(str(e) + ' In press_motor_stop_timer startRecycleItem Method')

                if hasattr(self, 'conveyor_motor_stop_timer'):
                    self.conveyor_motor_stop_timer.cancel()
                try:
                    self.conveyor_motor.on()
                    print('conveyor motor on')
                    self.conveyor_motor_stop_timer = Timer(motor_timer, self.conveyor_motor.stop)
                    self.conveyor_motor_stop_timer.start()
                except Exception as e:
                    print("error:", e) 
                    ErrorLog.writeToFile(str(e) + ' In conveyor_motor_stop_timer startRecycleItem Method')
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In startRecycleItem Method')

    def endRecycleItem(self):
        print('endRecycleItem')
        try:
            if self.detect_item_flag == True:
                self.detect_item_flag = False
                if self.device_mode == 'auto':
                    self.auto_delivery_items_thread.stop()

                    if len(self.predicted_items) > 0:
                        most_probability_item = stats.mode(self.predicted_items).mode[0]
                        self.selected_item = self.items[most_probability_item]
                        print('most probability item:', window.selected_item['name'])

                        self.ui.list_auto_delivery_items.addItems([self.selected_item['name']])

                        if self.selected_item['category_id'] == 1:
                            self.ui.lbl_num_category_1.setText(str(int(self.ui.lbl_num_category_1.text()) + 1))
                        elif self.selected_item['category_id'] == 2:
                            self.ui.lbl_num_category_2.setText(str(int(self.ui.lbl_num_category_2.text()) + 1))
                        elif self.selected_item['category_id'] == 3:
                            self.ui.lbl_num_category_3.setText(str(int(self.ui.lbl_num_category_3.text()) + 1))
                        elif self.selected_item['category_id'] == 4:
                            self.ui.lbl_num_category_4.setText(str(int(self.ui.lbl_num_category_4.text()) + 1))

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
                    ErrorLog.writeToFile(str(e) + ' In separation motor on endRecycleItem Method')

                self.playSound('audio3')
                self.showNotification(RECYCLE_MESSAGE)
                self.ui.btn_right.show()
                self.selected_item['count'] += 1
                self.ui.lbl_selected_item_count.setText(str(self.selected_item['count']))
                for user_item in self.user_items:
                    if self.selected_item['id'] == user_item['id']:
                        break
                else:
                    self.user_items.append(self.selected_item)
                self.total_price = sum(user_item['price'] * user_item['count'] for user_item in self.user_items)
                self.ui.lbl_total.setText(str(self.total_price))
             
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In endRecycleItem Method')


    def SelectItem(self, item, this_btn):
        self.selected_item = item
        self.selected_item['name'] = item['name']
        self.ui.lbl_selected_item.setText(self.selected_item['name'])
        self.ui.lbl_unit.setText(str(self.selected_item['price']))
        self.ui.lbl_selected_item_count.setText(str(self.selected_item['count']))
        # for btn in self.layout_FArea.findChildren(QPushButton):
        #     btn.setStyleSheet('background-color: #ffffff; border: 2px solid #28a745; border-radius: 10px; outline-style: none; font: 24pt "IRANSansFaNum"')

        # this_btn.setStyleSheet('background-color: #28a745; color:#ffffff; border-radius: 10px; outline-style: none; font: 24pt "IRANSansFaNum"')
        
    def manualDeliveryRecycleItem(self):
        self.startRecycleItem()
        self.endRecycleItem()

    def stackManualDeliveryItems(self):
        self.delivery_items_flag = True
        self.setButton(self.ui.btn_left, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, function=self.afterDelivery, text='پایان', icon='images/icon/tick.png', show=False)
        self.setButton(self.ui.btn_manual_delivery_recycle_item, function=self.manualDeliveryRecycleItem)
        self.playSound('audio7')
        self.ui.lbl_total.setText("0")
        self.ui.lbl_recycled_done.hide()
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
        self.ui.scroll_widget_manual_delivery.setLayout(self.layout_FArea)
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
            self.setButton(self.ui.btn_left, show=False)
            self.setButton(self.ui.btn_right, show=False)
            self.ui.lbl_notification.hide()
            gif_afterDelivery = QMovie("animations/earth.gif")
            self.ui.lbl_gif_after_delivery.setMovie(gif_afterDelivery)
            gif_afterDelivery.start()
            self.ui.lbl_total_price.setText(str(self.total_price))
        except:
            self.showNotification(SERVER_ERROR_MESSAGE)
            ErrorLog.writeToFile('Server Error Message')
    
        try:
            self.press_motor.off()
            self.conveyor_motor.off()
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In stackAfterDelivery Method')

    def fastChargingDeliveryRecycleItem(self):
        pass

    def stackFastCharging(self):
        self.setButton(self.ui.btn_left, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, show=False)
        self.setButton(self.ui.btn_recycle_item_fast_charging, function=self.fastChargingDeliveryRecycleItem)
        self.ui.lbl_recycled_done_fast_charging.hide()
        self.ui.tb_unit_fast_charging.setText('')
        self.ui.tb_weight_fast_charging.setText('')


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
        self.ui.scroll_area_widget_fast_charging.setLayout(self.layout_SArea_FastCharging)
        self.ui.Stack.setCurrentWidget(self.ui.pageFastDelivery)

    def stackWallet(self):
        self.setButton(self.ui.btn_left, function=self.stackWalletServices, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, show=False)
        self.ui.lbl_notification.hide()
        gif_wallet = QMovie("animations/wallet.gif")
        gif_wallet.setScaledSize(QSize().scaled(256, 256, Qt.KeepAspectRatio))
        self.ui.lbl_gif_wallet.setMovie(gif_wallet)
        gif_wallet.start()
        self.ui.lbl_wallet.setText(str(("{:,.0f}").format(self.user['wallet'])))
        self.ui.Stack.setCurrentWidget(self.ui.pageWallet)

    def stackChargingResidentialUnit(self):
        self.setButton(self.ui.btn_left, function=self.stackWalletServices, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, show=False)
        self.ui.lbl_user_address.setText(self.user['address'])
        print(self.user['address'])
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ui.tb_user_new_address.setSizePolicy(sp_retain)
        self.ui.btn_changed_user_address.setSizePolicy(sp_retain)
        self.ui.tb_user_new_address.hide()
        self.ui.btn_changed_user_address.hide()
        self.ui.btn_edit_user_address.clicked.connect(self.editUserAddress)
        self.ui.Stack.setCurrentWidget(self.ui.pageChargingResidentialUnit)

    def editUserAddress(self):
        self.ui.tb_user_new_address.show()
        self.ui.btn_changed_user_address.show()

    def depositToRFIDcard(self):
        try:
            print("Now place your tag to write")
            data = 'test'
            self.rfid_sensor.write(data)
            print("Written")
            self.showNotification(DEPOSITE_TO_RFID_MESSAGE)
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In depositToRFIDcard Method')

        self.stackWalletServices()

    def plusRFID(self):
        if self.user_wallet < int(self.ui.lbl_payment_rfid.text()):
            self.showNotification(MONEY_ERROR_MESSAGE)
        else:
            self.ui.lbl_deposit_to_rfid.setText(str(int(self.ui.lbl_deposit_to_rfid.text()) + self.money_RFID))
            self.user_wallet -= self.money_RFID
            self.ui.lbl_total_wallet_rfid.setText(str("{:,.0f}".format(self.user_wallet)))

    def minusRFID(self):
        if int(self.ui.lbl_deposit_to_rfid.text()) > 0:
            self.ui.lbl_deposit_to_rfid.setText(str(int(self.ui.lbl_deposit_to_rfid.text()) - self.money_RFID))
            self.user_wallet += self.money_RFID
            self.ui.lbl_total_wallet_rfid.setText(str("{:,.0f}".format(self.user_wallet)))
        else:
            print('End of minus operations')

    def stackRFID(self):
        self.setButton(self.ui.btn_left, function=self.stackWalletServices, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, show=False)
        self.hideNotification()

        self.user_wallet = self.user['wallet']
        self.money_RFID = int(self.ui.lbl_payment_rfid.text())

        self.ui.lbl_deposit_to_rfid.setText('0')
        self.ui.lbl_total_wallet_rfid.setText(str("{:,.0f}".format(self.user_wallet)))
        self.ui.Stack.setCurrentWidget(self.ui.pageRFID)

    def plusCharity(self):
        if self.user_wallet < int(self.ui.lbl_payment_charity.text()):
            self.showNotification(MONEY_ERROR_MESSAGE)
        else:
            self.ui.lbl_deposit_price_charity_organization.setText(str(int(self.ui.lbl_deposit_price_charity_organization.text()) + self.money_charity_organization))
            self.user_wallet -= self.money_charity_organization
            self.ui.lbl_total_price_charity.setText(str("{:,.0f}".format(self.user_wallet)))

    def minusCharity(self):
        if int(self.ui.lbl_deposit_price_charity_organization.text()) > 0:
            self.ui.lbl_deposit_price_charity_organization.setText(str(int(self.ui.lbl_deposit_price_charity_organization.text()) - self.money_charity_organization))
            self.user_wallet += self.money_charity_organization
            self.ui.lbl_total_price_charity.setText(str("{:,.0f}".format(self.user_wallet)))
        else:
            print('End of minus operations')

    def stackCharity(self):
        self.setButton(self.ui.btn_left, function=self.stackWalletServices, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, text='تایید', icon='images/icon/tick.png', show=True)
        self.hideNotification()

        self.user_wallet = self.user['wallet']
        self.money_charity_organization = int(self.ui.lbl_payment_charity.text())

        self.ui.lbl_deposit_price_charity_organization.setText('0')
        self.ui.lbl_total_price_charity.setText(str("{:,.0f}".format(self.user_wallet)))
        self.ui.lbl_selected_charity.setText(self.ui.lbl_charity_1.text())
        self.ui.Stack.setCurrentWidget(self.ui.pageCharity)

    def plusEnvirnment(self):
        if self.user_wallet < int(self.ui.lbl_payment_envirnmental_protection.text()):
            self.showNotification(MONEY_ERROR_MESSAGE)
        else:
            self.ui.lbl_deposit_price_environmental_organization.setText(str(int(self.ui.lbl_deposit_price_environmental_organization.text()) + self.money_envirnmental_organization))
            self.user_wallet -= self.money_envirnmental_organization
            self.ui.lbl_total_price_envirnmental_protection.setText(str("{:,.0f}".format(self.user_wallet)))

    def minusEnvirnment(self):
        if int(self.ui.lbl_deposit_price_environmental_organization.text()) > 0:
            self.ui.lbl_deposit_price_environmental_organization.setText(str(int(self.ui.lbl_deposit_price_environmental_organization.text()) - self.money_envirnmental_organization))
            self.user_wallet += self.money_envirnmental_organization
            self.ui.lbl_total_price_envirnmental_protection.setText(str("{:,.0f}".format(self.user_wallet)))
        else:
            print('End of minus operations')

    def stackEnvirnmentalProtection(self):
        self.setButton(self.ui.btn_left, function=self.stackWalletServices, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, text='تایید', icon='images/icon/tick.png', show=True)
        self.hideNotification()

        self.user_wallet = self.user['wallet']
        self.money_envirnmental_organization = int(self.ui.lbl_payment_envirnmental_protection.text())

        self.ui.lbl_deposit_price_environmental_organization.setText('0')
        self.ui.lbl_total_price_envirnmental_protection.setText(str("{:,.0f}".format(self.user_wallet)))
        self.ui.lbl_selected_envirnmental_protection.setText(self.ui.lbl_envirnmental_protection_1.text())

        self.ui.Stack.setCurrentWidget(self.ui.pageEnvirnmentalProtection)

    def stackSetting(self):
        self.setButton(self.ui.btn_left, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btn_right, function=self.saveSetting, text='ذخیره', icon='images/icon/save.png', show=True)
        self.qrcode_thread.stop()
        self.ui.lbl_notification.hide()
        self.ui.lbl_device_info.setText(self.deviceInfo)
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingEmpty)
        self.ui.Stack.setCurrentWidget(self.ui.pageSetting)

    def stackDisableDevice(self):
        self.ui.btn_left.hide()
        self.ui.btn_right.hide()
        self.ui.lbl_notification.hide()
        self.ui.Stack.setCurrentWidget(self.ui.pageDisableDevice)

    def checkDeviceMode(self):
        if self.device_mode == 'manual':
            self.stackManualDeliveryItems()
        elif self.device_mode == 'auto':
            self.stackAutoDeliveryItems()
    
    def stackDeviceMode(self):
        result = DataBase.select('bottle_recognize_mode')
        if result == 'manual':
            self.ui.rb_manual_device_mode_setting.setChecked(True)
        elif result == 'auto':
            self.ui.rb_auto_device_mode_setting.setChecked(True)
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingDeviceMode)

    def stackExitApp(self):
        self.ui.lbl_notification.hide()
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingExit)

    def stackPressMotor(self):
        self.ui.lbl_notification.hide()
        self.ui.tb_press_motor_forward_port.setText(str(DataBase.select('press_motor_forward_port')))
        self.ui.tb_press_motor_backward_port.setText(str(DataBase.select('press_motor_backward_port')))
        self.ui.tb_press_motor_timer.setText(str(DataBase.select('press_motor_timer')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingPressMotor)

    def stackSeparationMotor(self):
        self.ui.lbl_notification.hide()
        self.ui.tb_separation_motor_forward_port.setText(str(DataBase.select('separation_motor_forward_port')))
        self.ui.tb_separation_motor_backward_port.setText(str(DataBase.select('separation_motor_backward_port')))
        self.ui.tb_separation_motor_timer.setText(str(DataBase.select('separation_motor_timer')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingSeparationMotor)

    def stackSensor1Ports(self):
        self.ui.lbl_notification.hide()
        self.ui.tb_sensor1_trig_port.setText(str(DataBase.select('distance_sensor1_trig_port')))
        self.ui.tb_sensor1_echo_port.setText(str(DataBase.select('distance_sensor1_echo_port')))
        self.ui.tb_sensor1_depth_threshold.setText(str(DataBase.select('distance_sensor1_depth_threshold')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingDistanceSensor1)

    def stackSensor2Ports(self):
        self.ui.lbl_notification.hide()
        self.ui.tb_sensor2_trig_port.setText(str(DataBase.select('distance_sensor2_trig_port')))
        self.ui.tb_sensor2_echo_port.setText(str(DataBase.select('distance_sensor2_echo_port')))
        self.ui.tb_sensor2_depth_threshold.setText(str(DataBase.select('distance_sensor2_depth_threshold')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingDistanceSensor2)

    def stackConveyorPort(self):
        self.ui.lbl_notification.hide()
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
        self.ui.tb_license.setText(str(DataBase.select('app_version')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingLicense)

    def changePredictItemFlag(self, value):
        self.predict_item_flag = value
        self.ui.lblDeliveryItems.clear()

    def saveSetting(self):
        self.showNotification(SETTING_SAVE_MESSAGE)
        if self.ui.rb_manual_device_mode_setting.isChecked() == True:
            result = DataBase.update('bottle_recognize_mode', 'manual')
        if self.ui.rb_auto_device_mode_setting.isChecked() == True:
            result = DataBase.update('bottle_recognize_mode', 'auto')
        self.device_mode = DataBase.select('bottle_recognize_mode')
        if self.ui.tb_sensor1_trig_port.text() != '':
            result = DataBase.update('distance_sensor1_trig_port', self.ui.tb_sensor1_trig_port.text())
        if self.ui.tb_sensor1_echo_port.text() != '':
            result = DataBase.update('distance_sensor1_echo_port', self.ui.tb_sensor1_echo_port.text())
        if self.ui.tb_sensor1_depth_threshold.text() != '':
            result = DataBase.update('distance_sensor1_depth_threshold', self.ui.tb_sensor1_depth_threshold.text())

        if self.ui.tb_sensor2_trig_port.text() != '':
            result = DataBase.update('distance_sensor2_trig_port', self.ui.tb_sensor2_trig_port.text())
        if self.ui.tb_sensor2_echo_port.text() != '':
            result = DataBase.update('distance_sensor2_echo_port', self.ui.tb_sensor2_echo_port.text())
        if self.ui.tb_sensor2_depth_threshold.text() != '':
            result = DataBase.update('distance_sensor2_depth_threshold', self.ui.tb_sensor2_depth_threshold.text())

        if self.ui.tb_press_motor_forward_port.text() != '':
            result = DataBase.update('press_motor_forward_port', self.ui.tb_press_motor_forward_port.text())
        if self.ui.tb_press_motor_backward_port.text() != '':
            result = DataBase.update('press_motor_backward_port', self.ui.tb_press_motor_backward_port.text())
        if self.ui.tb_press_motor_timer.text() != '':
            result = DataBase.update('press_motor_timer', self.ui.tb_press_motor_timer.text())

        if self.ui.tb_separation_motor_forward_port.text() != '':
            result = DataBase.update('separation_motor_forward_port', self.ui.tb_separation_motor_forward_port.text())
        if self.ui.tb_separation_motor_backward_port.text() != '':
            result = DataBase.update('separation_motor_backward_port', self.ui.tb_separation_motor_backward_port.text())
        if self.ui.tb_separation_motor_timer.text() != '':
            result = DataBase.update('separation_motor_timer', self.ui.tb_separation_motor_timer.text())

        if self.ui.tb_conveyor_motor_forward_port.text() != '':
            result = DataBase.update('conveyor_motor_forward_port', self.ui.tb_conveyor_motor_forward_port.text())
        if self.ui.tb_conveyor_motor_backward_port.text() != '':
            result = DataBase.update('conveyor_motor_backward_port', self.ui.tb_conveyor_motor_backward_port.text())
        if self.ui.tb_conveyor_motor_timer.text() != '':
            result = DataBase.update('conveyor_motor_timer', self.ui.tb_conveyor_motor_timer.text())

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
        ErrorLog.writeToFile(str(e) + ' In NativeFactory')

    app = QApplication(sys.argv)
    window = MainWindow()
    #timer = QTimer()
    #timer.start(10000) #it's aboat 1 seconds
    app.exec_()
