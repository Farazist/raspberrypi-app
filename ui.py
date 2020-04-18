from PySide2.QtCore import QUrl
from PySide2.QtQuickWidgets import QQuickWidget
from PySide2.QtCore import Qt
import os
os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"


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
        self.setStyleSheet('background-color: #f6fdfa  ')

        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(0, 10, 0, 0)

        widget_header = QWidget()
        widget_header.setFixedHeight(100)
        widget_header.setStyleSheet('border: none')
        v_layout.addWidget(widget_header)

        h_layout_header = QHBoxLayout()
        h_layout_header.setContentsMargins(20, 0, 20, 0)
        widget_header.setLayout(h_layout_header)

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)

        self.btn_back = QPushButton()
        self.btn_back.setFont(btn_sign_font)
        self.btn_back.setText('')
        self.btn_back.setIcon(QIcon('images/sign/back.png'))
        self.btn_back.setIconSize(QSize(50, 50))
        self.btn_back.setMinimumSize(170, 70)
        self.btn_back.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fb5f15, stop:1 #f5834d);'
                                    'color: #ffffff; border: none; border-radius: 6px;')
        self.btn_back.clicked.connect(self.back_window)
        self.btn_back.setSizePolicy(sp_retain)
        h_layout_header.addWidget(self.btn_back, alignment=Qt.AlignLeft)

        logo = QPixmap('images/farazist.ico')
        self.lb_logo = QLabel()
        self.lb_logo.setPixmap(logo)
        h_layout_header.addWidget(self.lb_logo, alignment=Qt.AlignCenter)

        self.btn_tick = QPushButton()
        self.btn_tick.setFont(btn_sign_font)
        self.btn_tick.setText('تایید')
        self.btn_tick.setIcon(QIcon('images/sign/tick.png'))
        self.btn_tick.setIconSize(QSize(50, 50))
        self.btn_tick.setMinimumSize(170, 70)
        self.btn_tick.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fb5f15, stop:1 #f5834d);'
                                    'color: #ffffff; border: none; border-radius: 6px;')
        self.btn_tick.clicked.connect(self.tick_window)
        self.btn_tick.setSizePolicy(sp_retain)
        h_layout_header.addWidget(self.btn_tick, alignment=Qt.AlignRight)

        self.Stack = QStackedWidget(self)

        for i in range(14):
            self.Stack.addWidget(QWidget())

        # -------------------- stacks method --------------------
        self.stackLoading()
        self.stackAdminLogin()
        # self.stackAdminPassword()
        self.stackSettingMenu()
        self.stackStart()
        self.stackUserLogin()
        # self.stackUserPassword()
        self.stackMainMenu()
        self.stackDeliveryItems()
        self.stackWallet()
        # -------------------- end stacks method --------------------
        v_layout.addWidget(self.Stack)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showMaximized()

    def stackLoading(self):
        loader_font = QFont('IRANSans', 24)
        farazist_font = QFont('IRANSans', 48)
        btn_setting = self.setting_button()

        v_layout_loading_main = QVBoxLayout()
        v_layout_loading_main.setContentsMargins(0, 50, 0, 50)
        v_layout_loading_main.insertStretch(-1, -1)

        pixmap_loading = QPixmap('images/farazist256px.ico')
        txt_loading = 'در حال بارگزاری'
        gif_loading = QMovie("animation/Spinner.gif")

        lbl_pixmap_loading = QLabel()
        lbl_pixmap_loading.setAlignment(Qt.AlignTop)
        lbl_pixmap_loading.setPixmap(pixmap_loading)
        lbl_pixmap_loading.setMinimumHeight(500)

        lbl_gif_loading = QLabel()
        lbl_gif_loading.setMovie(gif_loading)
        gif_loading.start()

        lbl_txt_loading = QLabel()
        lbl_txt_loading.setFont(loader_font)
        lbl_txt_loading.setText(txt_loading)

        v_layout_loading_main.addWidget(lbl_pixmap_loading, alignment= Qt.AlignCenter | Qt.AlignTop)
        v_layout_loading_main.addWidget(lbl_gif_loading, alignment= Qt.AlignCenter | Qt.AlignBottom)
        v_layout_loading_main.addWidget(lbl_txt_loading, alignment= Qt.AlignCenter | Qt.AlignBottom)
        
        self.Stack.widget(0).setLayout(v_layout_loading_main)

    def stackAdminLogin(self):
        btn_setting = self.setting_button()

        qml_loading = QQuickWidget()
        qml_file = os.path.join(os.path.dirname(__file__),"admin.qml")
        qml_loading.setSource(QUrl.fromLocalFile(os.path.abspath(qml_file)))

        v_layout_AdminLogin_main = QVBoxLayout()

        v_layout_AdminLogin_main.addWidget(qml_loading, alignmet=Qt.AlignCenter)
        v_layout_AdminLogin_main.addWidget(btn_setting, alignment=Qt.AlignLeft| Qt.AlignBottom)

        self.Stack.widget(1).setLayout(v_layout_AdminLogin_main)

    """def stackAdminLogin(self):
        lb_font = QFont('IRANSans', 18)
        btn_font = QFont('IRANSans', 20)
        hoderText_font = QFont('IRANSansFaNum', 20, QFont.Bold)

        btn_setting = self.setting_button()
        
        v_layout_AdminLogin_main = QVBoxLayout()

        v_layout_AdminLogin_1 = QVBoxLayout()
        v_layout_AdminLogin_1.setContentsMargins(0, 50, 0, 20)

        v_layout_AdminLogin_2 = QVBoxLayout()

        lbl_AdminLogin_username = QLabel()
        lbl_AdminLogin_username.setAlignment(Qt.AlignTop)
        lbl_AdminLogin_username.setText('نام کاربری')
        lbl_AdminLogin_username.setFont(lb_font)
        lbl_AdminLogin_username.setFixedSize(290, 40)

        self.tb_AdminLogin_username = QLineEdit()
        self.tb_AdminLogin_username.setPlaceholderText('12********')
        self.tb_AdminLogin_username.setFont(hoderText_font)
        self.tb_AdminLogin_username.setStyleSheet(textbox_style)
        self.tb_AdminLogin_username.setFixedSize(290, 60)

        lbl_AdminLogin_password = QLabel()
        lbl_AdminLogin_password.setAlignment(Qt.AlignTop)
        lbl_AdminLogin_password.setText('رمز عبور')
        lbl_AdminLogin_password.setFont(lb_font)
        lbl_AdminLogin_password.setFixedSize(290, 40)

        self.tb_AdminLogin_password = QLineEdit()
        self.tb_AdminLogin_password.setPlaceholderText('**********')
        self.tb_AdminLogin_password.setFont(hoderText_font)
        self.tb_AdminLogin_password.setStyleSheet(textbox_style)
        self.tb_AdminLogin_password.setFixedSize(290, 60)

        btn_AdminLogin = QPushButton('ورود', self)
        btn_AdminLogin.setFont(btn_font)
        btn_AdminLogin.clicked.connect(self.showAdminLogin)
        btn_AdminLogin.setStyleSheet(btn_style)
        btn_AdminLogin.setFixedSize(290, 60)

        self.lbl_AdminLogin_Error = QLabel()
        self.lbl_AdminLogin_Error.setAlignment(Qt.AlignTop)
        self.lbl_AdminLogin_Error.setFont(lb_font)
        self.lbl_AdminLogin_Error.setFixedSize(290, 40)

        v_layout_AdminLogin_1.addWidget(lbl_AdminLogin_username, alignment=Qt.AlignCenter)
        v_layout_AdminLogin_1.addWidget(self.tb_AdminLogin_username, alignment=Qt.AlignCenter)
        v_layout_AdminLogin_1.addWidget(lbl_AdminLogin_password, alignment=Qt.AlignCenter)
        v_layout_AdminLogin_1.addWidget(self.tb_AdminLogin_password, alignment=Qt.AlignCenter)
        v_layout_AdminLogin_1.addWidget(btn_AdminLogin, alignment=Qt.AlignCenter)
        v_layout_AdminLogin_1.addWidget(self.lbl_AdminLogin_Error, alignment=Qt.AlignCenter)
        v_layout_AdminLogin_2.addWidget(btn_setting, alignment=Qt.AlignLeft| Qt.AlignBottom)
        v_layout_AdminLogin_main.addLayout(v_layout_AdminLogin_1)
        v_layout_AdminLogin_main.addLayout(v_layout_AdminLogin_2)

        self.Stack.widget(1).setLayout(v_layout_AdminLogin_main)"""

    """def stackAdminPassword(self):
        lb_font = QFont('IRANSans', 18)
        btn_font = QFont('IRANSans', 20)
        hoderText_font = QFont('IRANSansFaNum', 20, QFont.Bold)

        btn_setting = self.setting_button()

        v_layout_AdminPassword_main = QVBoxLayout()

        v_layout_AdminPassword_1 = QVBoxLayout()
        v_layout_AdminPassword_1.setContentsMargins(0, 50, 0, 250)

        v_layout_AdminPassword_2 = QHBoxLayout()

        lbl_AdminPassword = QLabel()
        lbl_AdminPassword.setAlignment(Qt.AlignTop)
        lbl_AdminPassword.setText('کلمه عبور')
        lbl_AdminPassword.setFont(lb_font)
        lbl_AdminPassword.setFixedSize(290, 40)

        self.tb_AdminPassword = QLineEdit()
        self.tb_AdminPassword.setPlaceholderText('***********')
        self.tb_AdminPassword.setEchoMode(QLineEdit.EchoMode.Password)
        self.tb_AdminPassword.setFont(hoderText_font)
        self.tb_AdminPassword.setStyleSheet(textbox_style)
        self.tb_AdminPassword.setFixedSize(290, 60)

        btn_password = QPushButton('ورود', self)
        btn_password.setFont(btn_font)
        btn_password.clicked.connect(self.showAdminPassword)
        btn_password.setStyleSheet(btn_style)
        btn_password.setFixedSize(290, 60)

        self.lbl_AdminPassword_Error = QLabel()
        self.lbl_AdminPassword_Error.setAlignment(Qt.AlignTop)
        self.lbl_AdminPassword_Error.setFont(lb_font)
        self.lbl_AdminPassword_Error.setFixedSize(290, 40)

        v_layout_AdminPassword_1.addWidget(lbl_AdminPassword, alignment=Qt.AlignCenter)
        v_layout_AdminPassword_1.addWidget(self.tb_AdminPassword, alignment=Qt.AlignCenter)
        v_layout_AdminPassword_1.addWidget(btn_password, alignment=Qt.AlignCenter)
        v_layout_AdminPassword_1.addWidget(self.lbl_AdminPassword_Error, alignment=Qt.AlignCenter)
        v_layout_AdminPassword_2.addWidget(btn_setting, alignment=Qt.AlignLeft| Qt.AlignBottom)
        v_layout_AdminPassword_main.addLayout(v_layout_AdminPassword_1)
        v_layout_AdminPassword_main.addLayout(v_layout_AdminPassword_2)

        self.Stack.widget(2).setLayout(v_layout_AdminPassword_main)"""
    
    def stackSettingMenu(self):

        h_layout_SettingMenu_main = QHBoxLayout()
        h_layout_SettingMenu_main.setSpacing(500)

        group_btns = QGroupBox()
        
        v_layout_SettingMenu_1 = QVBoxLayout()
        v_layout_SettingMenu_1.setSpacing(0)
        v_layout_SettingMenu_1.setContentsMargins(150, 0, 0, 400)
        
        lb_s12 = QLineEdit()
        lb_s12.setMaximumSize(260, 60)
        lb_s12.setStyleSheet('padding: 3px; border: 2px solid #1E5631; border-radius: 6px;')
        v_layout_SettingMenu_1.addWidget(lb_s12)

        v_layout_SettingMenu_2 = QVBoxLayout()
        v_layout_SettingMenu_2.setContentsMargins(20, 50, 20,100)

        btn_setPortNum = QPushButton()
        btn_setPortNum.setFont(menu_font)
        btn_setPortNum.setText('تنظیم شماره پورت')
        btn_setPortNum.setFixedSize(200, 60)
        btn_setPortNum.setStyleSheet(btn_style)
        v_layout_SettingMenu_2.addWidget(btn_setPortNum, alignment=Qt.AlignCenter)

        btn_setDeviceMode = QPushButton()
        btn_setDeviceMode.setFont(menu_font)
        btn_setDeviceMode.setText('تنظیم مُد دستگاه')
        btn_setDeviceMode.setFixedSize(200, 60)
        btn_setDeviceMode.setStyleSheet(btn_style)
        v_layout_SettingMenu_2.addWidget(btn_setDeviceMode, alignment=Qt.AlignCenter)

        btn_changePassword = QPushButton()
        btn_changePassword.setFont(menu_font)
        btn_changePassword.setText('تغییر رمز')
        btn_changePassword.setFixedSize(200, 60)
        btn_changePassword.setStyleSheet(btn_style)
        v_layout_SettingMenu_2.addWidget(btn_changePassword, alignment=Qt.AlignCenter)

        btn_exitApp = QPushButton()
        btn_exitApp.setFont(menu_font)
        btn_exitApp.setText('خروج از برنامه')
        btn_exitApp.setFixedSize(200, 60)
        btn_exitApp.setStyleSheet(btn_style)
        btn_exitApp.clicked.connect(self.showExitBox)
        v_layout_SettingMenu_2.addWidget(btn_exitApp, alignment=Qt.AlignCenter)

        group_btns.setLayout(v_layout_SettingMenu_2)
        
        h_layout_SettingMenu_main.addLayout(v_layout_SettingMenu_1)
        h_layout_SettingMenu_main.addWidget(group_btns)
        self.Stack.widget(3).setLayout(h_layout_SettingMenu_main)
    
    def stackStart(self):
        btn_setting = self.setting_button()
        btns_layout = self.login_button()

        v_layout_start_main = QVBoxLayout()
        h_layout_start_1 = QHBoxLayout()
        h_layout_start_2 = QHBoxLayout()

        widget_start = QWidget()
        widget_start.setStyleSheet('background-color: #fefcfc; border-radius: 30px; border :none;')
        widget_start.setLayout(h_layout_start_1)
        v_layout_start_main.addWidget(widget_start)

        gif_start = QMovie("animation/return.gif")

        lbl_gif_start = QLabel()
        h_layout_start_1.addWidget(lbl_gif_start, alignment=Qt.AlignHCenter)
        lbl_gif_start.setMovie(gif_start)
        gif_start.start()

        h_layout_start_2.addWidget(btn_setting, alignment=Qt.AlignLeft| Qt.AlignBottom)
        h_layout_start_2.addLayout(btns_layout)
        v_layout_start_main.addLayout(h_layout_start_2)

        self.Stack.widget(4).setLayout(v_layout_start_main)

    def stackUserLogin(self):
        btn_setting = self.setting_button()

        qml_loading = QQuickWidget()
        qml_file = os.path.join(os.path.dirname(__file__),"user.qml")
        qml_loading.setSource(QUrl.fromLocalFile(os.path.abspath(qml_file)))

        v_layout_UserLogin_main = QVBoxLayout()

        v_layout_UserLogin_main.addWidget(qml_loading, alignmet=Qt.AlignCenter)
        v_layout_UserLogin_main.addWidget(btn_setting, alignment=Qt.AlignLeft| Qt.AlignBottom)

        self.Stack.widget(5).setLayout(v_layout_UserLogin_main)

    """def stackUserLogin(self):
        lb_font = QFont('IRANSans', 18)
        btn_font = QFont('IRANSans', 20)
        hoderText_font = QFont('IRANSansFaNum', 20, QFont.Bold)

        btn_setting = self.setting_button()
        
        v_layout_UserLogin_main = QVBoxLayout()

        v_layout_UserLogin_1 = QVBoxLayout()
        v_layout_UserLogin_1.setContentsMargins(0, 50, 0, 20)

        v_layout_UserLogin_2 = QVBoxLayout()

        lbl_UserLogin_username = QLabel()
        lbl_UserLogin_username.setAlignment(Qt.AlignTop)
        lbl_UserLogin_username.setText('شماره موبایل')
        lbl_UserLogin_username.setFont(lb_font)
        lbl_UserLogin_username.setFixedSize(290, 40)

        self.tb_UserLogin_username = QLineEdit()
        self.tb_UserLogin_username.setPlaceholderText('09*********')
        self.tb_UserLogin_username.setFont(hoderText_font)
        self.tb_UserLogin_username.setStyleSheet(textbox_style)
        self.tb_UserLogin_username.setFixedSize(290, 60)


        lbl_UserLogin_password = QLabel()
        lbl_UserLogin_password.setAlignment(Qt.AlignTop)
        lbl_UserLogin_password.setText('رمز عبور')
        lbl_UserLogin_password.setFont(lb_font)
        lbl_UserLogin_password.setFixedSize(290, 40)

        self.tb_UserLogin_password = QLineEdit()
        self.tb_UserLogin_password.setPlaceholderText('***********')
        self.tb_UserLogin_password.setFont(hoderText_font)
        self.tb_UserLogin_password.setStyleSheet(textbox_style)
        self.tb_UserLogin_password.setFixedSize(290, 60)

        btn_UserLogin = QPushButton('ورود', self)
        btn_UserLogin.setFont(btn_font)
        btn_UserLogin.clicked.connect(self.showUserLogin)
        btn_UserLogin.setStyleSheet(btn_style)
        btn_UserLogin.setFixedSize(290, 60)

        self.lbl_UserLogin_Error = QLabel()
        self.lbl_UserLogin_Error.setAlignment(Qt.AlignTop)
        self.lbl_UserLogin_Error.setFont(lb_font)
        self.lbl_UserLogin_Error.setFixedSize(290, 40)

        v_layout_UserLogin_1.addWidget(lbl_UserLogin_username, alignment=Qt.AlignCenter)
        v_layout_UserLogin_1.addWidget(self.tb_UserLogin_username, alignment=Qt.AlignCenter)
        v_layout_UserLogin_1.addWidget(lbl_UserLogin_password, alignment=Qt.AlignCenter)
        v_layout_UserLogin_1.addWidget(self.tb_UserLogin_password, alignment=Qt.AlignCenter)
        v_layout_UserLogin_1.addWidget(btn_UserLogin, alignment=Qt.AlignCenter)
        v_layout_UserLogin_1.addWidget(self.lbl_UserLogin_Error, alignment=Qt.AlignCenter)
        v_layout_UserLogin_2.addWidget(btn_setting, alignment=Qt.AlignLeft| Qt.AlignBottom)
        v_layout_UserLogin_main.addLayout(v_layout_UserLogin_1)
        v_layout_UserLogin_main.addLayout(v_layout_UserLogin_2)

        self.Stack.widget(5).setLayout(v_layout_UserLogin_main)"""

    """def stackUserPassword(self):
        lb_font = QFont('IRANSans', 18)
        btn_font = QFont('IRANSans', 20)
        hoderText_font = QFont('IRANSansFaNum', 20, QFont.Bold)

        btn_setting = self.setting_button()

        v_layout_UserPassword_main = QVBoxLayout()

        v_layout_UserPassword_1 = QVBoxLayout()
        v_layout_UserPassword_1.setContentsMargins(0, 50, 0, 250)

        v_layout_UserPassword_2 = QHBoxLayout()

        lbl_UserPassword = QLabel()
        lbl_UserPassword.setAlignment(Qt.AlignTop)
        lbl_UserPassword.setText('کلمه عبور')
        lbl_UserPassword.setFont(lb_font)
        lbl_UserPassword.setFixedSize(290, 40)

        self.tb_UserPassword = QLineEdit()
        self.tb_UserPassword.setPlaceholderText('***********')
        self.tb_UserPassword.setEchoMode(QLineEdit.EchoMode.Password)
        self.tb_UserPassword.setFont(hoderText_font)
        self.tb_UserPassword.setStyleSheet(textbox_style)
        self.tb_UserPassword.setFixedSize(290, 60)

        btn_password = QPushButton('ورود', self)
        btn_password.setFont(btn_font)
        btn_password.clicked.connect(self.showUserPassword)
        btn_password.setStyleSheet(btn_style)
        btn_password.setFixedSize(290, 60)

        self.lbl_UserPassword_Error = QLabel()
        self.lbl_UserPassword_Error.setAlignment(Qt.AlignTop)
        self.lbl_UserPassword_Error.setFont(lb_font)
        self.lbl_UserPassword_Error.setFixedSize(290, 40)

        v_layout_UserPassword_1.addWidget(lbl_UserPassword, alignment=Qt.AlignCenter)
        v_layout_UserPassword_1.addWidget(self.tb_UserPassword, alignment=Qt.AlignCenter)
        v_layout_UserPassword_1.addWidget(btn_password, alignment=Qt.AlignCenter)
        v_layout_UserPassword_1.addWidget(self.lbl_UserPassword_Error, alignment=Qt.AlignCenter)
        v_layout_UserPassword_2.addWidget(btn_setting, alignment=Qt.AlignLeft| Qt.AlignBottom)
        v_layout_UserPassword_main.addLayout(v_layout_UserPassword_1)
        v_layout_UserPassword_main.addLayout(v_layout_UserPassword_2)

        self.Stack.widget(6).setLayout(v_layout_UserPassword_main)
    """
    def stackMainMenu(self):

        btn_setting = self.setting_button()

        v_layout_MainMenu_main = QVBoxLayout()
        h_layout_MainMenu = QHBoxLayout()

        g_layout_MainMenu = QGridLayout()
        h_layout_MainMenu.addLayout(g_layout_MainMenu)
        g_layout_MainMenu.setContentsMargins(10, 30, 10, 10)  # (left, top, right, bottom)

        btns_MainMenu = [   
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

        self.v_layouts_MainMenu = [[QVBoxLayout() for _ in range(4)] for _ in range(2)]
        
        for i in range(2):
            for j in range(4):
                g_layout_MainMenu.addLayout(self.v_layouts_MainMenu[i][j], i, j, Qt.AlignCenter)

                btn = QPushButton()
                btn.setIcon(QIcon(btns_MainMenu[i][j]['image']))
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setIconSize(QSize(110, 110))
                btn.setFixedSize(200, 200)
                btn.setStyleSheet('background-color: #ffffff; border: 3px solid #3b8686; border-radius: 30px;')

                if btns_MainMenu[i][j]['function']:
                    btn.clicked.connect(btns_MainMenu[i][j]['function'])
                self.v_layouts_MainMenu[i][j].addWidget(btn)

                lbl_MainMenu = QLabel()
                lbl_MainMenu.setText(btns_MainMenu[i][j]['text'])
                lbl_MainMenu.setFont(menu_font)
                self.v_layouts_MainMenu[i][j].addWidget(lbl_MainMenu, alignment=Qt.AlignHCenter)

        v_layout_MainMenu_main.addLayout(h_layout_MainMenu)
        v_layout_MainMenu_main.addWidget(btn_setting, alignment=Qt.AlignLeft)

        self.Stack.widget(7).setLayout(v_layout_MainMenu_main)

    def stackDeliveryItems(self):

        btn_setting = self.setting_button()

        v_layout_DeliveryItems_main = QVBoxLayout()
        v_layout_DeliveryItems_main.setSpacing(40)

        h_layout_DeliveryItems_1 = QHBoxLayout()
        h_layout_DeliveryItems_1.setContentsMargins(0, 0, 100, 0)

        g_layout_DeliveryItems = QGridLayout()
        g_layout_DeliveryItems.setContentsMargins(50, 30, 70, 20)
        g_layout_DeliveryItems.setSpacing(0)
        h_layout_DeliveryItems_1.addLayout(g_layout_DeliveryItems)

        widget_DeliveryItems = QWidget()
        widget_DeliveryItems.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=5, xOffset=0.2, yOffset=0.2))
        widget_DeliveryItems.getContentsMargins()
        widget_DeliveryItems.setStyleSheet('background-color: #ffffff; border-radius: 30px;')
        widget_DeliveryItems.setLayout(h_layout_DeliveryItems_1)
        v_layout_DeliveryItems_main.addWidget(widget_DeliveryItems)

        h_layout_DeliveryItems_2 = QHBoxLayout()
        
        v_layout_DeliveryItems_main.addLayout(h_layout_DeliveryItems_2)

        self.grid_widget_DeliveryItems = [[QLabel() for _ in range(len(self.categories))] for _ in range(3)]
        for i in range(3):
            for j in range(len(self.categories)):
                self.grid_widget_DeliveryItems[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                g_layout_DeliveryItems.addWidget(self.grid_widget_DeliveryItems[i][j], i, j)

        for i in range(len(self.categories)):
            
            img = QPixmap(self.categories[i]['image'][1:])
            img = img.scaledToWidth(128)
            img = img.scaledToHeight(128)

            self.grid_widget_DeliveryItems[0][i].setPixmap(img)
            self.grid_widget_DeliveryItems[0][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_DeliveryItems[1][i].setText(self.categories[i]['name'])
            self.grid_widget_DeliveryItems[1][i].setFont(package_font)
            self.grid_widget_DeliveryItems[1][i].setAlignment(Qt.AlignCenter)

            self.grid_widget_DeliveryItems[2][i].setText('0')
            self.grid_widget_DeliveryItems[2][i].setFont(number_font)
            self.grid_widget_DeliveryItems[2][i].setAlignment(Qt.AlignCenter)

        btn_DeliveryItems_finish = QPushButton('پایان')
        #btn_DeliveryItems_finish.setFont(label_font)
        btn_DeliveryItems_finish.clicked.connect(self.finishDelivery)
        btn_DeliveryItems_finish.setStyleSheet(btn_style)
        btn_DeliveryItems_finish.setMinimumSize(200, 130)
        btn_DeliveryItems_finish.setFont(btn_font)
        h_layout_DeliveryItems_1.addWidget(btn_DeliveryItems_finish, alignment=Qt.AlignCenter)

        h_layout_DeliveryItems_2.addWidget(btn_setting)

        self.lbl_item = QLabel()
        self.lbl_item.getContentsMargins()
        self.lbl_item.setFont(label_font)
        self.lbl_item.setAlignment(Qt.AlignCenter)
        self.lbl_item.setStyleSheet('padding: 3px; border: 2px solid #1E5631; border-radius: 6px;')
        h_layout_DeliveryItems_2.addWidget(self.lbl_item)

        btn_DeliveryItems_next = QPushButton('بعدی')
        btn_DeliveryItems_next.setMinimumSize(200, 60)
        btn_DeliveryItems_next.setFont(menu_font)
        btn_DeliveryItems_next.clicked.connect(partial(self.changePredictItemFlag, True))
        btn_DeliveryItems_next.setStyleSheet(btn_style)
        h_layout_DeliveryItems_2.addWidget(btn_DeliveryItems_next)

        self.Stack.widget(8).setLayout(v_layout_DeliveryItems_main)

    def stackWallet(self):
        global user

        btn_setting = self.setting_button()

        v_layout_wallet_main = QVBoxLayout()
        h_layout_wallet = QHBoxLayout()
        h_layout_wallet.setContentsMargins(0, 0, 100, 0)

        widget_wallet = QWidget()
        widget_wallet.setFixedHeight(500)
        widget_wallet.setLayout(h_layout_wallet)
        v_layout_wallet_main.addWidget(widget_wallet)

        gif_wallet = QMovie("animation/oie_1475355NRgGVDm8.gif")

        lbl_gif_wallet = QLabel()
        h_layout_wallet.addWidget(lbl_gif_wallet, alignment=Qt.AlignLeft)
        lbl_gif_wallet.setMovie(gif_wallet)
        gif_wallet.start()

        self.lbl_wallet = QLabel()
        self.lbl_wallet.setFont(label_font)        
        h_layout_wallet.addWidget(self.lbl_wallet, alignment=Qt.AlignRight)
        
        lbl_txt_wallet = QLabel("موجودی کیف پول")
        lbl_txt_wallet.setFont(label_font)
        h_layout_wallet.addWidget(lbl_txt_wallet, alignment=Qt.AlignRight)
        
        v_layout_wallet_main.addLayout(h_layout_wallet)
        v_layout_wallet_main.addWidget(btn_setting, alignment = Qt.AlignLeft| Qt.AlignBottom)

        self.Stack.widget(9).setLayout(v_layout_wallet_main)

    def login_button(self):
        btns_font = QFont('IRANSans', 24)

        btns_layout = QHBoxLayout()

        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)

        self.btn_login_phone_number = QPushButton()
        self.btn_login_phone_number.setFont(btns_font)
        self.btn_login_phone_number.setText('ورود با شماره همراه')
        self.btn_login_phone_number.setIcon(QIcon('images/sign/user-outline1.png'))
        self.btn_login_phone_number.setIconSize(QSize(50, 50))
        self.btn_login_phone_number.setStyleSheet(btn_style)
        self.btn_login_phone_number.setMinimumSize(290, 130)
        self.btn_login_phone_number.setSizePolicy(sp_retain)
        self.btn_login_phone_number.clicked.connect(self.showUserLogin)

        self.btn_login_qrcode = QPushButton()
        self.btn_login_qrcode.setFont(btns_font)
        self.btn_login_qrcode.setText('کد qr ورود با')
        self.btn_login_qrcode.setIcon(QIcon('images/sign/qr_code1.png'))
        self.btn_login_qrcode.setIconSize(QSize(50, 50))
        self.btn_login_qrcode.setStyleSheet(btn_style)
        self.btn_login_qrcode.setMinimumSize(290, 130)
        self.btn_login_qrcode.setSizePolicy(sp_retain)
        # self.btn_login_qrcode.clicked.connect(self.showQR)

        btns_layout.addWidget(self.btn_login_phone_number)
        # btns_layout.addWidget(self.btn_login_qrcode)

        return btns_layout

    def setting_button(self):
        self.setting = QPushButton()
        self.setting.setIcon(QIcon('images\sign\setting.png'))
        self.setting.setStyleSheet('border: none')
        self.setting.setIconSize(QSize(60, 60))
        sp_retain = QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.setting.setSizePolicy(sp_retain)
        self.setting.clicked.connect(self.showAdminLogin)
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
