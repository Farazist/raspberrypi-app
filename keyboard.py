from PyQt5.QtWidgets import QPushButton, QGridLayout, QApplication, QSizePolicy
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize
from functools import partial
import sys

result = 0
flag = True
# ---------- keyboard ----------
class KEYBoard:
    def __init__(self, textbox):
        self.box = textbox

        self.g_layout = QGridLayout()
        self.g_layout.setSpacing(10)
        
        # --- create numbers
        keyboard = [[0 for i in range(3)] for j in range(4)]
        font = QFont('Times', 18, QFont.Bold)

        for i in range(4):
            for j in range(3):
                btn = QPushButton()
                btn.getContentsMargins()
                btn.setFont(font)
                keyboard[i][j] = btn

                btn_num = [[1, 2, 3],
                          [4, 5, 6], 
                          [7, 8, 9], 
                          ['', 0, '']]
                keyboard[i][j].setText(str(btn_num[i][j]))
                keyboard[i][j].setFixedSize(60, 60)
                keyboard[i][j].setStyleSheet('background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #626060, stop:1 #7e7c7c);'
                                             'color: #ffffff; border: none; border-radius: 6px;')
                # keyboard[i][j].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.g_layout.addWidget(keyboard[i][j], i, j, alignment=Qt.AlignHCenter)


        keyboard[0][0].clicked.connect(partial(self.number_show, 1))
        keyboard[0][1].clicked.connect(partial(self.number_show, 2))
        keyboard[0][2].clicked.connect(partial(self.number_show, 3))

        keyboard[1][0].clicked.connect(partial(self.number_show, 4))
        keyboard[1][1].clicked.connect(partial(self.number_show, 5))
        keyboard[1][2].clicked.connect(partial(self.number_show, 6))

        keyboard[2][0].clicked.connect(partial(self.number_show, 7))
        keyboard[2][1].clicked.connect(partial(self.number_show, 8))
        keyboard[2][2].clicked.connect(partial(self.number_show, 9))

        keyboard[3][1].clicked.connect(partial(self.number_show, 0))
        keyboard[3][2].clicked.connect(self.delete_number)

        keyboard[3][2].setIcon(QIcon('images/sign/backspace.png'))
        keyboard[3][2].setIconSize(QSize(32, 32))
        
        keyboard[3][0].hide()
        # layout.addLayout(g_layout)

    def number_show(self, x):
        # if self.box.text() == str(result):
        #     self.box.setText(str(x))
        # else:
            self.box.setText(self.box.text() + str(x))
            

    def delete_number(self):
        self.box.setText(self.box.text()[0:-1])

    def output(self):
        return self.g_layout


