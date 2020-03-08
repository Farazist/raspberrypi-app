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
from login import Login_pass
from keyboard import KEYBoard
from aescipher import AESCipher
from localdatabase import LocalDataBase


def scanQrCode():
    global user, cap

    qrcode_camera_port = LocalDataBase.selectOne('system_id')[2]

    cap = cv.VideoCapture(int(qrcode_camera_port))
    
    detector = cv.QRCodeDetector()
    aes = AESCipher(key)
    print('start scan qrcode')

    user = Database.signInUser('09150471487', '1234')
    # window.show_menu()
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


def detectItem():
    global categories_count
    global flag
    global model
    global delivery_items_flag
    global predict_item_flag
    global user_items

    item_camera_port = LocalDataBase.selectOne('item_camera_port')[2]

    cap = cv.VideoCapture(int(item_camera_port))
    
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

                    window.lb_2_s3.setText(items[predicted]['name'])

                if predict_item_flag == False:
                    predict_item_list.append(predicted)

                if predict_item_flag == True:
                    most_probability_item = stats.mode(predict_item_list).mode[0]

                    print('most probability item:', most_probability_item)

                    category_index = items[most_probability_item]['category_id'] - 1
                    categories_count[category_index] += 1

                    for i in range(len(categories_count)):
                        window.grid_widget_s3[2][i].setText(str(categories_count[i]))

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
button_style = 'background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E5631, stop:1 #2ea444); color: #ffffff; padding: 3px; border: none; border-radius: 6px;'

class Main_Program(QWidget):
    
    def __init__(self):
        
        super(Main_Program, self).__init__()

        self.detectFlag = False

        self.setContentsMargins(10, 10, 10, 5)

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

        self.stacks = [QWidget() for _ in range(12)]

        # self.stack0 = QWidget()  # تیزر تبلیغاتی
        # self.stack1 = QWidget()  # qr پنجره
        # self.stack2 = QWidget()  # صفحه اصلی - منو
        # self.stack3 = QWidget()  # تحویل پکیج
        # self.stack4 = QWidget()  # کیف پول
        # self.stack5 = QWidget()  # شارژ واحد مسکونی
        # self.stack6 = QWidget()  # واریز به بازیافت کارت
        # self.stack7 = QWidget()  # کمک به محیط زیست
        # self.stack8 = QWidget()  # کمک به خیریه
        # self.stack9 = QWidget()  # خریز شارژ
        # self.stack10 = QWidget()  # فروشگاه

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
        self.stack_11_UI()

        # -------------------- add stack to main layout --------------------
        v_layout.addWidget(self.Stack)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showMaximized()
        
        # self.setFixedSize(1000, 600)
        # self.show()

    # -------------------- پنجره تیزر تبلیغاتی --------------------
    def stack_0_UI(self):
        btn_setting = self.setting_button()
        #btn_login, btn_qr = self.login_button()
        wwww = self.login_button()

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

        self.lb_1_s0 = QLabel()
        h_layout_1_s0.addWidget(self.lb_1_s0, alignment=Qt.AlignHCenter)
        self.lb_1_s0.setMovie(movie)
        movie.start()

        h_layout_2_s0.addWidget(btn_setting, alignment=Qt.AlignLeft)
        #h_layout_2_s0.addWidget(btn_qr, alignment=Qt.AlignRight)
        #h_layout_2_s0.addWidget(btn_login, alignment=Qt.AlignRight)
        h_layout_2_s0.addLayout(wwww)
        v_layout_s0.addLayout(h_layout_2_s0)

        self.stacks[0].setLayout(v_layout_s0)

    # -------------------- qr پنجره نمایش --------------------
    def stack_1_UI(self):
        btn_setting = self.setting_button()
        self.btn_back.clicked.connect(partial(self.back_window, 'back_to_teaser'))

        v_layout_s1 = QVBoxLayout()
        
        self.lb_1_s1 = QLabel()
        v_layout_s1.addWidget(self.lb_1_s1, alignment=Qt.AlignCenter)
        v_layout_s1.addWidget(btn_setting, alignment=Qt.AlignLeft)

        self.stacks[1].setLayout(v_layout_s1)

    # -------------------- پنجره منو برنامه --------------------
    def stack_2_UI(self):

        btn_setting = self.setting_button()
        self.btn_back.clicked.connect(partial(self.back_window, 'back_to_teaser'))
        # -------------------- main window layout --------------------
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        # ------- child  layout
        grid_layout_s2 = QGridLayout()
        h_layout.addLayout(grid_layout_s2)
        grid_layout_s2.setContentsMargins(0, 60, 0, 50)  # (left, top, right, bottom)

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
                
                grid_layout_s2.addLayout(self.v_layouts_main_menu[i][j], i, j, Qt.AlignCenter)

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

        self.stacks[2].setLayout(v_layout)

    # -------------------- پنجره تحویل پکیج --------------------
    def stack_3_UI(self):

        btn_setting = self.setting_button()

        self.btn_back.clicked.connect(partial(self.back_window, 'back_to_menu'))
        self.btn_tick.clicked.connect(partial(self.back_window, 'save_package'))

        btn_font = QFont('IRANSans', 11)
        label_font = QFont('IRANSans', 13)

        v_layout = QVBoxLayout()  # main window layout
        v_layout.setSpacing(40)

        # ------- child  layout
        # --- child 1
        h_layout1_s3 = QHBoxLayout()
        h_layout1_s3.setContentsMargins(0, 0, 100, 0)

        grid_layout_s3 = QGridLayout()
        grid_layout_s3.setContentsMargins(50, 30, 70, 20)
        grid_layout_s3.setSpacing(0)
        h_layout1_s3.addLayout(grid_layout_s3)

        widget_background_s3 = QWidget()
        widget_background_s3.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        widget_background_s3.getContentsMargins()
        widget_background_s3.setStyleSheet('background-color: #ffffff; border-radius: 30px;')
        # background_1_10.setGraphicsEffect(self.shadow)
        widget_background_s3.setLayout(h_layout1_s3)
        v_layout.addWidget(widget_background_s3)

        h_layout2_s3 = QHBoxLayout()
        h_layout2_s3.setContentsMargins(0, 0, 90, 20)
        v_layout.addLayout(h_layout2_s3)

        self.grid_widget_s3 = [[QLabel() for _ in range(len(categories))] for _ in range(3)]
        for i in range(3):
            for j in range(len(categories)):
                self.grid_widget_s3[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                grid_layout_s3.addWidget(self.grid_widget_s3[i][j], i, j)

        for i in range(len(categories)):
            
            img = QPixmap(categories[i]['image'][1:])
            img = img.scaledToWidth(128)
            img = img.scaledToHeight(128)

            self.grid_widget_s3[0][i].setPixmap(img)
            self.grid_widget_s3[0][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_s3[1][i].setText(categories[i]['name'])
            self.grid_widget_s3[1][i].setFont(label_font)
            self.grid_widget_s3[1][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_s3[2][i].setText('0')
            self.grid_widget_s3[2][i].setFont(label_font)
            self.grid_widget_s3[2][i].setAlignment(Qt.AlignCenter)

        lb_1_s3 = QLabel('اعتبار')
        lb_1_s3.setFont(label_font)
        h_layout1_s3.addWidget(lb_1_s3, alignment=Qt.AlignCenter)

        # --- child 3
        h_layout2_s3.addWidget(btn_setting)

        self.lb_2_s3 = QLabel()
        self.lb_2_s3.getContentsMargins()
        self.lb_2_s3.setFont(label_font)
        self.lb_2_s3.setStyleSheet('padding: 3px; border: 2px solid #1E5631; border-radius: 6px;')
        h_layout2_s3.addWidget(self.lb_2_s3, alignment=Qt.AlignLeft)

        btn_1_21 = QPushButton('بعدی')
        btn_1_21.setMinimumSize(200, 40)
        btn_1_21.setFont(btn_font)
        btn_1_21.clicked.connect(partial(self.changePredictItemFlag, True))
        btn_1_21.setStyleSheet(button_style)
        h_layout2_s3.addWidget(btn_1_21, alignment=Qt.AlignRight)
        
        btn_1_22 = QPushButton('پایان')
        btn_1_22.setMinimumSize(200, 40)
        btn_1_22.setFont(btn_font)
        # btn_1_22.clicked.connect(self.endDeliveryItems)
        btn_1_22.setStyleSheet(button_style)
        h_layout2_s3.addWidget(btn_1_22, alignment=Qt.AlignRight)

        self.stacks[3].setLayout(v_layout)

    # -------------------- پنجره کیف پول --------------------
    def stack_4_UI(self):
        global user

        btn_setting = self.setting_button()

        v_layout = QVBoxLayout()

        v_layout1_s4 = QVBoxLayout()
        # v_layout1_s3.getContentsMargins()
        v_layout1_s4.setAlignment(Qt.AlignCenter)

        v_layout2_s4 = QVBoxLayout()
        v_layout2_s4.setAlignment(Qt.AlignCenter)
        
        widget_background1_s4 = QWidget()
        widget_background1_s4.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        # widget_background.getContentsMargins()
        widget_background1_s4.setStyleSheet('background-color: #ffffff; border-radius: 30px;')
        widget_background1_s4.setLayout(v_layout1_s4)
        v_layout.addWidget(widget_background1_s4)


        widget_background2_s4 = QWidget()
        # widget_background_s4.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        widget_background2_s4.setMinimumSize(200,200)
        # widget_background2_s3.getContentsMargins()
        widget_background2_s4.setStyleSheet('background-color: #ffffff; border: 3px solid #1E5631; border-radius: 30px;')
        widget_background2_s4.setLayout(v_layout2_s4)
        v_layout1_s4.addWidget(widget_background2_s4)

        self.lb_1_s4 = QLabel()
        self.lb_1_s4.getContentsMargins()
        self.lb_1_s4.setText('موجودی')
        self.lb_1_s4.setStyleSheet('border: None')
        v_layout2_s4.addWidget(self.lb_1_s4)

        self.lb_2_s4 = QLabel()
        self.lb_2_s4.getContentsMargins()
        # self.lb_2_s3.setText(Database.getWallet())
        self.lb_2_s4.setStyleSheet('border: None')
        v_layout2_s4.addWidget(self.lb_2_s4)

        self.lb_3_s4 = QLabel()
        self.lb_3_s4.getContentsMargins()
        self.lb_3_s4.setText('ریال')
        self.lb_3_s4.setStyleSheet('border: None')
        self.lb_3_s4.setAlignment(Qt.AlignCenter)
        v_layout2_s4.addWidget(self.lb_3_s4)

        v_layout.addWidget(btn_setting)

        self.stacks[4].setLayout(v_layout)

    # -------------------- پنجره تنظیمات --------------------
    def stack_11_UI(self):

        h_layout = QHBoxLayout()  # main window layout
        h_layout.setSpacing(500)

        group2 = QGroupBox()

        # ------- child  layout
        # --- child 1
        v_layout1_s11 = QVBoxLayout()
        v_layout1_s11.setSpacing(0)
        v_layout1_s11.setContentsMargins(150, 0, 0, 0)
        
        # ---------- child 1 widgets ----------
        # --- create line edit
        self.lb_s11 = QLineEdit()
        self.lb_s11.setMaximumSize(260, 50)
        self.lb_s11.setStyleSheet('padding: 3px; border: 2px solid #1E5631; border-radius: 6px;')
        # lb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        v_layout1_s11.addWidget(self.lb_s11)

        self.key_widget = KEYBoard(self.lb_s11)
        self.key_layout = self.key_widget.output()
        v_layout1_s11.addLayout(self.key_layout)
        self.setLayout(v_layout1_s11)

        # --- child 2
        v_layout2_s11 = QVBoxLayout()
        v_layout2_s11.setContentsMargins(20, 0, 20, 200)
        # ---------- child 2 widgets ----------
        self.btn_00_s11 = QPushButton()
        self.btn_00_s11.setText('تنظیم شماره پورت')
        self.btn_00_s11.setFixedSize(200, 40)
        self.btn_00_s11.setStyleSheet(button_style)
        v_layout2_s11.addWidget(self.btn_00_s11, alignment=Qt.AlignCenter)


        self.btn_01_s11 = QPushButton()
        self.btn_01_s11.setText('خروج از برنامه')
        self.btn_01_s11.setFixedSize(200, 40)
        self.btn_01_s11.setStyleSheet(button_style)
        self.btn_01_s11.clicked.connect(self.exit_message_box)
        v_layout2_s11.addWidget(self.btn_01_s11, alignment=Qt.AlignCenter)

       
        # group1.setLayout(v_layout1_s10)
        group2.setLayout(v_layout2_s11)
        
        h_layout.addLayout(v_layout1_s11)
        h_layout.addWidget(group2)
        self.stacks[11].setLayout(h_layout)
    # -------------------- windows method --------------------
    # ---------- flag ----------
    def changePredictItemFlag(self, value):
        global predict_item_flag
        predict_item_flag = value

    # ---------- login ----------
    def login_button(self):
        btns_layout = QHBoxLayout()

        self.login_btn = QPushButton()
        self.login_btn.setText('ورود با نام کاربری')
        self.login_btn.setIcon(QIcon('images/sign/user-outline1.png'))
        self.login_btn.setIconSize(QSize(40, 40))
        self.login_btn.setStyleSheet(button_style)
        self.login_btn.setMinimumSize(200, 60)
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.login_btn.setSizePolicy(sp_retain)
        self.login_btn.clicked.connect(self.show_login_user)

        self.login_qr = QPushButton()
        self.login_qr.setText('کد qr ورود با')
        self.login_qr.setIcon(QIcon('images/sign/qr_code1.png'))
        self.login_qr.setIconSize(QSize(40, 40))
        self.login_qr.setStyleSheet(button_style)
        self.login_qr.setMinimumSize(200, 60)
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
        self.setting.setIconSize(QSize(40, 40))
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
            self.btn_back.show()
            self.btn_tick.show()
            self.Stack.setCurrentIndex(11)

    def showStart(self):
        import qrcode

        self.btn_back.hide()
        self.btn_tick.hide()
        # self.detect_thread.kill.set()
        self.thread_qr = threading.Thread(target=scanQrCode)
        self.thread_qr.start()
        self.Stack.setCurrentIndex(0)

    def showQR(self):
        import qrcode

        self.btn_back.show()

        data = "http://farazist.ir/"
        filename = 'images\qr\qrcode.png'

        img = qrcode.make(data)
        img.save(filename)

        open_img = QPixmap(filename)
        
        self.lb_1_s1.setPixmap(open_img)

        self.Stack.setCurrentIndex(1)

    def show_menu(self):
        self.btn_back.show()
        self.btn_tick.hide()
        self.Stack.setCurrentIndex(2)

    def show_delivery(self):
        self.btn_back.show()
        self.btn_tick.show()
        # self.thread_detect = threading.Thread(target=Detect_Thread)
        # self.thread_detect.start()
        self.detect_thread = threading.Thread(target=detectItem)
        self.detectFlag = True
        self.detect_thread.start()
        self.Stack.setCurrentIndex(3)

    def show_wallet(self):
        self.Stack.setCurrentIndex(4)

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
            self.Stack.setCurrentIndex(2)

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
        box.setStyleSheet('font-size : 16px')
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle('!فرازیست')
        box.setText('از برنامه خارج می شوید؟')
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)

        buttonY = box.button(QMessageBox.Yes)
        buttonY.setText('بله')
        buttonY.setStyleSheet(button_style)
        buttonY.setMinimumSize(60,30)
        
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('خیر')
        buttonN.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e11c1c, stop:1 #f86565);'
                              'color: #ffffff; padding: 3px; border: none; border-radius: 6px;')
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
