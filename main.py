import sys
import os
from cv2 import VideoCapture, cvtColor, resize, destroyAllWindows, COLOR_BGR2RGB
from threading import Thread
import numpy as np
from scipy import stats
from PySide2.QtCore import Qt, QTimer
from PySide2.QtWidgets import QApplication, QDialog, QSizePolicy, QMessageBox, QPushButton, QVBoxLayout, QLabel
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QMovie, QPixmap, QFont, QIcon
from functools import partial
import pyqrcode
from escpos.printer import Usb

from database import DataBase
from app import *
from aescipher import AESCipher
from local_database import LocalDataBase
from image_classifier import ImageClassifier

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

class MainWindow(QDialog):
   
    def __init__(self):
        super(MainWindow, self).__init__()

        self.widget_index_stack = []

        loader = QUiLoader()
        self.ui = loader.load('main.ui', self)

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ui.btnBack.setSizePolicy(sp_retain)
        self.ui.btnBack.clicked.connect(self.back_window)
        self.ui.btnTick.setSizePolicy(sp_retain) 

        self.ui.setWindowFlags(Qt.FramelessWindowHint|Qt.Dialog)
        self.ui.showMaximized()

        self.system_id = LocalDataBase.selectOne('system_id')[2]
        self.system = DataBase.getSystem(self.system_id)

        self.camera = None
        self.user_items = []
        self.device_mode = LocalDataBase.selectOne('bottle_recognize_mode')[2]
        print(self.device_mode)
        self.categories = DataBase.getCategories()
        self.image_classifier = ImageClassifier()

    def loginUser(self):
        mobile_number = self.ui.tbUserMobileNumber.text()
        password = self.ui.tbUserPassword.text()

        self.user = DataBase.signInUser(mobile_number, password)

        if self.user != None:
            self.stackMainMenu()
        else:
            print("mobile number or password is incurrect")
            self.ui.lblErrorUser.show()

    def loginAdmin(self):
#        mobile_number = self.ui.tbAdminLogin.text()
#        password = self.ui.tbAdminPassword.text()

##        if mobile_number == 1234 and password == 1234:
##            self.stackSetting()

#        else:
#            self.ui.lblErrorAdmin.setText('نام کاربری یا رمز عبور صحیح نیست.')
        self.stackSetting()

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
        destroyAllWindows()

    def stackStart(self):
        self.ui.btnBack.hide()
        self.ui.btnTick.hide()

        gif_start = QMovie("animations/return.gif")
        self.ui.lblGifStart.setMovie(gif_start)
        gif_start.start()

        self.ui.btnSettingStart.clicked.connect(self.stackAdminLogin)

        self.ui.btnLoginMobileNumber.clicked.connect(self.stackUserLogin)

        self.ui.btnLoginQrCode.clicked.connect(self.stackQR)

        self.ui.Stack.setCurrentIndex(1)
        self.widget_index_stack.append(1)

    def stackUserLogin(self):
        self.ui.btnBack.show()
        self.ui.btnBack.setText('انصراف')
        self.ui.btnBack.setIcon(QIcon('images/sign/cancle.png'))
        self.ui.btnTick.hide()

        self.ui.lblErrorUser.hide()
        
        self.ui.btnSettingUserLogin.clicked.connect(self.stackAdminLogin)
        # self.ui.btnBack.clicked.connect(self.back_window)

        self.ui.btnUserLogin.clicked.connect(self.loginUser)

        self.ui.Stack.setCurrentIndex(2)
        self.widget_index_stack.append(2)

    def stackMainMenu(self):
        self.ui.btnBack.show()
        self.ui.btnBack.setText('خروج')
        self.ui.btnBack.setIcon(QIcon('images/sign/cancle'))
        self.ui.btnTick.hide()
        
        self.ui.btnSettingMainMenu.clicked.connect(self.stackAdminLogin)

        # self.ui.btnMainMenu_1.clicked.connect(self.stackDeliveryItems)
        self.ui.btnMainMenu_1.clicked.connect(self.checkDeviceMode)
        self.ui.btnMainMenu_2.clicked.connect(self.stackWallet)

        self.ui.Stack.setCurrentIndex(3)
        self.widget_index_stack.append(3)

    def stackAdminLogin(self):
        self.ui.btnBack.show()
        self.ui.btnBack.setText('انصراف')
        self.ui.btnBack.setIcon(QIcon('images/sign/cancle.png'))
        self.ui.btnTick.hide()

#        self.ui.btnAdminLogin.clicked.connect(self.stackSetting)
        self.ui.btnAdminLogin.clicked.connect(self.loginAdmin)
        self.ui.btnAdminPassRecovery.clicked.connect(self.adminRecovery)

        self.ui.Stack.setCurrentIndex(4)
        self.widget_index_stack.append(4)

    def stackWallet(self):
        self.ui.btnBack.show()
        self.ui.btnBack.setText('بازگشت')
        self.ui.btnBack.setIcon(QIcon('images/sign/back'))
        self.ui.btnTick.hide()

        gif_wallet = QMovie("animations/wallet.gif")
        self.ui.lblGifWallet.setMovie(gif_wallet)
        gif_wallet.start()

        self.ui.lblWallet.setText(str(self.user['wallet']))

        self.ui.btnSettingWallet.clicked.connect(self.stackAdminLogin)
        # self.ui.btnBack.clicked.connect(self.back_window)

        self.ui.Stack.setCurrentIndex(5)
        self.widget_index_stack.append(5)

    def stackDeliveryItems(self):
        self.ui.btnBack.hide()
        self.ui.btnTick.hide()

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
        self.ui.btnSettingAutoDelivery.clicked.connect(self.stackAdminLogin)

        self.ui.Stack.setCurrentIndex(6)
        self.widget_index_stack.append(6)

    def setCurrentItem(self, item_name, item_index):
        self.ui.lblSelectedItem.setText(item_name)

    def showRecycledText(self):
        self.ui.lblRecycledDone.show()

    def stackManualDeliveryItems(self):
        self.ui.btnBack.hide()
        self.ui.btnTick.hide()
        self.ui.lblRecycledDone.hide()
        self.ui.btnFinishDelivery.clicked.connect(self.finishDelivery)
        self.ui.btnSettingManualDelivery.clicked.connect(self.stackAdminLogin)
        self.ui.btnNextManual.clicked.connect(self.showRecycledText)


        self.items = DataBase.getItems(self.system['owner_id'])
        self.layout_SArea = QVBoxLayout()


        for item in self.items:
            btn = QPushButton()
            btn.setMinimumHeight(60)
            btn.setText(item['name'])
            btn.setStyleSheet('QPushButton { background-color: rgb(246, 253, 250) } QPushButton:pressed { background-color: #9caf9f } QPushButton {border: 2px solid #1E5631} QPushButton {border-radius: 6px} QPushButton{font: 20pt "IRANSans";}')
            btn.clicked.connect(partial(self.setCurrentItem,item['name'], item['id']))
            self.layout_SArea.addWidget(btn)

        self.ui.scrollAreaWidgetManual.setLayout(self.layout_SArea)

        self.ui.Stack.setCurrentIndex(9)
        self.widget_index_stack.append(9)

    def stackSetting(self):
        self.ui.btnBack.hide()
        self.ui.btnTick.show()
        self.ui.btnTick.setText('تایید')
        self.ui.btnTick.setIcon(QIcon('images/sign/tick'))

        self.ui.btnSetting1.clicked.connect(self.stackDeviceMode)
        self.ui.btnSetting5.clicked.connect(self.stackDisableDevice)
        self.ui.btnSetting6.clicked.connect(self.stackExitApp)

        self.ui.btnTick.clicked.connect(self.tick_window)

        self.ui.Stack.setCurrentIndex(7)

    def stackQR(self):
        self.ui.btnBack.show()
        self.ui.btnBack.setText('انصراف')
        self.ui.btnBack.setIcon(QIcon('images/sign/cancle'))
        self.ui.btnTick.hide()

        data = "https://farazist.ir/@ngengesenior/qr-codes-generation-with-python-377735be6c5f"
        filename = 'images\qr\qrcode.png'

        url = pyqrcode.create(data)
        url.png(filename, scale=6, background='#f6fdfa')
    
        open_img = QPixmap(filename)
        self.ui.lblPixmapQr.setPixmap(open_img)

        self.ui.btnSettingQr.clicked.connect(self.stackAdminLogin)
        # self.ui.btnBack.clicked.connect(self.back_window)

        self.ui.Stack.setCurrentIndex(8)
        self.widget_index_stack.append(8)

    def stackDisableDevice(self):
        self.ui.btnBack.hide()
        self.ui.btnTick.hide()

        self.ui.Stack.setCurrentIndex(10)

    def checkDeviceMode(self):
        if self.device_mode == 'manual':
            self.stackManualDeliveryItems()
        if self.device_mode == 'auto':
            self.stackDeliveryItems()
    
    def stackDeviceMode(self): 
        self.ui.btnAutoDevice.toggled.connect(self.test)

        self.ui.StackSetting.setCurrentIndex(1)
    
    def test(self):
        if self.ui.btnManualDevice.isChecked()==True:
            result = LocalDataBase.updateOne('bottle_recognize_mode', 'manual')
            print('دستی')
        if self.ui.btnAutoDevice.isChecked() == True:
            result = LocalDataBase.updateOne('bottle_recognize_mode', 'auto')
            print('اتومات')

    def stackExitApp(self):
        self.ui.btnNExitApp.clicked.connect(self.noExitApp)
        self.ui.btnYExitApp.clicked.connect(self.exit_program)
        self.ui.StackSetting.setCurrentIndex(2)

    def noExitApp(self):
        self.ui.StackSetting.setCurrentIndex(0)






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

    def finishDelivery(self):
        self.printReceipt()
        # self.delivery_items_flag = False
        
        # DataBase.addNewDelivery(self.user, system_id, self.user_items)    
        # total_price = 0
        # for item in self.user_items:
        #     total_price += item['price'] * item['count']
        # DataBase.transferSecure(self.user, system_id, total_price)
        # self.user = DataBase.getUser(self.user)
        # self.showMainMenu()    

    def changePredictItemFlag(self, value):
        self.predict_item_flag = value
        self.ui.lblDeliveryItems.clear()

    def showIsLoading(self):
        self.lb_logo.hide()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(0)
        self.widget_index_stack.append(0)

    def showStart(self):
        self.lb_logo.show()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(1)
        self.widget_index_stack.append(1)

    def showLogin(self):
        self.lb_logo.show()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(2)
        self.widget_index_stack.append(2)

    def showLoginPhoneNumber(self):
        self.lb_logo.show()
        self.btn_back.show()

        self.Stack.setCurrentIndex(2)
        self.widget_index_stack.append(2)

    def showDelivery(self):
        self.lb_logo.show()
        self.btn_back.hide()
        self.btn_tick.hide()

        self.camera = VideoCapture(0)
        
        if self.camera is None or not self.camera.isOpened():
            print("error: camera not found")
            self.message_box('دوربین پیدا نشد')    
            return      

        self.detect_thread = Thread(target=self.detectItem)
        self.detect_thread.start()
        self.Stack.setCurrentIndex(5)
        self.widget_index_stack.append(5)

    def back_window(self):
        if self.ui.Stack.currentIndex() == 2:
            self.stackStart()

        if self.ui.Stack.currentIndex() == 3:
            self.stackStart()

        if self.ui.Stack.currentIndex() == 4:
            self.ui.lblErrorAdmin.clear()
            self.stackStart()

        if self.ui.Stack.currentIndex() == 5:
            self.stackMainMenu()

        if self.ui.Stack.currentIndex() == 8:
            self.stackStart()
        
    def tick_window(self):
        if self.ui.Stack.currentIndex() == 7:
            self.stackStart()

    def exit_program(self):
        self.delivery_items_flag = False
#        self.camera.release()
        destroyAllWindows()
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
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.stackStart()
    sys.exit(app.exec_())
