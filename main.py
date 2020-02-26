import sys
import requests
import cv2 as cv
import threading
import numpy as np
import mysql.connector
from scipy import stats
import tensorflow as tf
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from database import Database
from functools import partial
import pyzbar.pyzbar as pyzbar
from app import *
from login import Login_user
from login import Login_admin
from aescipher import AESCipher

x = 1

def scanQrCode():
    global user, cap

    cap = cv.VideoCapture(0)
    detector = cv.QRCodeDetector()
    aes = AESCipher(key)
    print('start scan qrcode')

    user = Database.signInUser('09150471487', 'Sajjad140573')
    window.show_menu()
    return

    while True:
        _, img = cap.read()
        decodedObjects = pyzbar.decode(img)

        for obj in decodedObjects:
            print('Type:', obj.type)
            print('Data:', obj.data)

            try:
                decrypted_data = aes.decrypt(obj.data)

                print("QR Code decrypted data:", decrypted_data)

                splited_decrypted_data = decrypted_data.split(' ')
                mobile_number = splited_decrypted_data[0]
                password = splited_decrypted_data[1]

                user = Database.signinUser(mobile_number, password)

                if user:
                    print(user)
                    window.show_menu()
                    return
                else:
                    print('user not found')

            except:
                print('QRCode data is not valid')


def loadModel():
    global model
    # model = tf.keras.models.load_model('../farazist.h5')
    print('model successfully loaded')


def deliveryItems():
    global categories_count
    global flag
    global model
    global delivery_items_flag
    global predict_item_flag
    global user_items

    cap = cv.VideoCapture(0)
    
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

                _, frame = cap.read()
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                frame = cv.resize(frame, (299, 299))
                frame = frame.reshape(1, 299, 299, 3)
                frame = frame / 255.0

                # prediction = model.predict([frame])
                prediction = np.random.rand(1, 20)

                if np.max(prediction) > 0.8:
                    predicted = np.argmax(prediction)
                    print(items[predicted])

                    window.lb_2_s2.setText(items[predicted]['name'])

                if predict_item_flag == False:
                    predict_item_list.append(predicted)

                if predict_item_flag == True:
                    most_probability_item = stats.mode(predict_item_list).mode[0]

                    print('most probability item:', most_probability_item)

                    category_index = items[most_probability_item]['category_id'] - 1
                    categories_count[category_index] += 1

                    for i in range(len(categories_count)):
                        window.grid_widget_s2[2][i].setText(str(categories_count[i]))

                    for item in user_items:
                        if item['id'] == items[most_probability_item]['id']:
                            item['count'] += 1
                            break
                    else:
                        user_items.append(items[most_probability_item])
                        user_items[-1]['count'] = 1

                    predict_item_list = []
                    predict_item_flag = False

            if cv.waitKey(1) & 0XFF == ord('q'):
                break

        except:
            print("error")

    cap.release()
    cv.destroyAllWindows()


cap = cv.VideoCapture(0)
class Main_Program(QWidget):
    
    def __init__(self):
        
        super(Main_Program, self).__init__()

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
        self.btn_back.setIcon(QIcon('images/sign/arrow-back-outline.png'))
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
        self.btn_tick.setIcon(QIcon('images/sign/tick-outline.png'))
        self.btn_tick.setIconSize(QSize(40, 40))

        # sp_retain = QSizePolicy()
        # sp_retain.setRetainSizeWhenHidden(True)
        self.btn_tick.setSizePolicy(sp_retain)

        h_layout_header.addWidget(self.btn_tick, alignment=Qt.AlignRight)

        # -------------------- creat stack widgets --------------------

        self.stacks = [QWidget() for _ in range(11)]

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
        self.stack_10_UI()

        # -------------------- add stack to main layout --------------------
        v_layout.addWidget(self.Stack)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showMaximized()

    # -------------------- پنجره تیزر تبلیغاتی --------------------
    def stack_0_UI(self):
        btn_setting = self.setting_button()
        btn_login = self.login_button()

        v_layout_s0 = QVBoxLayout()
        h_layout_1_s0 = QHBoxLayout()
        h_layout_2_s0 = QHBoxLayout()
        ## h_layout = QHBoxLayout()

        widget_background_s0 = QWidget()
        widget_background_s0.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        # widget_background.getContentsMargins()
        widget_background_s0.setStyleSheet('background-color: #fefcfc; border-radius: 30px;')
        widget_background_s0.setLayout(h_layout_1_s0)
        v_layout_s0.addWidget(widget_background_s0)

        movie = QMovie("animation/return.gif")

        lb_1_s0 = QLabel()
        h_layout_1_s0.addWidget(lb_1_s0, alignment=Qt.AlignHCenter)
        lb_1_s0.setMovie(movie)
        movie.start()

        h_layout_2_s0.addWidget(btn_setting, alignment=Qt.AlignLeft)
        h_layout_2_s0.addWidget(btn_login, alignment=Qt.AlignRight)
        v_layout_s0.addLayout(h_layout_2_s0)

        self.stacks[0].setLayout(v_layout_s0)

    # -------------------- پنجره منو برنامه --------------------
    def stack_1_UI(self):

        btn_setting = self.setting_button()
        self.btn_back.clicked.connect(partial(self.back_window, 'back_to_teaser'))
        # -------------------- main window layout --------------------
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        # ------- child  layout
        grid_layout_s1 = QGridLayout()
        h_layout.addLayout(grid_layout_s1)
        grid_layout_s1.setContentsMargins(0, 60, 0, 50)  # (left, top, right, bottom)

        main_menu_buttons = [   
            [
                {'text': 'تحویل پسماند', 'image': 'images/green_main_menu/Package Delivery.png', 'function': self.show_delivery},
                {'text': 'کیف پول', 'image': 'images/green_main_menu/wallet.png', 'function': self.show_wallet},
                {'text': 'شارژ واحد مسکونی', 'image': 'images/green_main_menu/Charging Residential Unit.png', 'function': None},
                {'text': 'واریز به بازیافت کارت', 'image': 'images/green_main_menu/Deposit to card recycling.png', 'function': None}
            ],
            [
                {'text': 'کمک به محیط زیست', 'image': 'images/green_main_menu/Helping the environment.png', 'function': None},
                {'text': 'کمک به خیریه', 'image': 'images/green_main_menu/Donate to charity.png', 'function': None},
                {'text': 'خرید شارژ', 'image': 'images/green_main_menu/to buy credit.png', 'function': None},
                {'text': 'فروشگاه', 'image': 'images/green_main_menu/Store.png', 'function': None}
            ]
        ]

        # grid layout children
        self.v_layouts_main_menu = [[QVBoxLayout() for _ in range(4)] for _ in range(2)]
        
        for i in range(2):
            for j in range(4):
                self.v_layouts_main_menu[i][j].setContentsMargins(10, 0, 10, 20)
                
                grid_layout_s1.addLayout(self.v_layouts_main_menu[i][j], i, j, Qt.AlignCenter)

                btn = QPushButton()
                btn.setIcon(QIcon(main_menu_buttons[i][j]['image']))
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setIconSize(QSize(110, 110))
                btn.setMaximumSize(200, 200)
                btn.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')

                if main_menu_buttons[i][j]['function']:
                    btn.clicked.connect(main_menu_buttons[i][j]['function'])
                self.v_layouts_main_menu[i][j].addWidget(btn)

                lbl = QLabel()
                lbl.setText(main_menu_buttons[i][j]['text'])
                self.v_layouts_main_menu[i][j].addWidget(lbl, alignment=Qt.AlignHCenter)

        v_layout.addLayout(h_layout)
        v_layout.addWidget(btn_setting)

        self.stacks[1].setLayout(v_layout)

    # -------------------- پنجره تحویل پکیج --------------------
    def stack_2_UI(self):

        btn_setting = self.setting_button()

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
        h_layout2_s2.setContentsMargins(0, 0, 90, 20)
        v_layout.addLayout(h_layout2_s2)

        self.grid_widget_s2 = [[QLabel() for _ in range(len(categories))] for _ in range(3)]
        for i in range(3):
            for j in range(len(categories)):
                self.grid_widget_s2[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                grid_layout_s2.addWidget(self.grid_widget_s2[i][j], i, j)

        for i in range(len(categories)):
            
            img = QPixmap(categories[i]['image'][1:])
            img = img.scaledToWidth(128)
            img = img.scaledToHeight(128)

            self.grid_widget_s2[0][i].setPixmap(img)
            self.grid_widget_s2[0][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_s2[1][i].setText(categories[i]['name'])
            self.grid_widget_s2[1][i].setFont(label_font)
            self.grid_widget_s2[1][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_s2[2][i].setText('0')
            self.grid_widget_s2[2][i].setFont(label_font)
            self.grid_widget_s2[2][i].setAlignment(Qt.AlignCenter)

        lb_1_s2 = QLabel('اعتبار')
        lb_1_s2.setFont(label_font)
        h_layout1_s2.addWidget(lb_1_s2, alignment=Qt.AlignCenter)

        # --- child 3
        h_layout2_s2.addWidget(btn_setting)

        self.lb_2_s2 = QLabel()
        self.lb_2_s2.getContentsMargins()
        self.lb_2_s2.setFont(label_font)
        self.lb_2_s2.setStyleSheet('padding: 3px; border: 2px solid #3b8686; border-radius: 6px;')
        h_layout2_s2.addWidget(self.lb_2_s2, alignment=Qt.AlignLeft)

        btn_1_21 = QPushButton('بعدی')
        btn_1_21.setMinimumSize(200, 40)
        btn_1_21.setFont(btn_font)
        btn_1_21.clicked.connect(partial(self.changePredictItemFlag, True))
        btn_1_21.setStyleSheet(
            'background-color: #3b8686; color: #ffffff; padding: 3px; border: 1px solid #3b8686; border-radius: 6px;')
        h_layout2_s2.addWidget(btn_1_21, alignment=Qt.AlignRight)
        
        btn_1_22 = QPushButton('پایان')
        btn_1_22.setMinimumSize(200, 40)
        btn_1_22.setFont(btn_font)
        btn_1_22.clicked.connect(self.endDeliveryItems)
        btn_1_22.setStyleSheet(
            'background-color: #3b8686; color: #ffffff; padding: 3px; border: 1px solid #3b8686; border-radius: 6px;')
        h_layout2_s2.addWidget(btn_1_22, alignment=Qt.AlignRight)

		
        self.stacks[2].setLayout(v_layout)

    # -------------------- پنجره تنظیمات --------------------
    def stack_10_UI(self):

        self.btns_keyboard = self.show_keyborad()
        
        h_layout = QHBoxLayout()  # main window layout
        h_layout.setSpacing(500)

        group2 = QGroupBox()

        # ------- child  layout
        # --- child 1
        v_layout1_s10 = QVBoxLayout()
        v_layout1_s10.setSpacing(0)
        v_layout1_s10.setContentsMargins(150, 0, 0, 0)
        
        # ---------- child 1 widgets ----------
        # --- create line edit
        self.lb_s10 = QLineEdit()
        self.lb_s10.setMaximumSize(260, 50)
        self.lb_s10.setStyleSheet('padding: 3px; border: 2px solid #3b8686; border-radius: 6px;')
        # lb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        v_layout1_s10.addWidget(self.lb_s10)

        v_layout1_s10.addLayout(self.btns_keyboard)
        self.setLayout(v_layout1_s10)

        # --- child 2
        v_layout2_s10 = QVBoxLayout()
        v_layout2_s10.setContentsMargins(20, 0, 20, 200)
        # ---------- child 2 widgets ----------
        self.btn_00_s10 = QPushButton()
        self.btn_00_s10.setText('تنظیم شماره پورت')
        self.btn_00_s10.setFixedSize(200, 40)
        self.btn_00_s10.setStyleSheet('background-color: #3b8686; color: #ffffff; '
                                      'padding: 3px; border: 1px solid #3b8686; border-radius: 6px;')
        v_layout2_s10.addWidget(self.btn_00_s10, alignment=Qt.AlignCenter)


        self.btn_01_s10 = QPushButton()
        self.btn_01_s10.setText('خروج از برنامه')
        self.btn_01_s10.setFixedSize(200, 40)
        self.btn_01_s10.setStyleSheet('background-color: #3b8686; color: #ffffff; '
                                      'padding: 3px; border: 1px solid #3b8686; border-radius: 6px;')
        self.btn_01_s10.clicked.connect(self.exit_message_box)
        v_layout2_s10.addWidget(self.btn_01_s10, alignment=Qt.AlignCenter)

       
        # group1.setLayout(v_layout1_s10)
        group2.setLayout(v_layout2_s10)
        
        h_layout.addLayout(v_layout1_s10)
        h_layout.addWidget(group2)
        self.stacks[10].setLayout(h_layout)
    # -------------------- پنجره کیف پول --------------------
    def stack_3_UI(self):
        global user

        btn_setting = self.setting_button()

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
        self.lb_2_s3.setStyleSheet('border: None')
        v_layout2_s3.addWidget(self.lb_2_s3)

        self.lb_3_s3 = QLabel()
        self.lb_3_s3.getContentsMargins()
        self.lb_3_s3.setText('ریال')
        self.lb_3_s3.setStyleSheet('border: None')
        self.lb_3_s3.setAlignment(Qt.AlignCenter)
        v_layout2_s3.addWidget(self.lb_3_s3)

        v_layout.addWidget(btn_setting)

        self.stacks[3].setLayout(v_layout)

    # -------------------- windows method --------------------
    # ---------- flag ----------
    def changePredictItemFlag(self, value):
        global predict_item_flag
        predict_item_flag = value

    # ---------- login ----------
    def login_button(self):
        self.login_btn = QPushButton()
        self.login_btn.setText('ورود به برنامه')
        self.login_btn.setStyleSheet('background-color: #3b8686; color: #ffffff; '
                                      'padding: 3px; border: 1px solid #3b8686; border-radius: 6px;')
        self.login_btn.setMinimumWidth(200)
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.login_btn.setSizePolicy(sp_retain)
        self.login_btn.clicked.connect(self.show_login_user)
        return self.login_btn
    
    def show_login_user(self):
        self.check_login_user = Login_user()
        if self.check_login_user.exec_() == QDialog.Accepted:
            self.show_menu()
    
    # ---------- setting ----------
    def setting_button(self):
        self.setting = QPushButton()
        self.setting.setIcon(QIcon('images\sign\setting.png'))
        self.setting.setStyleSheet('border: none')
        self.setting.setIconSize(QSize(40, 40))
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.setting.setSizePolicy(sp_retain)
        self.setting.clicked.connect(self.show_setting)
        return self.setting

    def show_setting(self):
        self.check_login_admin = Login_admin()
        if self.check_login_admin.exec_() == QDialog.Accepted:
            # self.show_menu()
            self.btn_back.show()
            self.btn_tick.show()
            self.Stack.setCurrentIndex(10)

    # ---------- keyboard ----------
    def show_keyborad(self):
        g_layout = QGridLayout()
        g_layout.setSpacing(10)
        
        # --- create numbers
        board = [[0 for i in range(3)] for j in range(4)]
        font = QFont('Times', 12, QFont.Bold)

        for i in range(4):
            for j in range(3):
                btn = QPushButton()
                btn.getContentsMargins()
                btn.setFont(font)
                board[i][j] = btn

                btn_num = [[1, 2, 3],
                          [4, 5, 6], 
                          [7, 8, 9], 
                          ['', 0, '']]
                board[i][j].setText(str(btn_num[i][j]))
                board[i][j].setFixedSize(80, 40)
                board[i][j].setStyleSheet('background-color: #3b8686; color: #ffffff; border: none;')
                # board[i][j].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                g_layout.addWidget(board[i][j], i, j, alignment=Qt.AlignHCenter)

        board[0][0].clicked.connect(partial(self.number_show, 1))
        board[0][1].clicked.connect(partial(self.number_show, 2))
        board[0][2].clicked.connect(partial(self.number_show, 3))

        board[1][0].clicked.connect(partial(self.number_show, 4))
        board[1][1].clicked.connect(partial(self.number_show, 5))
        board[1][2].clicked.connect(partial(self.number_show, 6))

        board[2][0].clicked.connect(partial(self.number_show, 7))
        board[2][1].clicked.connect(partial(self.number_show, 8))
        board[2][2].clicked.connect(partial(self.number_show, 9))

        board[3][1].clicked.connect(partial(self.number_show, 0))
        board[3][2].clicked.connect(self.delete_number)

        board[3][2].setIcon(QIcon('images/sign/216103-64.png'))
        board[3][2].setIconSize(QSize(32, 32))
        
        board[3][0].hide()
        return g_layout
        # v_layout1_s10.addLayout(g_layout_1_s10)

    def number_show(self, x):
        self.lb_s10.setText(str(x))

    def delete_number(self):
        self.lb_s10.setText(self.lb_s10.text()[0:-1])

    def changePredictItemFlag(self, value):
        global predict_item_flag
        predict_item_flag = value

    def showStart(self):

        self.btn_back.hide()
        self.btn_tick.hide()
        # self.detect_thread.kill.set()
        self.thread_qr = threading.Thread(target=scanQrCode)
        self.thread_qr.start()
        self.Stack.setCurrentIndex(0)

    def show_menu(self):
        self.btn_back.show()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(1)

    def show_delivery(self):
        self.btn_back.show()
        self.btn_tick.show()
        # self.thread_detect = threading.Thread(target=Detect_Thread)
        # self.thread_detect.start()
        self.detect_thread = threading.Thread(target=deliveryItems)
        self.detectFlag = True
        self.detect_thread.start()
        self.Stack.setCurrentIndex(2)

    def endDeliveryItems(self):
        global delivery_items_flag
        delivery_items_flag = False

        print('user delivered items:', user_items)
        result = Database.addNewDelivery(user, user_items, 4)

        print('add new delivery:', result)
        self.btn_back.show()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(1)
	

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
        global cap
        self.get_parameter = get_parameter

        if self.get_parameter == 'back_to_teaser':
            self.detectFlag = False
            self.btn_back.hide()
            self.Stack.setCurrentIndex(0)

        if self.get_parameter == 'back_to_menu':
            self.detectFlag = False            
            print('22222222')
            self.btn_tick.hide()
            self.btn_back.show()
            cap.release()
            self.Stack.setCurrentIndex(1)

        if self.get_parameter == 'save_package':
            self.btn_back.hide()
            self.btn_tick.hide()
            self.Stack.setCurrentIndex(0)
            self.detectFlag = False

    def display(self, i):
        self.Stack.setCurrentIndex(i)

    # ---------- exit ----------
    def exit_program(self):
        global cap, app, detect_item_flag
        detect_item_flag = False
        cap.release() 
        cv.destroyAllWindows()
       
        self.close()
        # QApplication.quit()

    def exit_message_box(self):
        box = QMessageBox()
        box.setStyleSheet('font-size : 14px')
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle('!فرازیست')
        box.setText('از برنامه خارج می شوید؟')
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)

        buttonY = box.button(QMessageBox.Yes)
        buttonY.setText('بله')
        buttonY.setStyleSheet('background-color: #3b8686; color: #ffffff; '
                                      'border-radius: 6px;')
        buttonY.setMinimumSize(60,30)
        
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('خیر')
        buttonN.setStyleSheet('background-color: #D41529; color: #ffffff; '
                                      'border-radius: 6px;')
        buttonN.setMinimumSize(60,30)

        box.exec_()
        if box.clickedButton() == buttonY:
            self.exit_program()
        elif box.clickedButton() == buttonN:
            box.close()
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
    
    user_items = []
    items = Database.getItems()
    categories = Database.getCategories()
    thred_load_model = threading.Thread(target=loadModel)
    thred_load_model.start()
    
    app = QApplication(sys.argv)
    app.setFont(QFont('IRANSans', 13))
    window = Main_Program()
    window.showStart()
    sys.exit(app.exec_())
