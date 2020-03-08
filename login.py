from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from keyboard import KEYBoard

textbox_style = 'background-color: #ffffff; padding: 3px; border: 1px solid #1E5631; border-radius: 6px;'
button_style = 'background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E5631, stop:1 #2ea444); color: #ffffff; padding: 3px; border: none; border-radius: 6px;'

def message_box():
    box = QtWidgets.QMessageBox()
    box.setStyleSheet('font-size : 16px')
    box.setIcon(QtWidgets.QMessageBox.Warning)
    box.setWindowTitle('!خطا')
    box.setText('اطلاعات کاربری نادرست است')
    box.setStandardButtons(QtWidgets.QMessageBox.Ok)

    buttonOK = box.button(QtWidgets.QMessageBox.Ok)
    buttonOK.setText('متوجه شدم')
    buttonOK.setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E5631, stop:1 #2ea444);'
                           'color: #ffffff; padding: 3px; border: none; border-radius: 6px;')
    buttonOK.setMinimumSize(80,30)
    return box

class Login_user(QtWidgets.QDialog):
    def __init__(self, parameter):
        self.prt = parameter
        super(Login_user, self).__init__()

        self.box = message_box()
        self.font = QFont()
        # font.setFamily("Arial")
        self.font.setPointSize(16)
        self.setFont(self.font)

        self.setStyleSheet('background-color: #f6fdfa')

        #self.btn_keyboard = QtWidgets.QPushButton()
        #self.btn_keyboard.setStyleSheet('border: none')
        #self.btn_keyboard.setIcon(QIcon('images/sign/th-small-outline.png'))
        #self.btn_keyboard.setIconSize(QSize(24, 24))

        self.username = QtWidgets.QLineEdit(self)
        self.username.setMinimumHeight(60)
        self.username.setStyleSheet(textbox_style)

        self.get_parameter()
        self.key_widget = KEYBoard(self.username)
        self.key_layout = self.key_widget.output()

        self.buttonLogin = QtWidgets.QPushButton('ورود', self)
        self.buttonLogin.setMinimumHeight(60)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.buttonLogin.setStyleSheet(button_style)

        layout = QtWidgets.QFormLayout(self)

        layout.addRow(self.lb_user)
        #layout.addRow(self.btn_keyboard, self.username)
        layout.addRow(self.username)
        layout.addRow(self.buttonLogin)
        layout.addRow(self.key_layout)
        self.setLayout(layout)

    def get_parameter(self):
        if self.prt == 'user':
            self.setWindowTitle('ورود کاربر')
            self.lb_user = QtWidgets.QLabel('شماره موبایل')
            self.username.setPlaceholderText("09*********")

        elif self.prt == 'admin':
            self.setWindowTitle('ورود مدیر')
            self.lb_user = QtWidgets.QLabel('نام کاربری')
            self.username.setPlaceholderText("12***")

    def handleLogin(self):
        if self.username.text() == '1111' and self.prt == 'user':
            self.accept()
        elif self.username.text() == '0000' and self.prt == 'admin':
            self.accept()
        else:
            self.box.exec_()
            self.username.clear()
            # QtWidgets.QMessageBox.warning(self, 'خطا', 'اطلاعات کاربری نادرست است')


class Login_pass(QtWidgets.QDialog):
    def __init__(self, parameter):
        self.prt = parameter
        super(Login_pass, self).__init__()
        self.box = message_box()
        self.font = QFont()
        # font.setFamily("Arial")
        self.font.setPointSize(16)
        self.setFont(self.font)

        self.setStyleSheet('background-color: #f6fdfa')

        self.password = QtWidgets.QLineEdit(self)

        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setMinimumHeight(60)
        self.password.setStyleSheet(textbox_style)

        self.buttonLogin = QtWidgets.QPushButton('ورود', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.buttonLogin.setStyleSheet(button_style)

        self.get_parameter()

        self.key_widget = KEYBoard(self.password)
        self.key_layout = self.key_widget.output()

        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(self.lb_password, alignment=Qt.AlignRight)
        layout.addWidget(self.password)
        layout.addWidget(self.buttonLogin)
        layout.addLayout(self.key_layout)

    def get_parameter(self):
        if self.prt == 'user':
            self.setWindowTitle('ورود کاربر')
            self.lb_password = QtWidgets.QLabel('رمز عبور')
            self.password.setPlaceholderText("***********")

        elif self.prt == 'admin':
            self.setWindowTitle('ورود مدیر')
            self.lb_password = QtWidgets.QLabel('رمز عبور')
            self.password.setPlaceholderText("***********")

    def handleLogin(self):
        if self.password.text() == '1234' and self.prt == 'user':
            self.accept()
        elif self.password.text() == '9876' and self.prt == 'admin':
            self.accept()
        else:
            self.box.exec_()
            self.password.clear()
            # QtWidgets.QMessageBox.warning(self, 'خطا', 'اطلاعات کاربری نادرست است')
