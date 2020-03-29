from PySide2.QtGui import (QFont, QIcon, QMovie, QPixmap)
from PySide2.QtCore import (Qt, QSize)
from PySide2.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QGraphicsDropShadowEffect, QMessageBox, QDialog, QGroupBox, QSizePolicy,
                            QWidget, QPushButton, QLabel, QLineEdit, QStackedWidget)
from functools import partial

from keyboard import KeyBoard

btn_style = 'background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E5631, stop:1 #2ea444); color: #ffffff; padding: 3px; border: none; border-radius: 6px;'
menu_font = QFont('IRANSans', 18)
package_font = QFont('IRANSans', 16)
label_font = QFont('IRANSans', 18)
number_font = QFont('IRANSansFaNum', 20, QFont.Bold)
btn_sign_font = QFont('IRANSans', 20)
textbox_style = 'background-color: #ffffff; padding: 3px; border: 1px solid #1E5631; border-radius: 6px;'
hoderText_font = QFont('IRANSansFaNum', 20, QFont.Bold)
btn_font = QFont('IRANSans', 20)
lb_font = QFont('IRANSans', 18)


class UI_MainWindow(QWidget):
    
    def __init__(self):
        
        super(UI_MainWindow, self).__init__()

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

        self.Stack = QStackedWidget(self)

        for i in range(14):
            self.Stack.addWidget(QWidget())

        # -------------------- stacks method --------------------
        self.stackLoading()
        self.stackStart()
        self.stackLogin()
        self.stackQRCode()
        self.stackMainMenu()
        self.stackDeliveryItems()
        self.stackWallet()
        self.stackSettingMenu()

        v_layout.addWidget(self.Stack)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showMaximized()
        
        # self.setFixedSize(1000, 600)
        # self.show()

    def stackLoading(self):
        loader_font = QFont('IRANSans', 24)
        farazist_font = QFont('IRANSans', 48)
        btn_setting = self.setting_button()

        v_layout_s0 = QVBoxLayout()
        v_layout_s0.setContentsMargins(0, 50, 0, 50)
        v_layout_s0.insertStretch(-1, -1)

        logo = QPixmap('images/farazist256px.ico')
        text = 'در حال بارگزاری'
        gif = QMovie("animation/Spinner.gif")

        lb_1_s0 = QLabel()
        lb_1_s0.setAlignment(Qt.AlignTop)
        lb_1_s0.setPixmap(logo)
        lb_1_s0.setMinimumHeight(500)

        lb_2_s0 = QLabel()
        lb_2_s0.setMovie(gif)
        gif.start()

        lb_3_s0 = QLabel()
        lb_3_s0.setFont(loader_font)
        lb_3_s0.setText(text)

        v_layout_s0.addWidget(lb_1_s0, alignment= Qt.AlignCenter | Qt.AlignTop)
        v_layout_s0.addWidget(lb_2_s0, alignment= Qt.AlignCenter | Qt.AlignBottom)
        v_layout_s0.addWidget(lb_3_s0, alignment= Qt.AlignCenter | Qt.AlignBottom)
        
        self.Stack.widget(0).setLayout(v_layout_s0)

    def stackStart(self):
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

        self.Stack.widget(1).setLayout(v_layout_s1)

    def stackLogin(self):
        loader_font = QFont('IRANSans', 24)
        farazist_font = QFont('IRANSans', 48)
        btn_setting = self.setting_button()

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 50, 0, 50)
        v_layout.insertStretch(-1, -1)

        lbl = QLabel()
        lbl.setAlignment(Qt.AlignTop)
        lbl.setText('ورود')
        lbl.setMinimumHeight(500)
        lbl.setMinimumSize(290, 130)

        tb_username = QLineEdit()
        tb_username.setFont(hoderText_font)
        tb_username.setFixedHeight(60)
        tb_username.setStyleSheet(textbox_style)
        tb_username.setMinimumSize(290, 130)

        btn_login = QPushButton('ورود', self)
        btn_login.setFont(btn_font)
        btn_login.setFixedHeight(60)
        #btn_login.clicked.connect(self.handleLogin)
        btn_login.setStyleSheet(btn_style)
        btn_login.setMinimumSize(290, 130)

        v_layout.addWidget(lbl, alignment=Qt.AlignCenter)
        v_layout.addWidget(tb_username, alignment=Qt.AlignCenter)
        v_layout.addWidget(btn_login, alignment=Qt.AlignCenter)

        self.Stack.widget(2).setLayout(v_layout)

    def stackQRCode(self):
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
        
        self.Stack.widget(3).setLayout(v_layout_s2)

    def stackMainMenu(self):

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
                {'text': 'تحویل پسماند', 'image': 'images/green_main_menu/Package Delivery.png', 'function': self.showDelivery},
                {'text': 'کیف پول', 'image': 'images/green_main_menu/wallet.png', 'function': self.showWallet},
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

        self.Stack.widget(4).setLayout(v_layout)

    def stackDeliveryItems(self):

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

        self.grid_widget_s4 = [[QLabel() for _ in range(len(self.categories))] for _ in range(3)]
        for i in range(3):
            for j in range(len(self.categories)):
                self.grid_widget_s4[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                grid_layout_s4.addWidget(self.grid_widget_s4[i][j], i, j)

        for i in range(len(self.categories)):
            
            img = QPixmap(self.categories[i]['image'][1:])
            img = img.scaledToWidth(128)
            img = img.scaledToHeight(128)

            self.grid_widget_s4[0][i].setPixmap(img)
            self.grid_widget_s4[0][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_s4[1][i].setText(self.categories[i]['name'])
            self.grid_widget_s4[1][i].setFont(package_font)
            self.grid_widget_s4[1][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_s4[2][i].setText('0')
            self.grid_widget_s4[2][i].setFont(number_font)
            self.grid_widget_s4[2][i].setAlignment(Qt.AlignCenter)

        lb_1_s4 = QLabel('اعتبار')
        lb_1_s4.setFont(label_font)
        #h_layout1_s4.addWidget(lb_1_s4, alignment=Qt.AlignCenter)

        btn_finish = QPushButton('پایان')
        #btn_finish.setFont(label_font)
        btn_finish.clicked.connect(self.finishDelivery)
        btn_finish.setStyleSheet(btn_style)
        btn_finish.setMinimumSize(200, 130)
        btn_finish.setFont(btn_font)
        h_layout1_s4.addWidget(btn_finish, alignment=Qt.AlignCenter)

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
        btn_1_21.setStyleSheet(btn_style)
        h_layout2_s4.addWidget(btn_1_21)

        self.Stack.widget(5).setLayout(v_layout)

    def stackWallet(self):
        global user

        btn_setting = self.setting_button()

        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 100, 0)

        widget_background_s5 = QWidget()
        widget_background_s5.setFixedHeight(500)
        widget_background_s5.setLayout(h_layout)
        v_layout.addWidget(widget_background_s5)

        movie = QMovie("animation/oie_1475355NRgGVDm8.gif")

        self.lb_1_s5 = QLabel()
        h_layout.addWidget(self.lb_1_s5, alignment=Qt.AlignLeft)
        self.lb_1_s5.setMovie(movie)
        movie.start()

        self.lbl_wallet = QLabel()
        self.lbl_wallet.setFont(label_font)        
        h_layout.addWidget(self.lbl_wallet, alignment=Qt.AlignRight)
        
        lbl1 = QLabel("موجودی کیف پول")
        lbl1.setFont(label_font)
        h_layout.addWidget(lbl1, alignment=Qt.AlignRight)
        
        v_layout.addLayout(h_layout)
        v_layout.addWidget(btn_setting, alignment = Qt.AlignLeft| Qt.AlignBottom)

        self.Stack.widget(6).setLayout(v_layout)

    def stackSettingMenu(self):

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

        self.key_widget = KeyBoard(self.lb_s12)
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
        self.btn_00_s12.setStyleSheet(btn_style)
        v_layout2_s12.addWidget(self.btn_00_s12, alignment=Qt.AlignCenter)

        self.btn_01_s12 = QPushButton()
        self.btn_01_s12.setFont(menu_font)
        self.btn_01_s12.setText('خروج از برنامه')
        self.btn_01_s12.setFixedSize(200, 60)
        self.btn_01_s12.setStyleSheet(btn_style)
        self.btn_01_s12.clicked.connect(self.exit_message_box)
        v_layout2_s12.addWidget(self.btn_01_s12, alignment=Qt.AlignCenter)

        # group1.setLayout(v_layout1_s10)
        group2.setLayout(v_layout2_s12)
        
        h_layout.addLayout(v_layout1_s12)
        h_layout.addWidget(group2)
        self.Stack.widget(12).setLayout(h_layout)

    def login_button(self):
        btns_font = QFont('IRANSans', 24)

        btns_layout = QHBoxLayout()

        self.btn_login_phone_number = QPushButton()
        self.btn_login_phone_number.setFont(btns_font)
        self.btn_login_phone_number.setText('ورود با شماره همراه')
        self.btn_login_phone_number.setIcon(QIcon('images/sign/user-outline1.png'))
        self.btn_login_phone_number.setIconSize(QSize(50, 50))
        self.btn_login_phone_number.setStyleSheet(btn_style)
        self.btn_login_phone_number.setMinimumSize(290, 130)
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.btn_login_phone_number.setSizePolicy(sp_retain)
        self.btn_login_phone_number.clicked.connect(self.showLoginPhoneNumber)

        self.btn_login_qrcode = QPushButton()
        self.btn_login_qrcode.setFont(btns_font)
        self.btn_login_qrcode.setText('کد qr ورود با')
        self.btn_login_qrcode.setIcon(QIcon('images/sign/qr_code1.png'))
        self.btn_login_qrcode.setIconSize(QSize(50, 50))
        self.btn_login_qrcode.setStyleSheet(btn_style)
        self.btn_login_qrcode.setMinimumSize(290, 130)
        # sp_retain = QSizePolicy()
        # sp_retain.setRetainSizeWhenHidden(True)
        self.btn_login_qrcode.setSizePolicy(sp_retain)
        self.btn_login_qrcode.clicked.connect(self.showQR)

        btns_layout.addWidget(self.btn_login_phone_number)
        btns_layout.addWidget(self.btn_login_qrcode)
        #return self.btn_login_phone_number, self.btn_login_qrcode
        return btns_layout

    def show_login_user(self):
        self.check_login_user = Login_user('user')
        if self.check_login_user.exec_() == QDialog.Accepted:
            self.show_login_pass()

    def show_login_pass(self):
        self.check_login_pass = Login_pass('user')
        if self.check_login_pass.exec_() == QDialog.Accepted:
            self.show_menu()

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

    def message_box(self, text):

        MessageBox = QMessageBox()
        MessageBox.setStyleSheet("QLabel{min-width: 150px; min-height: 50px;} QPushButton{min-width: 120px; min-height: 40px;}")
        MessageBox.setIcon(QMessageBox.Information)
        #box.setWindowTitle('!خطا')
        MessageBox.setText(text)
        MessageBox.setFont(QFont('IRANSans', 18))
        MessageBox.setStandardButtons(QMessageBox.Ok)

        buttonOK = MessageBox.button(QMessageBox.Ok)
        buttonOK.setText('متوجه شدم')
        buttonOK.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E5631, stop:1 #2ea444);'
                               'color: #ffffff; padding: 3px; border: none; border-radius: 6px;')
        buttonOK.setFont(QFont('IRANSans', 14))
        MessageBox.exec()
        
        if MessageBox.clickedButton() == buttonOK:
            MessageBox.close()
