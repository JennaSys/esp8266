from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame, QStatusBar, QApplication)
from PyQt5.QtGui import (QIcon, QFont, QPixmap)
from PyQt5.QtCore import Qt
import sys
import logging


logging.basicConfig(format='%(asctime)s %(levelname)s: %(funcName)s() --> %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class MainWindow(QWidget):

    # MSG_INIT = "Retrieving device status..."

    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.initUI()

    def initUI(self):
        devices = {'ABC':'Garage', 'DEF':'Living Room', 'GHI':'Kitchen'}

        for device_id, device_name in devices.items():
            line_item = DeviceInfo(device_id, device_name)
            self.main_layout.addLayout(line_item)
            self.main_layout.addWidget(self.draw_line())

        self.main_layout.addStretch(1)

        # self.status_bar = QStatusBar()
        # self.main_layout.addWidget(self.status_bar)
        # self.status_bar.showMessage(self.MSG_INIT)

        self.setLayout(self.main_layout)

        # self.setGeometry(300, 300, 280, 170)
        self.resize(300, 600)
        self.setWindowTitle('Assistance System')
        self.setWindowIcon(QIcon('./resources/vocademy.ico'))
        self.show()

    def draw_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine);
        line.setFrameShadow(QFrame.Sunken);
        return line


class DeviceInfo(QHBoxLayout):

    def __init__(self, device_id, device_name):
        super().__init__()

        self.device_id = device_id
        self.device_name = device_name

        self.initUI()

    def initUI(self):
        fnt_name = QFont()
        fnt_name.setPointSize(12)
        # fnt_name.setBold(True)
        lbl_height = 24

        self.ico_off = QIcon(QPixmap('./resources/light_green.png'))
        self.ico_on = QIcon(QPixmap('./resources/light_red.png'))
        self.ico_xx = QIcon(QPixmap('./resources/light_off.png'))

        self.btn = QPushButton()
        self.btn.setCheckable(True)
        self.btn.setIcon(self.ico_off)
        self.btn.clicked.connect(self.btn_click)
        self.addWidget(self.btn)

        self.lbl_name = QLabel()
        self.lbl_name.setAlignment(Qt.AlignLeft)
        self.lbl_name.setFixedHeight(lbl_height)
        self.lbl_name.setFont(fnt_name)
        self.lbl_name.setText(self.device_name)
        self.addWidget(self.lbl_name)

        self.addStretch(1)

        self.btn_ren = QPushButton()
        ico_ren = QIcon(QPixmap('./resources/edit.png'))
        self.btn_ren.setIcon(ico_ren)
        self.addWidget(self.btn_ren)

        self.btn_del = QPushButton()
        ico_del = QIcon(QPixmap('./resources/delete.png'))
        self.btn_del.setIcon(ico_del)
        self.addWidget(self.btn_del)

    def btn_click(self, pressed):
        if pressed:
            self.btn.setIcon(self.ico_on)
        else:
            self.btn.setIcon(self.ico_off)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(app.exec_())
