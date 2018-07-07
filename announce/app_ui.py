from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFrame, QStatusBar, QMessageBox, QInputDialog, QApplication)
from PyQt5.QtGui import (QIcon, QFont, QPixmap)
from PyQt5.QtCore import Qt
import sys
import logging


logging.basicConfig(format='%(asctime)s %(levelname)s: %(funcName)s() --> %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class MainWindow(QWidget):

    # MSG_INIT = "Retrieving device status..."
    APP_TITLE = "Assistance System"
    APP_ICON = "./resources/app.ico"

    def __init__(self):
        super().__init__()

        self.devices = {'ABC': 'Garage', 'DEF': 'Living Room', 'GHI': 'Kitchen'}
        self.device_line = {}

        self.main_layout = QVBoxLayout()
        self.initUI()


    def initUI(self):

        for device_id, device_name in self.devices.items():
            line_item = DeviceInfo(device_id, device_name)
            self.device_line[device_id] = line_item
            self.main_layout.addLayout(line_item)
            self.main_layout.addWidget(self.draw_line())

        self.main_layout.addStretch(1)

        # self.status_bar = QStatusBar()
        # self.main_layout.addWidget(self.status_bar)
        # self.status_bar.showMessage(self.MSG_INIT)

        self.setLayout(self.main_layout)

        # self.setGeometry(300, 300, 280, 170)
        # self.resize(300, 600)
        self.setMinimumWidth(300)
        self.adjustSize()
        self.setWindowTitle(self.APP_TITLE)
        self.setWindowIcon(QIcon(self.APP_ICON))
        self.show()

    def draw_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine);
        line.setFrameShadow(QFrame.Sunken);
        return line


class DeviceInfo(QHBoxLayout):

    APP_ICON = "./resources/app.ico"

    def __init__(self, device_id, device_name):
        super().__init__()

        self.device_id = device_id
        self.device_name = device_name

        self.initUI()

    def initUI(self):
        fnt_name = QFont()
        fnt_name.setPointSize(12)
        lbl_height = 24

        self.ico_off = QIcon(QPixmap('./resources/light_green.png'))
        self.ico_on = QIcon(QPixmap('./resources/light_red.png'))
        self.ico_xx = QIcon(QPixmap('./resources/light_off.png'))
        self.ico_app = QIcon(QPixmap(self.APP_ICON))

        self.btn_status = QPushButton()
        self.btn_status.setCheckable(True)
        self.btn_status.setIcon(self.ico_off)
        self.btn_status.clicked.connect(self.btn_status_click)
        self.addWidget(self.btn_status)

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
        self.btn_ren.clicked.connect(self.btn_rename_click)
        self.addWidget(self.btn_ren)

        self.btn_del = QPushButton()
        ico_del = QIcon(QPixmap('./resources/delete.png'))
        self.btn_del.setIcon(ico_del)
        self.btn_del.clicked.connect(self.btn_delete_click)
        self.addWidget(self.btn_del)

        self.btn_info = QPushButton()
        ico_info = QIcon(QPixmap('./resources/info.png'))
        self.btn_info.setIcon(ico_info)
        self.btn_info.clicked.connect(self.btn_info_click)
        self.addWidget(self.btn_info)

    def btn_status_click(self, pressed):
        if pressed:
            self.btn_status.setIcon(self.ico_on)
        else:
            self.btn_status.setIcon(self.ico_off)

    def btn_status_set(self, status):
        self.btn_status.setChecked(status)
        self.btn_status_click(status)


    def btn_rename_click(self):
        msg = QInputDialog()
        msg.setWindowTitle("Rename Device")
        msg.setWindowIcon(self.ico_app)
        msg.setLabelText("Enter the new device name for [{}]:".format(self.device_name))
        msg.setTextValue(self.device_name)
        result = msg.exec()
        if result:
            print(msg.textValue())

    def btn_delete_click(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("DELETE DEVICE")
        msg.setWindowIcon(self.ico_app)
        msg.setText("Remove [{}] from the list?".format(self.device_name))
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        result = msg.exec()
        if result == QMessageBox.Ok:
            print("Deleting {} ({})".format(self.device_name, self.device_id))

    def btn_info_click(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Device Information")
        msg.setWindowIcon(self.ico_app)
        msg.setText("Device Name: {}".format(self.device_name))
        msg.setInformativeText("Device ID: {}".format(self.device_id))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(app.exec_())


# TODO: sort device list by name before displaying
# TODO: create mqtt module and hook UI to it