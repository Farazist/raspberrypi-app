import sys
import os
from threading import Thread
from PySide2.QtCore import Qt, QTimer, QDate, QTime, QSize
from PySide2.QtWidgets import QApplication, QDialog, QSizePolicy, QMessageBox, QPushButton, QVBoxLayout
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QMovie, QPixmap, QFont, QIcon, QImage
from functools import partial
import qrcode
from PIL.ImageQt import ImageQt
from escpos.printer import Usb
from gpiozero import LightSensor, LED
from gpiozero.pins.native import NativeFactory
from time import sleep, time

from server import Server
from database import DataBase
from image_classifier import ImageClassifier

__author__ = "Sara Zarei, Sajjad Aemmi"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.1.5"
__email__ = "sajjadaemmi@gmail.com"
__status__ = "Production"

class MainWindow(QDialog):
   
    def __init__(self):
        super(MainWindow, self).__init__()

        loader = QUiLoader()
        self.ui = loader.load('main.ui', self)

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ui.btnLeft.setSizePolicy(sp_retain)
        self.ui.btnRight.setSizePolicy(sp_retain) 
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)
        self.ui.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog)
        self.ui.showMaximized()

        self.system_id = DataBase.select('system_id')[2]
        self.system = Server.getSystem(self.system_id)

        self.camera = None
        self.device_mode = DataBase.select('bottle_recognize_mode')[2]
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
        mobile_number = self.ui.tbUserMobileNumber.text()
        password = self.ui.tbUserPassword.text()

        self.user = Server.signInUser(mobile_number, password)

        if self.user != None:
            self.stackMainMenu()
        else:
            print("mobile number or password is incurrect")
            self.ui.lblErrorUser.show()

    def signOutUser(self):
        self.user = None
        self.stackStart()

    def signInAdmin(self):
        if DataBase.select('username') == self.ui.tbAdminUsername.text() and DataBase.select('password') == self.ui.tbAdminPassword.text():
            self.stackSetting()
        else:
            self.ui.lblErrorAdmin.setText('نام کاربری یا رمز عبور صحیح نیست')

    def adminRecovery(self):
        self.ui.lblErrorAdmin.setText('لطفا با واحد پشتیبانی فرازیست تماس حاصل فرمایید')

    def detectItem(self):      
        predict_item_list = []
        categories_count = np.zeros(len(self.categories), np.uint8)

        time = 0
    
        self.predict_item_flag = False
        self.delivery_items_flag = True
        while self.delivery_items_flag:
            try:
                time += 1
                if time == 30:
                    time = 0

                    if self.camera is None or not self.camera.isOpened():
                        print("error: camera not found")
                        return      

                    _, frame = self.camera.read()
      
                    prediction = self.image_classifier.predict(frame)
                    #prediction = np.random.rand(1, 20)

                    if np.max(prediction) > 0.5:
                        predicted = np.argmax(prediction)
                        print(self.items[predicted])

                        window.lb_2_s4.setText(self.items[predicted]['name'])

                    if self.predict_item_flag == False:
                        predict_item_list.append(predicted)

                    if self.predict_item_flag == True:
                        most_probability_item = stats.mode(predict_item_list).mode[0]

                        print('most probability item:', most_probability_item)

                        category_index = self.items[most_probability_item]['category_id'] - 1
                        categories_count[category_index] += 1

                        for i in range(len(categories_count)):
                            window.grid_widget_s4[2][i].setText(str(categories_count[i]))

                        for item in self.user_items:
                            if item['id'] == self.items[most_probability_item]['id']:
                                item['count'] += 1
                                break
                        else:
                            self.user_items.append(self.items[most_probability_item])
                            self.user_items[-1]['count'] = 1

                        predict_item_list = []
                        self.predict_item_flag = False

            except Exception as e:
                print("error:", e)

        self.camera.release()

    def stackStart(self):
        self.setButton(self.ui.btnLeft, show=False)
        self.setButton(self.ui.btnRight, show=False)

        gif_start = QMovie("animations/return.gif")
        self.ui.lblGifStart.setMovie(gif_start)
        gif_start.start()

#        self.ui.lblGifStart.mousePressEvent  = self.stackLoginMethod()
        self.ui.btnHere.clicked.connect(self.stackLoginMethod)

        self.ui.Stack.setCurrentIndex(1)

    def stackLoginMethod(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)

        self.ui.btnSignInUserMobileNumber.clicked.connect(self.stackUserLogin)
        self.ui.btnSignInUserQrCode.clicked.connect(self.stackQRCode)

        self.ui.Stack.setCurrentIndex(12)

    def stackUserLogin(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)

        self.ui.lblErrorUser.hide()
        # self.ui.btnLeft.clicked.connect(self.back)
        self.ui.btnUserLogin.clicked.connect(self.signInUser)

        self.ui.Stack.setCurrentIndex(2)

    def makeQRCode(self):
        while self.qrcode_flag:
            qrcode_signin_token = Server.makeQrcodeSignInToken(self.system['id'])
            qrcode_img = qrcode.make(qrcode_signin_token)
            self.ui.lblPixmapQr.setPixmap(QPixmap.fromImage(ImageQt(qrcode_img)))
        
            time_end = time() + 30
            while time() < time_end:
                self.user = Server.checkQrcodeSignInToken(qrcode_signin_token)
                if self.user:
                    self.qrcode_flag = False
                    break
                sleep(5)
        
        if self.user:
            self.stackMainMenu()
        else:
            self.stackStart()

    def stackQRCode(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)

        self.qrcode_flag = True
        self.qrcode_thread = Thread(target=self.makeQRCode)
        self.qrcode_thread.start()
        
        self.ui.Stack.setCurrentIndex(8)

    def stackMainMenu(self):
        self.setButton(self.ui.btnLeft, function=self.signOutUser, text='خروج', icon='images/icon/log-out.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)

        # self.ui.btnMainMenu_1.clicked.connect(self.stackDeliveryItems)
        self.ui.btnMainMenu_1.clicked.connect(self.checkDeviceMode)
        self.ui.btnMainMenu_2.clicked.connect(self.stackWallet)

        self.ui.Stack.setCurrentIndex(3)

    def stackAdminLogin(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)

        self.ui.btnAdminLogin.clicked.connect(self.signInAdmin)
        self.ui.btnAdminPassRecovery.clicked.connect(self.adminRecovery)

        self.ui.Stack.setCurrentIndex(4)

    def stackWallet(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)

        gif_wallet = QMovie("animations/wallet.gif")
        gif_wallet.setScaledSize(QSize().scaled(450, 450, Qt.KeepAspectRatio))
        self.ui.lblGifWallet.setMovie(gif_wallet)
        gif_wallet.start()

        self.ui.lblWallet.setText(str(self.user['wallet']))

        # self.ui.btnLeft.clicked.connect(self.back)

        self.ui.Stack.setCurrentIndex(5)

    def stackDeliveryItems(self):
        self.ui.btnLeft.hide()
        self.ui.btnRight.hide()
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)

        img1 = QPixmap("images\item\category1.png")
        img1 = img1.scaledToWidth(128)
        img1 = img1.scaledToHeight(128)
        self.ui.lblPixmapCategory1.setPixmap(img1)

        img2 = QPixmap("images\item\category2.png")
        img2 = img2.scaledToWidth(128)
        img2 = img2.scaledToHeight(128)
        self.ui.lblPixmapCategory2.setPixmap(img2)

        img3 = QPixmap("images\item\category3.png")
        img3 = img3.scaledToWidth(128)
        img3 = img3.scaledToHeight(128)
        self.ui.lblPixmapCategory3.setPixmap(img3)

        img4 = QPixmap("images\item\category4.png")
        img4 = img4.scaledToWidth(128)
        img4 = img4.scaledToHeight(128)
        self.ui.lblPixmapCategory4.setPixmap(img4)

        self.camera = VideoCapture(0)
        
        if self.camera is None or not self.camera.isOpened():
            print("error: camera not found")
            # self.message_box('دوربین پیدا نشد')    
            return      

        self.detect_thread = Thread(target=self.detectItem)
        self.detect_thread.start()

        self.ui.btnDeliveryItemsNext.clicked.connect(partial(self.changePredictItemFlag, True))

        self.ui.Stack.setCurrentIndex(6)
        self.widget_index_stack.append(6)

    def SelectItem(self, item):
        self.selected_item = item
        self.ui.lblSelectedItemName.setText(self.selected_item['name'])
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

    def hideRecycleItem(self):
        nowDate = QDate.currentDate()
        date = nowDate.toString(Qt.DefaultLocaleLongDate)

        nowTime = QTime.currentTime()
        time = nowTime.toString(Qt.DefaultLocaleLongDate)

        self.ui.date.setText(date)
        self.ui.time.setText(time)

        self.ui.lblRecycledDone.hide()

    def sensorTest(self):
        try:
            while True:
                self.sensor.wait_for_light()
                print("bottle detected!")
                self.sensor.wait_for_dark()
                sleep(1)
        except:
            print('There is a problem for GPIO')

    def stackManualDeliveryItems(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, function=self.stackAfterDelivery, text='پایان', icon='images/icon/tick.png', show=True)
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)
     
        self.ui.lblRecycledDone.hide()

        self.ui.btnRecycleItem.clicked.connect(self.recycleItem)

        self.user_items = []
        self.items = Server.getItems(self.system['owner_id'])
        self.layout_SArea = QVBoxLayout()

        for item in self.items:
            item['count'] = 0

            btn = QPushButton()
            btn.setMinimumHeight(60)
            btn.setText(item['name'])
            btn.setStyleSheet('QPushButton { background-color: rgb(246, 253, 250) } QPushButton:pressed { background-color: #9caf9f } QPushButton {border: 2px solid #1E5631} QPushButton {border-radius: 6px} QPushButton{font: 20pt "IRANSans";}')
            btn.clicked.connect(partial(self.SelectItem, item))
            self.layout_SArea.addWidget(btn)

        self.SelectItem(self.items[0])  # default
        self.ui.scrollAreaWidgetManual.setLayout(self.layout_SArea)

        self.ui.Stack.setCurrentIndex(9)

        try:
            self.motor_port = int(DataBase.select('motor_port')[2])
            self.sensor_port = int(DataBase.select('sensor_port')[2])
            self.motor = LED(self.motor_port, pin_factory=factory)
            self.sensor = LightSensor(self.sensor_port, pin_factory=factory)
            print('motor on')
            self.motor.on()
        except:
            print('There is a problem for GPIO')

        self.sensorTest_thread = Thread(target=self.sensorTest)
        self.sensorTest_thread.start()

    def stackSetting(self):
        self.setButton(self.ui.btnLeft, function=self.stackStart, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, function=self.saveSetting, text='ذخیره', icon='images/icon/save.png', show=True)
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=False)

        self.ui.btnSetting1.clicked.connect(self.stackDeviceMode)
        self.ui.btnSetting5.clicked.connect(self.stackDisableDevice)
        self.ui.btnSetting2.clicked.connect(self.stackMotorPort)
        self.ui.btnSetting3.clicked.connect(self.stackSensorPort)
        self.ui.btnSetting6.clicked.connect(self.stackExitApp)

        self.ui.Stack.setCurrentIndex(7)

    def stackDisableDevice(self):
        self.ui.btnLeft.hide()
        self.ui.btnRight.hide()
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)

        self.ui.Stack.setCurrentIndex(10)

    def checkDeviceMode(self):
        if self.device_mode == 'manual':
            self.stackManualDeliveryItems()
        if self.device_mode == 'auto':
            self.stackDeliveryItems()
    
    def stackDeviceMode(self): 
#        self.ui.btnManualDevice.setStyleSheet('QRadioButton::indicator {width: 30px; height: 30px;image:url(images/icon/cancle.png);}')
        self.ui.btnAutoDevice.toggled.connect(self.selectDeviceMode)
        self.ui.StackSetting.setCurrentIndex(1)
    
    def selectDeviceMode(self):
        if self.ui.btnManualDevice.isChecked()==True:
            result = DataBase.update('bottle_recognize_mode', 'manual')
            print('دستی')
        if self.ui.btnAutoDevice.isChecked() == True:
            result = DataBase.update('bottle_recognize_mode', 'auto')
            print('اتومات')

    def stackExitApp(self):
        self.ui.btnNExitApp.clicked.connect(self.stackSetting)
        self.ui.btnYExitApp.clicked.connect(self.exit_program)
        self.ui.StackSetting.setCurrentIndex(2)

    def stackMotorPort(self):
        self.ui.tbMotorPort.setText(str(DataBase.select('motor_port')[2]))
        self.ui.StackSetting.setCurrentIndex(3)

    def stackSensorPort(self):
        self.ui.tbSensorPort.setText(str(DataBase.select('sensor_port')[2]))
        self.ui.StackSetting.setCurrentIndex(4)

    def printReceipt(self):
        try:
            print("printing...")
            printer = Usb(idVendor=0x0416, idProduct=0x5011, timeout=0, in_ep=0x81, out_ep=0x03)
            printer.image("images/logo-small.png")
            printer.set(align=u'center')
            printer.text("Farazist\n")
            printer.text(str(12500) + " Rial")
            # printer.barcode('1324354657687', 'EAN13', 64, 2, '', '')
            # printer.qr('content', ec=0, size=3, model=2, native=False, center=False, impl=u'bitImageRaster')
            printer.text(self.system['owner']['mobile_number'])
            printer.text("farazist.ir\n")
            printer.cut()
        except:
            print("Printer not found")
        
        self.stackMainMenu()

    def stackAfterDelivery(self):
        self.setButton(self.ui.btnLeft, function=self.stackMainMenu, text='بازگشت', icon='images/icon/back.png', show=True)
        self.setButton(self.ui.btnRight, show=False)
        self.setButton(self.ui.btnSetting, function=self.stackAdminLogin, show=True)

#        self.ui.btnPrintReceiptNo.clicked.connect(self.back)
        self.ui.btnPrintReceiptYes.clicked.connect(self.printReceipt)

        self.total_price = 0
        for user_item in self.user_items:
            self.total_price += user_item['price'] * user_item['count']
        
        self.ui.lblTotalPrice.setText(str(self.total_price))
        # self.delivery_items_flag = False
        
        Server.addNewDelivery(self.user, self.system['id'], self.user_items)
        Server.transferSecure(self.user, self.system['id'], self.total_price)
        self.user = Server.getUser(self.user)
       
        try:
            self.motor.off()
        except:
            print('There is a problem for GPIO')

        self.ui.Stack.setCurrentIndex(11)
        self.widget_index_stack.append(11)

    def changePredictItemFlag(self, value):
        self.predict_item_flag = value
        self.ui.lblDeliveryItems.clear()

    def saveSetting(self):
         if self.ui.tbSensorPort.text() != '':
            result = DataBase.update('sensor_port', self.ui.tbSensorPort.text())

         if self.ui.tbMotorPort.text() != '':
            result = DataBase.update('motor_port', self.ui.tbMotorPort.text())

    def exit_program(self):
        self.delivery_items_flag = False
        # self.camera.release()
        self.close()
        # QApplication.quit()

    def exitMessageBox(self):
        btnFont = QFont('IRANSans', 16)
        lblFont = QFont('IRANSans', 18)
        btnOkStyle = 'background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E5631, stop:1 #2ea444); color: #ffffff; padding: 3px; border: none; border-radius: 6px;'
        btnNoStyle = 'background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e11c1c, stop:1 #f86565);color: #ffffff; padding: 3px; border: none; border-radius: 6px;'

        box = QMessageBox()
        box.setStyleSheet("QPushButton{min-width: 60px; min-height: 40px;}")
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle('!فرازیست')
        box.setText('از برنامه خارج می شوید؟')
        box.setFont(lblFont)
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)

        buttonY = box.button(QMessageBox.Yes)
        buttonY.setText('بله')
        buttonY.setFont(btnFont)
        buttonY.setStyleSheet(btnOkStyle)
        buttonY.setMinimumSize(60,30)
        
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('خیر')
        buttonN.setFont(btnFont)
        buttonN.setStyleSheet(btnNoStyle)
        buttonN.setMinimumSize(60,30)

        box.exec_()
        if box.clickedButton() == buttonY:
            self.exit_program()
        elif box.clickedButton() == buttonN:
            box.close()

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
