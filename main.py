from io import BytesIO
import os
import sys
import qrcode
from pygame import mixer
from time import sleep, time
from threading import Thread, Timer, Event
from functools import partial
from escpos.printer import Usb
from gpiozero import DistanceSensor
from gpiozero.pins.native import NativeFactory
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt, QTimer, QDate, QTime, QSize, QThread, Signal
from PySide2.QtGui import QMovie, QPixmap, QFont, QIcon
from PySide2.QtWidgets import QApplication, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QGridLayout, QLabel
from PIL.ImageQt import ImageQt
from scipy import stats
from mfrc522 import SimpleMFRC522
import picamera

from utils.motor import Motor
from utils.server import Server
from utils.database import DataBase
from utils.custombutton import CustomButton
from utils.image_classifier import ImageClassifier
from utils.error_log import ErrorLog
from utils.messages import *

__author__ = "Sara Zarei, Sajjad Aemmi"
__copyright__ = "Copyright 2020"
__license__ = "MIT"
__email__ = "developer@farazist.ir"
__status__ = "Production"

DEVICE_VERSION = 'ورژن {}'
BTN_PASS_RECOVERY_STYLE = 'font: 18pt "IRANSans";color: rgb(121, 121, 121);border: none; outline-style: none;'

stack_timer = 240000
delivery_cancel_time = 20.0


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
                while not self.event.wait(4) and counter < 32:
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
            window.ui.lbl_device_info.setText(window.user['name'] + '\nخوش آمدید')
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
            ErrorLog.writeToFile('Server Error Message In LoadingThread')
            self.fail_signal.emit()
            

class AutoDeliveryItemsThread(QThread):

    def __init__(self):
        QThread.__init__(self)
    
    def run(self):
        self.predicted_items = []
        try:
            with picamera.PiCamera(resolution=(1280, 720), framerate=30) as camera:
                # camera.start_preview()
                stream = BytesIO()
                for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                    if window.delivery_state in ['recognize', 'enter']:
                        print('capturing...')
                        stream.seek(0)
                        label, score = window.image_classifier(stream)
                        if score > window.predict_item_threshold:
                            self.predicted_items.append(label)
                            print(label, score)
                        stream.seek(0)
                        stream.truncate()
                    else:
                        # camera.stop_preview()
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


class RFIDThread(QThread):
    success_signal = Signal()
    fail_signal = Signal()
    
    def __init__(self):
        QThread.__init__(self)
    
    def run(self):
        try:
            print("Now place your tag to write")
            id, old_data = window.rfid_sensor.read()
            new_data = window.ui.lbl_transfer_to_rfid.text()
            
            if old_data.isdigit():
                data = int(new_data) + int(old_data)
            else:
                data = int(new_data)
            window.rfid_sensor.write(str(data))
            print("Written")
            self.success_signal.emit()
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In transferToRFIDCard Method')
            self.fail_signal.emit()


class MainWindow(QWidget):
   
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.system_id = DataBase.select('system_id')
        self.device_version = DataBase.select('app_version')
        self.device_mode = DataBase.select('device_mode')
        
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
        self.loading_thread.fail_signal.connect(self.loadingFail)
    
        self.auto_delivery_items_thread = AutoDeliveryItemsThread()

        self.after_delivery_thread = AfterDeliveryThread()
        self.after_delivery_thread.success_signal.connect(self.stackAfterDelivery)

        self.rfid_thread = RFIDThread()
        self.rfid_thread.success_signal.connect(self.successTransferToRFIDCard)
        self.rfid_thread.fail_signal.connect(self.transferToRFIDCard)

        # signals
        self.ui.btn_refresh_loading.clicked.connect(self.refresh)
        self.ui.btn_setting.clicked.connect(self.stackSignInOwner)
        self.ui.btn_start.clicked.connect(self.stackSignInUserMethods)
        self.ui.btn_sign_in_user_id_number.clicked.connect(self.stackSignInUserIDNumber)
        self.btnUserLoginID.clicked.connect(self.signInUser)
        self.btnUserLoginMobile.clicked.connect(self.signInUserMobile)
        self.ui.btn_main_menu_1.clicked.connect(self.checkDeviceMode)
        #self.ui.btn_main_menu_3.clicked.connect(self.stackFastCharging)
        self.ui.btn_main_menu_4.clicked.connect(self.stackWalletServices)
        self.btnOwnerLogin.clicked.connect(self.signInOwner)
        self.ui.btn_print_receipt_no.clicked.connect(self.stackMainMenu)
        self.ui.btn_print_receipt_yes.clicked.connect(self.printReceipt)
        self.ui.btn_other_services_after_delivery.clicked.connect(self.stackWalletServices)
        self.ui.btn_no_exit_app_setting.clicked.connect(self.stackSetting)
        self.ui.btn_yes_exit_app_setting.clicked.connect(self.exitProgram)
        self.ui.btn_setting_start.clicked.connect(self.stackStart)
        self.ui.btn_setting_1.clicked.connect(self.stackDeviceMode)
        self.ui.btn_setting_5.clicked.connect(self.stackConveyorPort)
        self.ui.btn_setting_2.clicked.connect(self.stackPressMotor)
        # self.ui.btn_setting_10.clicked.connect(self.stackSeparationMotor)
        self.ui.btn_setting_3.clicked.connect(self.stackSensor1Ports)
        self.ui.btn_setting_9.clicked.connect(self.stackSensor2Ports)
        self.ui.btn_setting_6.clicked.connect(self.stackExitApp)
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
        self.ui.btn_confirm_transfer_to_RFIDcard.clicked.connect(self.transferToRFIDCard)

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

        self.back_delivery_item_flag = False
        self.flag_system_startup_now = True

        self.delivery_state = 'default'

        # self.categories = Server.getCategories()
        self.image_classifier = ImageClassifier()
        self.predict_item_threshold = float(DataBase.select('predict_item_threshold'))
        self.initHardwares()

        self.stackLoading()
        self.playSound('audio2')
        self.refresh()

    def initHardwares(self):

        # if self.device_mode == 'auto':
        #     try:
        #         with picamera.PiCamera(resolution=(1280, 720), framerate=30) as camera:
        #             camera.start_preview()
        #             camera.stop_preview()
        #     except Exception as e:
        #         print("error:", e)

        try:
            # if hasattr(self, 'separation_motor'):
            #     self.separation_motor.close()
        
            if hasattr(self, 'press_motor'):
                self.press_motor.close()
            
            if hasattr(self, 'conveyor_motor'):
                self.conveyor_motor.close()

            if hasattr(self, 'distance_sensor1'):
                self.distance_sensor1.close()
                print("distance sensor 1 close")
            
            if hasattr(self, 'distance_sensor2'):
                self.distance_sensor2.close()
                print("distance sensor 2 close")
        
        except Exception as e:
            print("error:", e)
        
        try:
            self.press_motor = Motor(name='press_motor', pin_factory=factory)
          
            self.setButton(self.ui.btn_press_motor_forward_on, function=self.press_motor.forward)
            self.setButton(self.ui.btn_press_motor_backward_on, function=self.press_motor.backward)
            self.setButton(self.ui.btn_press_motor_off, function=self.press_motor.stop)
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In press_motor initHardwares Method')

        # try:
        #     self.separation_motor = Motor(name='separation_motor', pin_factory=factory)
       
        #     self.setButton(self.ui.btn_separation_motor_forward_on, function=self.separation_motor.forward)
        #     self.setButton(self.ui.btn_separation_motor_backward_on, function=self.separation_motor.backward)
        #     self.setButton(self.ui.btn_separation_motor_off, function=self.separation_motor.stop)
        # except Exception as e:
        #     print("error:", e)
        #     ErrorLog.writeToFile(str(e) + ' In separation_motor initHardwares Method')

        try:
            self.conveyor_motor = Motor(name='conveyor_motor', pin_factory=factory)
            self.conveyor_motor_time_2 = float(DataBase.select('conveyor_motor_time_2'))
         
            self.setButton(self.ui.btn_conveyor_motor_forward_on, function=self.conveyor_motor.forward)
            self.setButton(self.ui.btn_conveyor_motor_backward_on, function=self.conveyor_motor.backward)
            self.setButton(self.ui.btn_conveyor_motor_off, function=self.conveyor_motor.stop)
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In conveyor_motor initHardwares Method')
        
        try:
            distance_sensor1_trig_port = int(DataBase.select('distance_sensor1_trig_port'))
            distance_sensor1_echo_port = int(DataBase.select('distance_sensor1_echo_port'))
            distance_sensor1_threshold_distance = float(DataBase.select('distance_sensor1_threshold_distance'))
            self.distance_sensor1 = DistanceSensor(distance_sensor1_echo_port, distance_sensor1_trig_port, max_distance=1, threshold_distance=distance_sensor1_threshold_distance/100, pin_factory=factory)
            self.distance_sensor1.when_in_range = self.distanceSensor1WhenInRange
            self.distance_sensor1.when_out_of_range = self.distanceSensor1WhenOutOfRange
            print('distance sensor 1 ready')
        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In distance_sensor1 initHardwares Method')

        try:
            distance_sensor2_trig_port = int(DataBase.select('distance_sensor2_trig_port'))
            distance_sensor2_echo_port = int(DataBase.select('distance_sensor2_echo_port'))
            distance_sensor2_threshold_distance = float(DataBase.select('distance_sensor2_threshold_distance'))
            self.distance_sensor2 = DistanceSensor(distance_sensor2_echo_port, distance_sensor2_trig_port, max_distance=1, threshold_distance=distance_sensor2_threshold_distance/100, pin_factory=factory)
            self.distance_sensor2.when_in_range = self.distanceSensor2WhenInRange
            self.distance_sensor2.when_out_of_range = self.distanceSensor2WhenOutOfRange
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

    def loadingFail(self):
        self.ui.btn_refresh_loading.show()
        self.showNotification(SERVER_ERROR_MESSAGE)

    def refresh(self):
        self.showNotification(PLEASE_WAIT_MESSAGE)
        self.loading_thread.start()  
        
    def showSoonNotification(self):
        self.showNotification(SOON_MESSAGE)

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
                    self.items = Server.getItems(self.owner['id'])
                    Server.turnOnSystemSMS(self.owner, self.system)
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
        self.ui.lbl_pixmap_category_3.setPixmap(QPixmap("images/item/category3.png").scaledToHeight(128))
        self.ui.lbl_pixmap_category_4.setPixmap(QPixmap("images/item/category4.png").scaledToHeight(128))   

        self.ui.lbl_num_category_1.setText(str(0))
        self.ui.lbl_num_category_3.setText(str(0))
        self.ui.lbl_num_category_4.setText(str(0))
        
        self.ui.lbl_total_price_auto_delivery_items.setText(str(0))

        self.setButton(self.ui.btn_recycle_auto_delivery_items, function=self.startDeliveryItem)
        
        self.delivery_state = 'ready'

        self.user_items = []
        for item in self.items:
            item['count'] = 0

        self.ui.Stack.setCurrentWidget(self.ui.pageAutoDeliveryItems)

    def distanceSensor1WhenInRange(self):
        print('distanceSensor1WhenInRange')
        if self.device_mode == 'auto' and self.delivery_state != 'default':
            if self.delivery_state == 'ready':
                self.delivery_state = 'enter'
                print('delivery state changed: ready to enter')
                self.enterDeliveryItem()

            elif self.delivery_state == 'reject':
                self.delivery_state = 'pickup'
                print('delivery state changed: reject to pickup')
                self.pickupDeliveryItem()
            
            else:
                self.delivery_state = 'cancel'
                print('delivery state changed: cancel')
                self.cancelDeliveryItem()

        elif self.device_mode == 'manual':
            self.manualDeliveryRecycleItem()

    def distanceSensor1WhenOutOfRange(self):
        print('distanceSensor1WhenOutOfRange')
        if self.delivery_state == 'enter':
            self.delivery_state = 'recognize'
            print('delivery state changed: enter to recognize')
            self.startDeliveryItem()
        elif self.delivery_state == 'pickup':
            self.delivery_state = 'ready'
            print('delivery state changed: pickup to ready')

    def distanceSensor2WhenInRange(self):
        print('distanceSensor2WhenInRange')
        # if self.delivery_state == 'accept':
        #     self.endDeliveryItem()

    def distanceSensor2WhenOutOfRange(self):
        print('distanceSensor2WhenOutOfRange')

    def pickupDeliveryItem(self):
        print('distanceSensor2WhenOutOfRange')
        try:
            self.cancel_delivery_item_timer.cancel()
            self.conveyor_motor.stop()
        except Exception as e:
            print("error:", e)

    def enterDeliveryItem(self):
        print('enterDeliveryItem')
        try:
            self.conveyor_motor.forward(timer=True)

        except Exception as e:
            print("error:", e)

    def startDeliveryItem(self):
        print('startDeliveryItem')
        try:
            self.conveyor_motor.stop()
            self.auto_delivery_items_thread.start()
            self.auto_delivery_items_timer = Timer(2, self.validationDeliveryItem)
            self.auto_delivery_items_timer.start()
            self.cancel_delivery_item_timer = Timer(delivery_cancel_time, self.cancelDeliveryItem)
            self.cancel_delivery_item_timer.start()
        except Exception as e:
            print("error:", e)

    def rejectDeliveryItem(self):
        print('rejectDeliveryItem')
        self.showNotification(ITEM_NOT_RECOGNIZED_ERROR_MESSAGE)
        sleep(0.01)
        self.conveyor_motor.backward()

    def acceptDeliveryItem(self):
        print('acceptDeliveryItem')
        most_probability_item_index = stats.mode(self.auto_delivery_items_thread.predicted_items).mode[0]
        self.selected_item = self.items[most_probability_item_index]
        print('most probability item:', window.selected_item['name'])

        self.ui.list_auto_delivery_items.insertItem(0, self.selected_item['name'])

        if self.selected_item['category_id'] == 1:
            self.ui.lbl_num_category_1.setText(str(int(self.ui.lbl_num_category_1.text()) + 1))
        elif self.selected_item['category_id'] == 3:
            self.ui.lbl_num_category_3.setText(str(int(self.ui.lbl_num_category_3.text()) + 1))
        elif self.selected_item['category_id'] == 4:
            self.ui.lbl_num_category_4.setText(str(int(self.ui.lbl_num_category_4.text()) + 1))

        self.ui.lbl_total_price_auto_delivery_items.setText(str(int(self.ui.lbl_total_price_auto_delivery_items.text()) + self.selected_item['price']))

        self.conveyor_motor.forward()
        self.end_delivery_items_timer = Timer(self.conveyor_motor_time_2, self.endDeliveryItem)
        self.end_delivery_items_timer.start()
        self.delivery_state = 'end'
        # self.endDeliveryItem()

    def validationDeliveryItem(self):
        print('validationDeliveryItem')
        if self.delivery_state == 'recognize':
            self.delivery_state = 'validate'
            print('delivery state changed: recognize to validate')
    
            sleep(0.1)

            if len(self.auto_delivery_items_thread.predicted_items) > 0:
                self.delivery_state = 'accept'
                print('delivery state changed: validate to accept')
                self.acceptDeliveryItem()
            else:
                self.delivery_state = 'reject'
                print('delivery state changed: validate to reject')
                self.rejectDeliveryItem()

    def cancelDeliveryItem(self):
        self.showNotification(DELIVERY_ERROR_MESSAGE)
        sleep(0.01)
        print('cancelDeliveryItem')
        self.conveyor_motor.stop()
        self.press_motor.stop()
        # self.separation_motor.stop()
        self.delivery_state = 'ready'
        print('delivery state changed: ready')

    def endDeliveryItem(self):
        print('endDeliveryItem')
        if self.delivery_state == 'end':
            try:                
                self.showNotification(RECYCLE_MESSAGE)
                sleep(0.01)
                self.cancel_delivery_item_timer.cancel()

                self.playSound('audio3')
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
                
                self.delivery_state = 'ready'
                self.conveyor_motor.stop()

                try:
                    self.press_motor.forward(True)
                except Exception as e:
                    print("error:", e)
                    ErrorLog.writeToFile(str(e) + ' In press_motor_stop_timer startDeliveryItem Method')

            except Exception as e:
                print("error:", e)
                ErrorLog.writeToFile(str(e) + ' In endDeliveryItem Method')

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
        try: 
            self.showNotification(RECYCLE_MESSAGE)
            self.conveyor_motor.forward(timer=True)
        
            self.playSound('audio3')
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

            try:
                self.press_motor.forward(timer=True)
            except Exception as e:
                print("error:", e)
                ErrorLog.writeToFile(str(e) + ' In press_motor_stop_timer startDeliveryItem Method')

        except Exception as e:
            print("error:", e)
            ErrorLog.writeToFile(str(e) + ' In endDeliveryItem Method')

    def stackManualDeliveryItems(self):
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
            self.delivery_state = 'default'
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
            self.press_motor.stop()
            self.conveyor_motor.stop()
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

    def transferToRFIDCard(self):
        self.showNotification(TRANSFER_TO_RFID_MESSAGE)
        self.rfid_thread.start()

    def successTransferToRFIDCard(self):
        self.stackWalletServices()
        self.showNotification(SUCCESS_TRANSFER_TO_RFID_MESSAGE)

    def plusRFID(self):
        if self.user_wallet < int(self.ui.lbl_payment_rfid.text()):
            self.showNotification(MONEY_ERROR_MESSAGE)
        else:
            self.ui.lbl_transfer_to_rfid.setText(str(int(self.ui.lbl_transfer_to_rfid.text()) + self.money_RFID))
            self.user_wallet -= self.money_RFID
            self.ui.lbl_total_wallet_rfid.setText(str("{:,.0f}".format(self.user_wallet)))

    def minusRFID(self):
        if int(self.ui.lbl_transfer_to_rfid.text()) > 0:
            self.ui.lbl_transfer_to_rfid.setText(str(int(self.ui.lbl_transfer_to_rfid.text()) - self.money_RFID))
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

        self.ui.lbl_transfer_to_rfid.setText('0')
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
        
        result = DataBase.select('device_mode')
        if result == 'manual':
            self.ui.rb_manual_device_mode_setting.setChecked(True)
        elif result == 'auto':
            self.ui.rb_auto_device_mode_setting.setChecked(True)

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
        result = DataBase.select('device_mode')
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
        self.ui.tb_press_motor_time.setText(str(DataBase.select('press_motor_time')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingPressMotor)

    def stackSeparationMotor(self):
        self.ui.lbl_notification.hide()
        # self.ui.tb_separation_motor_forward_port.setText(str(DataBase.select('separation_motor_forward_port')))
        # self.ui.tb_separation_motor_backward_port.setText(str(DataBase.select('separation_motor_backward_port')))
        # self.ui.tb_separation_motor_time.setText(str(DataBase.select('separation_motor_time')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingSeparationMotor)

    def stackSensor1Ports(self):
        self.ui.lbl_notification.hide()
        self.ui.tb_sensor1_trig_port.setText(str(DataBase.select('distance_sensor1_trig_port')))
        self.ui.tb_sensor1_echo_port.setText(str(DataBase.select('distance_sensor1_echo_port')))
        self.ui.tb_sensor1_depth_threshold.setText(str(DataBase.select('distance_sensor1_threshold_distance')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingDistanceSensor1)

    def stackSensor2Ports(self):
        self.ui.lbl_notification.hide()
        self.ui.tb_sensor2_trig_port.setText(str(DataBase.select('distance_sensor2_trig_port')))
        self.ui.tb_sensor2_echo_port.setText(str(DataBase.select('distance_sensor2_echo_port')))
        self.ui.tb_sensor2_depth_threshold.setText(str(DataBase.select('distance_sensor2_threshold_distance')))
        self.ui.StackSetting.setCurrentWidget(self.ui.pageSettingDistanceSensor2)

    def stackConveyorPort(self):
        self.ui.lbl_notification.hide()
        self.ui.tb_conveyor_motor_forward_port.setText(str(DataBase.select('conveyor_motor_forward_port')))
        self.ui.tb_conveyor_motor_backward_port.setText(str(DataBase.select('conveyor_motor_backward_port')))
        self.ui.tb_conveyor_motor_time_1.setText(str(DataBase.select('conveyor_motor_time')))
        self.ui.tb_conveyor_motor_time_2.setText(str(DataBase.select('conveyor_motor_time_2')))
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
        if self.ui.rb_manual_device_mode_setting.isChecked():
            DataBase.update('device_mode', 'manual')
        elif self.ui.rb_auto_device_mode_setting.isChecked():
            DataBase.update('device_mode', 'auto')
        self.device_mode = DataBase.select('device_mode')
        
        if self.ui.tb_sensor1_trig_port.text() != '':
            result = DataBase.update('distance_sensor1_trig_port', self.ui.tb_sensor1_trig_port.text())
        if self.ui.tb_sensor1_echo_port.text() != '':
            result = DataBase.update('distance_sensor1_echo_port', self.ui.tb_sensor1_echo_port.text())
        if self.ui.tb_sensor1_depth_threshold.text() != '':
            result = DataBase.update('distance_sensor1_threshold_distance', self.ui.tb_sensor1_depth_threshold.text())

        if self.ui.tb_sensor2_trig_port.text() != '':
            result = DataBase.update('distance_sensor2_trig_port', self.ui.tb_sensor2_trig_port.text())
        if self.ui.tb_sensor2_echo_port.text() != '':
            result = DataBase.update('distance_sensor2_echo_port', self.ui.tb_sensor2_echo_port.text())
        if self.ui.tb_sensor2_depth_threshold.text() != '':
            result = DataBase.update('distance_sensor2_threshold_distance', self.ui.tb_sensor2_depth_threshold.text())

        if self.ui.tb_press_motor_forward_port.text() != '':
            result = DataBase.update('press_motor_forward_port', self.ui.tb_press_motor_forward_port.text())
        if self.ui.tb_press_motor_backward_port.text() != '':
            result = DataBase.update('press_motor_backward_port', self.ui.tb_press_motor_backward_port.text())
        if self.ui.tb_press_motor_time.text() != '':
            result = DataBase.update('press_motor_time', self.ui.tb_press_motor_time.text())
    
        # if self.ui.tb_separation_motor_forward_port.text() != '':
        #     result = DataBase.update('separation_motor_forward_port', self.ui.tb_separation_motor_forward_port.text())
        # if self.ui.tb_separation_motor_backward_port.text() != '':
        #     result = DataBase.update('separation_motor_backward_port', self.ui.tb_separation_motor_backward_port.text())
        # if self.ui.tb_separation_motor_time.text() != '':
        #     result = DataBase.update('separation_motor_time', self.ui.tb_separation_motor_time.text())
     
        if self.ui.tb_conveyor_motor_forward_port.text() != '':
            result = DataBase.update('conveyor_motor_forward_port', self.ui.tb_conveyor_motor_forward_port.text())
        if self.ui.tb_conveyor_motor_backward_port.text() != '':
            result = DataBase.update('conveyor_motor_backward_port', self.ui.tb_conveyor_motor_backward_port.text())
        if self.ui.tb_conveyor_motor_time_1.text() != '':
            result = DataBase.update('conveyor_motor_time', self.ui.tb_conveyor_motor_time_1.text())
        if self.ui.tb_conveyor_motor_time_2.text() != '':
            result = DataBase.update('conveyor_motor_time_2', self.ui.tb_conveyor_motor_time_2.text())
        
        self.initHardwares()

    def exitProgram(self):
        Server.turnOffSystemSMS(self.owner, self.system)
        self.delivery_item_flag = False
        self.close()
        QApplication.quit()


if __name__ == '__main__':

    os.environ["QT_QPA_FB_FORCE_FULLSCREEN"] = "0"
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    os.environ["QT_QPA_FONTDIR"] = "/fonts"
    # os.environ["ESCPOS_CAPABILITIES_FILE"] = "/usr/python-escpos/capabilities.json"
    mixer.init()
    qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
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
