from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame, QMessageBox, QInputDialog, QApplication, QSpacerItem)
from PyQt5.QtGui import (QIcon, QFont, QPixmap)
from PyQt5.QtCore import (Qt, QThread, pyqtSignal, pyqtSlot)
import sys
import signal
import json
from time import sleep
import logging

from app_mqtt import AssistanceApp


logging.basicConfig(format='%(asctime)s %(levelname)s: %(funcName)s() --> %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class AssistanceUI(QWidget):

    APP_ICON = "./resources/app.ico"
    APP_TITLE = "Assistance System"
    DEVICE_FILE = 'devices.json'

    def __init__(self):
        super().__init__()

        self.ico_app = QIcon(QPixmap(self.APP_ICON))

        # self.devices = {'ABC': 'Garage', 'DEF': 'Living Room', 'GHI': 'Kitchen', '5CCF7F1952F7':'ESP8862'}
        self.devices = {}
        self.device_panels = {}

        self.mqtt = self.init_mqtt()

        self.msg_thread = MessageReceived()
        self.msg_thread.signal_status.connect(self.btn_status_set)
        self.msg_thread.signal_devices.connect(self.update_devices)

        self.main_layout = QVBoxLayout()
        self.init_ui()

        sleep(2)
        self.mqtt.device_get_all()

    def init_ui(self):

        self.setLayout(self.main_layout)

        self.setMinimumWidth(350)
        self.adjustSize()
        self.setWindowTitle(self.APP_TITLE)
        self.setWindowIcon(self.ico_app)

        # self.update_devices(self.devices)

    def init_mqtt(self):
        mqtt = AssistanceApp(self.on_status, self.on_devices)
        return mqtt

    @staticmethod
    def draw_line():
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def on_status(self, device_id, status):
        """callback function for mqtt message that triggers signal to Qt thread"""
        self.msg_thread.status_received(device_id, status)

    def on_devices(self, devices):
        """callback function for mqtt message that triggers signal to Qt thread"""
        self.msg_thread.devices_received(devices)

    @pyqtSlot(str, str)
    def btn_status_set(self, device_id, status):
        if device_id in self.device_panels:
            self.device_panels[device_id].btn_status_set(status)
        else:
            self.new_device(device_id, status)

    def new_device(self, device_id, status='OFFLINE'):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Add Device")
        msg.setWindowIcon(self.ico_app)
        msg.setText("Add device [{}] to the list?".format(device_id))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        result = msg.exec()
        if result == QMessageBox.Yes:
            log.info("Adding [{}]".format(device_id))
            self.mqtt.device_add(device_id, device_id)
            self.add_device(device_id, device_id)
            self.device_panels[device_id].btn_status_set(status)

    @pyqtSlot(object)
    def update_devices(self, devices):
        # Rebuild entire UI
        self.devices = devices
        self.device_panels ={}
        log.info('Devices updated: {}'.format(self.devices))
        self.clear_layout(self.main_layout)

        for device_id, device_name in sorted(devices.items(), key=lambda x: x[1]):
            log.debug("Adding device '{}' to UI...".format(device_id))
            self.add_device(device_id, device_name)

        self.main_layout.addStretch(1)
        self.repaint()

    def add_device(self, device_id, device_name):
        line_item = DevicePanel(device_id, device_name)
        layout_size = self.main_layout.count()
        if type(self.main_layout.itemAt(layout_size - 1)) == QSpacerItem:
            self.main_layout.insertLayout(layout_size - 1, line_item)
            self.main_layout.insertWidget(layout_size, self.draw_line())
        else:
            self.main_layout.addLayout(line_item)
            self.main_layout.addWidget(self.draw_line())
        self.device_panels[device_id] = line_item
        self.mqtt.device_get_status(device_id)

    def remove_device(self, device_id):
        for i in range(0,self.main_layout.count(),2):
            layout_item = self.main_layout.itemAt(i)
            if type(layout_item) == DevicePanel:
                if layout_item.device_id == device_id:
                    self.clear_layout(layout_item)                      # Remove panel widgeta
                    self.main_layout.removeItem(layout_item)            # Delete device panel
                    self.main_layout.takeAt(i).widget().deleteLater()   # Delete dividing line
                    self.device_panels.pop(device_id, None)
                    self.devices.pop(device_id, None)
                    self.repaint()
                    break

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif type(child) == DevicePanel:
                self.clear_layout(child)
                layout.removeItem(child)

    def load_devices(self):
        try:
            with open(self.DEVICE_FILE) as f:
                self.devices = json.load(f)
        except FileNotFoundError:
            self.devices = {}

    def save_devices(self):
        data = json.dumps(self.devices)
        with open(self.DEVICE_FILE, "w") as f:
            f.write(data)


class DevicePanel(QHBoxLayout):

    APP_ICON = "./resources/app.ico"

    def __init__(self, device_id, device_name):
        super().__init__()

        self.device_id = device_id
        self.device_name = device_name

        self.init_panel()

    def init_panel(self):
        fnt_name = QFont()
        fnt_name.setPointSize(12)
        lbl_height = 24

        self.ico_off = QIcon(QPixmap('./resources/light_green.png'))
        self.ico_on = QIcon(QPixmap('./resources/light_red.png'))
        self.ico_xx = QIcon(QPixmap('./resources/light_off.png'))
        self.ico_app = QIcon(QPixmap(self.APP_ICON))

        self.btn_status = QPushButton()
        self.btn_status.setCheckable(True)
        self.btn_status.setIcon(self.ico_xx)
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
        # if pressed:
        #     self.btn_status.setIcon(self.ico_on)
        # else:
        #     self.btn_status.setIcon(self.ico_off)
        self.parent().parent().mqtt.device_set_status(self.device_id, pressed)

    def btn_status_set(self, status):
        if status =='OFFLINE':
            self.btn_status.setChecked(False)
            self.btn_status.setIcon(self.ico_xx)
        elif status == 'ON':
            self.btn_status.setChecked(True)
            self.btn_status.setIcon(self.ico_on)
        elif status == 'OFF':
            self.btn_status.setChecked(False)
            self.btn_status.setIcon(self.ico_off)

    def btn_rename_click(self):
        msg = QInputDialog()
        msg.setWindowTitle("Rename Device")
        msg.setWindowIcon(self.ico_app)
        msg.setLabelText("Enter the new device name for [{}]:".format(self.device_name))
        msg.setTextValue(self.device_name)
        result = msg.exec()
        if result:
            log.info("Renaming {} from '{}' to '{}'".format(self.device_id, self.device_name, msg.textValue()))
            self.device_name = msg.textValue()
            self.parent().parent().mqtt.device_ren(self.device_id, self.device_name)
            self.lbl_name.setText(self.device_name)

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
            log.info("Deleting {} ({})".format(self.device_name, self.device_id))
            self.parent().parent().mqtt.device_del(self.device_id)
            self.parent().parent().remove_device(self.device_id)

    def btn_info_click(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Device Information")
        msg.setWindowIcon(self.ico_app)
        msg.setText("Device Name: {}".format(self.device_name))
        msg.setInformativeText("Device ID: {}".format(self.device_id))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()


class MessageReceived(QThread):
    """Signal used to connect the mqqt message thread to the Qt GUI thread"""
    signal_status = pyqtSignal(str, str)
    signal_devices = pyqtSignal(object)

    def __init__(self):
        QThread.__init__(self)

    def status_received(self, device_id, status):
        self.signal_status.emit(device_id, status)

    def devices_received(self, devices):
        self.signal_devices.emit(devices)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        assistance = AssistanceUI()

        signal.signal(signal.SIGINT, signal.SIG_DFL)  # trap ctrl-c for exit
        app.aboutToQuit.connect(assistance.mqtt.stop)

        assistance.show()

        sys.exit(app.exec_())

    except KeyboardInterrupt:
        print("Ctrl-C pressed")
    except Exception as e:
        log.error("Error: {}".format(e))


# TODO: save device list locally for backup
# TODO: Add watchdog timer for devices - if one doesn't ping in a period of time, mark it as unavailable

