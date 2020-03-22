import sys
from cv2 import VideoCapture, cvtColor, resize, destroyAllWindows, COLOR_BGR2RGB
from threading import Thread
import numpy as np
from scipy import stats
from tensorflow.keras.models import load_model
from PyQt5.QtGui import (QFont, QIcon, QMovie, QPixmap)
from PyQt5.QtCore import (Qt, QSize)
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QGraphicsDropShadowEffect, QMessageBox, QDialog, QGroupBox, QSizePolicy,
                            QWidget, QPushButton, QLabel, QLineEdit, QStackedWidget)
from functools import partial
import pyqrcode
import time

from database import Database
from app import *
from login import Login_user
from login import Login_pass
from keyboard import KEYBoard
from aescipher import AESCipher
from localdatabase import LocalDataBase


global widget_index_stack

def loadModel():
    global model
    model = load_model('farazist.h5')
    print('model successfully loaded')
    window.showStart()

def detectItem():
    global delivery_items_flag
    global predict_item_flag
    global user_items
    global categories_count
    global camera

    camera = VideoCapture(0)
    
    predict_item_list = []
    categories_count = np.zeros(len(categories), np.uint8)

    time = 0
    
    predict_item_flag = False
    delivery_items_flag = True
    while delivery_items_flag:
        try:
            time += 1
            if time == 30:
                time = 0

                _, frame = camera.read()
                frame = cvtColor(frame, COLOR_BGR2RGB)
                frame = resize(frame, (299, 299))
                frame = frame.reshape(1, 299, 299, 3)
                frame = frame / 255.0

                prediction = model.predict([frame])
                #prediction = np.random.rand(1, 20)

                if np.max(prediction) > 0.4:
                    predicted = np.argmax(prediction)
                    print(items[predicted])

                    window.lb_2_s4.setText(items[predicted]['name'])

                if predict_item_flag == False:
                    predict_item_list.append(predicted)

                if predict_item_flag == True:
                    most_probability_item = stats.mode(predict_item_list).mode[0]

                    print('most probability item:', most_probability_item)

                    category_index = items[most_probability_item]['category_id'] - 1
                    categories_count[category_index] += 1

                    for i in range(len(categories_count)):
                        window.grid_widget_s4[2][i].setText(str(categories_count[i]))

                    for item in user_items:
                        if item['id'] == items[most_probability_item]['id']:
                            item['count'] += 1
                            break
                    else:
                        user_items.append(items[most_probability_item])
                        user_items[-1]['count'] = 1

                    predict_item_list = []
                    predict_item_flag = False

        except Exception as e:
            print("error:", e)

    camera.release()
    destroyAllWindows()


button_style = 'background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E5631, stop:1 #2ea444); color: #ffffff; padding: 3px; border: none; border-radius: 6px;'
menu_font = QFont('IRANSans', 18)
package_font = QFont('IRANSans', 16)
label_font = QFont('IRANSans', 18)
number_font = QFont('IRANSansFaNum', 20, QFont.Bold)
btn_sign_font = QFont('IRANSans', 20)

class Main_Program(QWidget):
    
    def __init__(self):
        
        super(Main_Program, self).__init__()

        #self.setContentsMargins(10, 10, 10, 5)
        self.setStyleSheet('background-color: #f6fdfa  ')
        #self.setGeometry(300, 50, 10, 10)
        self.setWindowTitle('فرازیست')

        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(0, 10, 0, 0)

        widget_header = QWidget()
        #widget_header.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        #widget_header.getContentsMargins()
        widget_header.setFixedHeight(100)
        widget_header.setStyleSheet('border: none')
        v_layout.addWidget(widget_header)

        h_layout_header = QHBoxLayout()
        h_layout_header.setContentsMargins(20, 0, 20, 0)
        widget_header.setLayout(h_layout_header)

        # --- child 1
        self.btn_back = QPushButton()
        self.btn_back.setFont(btn_sign_font)
        self.btn_back.setText('بازگشت')
        self.btn_back.setIcon(QIcon('images/sign/back.png'))
        self.btn_back.setIconSize(QSize(50, 50))
        self.btn_back.setMinimumSize(170, 70)
        self.btn_back.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fb5f15, stop:1 #f5834d);'
                                    'color: #ffffff; border: none; border-radius: 6px;')
        self.btn_back.clicked.connect(self.back_window)
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.btn_back.setSizePolicy(sp_retain)
        h_layout_header.addWidget(self.btn_back, alignment=Qt.AlignLeft)


        # --- child 2
        logo = QPixmap('images/farazist.ico')
        self.lb_logo = QLabel()
        self.lb_logo.setPixmap(logo)
        h_layout_header.addWidget(self.lb_logo, alignment=Qt.AlignCenter)

        # --- child 3
        self.btn_tick = QPushButton()
        self.btn_tick.setFont(btn_sign_font)
        self.btn_tick.setText('تایید')
        self.btn_tick.setIcon(QIcon('images/sign/tick.png'))
        self.btn_tick.setIconSize(QSize(50, 50))
        self.btn_tick.setMinimumSize(170, 70)
        self.btn_tick.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fb5f15, stop:1 #f5834d);'
                                    'color: #ffffff; border: none; border-radius: 6px;')
        self.btn_tick.clicked.connect(self.tick_window)
        # sp_retain = QSizePolicy()
        # sp_retain.setRetainSizeWhenHidden(True)
        self.btn_tick.setSizePolicy(sp_retain)
        h_layout_header.addWidget(self.btn_tick, alignment=Qt.AlignRight)

        self.stacks = [QWidget() for _ in range(13)]

        # -------------------- create stacks --------------------
        self.Stack = QStackedWidget(self)

        for stack in self.stacks:
            self.Stack.addWidget(stack)

        # -------------------- stacks method --------------------
        self.stack_0_UI()
        self.stack_1_UI()
        self.stack_2_UI()
        self.stack_3_UI()
        self.stack_4_UI()
        self.stack_5_UI()
        self.stack_12_UI()

        # -------------------- add stack to main layout --------------------
        v_layout.addWidget(self.Stack)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showMaximized()
        
        # self.setFixedSize(1000, 600)
        # self.show()

    # -------------------- پنجره بارگزاری --------------------
    def stack_0_UI(self):
        loader_font = QFont('IRANSans', 16)
        farazist_font = QFont('IRANSans', 48)
        btn_setting = self.setting_button()

        v_layout_s0 = QVBoxLayout()
        v_layout_s0.setContentsMargins(0, 0, 0, 100)
        v_layout_s0.insertStretch(-1, -1)

        logo = QPixmap('images/farazist.ico')
        text = 'در حال بارگزاری'
        gif = QMovie("animation/Spinner-1.2s-58px.gif")

        lb_1_s0 = QLabel()
        lb_1_s0.setPixmap(logo)
        lb_1_s0.setMinimumHeight(400)

        lb_2_s0 = QLabel()
        lb_2_s0.setMovie(gif)
        gif.start()

        lb_3_s0 = QLabel()
        lb_3_s0.setFont(loader_font)
        lb_3_s0.setText(text)

        v_layout_s0.addWidget(lb_1_s0, alignment= Qt.AlignCenter)
        v_layout_s0.addWidget(lb_2_s0, alignment= Qt.AlignCenter | Qt.AlignBottom)
        v_layout_s0.addWidget(lb_3_s0, alignment= Qt.AlignCenter | Qt.AlignBottom)
        self.stacks[0].setLayout(v_layout_s0)

    # -------------------- پنجره تیزر تبلیغاتی --------------------
    def stack_1_UI(self):
        btn_setting = self.setting_button()
        btns_layout = self.login_button()

        v_layout_s1 = QVBoxLayout()
        h_layout_1_s1 = QHBoxLayout()
        h_layout_2_s1 = QHBoxLayout()

        widget_background_s1 = QWidget()
        #widget_background_s1.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        # widget_background.getContentsMargins()
        widget_background_s1.setStyleSheet('background-color: #fefcfc; border-radius: 30px; border :none;')
        widget_background_s1.setLayout(h_layout_1_s1)
        v_layout_s1.addWidget(widget_background_s1)

        movie = QMovie("animation/return.gif")

        self.lb_1_s1 = QLabel()
        h_layout_1_s1.addWidget(self.lb_1_s1, alignment=Qt.AlignHCenter)
        self.lb_1_s1.setMovie(movie)
        movie.start()

        h_layout_2_s1.addWidget(btn_setting, alignment=Qt.AlignLeft| Qt.AlignBottom)
        h_layout_2_s1.addLayout(btns_layout)
        v_layout_s1.addLayout(h_layout_2_s1)

        self.stacks[1].setLayout(v_layout_s1)

    # -------------------- qr پنجره نمایش --------------------
    def stack_2_UI(self):
        btn_setting = self.setting_button()

        label_font = QFont('IRANSans', 19)

        v_layout_s2 = QVBoxLayout()
        h_layout_s2 = QHBoxLayout()
        h_layout_s2.setContentsMargins(0, 0, 100, 0)
        
        self.lb_1_s2 = QLabel()
        h_layout_s2.addWidget(self.lb_1_s2, alignment=Qt.AlignCenter)

        text = 'برنامه فرازیست را بر روی گوشی خود باز کنید\n'\
               'در صفحه اصلی برنامه بر روی آیکن qr در بالای سمت راست برنامه کلید کنید\n'\
               'و بر روی گزینه اسکن کلیک کنید'
        self.lb_2_s2 = QLabel()
        self.lb_2_s2.setText(text)
        self.lb_2_s2.setFont(label_font)
        h_layout_s2.addWidget(self.lb_2_s2, alignment=Qt.AlignCenter)

        v_layout_s2.addLayout(h_layout_s2)
        v_layout_s2.addWidget(btn_setting, alignment=Qt.AlignLeft)
        
        self.stacks[2].setLayout(v_layout_s2)

    # -------------------- پنجره منو برنامه --------------------
    def stack_3_UI(self):

        btn_setting = self.setting_button()
        # -------------------- main window layout --------------------
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        # ------- child  layout
        grid_layout_s3 = QGridLayout()
        h_layout.addLayout(grid_layout_s3)
        grid_layout_s3.setContentsMargins(10, 30, 10, 10)  # (left, top, right, bottom)

        main_menu_buttons = [   
            [
                {'text': 'تحویل پسماند', 'image': 'images/green_main_menu/Package Delivery.png', 'function': self.show_delivery},
                {'text': 'کیف پول', 'image': 'images/green_main_menu/wallet.png', 'function': self.show_wallet},
                {'text': 'شارژ واحد مسکونی', 'image': 'images/green_main_menu/Charging Residential Unit.png', 'function': self.menu_message_box},
                {'text': 'واریز به بازیافت کارت', 'image': 'images/green_main_menu/Deposit to card recycling.png', 'function': self.menu_message_box}
            ],
            [
                {'text': 'کمک به محیط زیست', 'image': 'images/green_main_menu/Helping the environment.png', 'function': self.menu_message_box},
                {'text': 'کمک به خیریه', 'image': 'images/green_main_menu/Donate to charity.png', 'function': self.menu_message_box},
                {'text': 'خرید شارژ', 'image': 'images/green_main_menu/to buy credit.png', 'function': self.menu_message_box},
                {'text': 'فروشگاه', 'image': 'images/green_main_menu/Store.png', 'function': self.menu_message_box}
            ]
        ]

        # grid layout children
        self.v_layouts_main_menu = [[QVBoxLayout() for _ in range(4)] for _ in range(2)]
        
        for i in range(2):
            for j in range(4):
                # self.v_layouts_main_menu[i][j].setContentsMargins(20, 0, 20, 10)
                
                grid_layout_s3.addLayout(self.v_layouts_main_menu[i][j], i, j, Qt.AlignCenter)

                btn = QPushButton()
                btn.setIcon(QIcon(main_menu_buttons[i][j]['image']))
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setIconSize(QSize(110, 110))
                btn.setFixedSize(200, 200)
                btn.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')

                if main_menu_buttons[i][j]['function']:
                    btn.clicked.connect(main_menu_buttons[i][j]['function'])
                self.v_layouts_main_menu[i][j].addWidget(btn)

                lbl = QLabel()
                lbl.setText(main_menu_buttons[i][j]['text'])
                lbl.setFont(menu_font)
                self.v_layouts_main_menu[i][j].addWidget(lbl, alignment=Qt.AlignHCenter)

        v_layout.addLayout(h_layout)
        v_layout.addWidget(btn_setting, alignment=Qt.AlignLeft)

        self.stacks[3].setLayout(v_layout)

    # -------------------- پنجره تحویل پکیج --------------------
    def stack_4_UI(self):

        btn_setting = self.setting_button()

        v_layout = QVBoxLayout()  # main window layout
        v_layout.setSpacing(40)

        # ------- child  layout
        # --- child 1
        h_layout1_s4 = QHBoxLayout()
        h_layout1_s4.setContentsMargins(0, 0, 100, 0)

        grid_layout_s4 = QGridLayout()
        grid_layout_s4.setContentsMargins(50, 30, 70, 20)
        grid_layout_s4.setSpacing(0)
        h_layout1_s4.addLayout(grid_layout_s4)

        widget_background_s4 = QWidget()
        widget_background_s4.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        widget_background_s4.getContentsMargins()
        widget_background_s4.setStyleSheet('background-color: #ffffff; border-radius: 30px;')
        # background_1_10.setGraphicsEffect(self.shadow)
        widget_background_s4.setLayout(h_layout1_s4)
        v_layout.addWidget(widget_background_s4)

        h_layout2_s4 = QHBoxLayout()
        #h_layout2_s4.setContentsMargins(0, 0, 90, 20)
        v_layout.addLayout(h_layout2_s4)

        self.grid_widget_s4 = [[QLabel() for _ in range(len(categories))] for _ in range(3)]
        for i in range(3):
            for j in range(len(categories)):
                self.grid_widget_s4[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                grid_layout_s4.addWidget(self.grid_widget_s4[i][j], i, j)

        for i in range(len(categories)):
            
            img = QPixmap(categories[i]['image'][1:])
            img = img.scaledToWidth(128)
            img = img.scaledToHeight(128)

            self.grid_widget_s4[0][i].setPixmap(img)
            self.grid_widget_s4[0][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_s4[1][i].setText(categories[i]['name'])
            self.grid_widget_s4[1][i].setFont(package_font)
            self.grid_widget_s4[1][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_s4[2][i].setText('0')
            self.grid_widget_s4[2][i].setFont(number_font)
            self.grid_widget_s4[2][i].setAlignment(Qt.AlignCenter)

        lb_1_s4 = QLabel('اعتبار')
        lb_1_s4.setFont(label_font)
        h_layout1_s4.addWidget(lb_1_s4, alignment=Qt.AlignCenter)

        # --- child 3
        h_layout2_s4.addWidget(btn_setting)

        self.lb_2_s4 = QLabel()
        self.lb_2_s4.getContentsMargins()
        self.lb_2_s4.setFont(label_font)
        self.lb_2_s4.setAlignment(Qt.AlignCenter)
        self.lb_2_s4.setStyleSheet('padding: 3px; border: 2px solid #1E5631; border-radius: 6px;')
        h_layout2_s4.addWidget(self.lb_2_s4)

        btn_1_21 = QPushButton('بعدی')
        btn_1_21.setMinimumSize(200, 60)
        btn_1_21.setFont(menu_font)
        btn_1_21.clicked.connect(partial(self.changePredictItemFlag, True))
        btn_1_21.setStyleSheet(button_style)
        h_layout2_s4.addWidget(btn_1_21)

        self.stacks[4].setLayout(v_layout)

    # -------------------- پنجره کیف پول --------------------
    def stack_5_UI(self):
        global user

        btn_setting = self.setting_button()

        v_layout = QVBoxLayout()
        h_layout1_s5 = QHBoxLayout()
        h_layout1_s5.setContentsMargins(0, 0, 100, 0)

        widget_background_s5 = QWidget()
        widget_background_s5.setFixedHeight(500)
        widget_background_s5.setLayout(h_layout1_s5)
        v_layout.addWidget(widget_background_s5)

        movie = QMovie("animation/oie_1475355NRgGVDm8.gif")

        self.lb_1_s5 = QLabel()
        h_layout1_s5.addWidget(self.lb_1_s5, alignment=Qt.AlignLeft)
        self.lb_1_s5.setMovie(movie)
        movie.start()

        lb_text = "موجودی\n{}\nریال"


        self.lb_2_s5 = QLabel()
        self.lb_2_s5.setFont(label_font)
        self.lb_2_s5.setText(lb_text.format(5015))
        h_layout1_s5.addWidget(self.lb_2_s5, alignment=Qt.AlignRight)
        
        v_layout.addLayout(h_layout1_s5)
        v_layout.addWidget(btn_setting, alignment = Qt.AlignLeft| Qt.AlignBottom)

        self.stacks[5].setLayout(v_layout)

    # -------------------- پنجره تنظیمات --------------------
    def stack_12_UI(self):

        h_layout = QHBoxLayout()  # main window layout
        h_layout.setSpacing(500)

        group2 = QGroupBox()

        # ------- child  layout
        # --- child 1
        v_layout1_s12 = QVBoxLayout()
        v_layout1_s12.setSpacing(0)
        v_layout1_s12.setContentsMargins(150, 0, 0, 0)
        
        # ---------- child 1 widgets ----------
        # --- create line edit
        self.lb_s12 = QLineEdit()
        self.lb_s12.setMaximumSize(260, 60)
        self.lb_s12.setStyleSheet('padding: 3px; border: 2px solid #1E5631; border-radius: 6px;')
        # lb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        v_layout1_s12.addWidget(self.lb_s12)

        self.key_widget = KEYBoard(self.lb_s12)
        self.key_layout = self.key_widget.output()
        v_layout1_s12.addLayout(self.key_layout)
        self.setLayout(v_layout1_s12)

        # --- child 2
        v_layout2_s12 = QVBoxLayout()
        v_layout2_s12.setContentsMargins(20, 0, 20, 200)
        # ---------- child 2 widgets ----------
        self.btn_00_s12 = QPushButton()
        self.btn_00_s12.setFont(menu_font)
        self.btn_00_s12.setText('تنظیم شماره پورت')
        self.btn_00_s12.setFixedSize(200, 60)
        self.btn_00_s12.setStyleSheet(button_style)
        v_layout2_s12.addWidget(self.btn_00_s12, alignment=Qt.AlignCenter)

        self.btn_01_s12 = QPushButton()
        self.btn_01_s12.setFont(menu_font)
        self.btn_01_s12.setText('خروج از برنامه')
        self.btn_01_s12.setFixedSize(200, 60)
        self.btn_01_s12.setStyleSheet(button_style)
        self.btn_01_s12.clicked.connect(self.exit_message_box)
        v_layout2_s12.addWidget(self.btn_01_s12, alignment=Qt.AlignCenter)

        # group1.setLayout(v_layout1_s10)
        group2.setLayout(v_layout2_s12)
        
        h_layout.addLayout(v_layout1_s12)
        h_layout.addWidget(group2)
        self.stacks[12].setLayout(h_layout)
    # -------------------- windows method --------------------
    # ---------- flag ----------
    def changePredictItemFlag(self, value):
        global predict_item_flag
        predict_item_flag = value
        self.lb_2_s4.clear()

    # ---------- login ----------
    def login_button(self):
        btns_font = QFont('IRANSans', 24)

        btns_layout = QHBoxLayout()

        self.login_btn = QPushButton()
        self.login_btn.setFont(btns_font)
        self.login_btn.setStyleSheet("QPushButton { text-align: center; }")
        self.login_btn.setText('ورود با نام کاربری')
        self.login_btn.setIcon(QIcon('images/sign/user-outline1.png'))
        self.login_btn.setIconSize(QSize(50, 50))
        self.login_btn.setStyleSheet(button_style)
        self.login_btn.setMinimumSize(290, 130)
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.login_btn.setSizePolicy(sp_retain)
        self.login_btn.clicked.connect(self.show_login_user)

        self.login_qr = QPushButton()
        self.login_qr.setFont(btns_font)
        self.login_qr.setStyleSheet("QPushButton { text-align: center; }")
        self.login_qr.setText('کد qr ورود با')
        self.login_qr.setIcon(QIcon('images/sign/qr_code1.png'))
        self.login_qr.setIconSize(QSize(50, 50))
        self.login_qr.setStyleSheet(button_style)
        self.login_qr.setMinimumSize(290, 130)
        # sp_retain = QSizePolicy()
        # sp_retain.setRetainSizeWhenHidden(True)
        self.login_qr.setSizePolicy(sp_retain)
        self.login_qr.clicked.connect(self.showQR)

        btns_layout.addWidget(self.login_btn)
        btns_layout.addWidget(self.login_qr)
        #return self.login_btn, self.login_qr
        return btns_layout

    def show_login_user(self):
        self.check_login_user = Login_user('user')
        if self.check_login_user.exec_() == QDialog.Accepted:
            self.show_login_pass()

    def show_login_pass(self):
        self.check_login_pass = Login_pass('user')
        if self.check_login_pass.exec_() == QDialog.Accepted:
            self.show_menu()

    # ---------- setting ----------
    def setting_button(self):
        self.setting = QPushButton()
        self.setting.setIcon(QIcon('images\sign\setting.png'))
        self.setting.setStyleSheet('border: none')
        self.setting.setIconSize(QSize(60, 60))
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.setting.setSizePolicy(sp_retain)
        self.setting.clicked.connect(self.show_setting_user)
        return self.setting

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
            widget_index_stack.append(12)

    def showIsLoading(self):
        self.lb_logo.hide()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(0)
        widget_index_stack.append(0)

    def showStart(self):
        self.lb_logo.show()
        self.btn_back.hide()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(1)
        widget_index_stack.append(1)

    def showQR(self):
        self.lb_logo.show()
        self.btn_back.show()

        data = "https://farazist.ir/@ngengesenior/qr-codes-generation-with-python-377735be6c5f"
        filename = 'images\qr\qrcode.png'

        url = pyqrcode.create(data)
        url.png(filename, scale=6, background='#f6fdfa')
    
        open_img = QPixmap(filename)
        self.lb_1_s2.setPixmap(open_img)

        self.Stack.setCurrentIndex(2)
        widget_index_stack.append(2)

    def show_menu(self):
        self.lb_logo.show()
        self.btn_back.show()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(3)
        widget_index_stack.append(3)

    def show_delivery(self):
        self.lb_logo.show()
        self.btn_back.hide()
        self.btn_tick.show()
        self.detect_thread = Thread(target=detectItem)
        self.detect_thread.start()
        self.Stack.setCurrentIndex(4)
        widget_index_stack.append(4)

    def show_wallet(self):
        self.lb_logo.show()
        self.btn_back.show()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(5)
        widget_index_stack.append(5)

    def show_charging_unit(self):
        self.Stack.setCurrentIndex(6)
        widget_index_stack.append(6)

    def show_deposit_to_card(self):
        self.Stack.setCurrentIndex(7)
        widget_index_stack.append(7)

    def show_helping_to_environment(self):
        self.Stack.setCurrentIndex(8)
        widget_index_stack.append(8)

    def show_charity(self):
        self.Stack.setCurrentIndex(9)
        widget_index_stack.append(9)

    def show_buy_credit(self):
        self.Stack.setCurrentIndex(10)
        widget_index_stack.append(10)

    def show_store(self):
        self.Stack.setCurrentIndex(11)
        widget_index_stack.append(11)

    def back_window(self):

        self.delivery_items_flag = False            
        if camera: 
            camera.release()
        
        self.btn_tick.hide()
        self.btn_back.show()    

        widget_index_stack.pop()
        
        if widget_index_stack[-1] == 1:
            self.btn_back.hide()

        self.Stack.setCurrentIndex(widget_index_stack[-1])

    def tick_window(self):

        widget_index_stack.pop()

        if widget_index_stack[-1] == 1:
            self.btn_back.hide()
            self.btn_tick.hide()
        elif widget_index_stack[-1] == 2:
            self.btn_back.show()
            self.btn_tick.hide()
        elif widget_index_stack[-1] == 3:
            self.btn_back.show()
            self.btn_tick.hide()
        elif widget_index_stack[-1] == 4:
            self.btn_back.hide()
            self.btn_tick.show()
        elif widget_index_stack[-1] == 5:
            self.btn_back.show()
            self.btn_tick.hide()

        self.Stack.setCurrentIndex(widget_index_stack[-1])


    def display(self, i):
        self.Stack.setCurrentIndex(i)

    # ---------- exit ----------
    def exit_program(self):
        global app, detect_item_flag
        detect_item_flag = False
        camera.release() 
        destroyAllWindows()
        self.close()
        # QApplication.quit()

    def menu_message_box(self):
        btn_font = QFont('IRANSans', 14)
        lb_font = QFont('IRANSans', 18)

        box = QMessageBox()
        box.setStyleSheet("QLabel{min-width: 150px; min-height: 50px;} QPushButton{min-width: 120px; min-height: 40px;}")
        #box.setStyleSheet('font-size : 18px')
        box.setIcon(QMessageBox.Information)
        #box.setWindowTitle('!خطا')
        box.setText('به زودی!')
        box.setFont(lb_font)
        box.setStandardButtons(QMessageBox.Ok)

        buttonOK = box.button(QMessageBox.Ok)
        buttonOK.setText('متوجه شدم')
        buttonOK.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E5631, stop:1 #2ea444);'
                               'color: #ffffff; padding: 3px; border: none; border-radius: 6px;')
        buttonOK.setFont(btn_font)
        box.exec_()
        
        if box.clickedButton() == buttonOK:
            box.close()

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
    
    camera = 0
    user_items = []
    widget_index_stack = []
    items = Database.getItems()
    categories = Database.getCategories()
    thred_load_model = Thread(target=loadModel)
    thred_load_model.start()
    
    app = QApplication(sys.argv)
    app.setFont(QFont('IRANSans', 13))
    window = Main_Program()
    window.showIsLoading()
    sys.exit(app.exec_())