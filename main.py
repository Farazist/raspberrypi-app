import sys
from cv2 import VideoCapture, cvtColor, resize, destroyAllWindows, COLOR_BGR2RGB
from threading import Thread
import numpy as np
from scipy import stats
from tensorflow import keras
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QFont
from functools import partial
import pyqrcode
import time

from ui import UI_MainWindow
from database import Database
from app import *
from login import Login_user
from login import Login_pass
from aescipher import AESCipher
from localdatabase import LocalDataBase


class MainWindow(UI_MainWindow):
   
    def __init__(self):

        self.user = Database.signInUser('09150471487', '1234')
        self.camera = None
        self.user_items = []
        self.widget_index_stack = []
        self.items = Database.getItems()
        self.categories = Database.getCategories()

        super(MainWindow, self).__init__()

        thred_load_model = Thread(target=self.loadModel)
        thred_load_model.start()

    def loadModel(self):
        self.model = keras.models.load_model('farazist.h5')
        print('model successfully loaded')
        self.showStart()

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
        self.lb_2_s4.clear()

    def show_setting_user(self):
        self.check_setting_user = Login_user('admin')
        if self.check_setting_user.exec_() == QDialog.Accepted:
            self.show_setting_pass()

    def show_setting_pass(self):
        #self.check_setting_pass = Login_pass('admin')
        #if self.check_setting_pass.exec_() == QDialog.Accepted:
            # self.show_menu()
            self.lbl_logo.show()
            self.btn_back.hide()
            self.btn_tick.show()
            self.Stack.setCurrentIndex(13)
            self.widget_index_stack.append(13)

    def showIsLoading(self):
        self.lbl_logo.hide()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(0)
        self.widget_index_stack.append(0)

    def showStart(self):
        self.lbl_logo.show()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(1)
        self.widget_index_stack.append(1)

    def showLogin(self):
        self.lbl_logo.show()
        self.btn_back.show()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(2)
        self.widget_index_stack.append(2)

        if self.tb_login.text() == '09150471487':
            self.showPassword()
        else:
            self.tb_login.clear()

    #def checkLoginPhoneNumber(self):
    #    self.lbl_logo.show()
    #    self.btn_back.show()
    #    if self.tb_login.text() == '09150471487':
    #        self.showPassword()
    #    else:
    #        self.tb_login.clear()

    def showPassword(self):
        self.lbl_logo.show()
        self.btn_back.show()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(3)
        self.widget_index_stack.append(3)

        if self.tb_password.text() == '1234':
            self.showMainMenu()
        else:
            self.tb_password.clear()

    #def checkPassword(self):
    #    self.lbl_logo.show()
    #    self.btn_back.show()
    #    if self.tb_password.text() == '1234':
    #        self.showMainMenu()
    #    else:
    #        self.tb_password.clear()

    def showQR(self):
        self.lbl_logo.show()
        self.btn_back.show()

        data = "https://farazist.ir/@ngengesenior/qr-codes-generation-with-python-377735be6c5f"
        filename = 'images\qr\qrcode.png'

        url = pyqrcode.create(data)
        url.png(filename, scale=6, background='#f6fdfa')
    
        open_img = QPixmap(filename)
        self.lb_1_s2.setPixmap(open_img)
        self.Stack.setCurrentIndex(4)
        self.widget_index_stack.append(4)

    def showMainMenu(self):
        self.lbl_logo.show()
        self.btn_back.show()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(5)
        self.widget_index_stack.append(5)

    def showDelivery(self):
        self.lbl_logo.show()
        self.btn_back.hide()
        self.btn_tick.hide()

        self.camera = VideoCapture(0)
        
        if self.camera is None or not self.camera.isOpened():
            print("error: camera not found")
            self.message_box('دوربین پیدا نشد')    
            return      

        self.detect_thread = Thread(target=self.detectItem)
        self.detect_thread.start()
        self.Stack.setCurrentIndex(6)
        self.widget_index_stack.append(6)

    def showWallet(self):
        self.lbl_logo.show()
        self.btn_back.show()
        self.btn_tick.hide()
        self.lbl_wallet.setText(str(self.user['wallet']))
        self.Stack.setCurrentIndex(7)
        self.widget_index_stack.append(7)

    def show_charging_unit(self):
        self.Stack.setCurrentIndex(8)
        self.widget_index_stack.append(8)

    def show_deposit_to_card(self):
        self.Stack.setCurrentIndex(9)
        self.widget_index_stack.append(9)

    def show_helping_to_environment(self):
        self.Stack.setCurrentIndex(10)
        self.widget_index_stack.append(10)

    def show_charity(self):
        self.Stack.setCurrentIndex(11)
        self.widget_index_stack.append(11)

    def show_buy_credit(self):
        self.Stack.setCurrentIndex(12)
        self.widget_index_stack.append(12)

    def show_store(self):
        self.Stack.setCurrentIndex(14)
        self.widget_index_stack.append(14)

    def back_window(self):

        self.delivery_items_flag = False
        if self.camera: 
            self.camera.release()

        self.btn_tick.hide()
        self.btn_back.show()    

        self.widget_index_stack.pop()

        if self.widget_index_stack[-1] == 0:
            self.lbl_logo.hide()
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


    def display(self, i):
        self.Stack.setCurrentIndex(i)

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
    app.setFont(QFont('IRANSans', 13))
    window = MainWindow()
    window.showIsLoading()
    sys.exit(app.exec_())