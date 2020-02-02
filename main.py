__author__ = "Sara Zarei, Sajjad Aemmi"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.5"
__email__ = "sajjadaemmi@gmail.com"
__status__ = "Production"

# coding=utf-8
import sys
import requests
import cv2 as cv
import threading
import mysql.connector
import tensorflow as tf
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from functools import partial
import numpy as np
from database import Database
from scipy import stats

group1 = 0
group2 = 0
group3 = 0
group4 = 0
group5 = 0
group6 = 0
flag = False
user = ''

def qrcode_scan():
    global user
    cap = cv.VideoCapture(0)
    detector = cv.QRCodeDetector()

    print('scan 1')

    while True:
        print('scan 2')
        _, img = cap.read()
        data, bbox, _ = detector.detectAndDecode(img)  # detect and decode qr code
        user = data

        # window.show_menu()
        # break

        if data:
            print("QR Code detected, data:", data)
        
            if Database.login(data):
                window.show_menu()
                break

    cap.release()
    cv.destroyAllWindows()


def load_model():
    global model
    model = tf.keras.models.load_model('farazist.h5')


def detect_bottle():
    global group1
    global group2
    global group3
    global group4
    global group5
    global group6
    global flag

    cap = cv.VideoCapture(0)
    
    wastes = Database.getWastes()
    predict_list = []
    time = 0
    while True:
        try:
            time += 1
            if time == 30:
                time = 0

                _, frame = cap.read()
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                frame = cv.resize(frame, (299, 299))
                frame = frame.reshape(1, 299, 299, 3)

                frame = frame / 255.0
                predicted = np.argmax(model.predict([frame]))

                print(wastes[predicted])

                window.lb_2_s2.setText(wastes[predicted][1])

                if flag == False:
                    predict_list.append(predicted)

                if flag == True:
                    most_probability_bottle = stats.mode(predict_list).mode[0]

                    print('%%%%%%%%%%%%%%%%%%%%')
                    print(most_probability_bottle)
                    print('%%%%%%%%%%%%%%%%%%%%')

                    if most_probability_bottle in [13, 14, 15, 16, 17, 18, 19, 20]:
                        group1 += 1
                    elif most_probability_bottle in [1, 2, 3, 11]:
                        group2 += 1
                    elif most_probability_bottle in [4, 5, 6, 7]:
                        group3 += 1
                    elif most_probability_bottle in [8, 9]:
                        group4 += 1
                    elif most_probability_bottle in [10, 12]:
                        group5 += 1

                    window.grid_widget_s2[1][0].setText(str(group1))
                    window.grid_widget_s2[1][1].setText(str(group2))
                    window.grid_widget_s2[1][2].setText(str(group3))

                    window.grid_widget_s2[3][0].setText(str(group4))
                    window.grid_widget_s2[3][1].setText(str(group5))
                    window.grid_widget_s2[3][2].setText(str(group6))

                    predict_list = []
                    flag = False



            if cv.waitKey(1) & 0XFF == ord('q'):
                break

        except:
            print("error")

    cap.release()
    cv.destroyAllWindows()


class Main_Program(QWidget):
    

    def __init__(self):
        
        super(Main_Program, self).__init__()

        thred_load_model = threading.Thread(target=load_model)
        thred_load_model.start()

        self.detectFlag = False

        self.setStyleSheet('background-color: #f6fdfa  ')
        self.setGeometry(300, 50, 10, 10)
        self.setWindowTitle('فرازیست')

        v_layout = QVBoxLayout(self)

        widget_header = QWidget()
        widget_header.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        widget_header.getContentsMargins()
        widget_header.setFixedHeight(100)
        widget_header.setStyleSheet('background-color: #ffffff; border-radius: 30px;')
        v_layout.addWidget(widget_header)

        h_layout_header = QHBoxLayout()
        h_layout_header.setContentsMargins(40, 0, 40, 0)
        widget_header.setLayout(h_layout_header)

        # --- child 1
        self.btn_back = QPushButton()
        self.btn_back.setIcon(QIcon('images/sign/cross_basic_red.png'))
        self.btn_back.setIconSize(QSize(40, 40))

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.btn_back.setSizePolicy(sp_retain)

        h_layout_header.addWidget(self.btn_back, alignment=Qt.AlignLeft)

        # --- child 2
        logo = QPixmap('images/logo/artboard_1_0_25x_8rX_icon.ico')

        lb_logo = QLabel()
        lb_logo.setPixmap(logo)
        h_layout_header.addWidget(lb_logo, alignment=Qt.AlignCenter)

        # --- child 3
        self.btn_tick = QPushButton()
        self.btn_tick.setIcon(QIcon('images/sign/check_basic_gree.png'))
        self.btn_tick.setIconSize(QSize(40, 40))

        # sp_retain = QSizePolicy()
        # sp_retain.setRetainSizeWhenHidden(True)
        self.btn_tick.setSizePolicy(sp_retain)

        h_layout_header.addWidget(self.btn_tick, alignment=Qt.AlignRight)

        # -------------------- creat stack widgets --------------------

        self.stacks = [QWidget() for _ in range(10)]

        # self.stack0 = QWidget()  # تیزر تبلیغاتی
        # self.stack1 = QWidget()  # صفحه اصلی - منو
        # self.stack2 = QWidget()  # تحویل پکیج
        # self.stack3 = QWidget()  # کیف پول
        # self.stack4 = QWidget()  # شارژ واحد مسکونی
        # self.stack5 = QWidget()  # واریز به بازیافت کارت
        # self.stack6 = QWidget()  # کمک به محیط زیست
        # self.stack7 = QWidget()  # کمک به خیریه
        # self.stack8 = QWidget()  # خریز شارژ
        # self.stack9 = QWidget()  # فروشگاه

        # -------------------- create stacks --------------------
        self.Stack = QStackedWidget(self)

        for stack in self.stacks:
            self.Stack.addWidget(stack)

        # -------------------- stacks method --------------------
        self.stack_0_UI()
        self.stack_1_UI()
        self.stack_2_UI()
        self.stack_3_UI()

        # -------------------- add stack to main layout --------------------
        v_layout.addWidget(self.Stack)

        self.show_teaser()

        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

    # -------------------- پنجره تیزر تبلیغاتی --------------------
    def stack_0_UI(self):
        v_layout_s0 = QVBoxLayout()
        h_layout = QHBoxLayout()

        widget_background_s0 = QWidget()
        widget_background_s0.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        # widget_background.getContentsMargins()
        widget_background_s0.setStyleSheet('background-color: #fefcfc; border-radius: 30px;')
        widget_background_s0.setLayout(h_layout)
        v_layout_s0.addWidget(widget_background_s0)

        movie = QMovie("animation/return.gif")

        lb_1_s0 = QLabel()
        h_layout.addWidget(lb_1_s0, alignment=Qt.AlignHCenter)
        lb_1_s0.setMovie(movie)
        movie.start()

        self.stacks[0].setLayout(v_layout_s0)

    # -------------------- پنجره منو برنامه --------------------
    def stack_1_UI(self):

        self.btn_back.clicked.connect(partial(self.back_window, 'back_to_teaser'))
        # -------------------- main window layout --------------------
        h_layout = QHBoxLayout()

        # ------- child  layout
        # --- child 1
        grid_layout_s1 = QGridLayout()
        h_layout.addLayout(grid_layout_s1)
        grid_layout_s1.setContentsMargins(0, 60, 0, 50)  # (left, top, right, bottom)

        # grid layout children
        self.v_layout_00_s1 = QVBoxLayout()
        self.v_layout_00_s1.setContentsMargins(10, 0, 10, 20)

        self.v_layout_01_s1 = QVBoxLayout()
        self.v_layout_01_s1.setContentsMargins(10, 0, 10, 20)

        self.v_layout_02_s1 = QVBoxLayout()
        self.v_layout_02_s1.setContentsMargins(10, 0, 10, 20)

        self.v_layout_03_s1 = QVBoxLayout()
        self.v_layout_03_s1.setContentsMargins(10, 0, 10, 20)

        # row 1
        self.v_layout_10_s1 = QVBoxLayout()
        self.v_layout_10_s1.setContentsMargins(10, 20, 10, 0)

        self.v_layout_11_s1 = QVBoxLayout()
        self.v_layout_11_s1.setContentsMargins(10, 20, 10, 0)

        self.v_layout_12_s1 = QVBoxLayout()
        self.v_layout_12_s1.setContentsMargins(10, 20, 10, 0)

        self.v_layout_13_s1 = QVBoxLayout()
        self.v_layout_13_s1.setContentsMargins(10, 20, 10, 0)

        # ------- add child layout to grid layout
        # row 0
        grid_layout_s1.addLayout(self.v_layout_00_s1, 0, 0, Qt.AlignCenter)
        grid_layout_s1.addLayout(self.v_layout_01_s1, 0, 1, Qt.AlignCenter)
        grid_layout_s1.addLayout(self.v_layout_02_s1, 0, 2, Qt.AlignCenter)
        grid_layout_s1.addLayout(self.v_layout_03_s1, 0, 3, Qt.AlignCenter)

        # row 1
        grid_layout_s1.addLayout(self.v_layout_10_s1, 1, 0, Qt.AlignCenter)
        grid_layout_s1.addLayout(self.v_layout_11_s1, 1, 1, Qt.AlignCenter)
        grid_layout_s1.addLayout(self.v_layout_12_s1, 1, 2, Qt.AlignCenter)
        grid_layout_s1.addLayout(self.v_layout_13_s1, 1, 3, Qt.AlignCenter)

        # -------------------- create widgets of grid layout --------------------
        # ------- buttons
        # row 0
        self.btn_00_s1 = QPushButton()
        self.btn_00_s1.setIcon(QIcon('images/green_main_menu/Package Delivery.png'))
        self.btn_00_s1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_00_s1.setIconSize(QSize(110, 110))
        self.btn_00_s1.setMaximumSize(200, 200)
        self.btn_00_s1.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')
        self.btn_00_s1.clicked.connect(self.show_package_delivery)
        self.v_layout_00_s1.addWidget(self.btn_00_s1)

        self.btn_01_s1 = QPushButton()
        self.btn_01_s1.setIcon(QIcon('images/green_main_menu/wallet.png'))
        self.btn_01_s1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_01_s1.setIconSize(QSize(110, 110))
        self.btn_01_s1.setMaximumSize(200, 200)
        self.btn_01_s1.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')
        self.btn_01_s1.clicked.connect(self.show_wallet)
        self.v_layout_01_s1.addWidget(self.btn_01_s1)

        self.btn_02_s1 = QPushButton()
        self.btn_02_s1.setIcon(QIcon('images/green_main_menu/Charging Residential Unit.png'))
        self.btn_02_s1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_02_s1.setIconSize(QSize(110, 110))
        self.btn_02_s1.setMaximumSize(200, 200)
        self.btn_02_s1.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')
        # self.btn_2_02.clicked.connect(self.show_taxes_page)
        self.v_layout_02_s1.addWidget(self.btn_02_s1)

        self.btn_03_s1 = QPushButton()
        self.btn_03_s1.setIcon(QIcon('images/green_main_menu/Deposit to card recycling.png'))
        self.btn_03_s1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_03_s1.setIconSize(QSize(110, 110))
        self.btn_03_s1.setMaximumSize(200, 200)
        self.btn_03_s1.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')
        # self.btn_2_03.clicked.connect(self.show_store_page)
        self.v_layout_03_s1.addWidget(self.btn_03_s1)

        # row 1
        self.btn_10_s1 = QPushButton()
        self.btn_10_s1.setIcon(QIcon('images/green_main_menu/Helping the environment.png'))
        self.btn_10_s1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_10_s1.setIconSize(QSize(110, 110))
        self.btn_10_s1.setMaximumSize(200, 200)
        self.btn_10_s1.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')
        # self.btn_2_10.clicked.connect(self.show_bill_page)
        self.v_layout_10_s1.addWidget(self.btn_10_s1)

        self.btn_11_s1 = QPushButton()
        self.btn_11_s1.setIcon(QIcon('images/green_main_menu/Donate to charity.png'))
        self.btn_11_s1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_11_s1.setIconSize(QSize(110, 110))
        self.btn_11_s1.setMaximumSize(200, 200)
        self.btn_11_s1.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')
        # self.btn_2_11.clicked.connect(self.show_credit_page)
        self.v_layout_11_s1.addWidget(self.btn_11_s1)

        self.btn_12_s1 = QPushButton()
        self.btn_12_s1.setIcon(QIcon('images/green_main_menu/to buy credit.png'))
        self.btn_12_s1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_12_s1.setIconSize(QSize(110, 110))
        self.btn_12_s1.setMaximumSize(200, 200)
        self.btn_12_s1.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')
        # self.btn_2_12.clicked.connect(self.show_wallet_page)
        self.v_layout_12_s1.addWidget(self.btn_12_s1)

        self.btn_13_s1 = QPushButton()
        self.btn_13_s1.setIcon(QIcon('images/green_main_menu/Store.png'))
        self.btn_13_s1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_13_s1.setIconSize(QSize(110, 110))
        self.btn_13_s1.setMaximumSize(200, 200)
        self.btn_13_s1.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686 ; border-radius: 30px;')
        # self.btn_2_13.clicked.connect(self.show_manage_show)
        self.v_layout_13_s1.addWidget(self.btn_13_s1)

        # ------- labels
        # row 0
        lb_00_s1 = QLabel()
        lb_00_s1.setText('تحویل پکیج')
        self.v_layout_00_s1.addWidget(lb_00_s1, alignment=Qt.AlignHCenter)

        lb_01_s1 = QLabel()
        lb_01_s1.setText('کیف پول')
        self.v_layout_01_s1.addWidget(lb_01_s1, alignment=Qt.AlignHCenter)

        lb_02_s1 = QLabel()
        lb_02_s1.setText('شارژ واحد مسکونی')
        self.v_layout_02_s1.addWidget(lb_02_s1, alignment=Qt.AlignHCenter)

        lb_03_s1 = QLabel()
        lb_03_s1.setText('واریز به بازیافت کارت')
        self.v_layout_03_s1.addWidget(lb_03_s1, alignment=Qt.AlignHCenter)

        # row 1
        lb_10_s1 = QLabel()
        lb_10_s1.setText('کمک به محیط زیست')
        self.v_layout_10_s1.addWidget(lb_10_s1, alignment=Qt.AlignHCenter)

        lb_11_s1 = QLabel()
        lb_11_s1.setText('کمک به سازمانهای خیریه')
        self.v_layout_11_s1.addWidget(lb_11_s1, alignment=Qt.AlignHCenter)

        lb_12_s1 = QLabel()
        lb_12_s1.setText('خرید شارژ')
        self.v_layout_12_s1.addWidget(lb_12_s1, alignment=Qt.AlignHCenter)

        lb_13_s1 = QLabel()
        lb_13_s1.setText('فروشگاه')
        self.v_layout_13_s1.addWidget(lb_13_s1, alignment=Qt.AlignHCenter)

        self.stacks[1].setLayout(h_layout)

    # -------------------- پنجره تحویل پکیج --------------------
    def stack_2_UI(self):

        self.btn_back.clicked.connect(partial(self.back_window, 'back_to_menu'))
        self.btn_tick.clicked.connect(partial(self.back_window, 'save_package'))

        btn_font = QFont('IRANSans', 11)
        label_font = QFont('IRANSans', 13)

        v_layout = QVBoxLayout()  # main window layout
        v_layout.setSpacing(40)


        # ------- child  layout
        # --- child 1
        h_layout1_s2 = QHBoxLayout()
        h_layout1_s2.setContentsMargins(0, 0, 100, 0)

        grid_layout_s2 = QGridLayout()
        grid_layout_s2.setContentsMargins(50, 30, 70, 20)
        grid_layout_s2.setSpacing(0)
        h_layout1_s2.addLayout(grid_layout_s2)

        widget_background_s2 = QWidget()
        widget_background_s2.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        widget_background_s2.getContentsMargins()
        widget_background_s2.setStyleSheet('background-color: #ffffff; border-radius: 30px;')
        # background_1_10.setGraphicsEffect(self.shadow)
        widget_background_s2.setLayout(h_layout1_s2)
        v_layout.addWidget(widget_background_s2)

        h_layout2_s2 = QHBoxLayout()
        h_layout2_s2.setContentsMargins(90, 0, 90, 20)
        v_layout.addLayout(h_layout2_s2)

        self.grid_widget_s2 = [[QLabel() for _ in range(3)] for _ in range(4)]
        for i in range(4):
            for j in range(3):
                self.grid_widget_s2[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                grid_layout_s2.addWidget(self.grid_widget_s2[i][j], i, j)

        # row0
        img_1_s2 = QPixmap('images/bottles/noshabe.png')
        # img_1_s2 = img_1_s2.scaledToWidth(100)
        # img_1_s2 = img_1_s2.scaledToHeight(100)
        self.grid_widget_s2[0][0].setPixmap(img_1_s2)
        self.grid_widget_s2[0][0].setAlignment(Qt.AlignCenter)


        img_2_s2 = QPixmap('images/bottles/ab.png')
        # img_2_s2 = img_2_s2.scaledToWidth(80)
        # img_2_s2 = img_2_s2.scaledToHeight(80)
        self.grid_widget_s2[0][1].setPixmap(img_2_s2)
        self.grid_widget_s2[0][1].setAlignment(Qt.AlignCenter)

        img_3_s2 = QPixmap('images/bottles/delester.png')
        # img_3_s2 = img_3_s2.scaledToWidth(80)
        # img_3_s2 = img_3_s2.scaledToHeight(80)
        self.grid_widget_s2[0][2].setPixmap(img_3_s2)
        self.grid_widget_s2[0][2].setAlignment(Qt.AlignCenter)


        # row 1
        self.grid_widget_s2[1][0].setText('0')
        self.grid_widget_s2[1][0].setFont(label_font)
        self.grid_widget_s2[1][0].setAlignment(Qt.AlignCenter)

        self.grid_widget_s2[1][1].setText('0')
        self.grid_widget_s2[1][1].setFont(label_font)
        self.grid_widget_s2[1][1].setAlignment(Qt.AlignCenter)

        self.grid_widget_s2[1][2].setText('0')
        self.grid_widget_s2[1][2].setFont(label_font)
        self.grid_widget_s2[1][2].setAlignment(Qt.AlignCenter)

        # row 2
        img_4_s2 = QPixmap('images/bottles/cola.png')
        img_4_s2 = img_4_s2.scaledToWidth(80)
        img_4_s2 = img_4_s2.scaledToHeight(80)
        self.grid_widget_s2[2][0].setPixmap(img_4_s2)
        self.grid_widget_s2[2][0].setAlignment(Qt.AlignCenter)

        img_5_s2 = QPixmap('images/bottles/can.png')
        # img_5_s2 = img_5_s2.scaledToWidth(80)
        # img_5_s2 = img_5_s2.scaledToHeight(80)
        self.grid_widget_s2[2][1].setPixmap(img_5_s2)
        self.grid_widget_s2[2][1].setAlignment(Qt.AlignCenter)

        img_6_s2 = QPixmap('images/bottles/shishe.png')
        # img_6_s2 = img_6_s2.scaledToWidth(80)
        # img_6_s2 = img_6_s2.scaledToHeight(80)
        self.grid_widget_s2[2][2].setPixmap(img_6_s2)
        self.grid_widget_s2[2][2].setAlignment(Qt.AlignCenter)

        # row 3
        self.grid_widget_s2[3][0].setText('0')
        self.grid_widget_s2[3][0].setFont(label_font)
        self.grid_widget_s2[3][0].setAlignment(Qt.AlignCenter)

        self.grid_widget_s2[3][1].setText('0')
        self.grid_widget_s2[3][1].setFont(label_font)
        self.grid_widget_s2[3][1].setAlignment(Qt.AlignCenter)

        self.grid_widget_s2[3][2].setText('0')
        self.grid_widget_s2[3][2].setFont(label_font)
        self.grid_widget_s2[3][2].setAlignment(Qt.AlignCenter)

        lb_1_s2 = QLabel('اعتبار')
        lb_1_s2.setFont(label_font)
        h_layout1_s2.addWidget(lb_1_s2, alignment=Qt.AlignCenter)

        # --- child 3
        self.lb_2_s2 = QLabel()
        self.lb_2_s2.getContentsMargins()
        self.lb_2_s2.setFont(label_font)
        self.lb_2_s2.setStyleSheet('padding: 3px; border: 2px solid #3b8686; border-radius: 6px;')
        h_layout2_s2.addWidget(self.lb_2_s2, alignment=Qt.AlignLeft)

        btn_1_21 = QPushButton('بعدی')
        btn_1_21.setMinimumSize(200, 40)
        btn_1_21.setFont(btn_font)
        btn_1_21.clicked.connect(self.change_flag)
        btn_1_21.setStyleSheet(
            'background-color: #3b8686; color: #ffffff; padding: 3px; border: 1px solid #3b8686; border-radius: 6px;')
        h_layout2_s2.addWidget(btn_1_21, alignment=Qt.AlignRight)

        self.stacks[2].setLayout(v_layout)

    # -------------------- پنجره کیف پول --------------------
    def stack_3_UI(self):
        global user

        v_layout = QVBoxLayout()

        v_layout1_s3 = QVBoxLayout()
        # v_layout1_s3.getContentsMargins()
        v_layout1_s3.setAlignment(Qt.AlignCenter)

        v_layout2_s3 = QVBoxLayout()
        v_layout2_s3.setAlignment(Qt.AlignCenter)
        
        widget_background1_s3 = QWidget()
        widget_background1_s3.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        # widget_background.getContentsMargins()
        widget_background1_s3.setStyleSheet('background-color: #ffffff; border-radius: 30px;')
        widget_background1_s3.setLayout(v_layout1_s3)
        v_layout.addWidget(widget_background1_s3)


        widget_background2_s3 = QWidget()
        # widget_background_s4.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        widget_background2_s3.setMinimumSize(200,200)
        # widget_background2_s3.getContentsMargins()
        widget_background2_s3.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')
        widget_background2_s3.setLayout(v_layout2_s3)
        v_layout1_s3.addWidget(widget_background2_s3)

        self.lb_1_s3 = QLabel()
        self.lb_1_s3.getContentsMargins()
        self.lb_1_s3.setText('موجودی')
        self.lb_1_s3.setStyleSheet('border: None')
        v_layout2_s3.addWidget(self.lb_1_s3)

        self.lb_2_s3 = QLabel()
        self.lb_2_s3.getContentsMargins()
        # self.lb_2_s3.setText(Database.getWallet())
        print('@@@@@@@', Database.getWallet(user))
        self.lb_2_s3.setStyleSheet('border: None')
        v_layout2_s3.addWidget(self.lb_2_s3)

        self.lb_3_s3 = QLabel()
        self.lb_3_s3.getContentsMargins()
        self.lb_3_s3.setText('ریال')
        self.lb_3_s3.setStyleSheet('border: None')
        self.lb_3_s3.setAlignment(Qt.AlignCenter)
        v_layout2_s3.addWidget(self.lb_3_s3)


        self.stacks[3].setLayout(v_layout)

    # -------------------- windows method --------------------
    def change_flag(self):
        global flag
        flag = True

    def show_teaser(self):
        self.btn_back.hide()
        self.btn_tick.hide()
        # self.detect_thread.kill.set()
        self.thread_qr = threading.Thread(target=qrcode_scan)
        self.thread_qr.start()
        self.Stack.setCurrentIndex(0)

    def show_menu(self):
        self.btn_back.show()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(1)

    def show_package_delivery(self):
        self.btn_back.show()
        self.btn_tick.show()
        # self.thread_detect = threading.Thread(target=Detect_Thread)
        # self.thread_detect.start()
        self.detect_thread = threading.Thread(target=detect_bottle)
        self.detectFlag = True
        self.detect_thread.start()
        self.Stack.setCurrentIndex(2)

    def show_wallet(self):
        self.Stack.setCurrentIndex(3)

    def show_charging_unit(self):
        self.Stack.setCurrentIndex(5)

    def show_deposit_to_card(self):
        self.Stack.setCurrentIndex(6)

    def show_helping_to_environment(self):
        self.Stack.setCurrentIndex(7)

    def show_charity(self):
        self.Stack.setCurrentIndex(8)

    def show_buy_credit(self):
        self.Stack.setCurrentIndex(9)

    def show_store(self):
        self.Stack.setCurrentIndex(10)

    def back_window(self, get_parameter):
        self.get_parameter = get_parameter

        if self.get_parameter == 'back_to_teaser':
            self.btn_back.hide()
            self.Stack.setCurrentIndex(0)

        if self.get_parameter == 'back_to_menu':
            # self.detectFlag = False
            self.detect_thread.kill()            
            print('22222222')
            self.btn_tick.hide()
            self.btn_back.show()
            self.Stack.setCurrentIndex(1)

        if self.get_parameter == 'save_package':
            self.btn_back.hide()
            self.btn_tick.hide()
            self.Stack.setCurrentIndex(0)
            self.detectFlag = False

    def display(self, i):
        self.Stack.setCurrentIndex(i)

    # def show_main_menu(self):
    #     self.thread_obj.kill.set()
    #     cv.destroyWindow('Window1')
    #     # cv.waitKey(1)
    #     self.Stack.setCurrentIndex(0)

    # def show_garbage_page(self):
    #     self.thread_obj = Thread_()
    #     self.thread_obj.start()
    #     self.Stack.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('IRANSans', 13))
    window = Main_Program()
    sys.exit(app.exec_())
