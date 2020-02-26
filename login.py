from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

textbox_style = 'background-color: #ffffff; padding: 3px; border: 1px solid #3b8686; border-radius: 6px;'
button_style = 'background-color: #3b8686; color: #ffffff; padding: 3px; border: 1px solid #3b8686; border-radius: 6px;'

def message_box():
    box = QtWidgets.QMessageBox()
    box.setStyleSheet('font-size : 14px')
    box.setIcon(QtWidgets.QMessageBox.Warning)
    box.setWindowTitle('!خطا')
    box.setText('اطلاعات کاربری نادرست است')
    box.setStandardButtons(QtWidgets.QMessageBox.Ok)

    buttonOK = box.button(QtWidgets.QMessageBox.Ok)
    buttonOK.setText('متوجه شدم')
    buttonOK.setStyleSheet('background-color: #3b8686; color: #ffffff; '
                                'border-radius: 6px;')
    buttonOK.setMinimumSize(80,30)
    return box

class Login_user(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login_user, self).__init__(parent)
        self.box = message_box()
        self.font = QFont()
        # font.setFamily("Arial")
        self.font.setPointSize(10)
        self.setFont(self.font)

        self.setStyleSheet('background-color: #f6fdfa')

        self.setWindowTitle('ورود کاربر')
        self.lb_user = QtWidgets.QLabel('شماره موبایل')

        self.username = QtWidgets.QLineEdit(self)
        self.username.setPlaceholderText("09*********") 
        self.username.setStyleSheet(textbox_style)
        
        self.lb_password = QtWidgets.QLabel('رمز عبور')
        
        self.password = QtWidgets.QLineEdit(self)
        self.password.setPlaceholderText("***********") 
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setStyleSheet(textbox_style)
        
        self.buttonLogin = QtWidgets.QPushButton('ورود', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.buttonLogin.setStyleSheet(button_style)
        

        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(self.lb_user, alignment=Qt.AlignRight)
        layout.addWidget(self.username)
        layout.addWidget(self.lb_password, alignment=Qt.AlignRight)
        layout.addWidget(self.password)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        if (self.username.text() == 'farazist' and
            self.password.text() == '1234'):
            self.accept()
        else:
            self.box.exec_()
            # QtWidgets.QMessageBox.warning(self, 'خطا', 'اطلاعات کاربری نادرست است')

class Login_admin(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login_admin, self).__init__(parent)
        self.box = message_box()
        self.font = QFont()
        # font.setFamily("Arial")
        self.font.setPointSize(10)
        self.setFont(self.font)

        self.setStyleSheet('background-color: #f6fdfa')

        self.setWindowTitle('تنظیمات')
        self.lb_user = QtWidgets.QLabel('نام کاربری')

        self.username = QtWidgets.QLineEdit(self)
        
        self.username.setPlaceholderText("نام کاربری خود را وارد نمایید") 
        self.username.setStyleSheet(textbox_style)
        
        self.lb_password = QtWidgets.QLabel('رمز عبور')
        
        self.password = QtWidgets.QLineEdit(self)
        self.password.setPlaceholderText('رمز عبور خود را وارد نمایید') 
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setStyleSheet(textbox_style)
        
        self.buttonLogin = QtWidgets.QPushButton('ورود', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.buttonLogin.setStyleSheet(button_style)

        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(self.lb_user, alignment=Qt.AlignRight)
        layout.addWidget(self.username)
        layout.addWidget(self.lb_password, alignment=Qt.AlignRight)
        layout.addWidget(self.password)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        if (self.username.text() == 'farazist' and
            self.password.text() == '1234'):
            self.accept()
        else:
            self.box.exec_()