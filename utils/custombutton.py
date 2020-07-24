from PySide2.QtWidgets import QPushButton, QApplication, QWidget, QVBoxLayout
from PySide2.QtCore import Slot, QTimer, QSize
from PySide2.QtGui import QIcon, QMovie


class CustomButton(QPushButton):
   
    def __init__(self):
        super(CustomButton, self).__init__()
        self.setMinimumSize(290, 70)
        self.setMaximumSize(290, 70)
        self.setStyleSheet('QPushButton{background-color: #28a745; color: rgb(255, 255, 255); font: 24pt "IRANSans"; '
                           'padding: 3px; border: none; border-radius: 6px; outline-style: none;}'
                           'QPushButton:pressed {background-color: #145222;border-style: inset;}')
    @Slot ()
    def start(self):
        if hasattr(self, "gifBtn"):
            self.setText(None)
            self.gifBtn.start()

    @Slot ()
    def stop(self):
        if hasattr(self, "gifBtn"):
            self.setText('ورود')
            self.gifBtn.stop()
            self.setIcon(QIcon())

    def setGif(self, filename):
        if not hasattr(self, "gifBtn"):
            self.gifBtn = QMovie(self)
            self.gifBtn.setFileName(filename)
            self.gifBtn.frameChanged.connect(self.on_frameChanged)
            if self.gifBtn.loopCount() != -1:
                self.gifBtn.finished.connect(self.start)
        self.stop()

    @Slot (int)
    def on_frameChanged(self, frameNumber):
        self.setIcon(QIcon(self.gifBtn.currentPixmap()))
        self.setIconSize(QSize(70, 70))

#if __name__ == '__main__':
#    import sys
#    import random
#    app = QApplication(sys.argv)
#    w = QWidget()
#    lay = QVBoxLayout(w)
#    for i in range(5):
#        button = CustomButton()
#        button.setGif("animations/Rolling-white.gif")
#        button.clicked.connect(button.start)
#        #QTimer.singleShot(random.randint(3000, 6000), button.start)
#        #QTimer.singleShot(random.randint(8000, 12000), button.stop)
#        lay.addWidget(button)
#    w.show()
#    sys.exit(app.exec_())