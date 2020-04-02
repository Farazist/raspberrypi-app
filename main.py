import sys
from cv2 import VideoCapture, cvtColor, resize, destroyAllWindows, COLOR_BGR2RGB
from threading import Thread
import numpy as np
from scipy import stats
from tensorflow import keras
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtGui import QFont
from functools import partial
import pyqrcode
import time

from ui import UI_MainWindow
from ui import btn_style
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

                        window.lbl_item.setText(self.items[predicted]['name'])

                    if self.predict_item_flag == False:
                        predict_item_list.append(predicted)

                    if self.predict_item_flag == True:
                        most_probability_item = stats.mode(predict_item_list).mode[0]

                        print('most probability item:', most_probability_item)

                        category_index = self.items[most_probability_item]['category_id'] - 1
                        categories_count[category_index] += 1

                        for i in range(len(categories_count)):
                            window.grid_widget_DeliveryItems[2][i].setText(str(categories_count[i]))

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
        
        categories_count = np.zeros(len(self.categories), np.uint8)
        for i in range(len(categories_count)):
                            window.grid_widget_DeliveryItems[2][i].setText(str(0))
        
        self.showMainMenu()    

    def changePredictItemFlag(self, value):
        self.predict_item_flag = value
        self.lbl_item.clear()

    def showIsLoading(self):
        self.lb_logo.hide()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(0)
        self.widget_index_stack.append(0)

    def showAdminLogin(self):
        self.lb_logo.show()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(1)
        self.widget_index_stack.append(1)

        if self.tb_AdminLogin.text() == '09150471487':
            self.showAdminPassword()
        elif self.tb_AdminLogin.text() != '09150471487' and self.tb_AdminLogin.text() != '':
            self.lbl_AdminLogin_Error.setText('نام کاربری نادرست است')
            self.tb_AdminLogin.clear()
    
    def showAdminPassword(self):
        self.lb_logo.show()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(2)
        self.widget_index_stack.append(2)

        if self.tb_AdminPassword.text() == '1234':
            self.showSettingMenu()
        elif self.tb_AdminPassword.text() != '1234' and self.tb_AdminPassword.text() != '':
            self.lbl_AdminPassword_Error.setText('رمز عبور نادرست است')
            self.tb_AdminPassword.clear()
    
    def showSettingMenu(self):
        self.lb_logo.show()
        self.btn_back.hide()
        self.btn_tick.show()
        self.Stack.setCurrentIndex(3)
        self.widget_index_stack.append(3)

    def showStart(self):
        self.lb_logo.show()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(4)
        self.widget_index_stack.append(4)

    def showUserLogin(self):
        self.lb_logo.show()
        self.btn_back.show()
        self.btn_back.setText('خروج')
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(5)
        self.widget_index_stack.append(5)

        if self.tb_UserLogin.text() == '09150471487':
            self.showUserPassword()
        elif self.tb_UserLogin.text() != '09150471487' and self.tb_UserLogin.text() != '':
            self.lbl_UserLogin_Error.setText('نام کاربری نادرست است')
            self.tb_UserLogin.clear()

    def showUserPassword(self):
        self.lb_logo.show()
        self.btn_back.show()
        self.btn_back.setText('خروج')
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(6)
        self.widget_index_stack.append(6)

        if self.tb_UserPassword.text() == '1234':
            self.showMainMenu()
        elif self.tb_UserPassword.text() != '1234' and self.tb_UserPassword.text() != '':
            self.lbl_UserPassword_Error.setText('رمز عبور نادرست است')
            self.tb_UserPassword.clear()

    def showMainMenu(self):
        self.lb_logo.show()
        self.btn_back.show()
        self.btn_back.setText('خروج')
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(7)
        self.widget_index_stack.append(7)

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
        self.Stack.setCurrentIndex(8)
        self.widget_index_stack.append(8)

    def showWallet(self):
        self.lb_logo.show()
        self.btn_back.show()
        self.btn_back.setText('بازگشت')
        self.btn_tick.hide()
        self.lbl_wallet.setText(str(self.user['wallet']))
        self.Stack.setCurrentIndex(9)
        self.widget_index_stack.append(9)

    def back_window(self):

        self.delivery_items_flag = False            
        if self.camera: 
            self.camera.release()
        
        # self.btn_tick.hide()
        # self.btn_back.show()    

        self.widget_index_stack.pop()

        if self.Stack.currentIndex() in [5, 6]:
            self.tb_UserLogin.setText('')
            self.tb_UserPassword.setText('')
            self.showStart()
        
        if self.Stack.currentIndex() == 7:
            self.tb_UserLogin.setText('')
            self.tb_UserPassword.setText('')
            self.showStart()
        
        if self.Stack.currentIndex() == 9:
            self.tb_UserLogin.setText('')
            self.tb_UserPassword.setText('')
            self.showMainMenu()
        
        # self.Stack.setCurrentIndex(self.widget_index_stack[-1])
        
    def tick_window(self):
        self.widget_index_stack.pop()

        if self.Stack.currentIndex() == 3:
            self.tb_AdminLogin.setText('')
            self.tb_AdminPassword.setText('')
            self.showStart()
        
        # self.Stack.setCurrentIndex(self.widget_index_stack[-1])

    def display(self, i):
        self.Stack.setCurrentIndex(i)

    def exitApp(self):
        self.delivery_items_flag = False
        if self.camera is not None:
            self.camera.release() 
        destroyAllWindows()
        self.close()

    def showExitBox(self):
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
        buttonY.setStyleSheet(btn_style)
        buttonY.setMinimumSize(60,30)
        
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('خیر')
        buttonN.setFont(btn_font)
        buttonN.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e11c1c, stop:1 #f86565);'
                              'color: #ffffff; padding: 3px; border: none; border-radius: 6px;')
        buttonN.setMinimumSize(60,30)

        box.exec_()
        if box.clickedButton() == buttonY:
            self.exitApp()
        elif box.clickedButton() == buttonN:
            box.close()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    app.setFont(QFont('IRANSans', 13))
    window = MainWindow()
    window.showIsLoading()
    sys.exit(app.exec_())