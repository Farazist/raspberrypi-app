import sys
import os
from cv2 import VideoCapture, cvtColor, resize, destroyAllWindows, COLOR_BGR2RGB
from threading import Thread
import numpy as np
from scipy import stats
from PySide2.QtWidgets import QApplication, QDialog, QSizePolicy, QMessageBox, QPushButton
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QMovie, QPixmap, QFont
from functools import partial
import pyqrcode
from escpos import printer

from database import Database
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
        self.ui.btnTick.setSizePolicy(sp_retain)        

        self.ui.showMaximized()

        self.camera = None
        self.user_items = []
        self.device_mode = LocalDataBase.selectOne('bottle_recognize_mode')[2]
        print(self.device_mode)
        # self.items = Database.getItems()
        self.categories = Database.getCategories()
        self.image_classifier = ImageClassifier()

    def afterDelivery(self):
        
        try:
            printer = printer.Usb(idVendor=0x0416, idProduct=0x5011)
            printer.image("logo.png")
            printer.text("فرازیست\n")
            printer.barcode('1324354657687', 'EAN13', 64, 2, '', '')
            printer.qr('content', ec=0, size=3, model=2, native=False, center=False, impl=u'bitImageRaster')
            printer.cut()
        except:
            print("Printer not found")


    def loginUser(self):
        mobile_number = self.ui.tbUserMobileNumber.text()
        password = self.ui.tbUserPassword.text()

        self.user = Database.signInUser(mobile_number, password)

        if self.user != None:
            self.stackMainMenu()
        else:
            print("mobile number or password is incurrect")
            self.ui.lblErrorUser.show()

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
        self.ui.btnTick.hide()

        self.ui.lblErrorUser.hide()
        
        self.ui.btnSettingUserLogin.clicked.connect(self.stackAdminLogin)

        self.ui.btnUserLogin.clicked.connect(self.loginUser)

        self.ui.Stack.setCurrentIndex(2)
        self.widget_index_stack.append(2)

    def stackMainMenu(self):
        self.ui.btnBack.show()
        self.ui.btnTick.hide()
        
        self.ui.btnSettingMainMenu.clicked.connect(self.stackAdminLogin)

        # self.ui.btnMainMenu_1.clicked.connect(self.stackDeliveryItems)
        self.ui.btnMainMenu_1.clicked.connect(self.checkDeviceMode)
        self.ui.btnMainMenu_2.clicked.connect(self.stackWallet)

        self.ui.Stack.setCurrentIndex(3)
        self.widget_index_stack.append(3)

    def stackAdminLogin(self):
        self.ui.btnBack.show()
        self.ui.btnTick.hide()

        self.ui.btnAdminLogin.clicked.connect(self.stackSetting)

        self.ui.Stack.setCurrentIndex(4)
        self.widget_index_stack.append(4)

    def stackWallet(self):
        self.ui.btnBack.show()
        self.ui.btnTick.hide()

        gif_wallet = QMovie("animations/wallet.gif")
        self.ui.lblGifWallet.setMovie(gif_wallet)
        gif_wallet.start()

        self.ui.lblWallet.setText(str(self.user['wallet'])+ ' ' +'تومان')

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

        self.ui.Stack.setCurrentIndex(6)
        self.widget_index_stack.append(6)



    def stackManualDeliveryItems(self):
        self.ui.btnBack.hide()
        self.ui.btnTick.hide()


        self.ui.Stack.setCurrentIndex(9)
        self.widget_index_stack.append(9)

    def stackSetting(self):
        self.ui.btnBack.hide()
        self.ui.btnTick.show()

        self.ui.pushButton1.clicked.connect(self.stackDeviceMode)
        self.ui.pushButton2.clicked.connect(self.stackPort)

        self.ui.Stack.setCurrentIndex(7)

    def stackQR(self):
        self.ui.btnBack.show()
        self.ui.btnTick.hide()

        data = "https://farazist.ir/@ngengesenior/qr-codes-generation-with-python-377735be6c5f"
        filename = 'images\qr\qrcode.png'

        url = pyqrcode.create(data)
        url.png(filename, scale=6, background='#f6fdfa')
    
        open_img = QPixmap(filename)
        self.ui.lblPixmapQr.setPixmap(open_img)

        self.ui.btnSettingQr.clicked.connect(self.stackAdminLogin)

        self.ui.Stack.setCurrentIndex(8)
        self.widget_index_stack.append(8)

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

    def stackPort(self):
        print('aksdshdsfghghdsdstd')
        self.ui.StackSetting.setCurrentIndex(1)

    def finishDelivery(self):
        self.delivery_items_flag = False
        system_id = LocalDataBase.selectOne('system_id')[2]
        Database.addNewDelivery(self.user, system_id, self.user_items)    
        total_price = 0
        for item in self.user_items:
            total_price += item['price'] * item['count']
        Database.transferSecure(self.user, system_id, total_price)
        self.user = Database.getUser(self.user)
        self.showMainMenu()    

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
        self.delivery_items_flag = False
        if self.camera: 
            self.camera.release()

        self.btn_tick.hide()
        self.btn_back.show()    

        self.widget_index_stack.pop()

        if self.widget_index_stack[-1] == 0:
            self.lb_logo.hide()
            self.btn_back.hide()
        if self.widget_index_stack[-1] == 1:
            self.btn_back.hide()

        self.Stack.setCurrentIndex(self.widget_index_stack[-1])

    def tick_window(self):
        self.widget_index_stack.pop()

        if self.widget_index_stack[-1] == 1:
            self.btn_back.hide()
            self.btn_tick.hide()
        elif self.widget_index_stack[-1] == 2:
            self.btn_back.show()
            self.btn_tick.hide()
        elif self.widget_index_stack[-1] == 3:
            self.btn_back.show()
            self.btn_tick.hide()
        elif self.widget_index_stack[-1] == 4:
            self.btn_back.hide()
            self.btn_tick.show()
        elif self.widget_index_stack[-1] == 5:
            self.btn_back.show()
            self.btn_tick.hide()

        self.Stack.setCurrentIndex(self.widget_index_stack[-1])

    def exit_program(self):
        self.delivery_items_flag = False
        self.camera.release() 
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
