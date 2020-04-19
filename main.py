import sys
import os
from cv2 import VideoCapture, cvtColor, resize, destroyAllWindows, COLOR_BGR2RGB
from threading import Thread
import numpy as np
from scipy import stats
# from tensorflow import keras
from PySide2.QtWidgets import QApplication, QDialog, QSizePolicy, QMainWindow
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt
from PySide2.QtGui import QMovie, QPixmap
from functools import partial
import pyqrcode
import time

from database import Database
from app import *
from aescipher import AESCipher
from localdatabase import LocalDataBase

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

class MainWindow(QDialog):
   
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # self.user = Database.signInUser('09150471487', '1234')
        self.camera = None
        self.user_items = []
        self.widget_index_stack = []
        # self.items = Database.getItems()
        self.categories = Database.getCategories()

        loader = QUiLoader()
        self.ui = loader.load('main.ui', self)

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)

        self.ui.btnBack.setSizePolicy(sp_retain)
        self.ui.btnTick.setSizePolicy(sp_retain)

#        thred_load_model = Thread(target=self.loadModel)
#        thred_load_model.start()

        self.ui.showMaximized()


    def loadModel(self):
        # self.model = keras.models.load_model('farazist.h5')
        print('model successfully loaded')
        self.stackStart()

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
                    frame = cvtColor(frame, COLOR_BGR2RGB)
                    frame = resize(frame, (299, 299))
                    frame = frame.reshape(1, 299, 299, 3)
                    frame = frame / 255.0

                    prediction = self.model.predict([frame])
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

    def stackLoading(self):
        self.ui.btnBack.hide()
        self.ui.btnTick.hide()
        self.ui.lblLogo.hide()

        gif_loading = QMovie("animations/Spinner.gif")
        self.ui.lblGifLoading.setMovie(gif_loading)
        gif_loading.start()

        self.ui.Stack.setCurrentIndex(0)
        self.widget_index_stack.append(0)

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
        self.ui.btnTick.hide()
        
        self.ui.btnSettingUserLogin.clicked.connect(self.stackAdminLogin)

        self.ui.btnUserLogin.clicked.connect(self.stackMainMenu)

        self.ui.Stack.setCurrentIndex(2)
        self.widget_index_stack.append(2)

    def stackMainMenu(self):
        self.ui.btnTick.hide()
        
        self.ui.btnSettingMainMenu.clicked.connect(self.stackAdminLogin)

        self.ui.btnMainMenu_1.clicked.connect(self.stackDeliveryItems)
        self.ui.btnMainMenu_2.clicked.connect(self.stackWallet)

        self.ui.Stack.setCurrentIndex(3)
        self.widget_index_stack.append(3)

    def stackAdminLogin(self):
        self.ui.btnTick.hide()

        self.ui.btnAdminLogin.clicked.connect(self.stackSetting)

        self.ui.Stack.setCurrentIndex(4)
        self.widget_index_stack.append(4)

    def stackWallet(self):
        self.ui.btnTick.hide()

        gif_wallet = QMovie("animations/wallet.gif")
        self.ui.lblGifWallet.setMovie(gif_wallet)
        gif_wallet.start()

        # self.ui.lblWallet.setText(str(self.user['wallet']))

        self.ui.Stack.setCurrentIndex(5)
        self.widget_index_stack.append(5)

    def stackDeliveryItems(self):
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

    def stackSetting(self):
        self.ui.btnBack.hide()

        self.ui.Stack.setCurrentIndex(7)

    def stackQR(self):

        data = "https://farazist.ir/@ngengesenior/qr-codes-generation-with-python-377735be6c5f"
        filename = 'images\qr\qrcode.png'

        url = pyqrcode.create(data)
        url.png(filename, scale=6, background='#f6fdfa')
    
        open_img = QPixmap(filename)
        self.ui.lblPixmapQr.setPixmap(open_img)

        self.ui.btnSettingQr.clicked.connect(self.stackAdminLogin)

        self.ui.Stack.setCurrentIndex(8)
        self.widget_index_stack.append(8)

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

    def show_setting_user(self):
        self.check_setting_user = Login_user('admin')
        if self.check_setting_user.exec_() == QDialog.Accepted:
            self.show_setting_pass()

    def show_setting_pass(self):
        self.check_setting_pass = Login_pass('admin')
        if self.check_setting_pass.exec_() == QDialog.Accepted:
            # self.show_menu()
            self.lb_logo.show()
            self.btn_back.hide()
            self.btn_tick.show()
            self.Stack.setCurrentIndex(12)
            self.widget_index_stack.append(12)

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

    def exit_message_box(self):
        btn_font = QFont('IRANSans', 16)
        lb_font = QFont('IRANSans', 18)

        box = QMessageBox()
        box.setStyleSheet("QPushButton{min-width: 60px; min-height: 40px;}")
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle('!فرازیست')
        box.setText('از برنامه خارج می شوید؟')
        box.setFont(lb_font)
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)

        buttonY = box.button(QMessageBox.Yes)
        buttonY.setText('بله')
        buttonY.setFont(btn_font)
        buttonY.setStyleSheet(button_style)
        buttonY.setMinimumSize(60,30)
        
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('خیر')
        buttonN.setFont(btn_font)
        buttonN.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e11c1c, stop:1 #f86565);'
                              'color: #ffffff; padding: 3px; border: none; border-radius: 6px;')
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
