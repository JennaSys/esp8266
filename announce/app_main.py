import time
import json
import ast
import signal
import logging
import sys
import paho.mqtt.client as MQTTClient
from uuid import getnode
from PyQt5 import QtWidgets, QtCore

from announce_config import config
from app_ui import MainWindow


logging.basicConfig(format='%(asctime)s %(levelname)s: %(funcName)s() --> %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class AnnounceApp:

    MQTT_BROKER = config['broker']
    MQTT_SUB = config['topic_root']
    MQTT_APP = config['topic_app']
    MQTT_SYS = config['topic_sys']
    DEVICE_FILE = 'devices.json'

    def __init__(self):
        self.mqtt_sub_app = ''.join([self.MQTT_SUB, '/+'])
        self.mqtt_pub_sys = ''.join([self.MQTT_SUB, '/', self.MQTT_SYS])
        self.mac = self.get_mac()

        self.devices = {}

        self.app = None
        self.gui = None

        self.mqtt = self.init_mqtt()
        time.sleep(0.1)
        self.mqtt_start()

        self.start_ui()
        self.get_devices()

    def start_ui(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)  # trap ctrl-c for exit
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.aboutToQuit.connect(self.mqtt_stop)
        self.gui = MainWindow()
        self.gui.show()

        sys.exit(self.app.exec_())

    def init_mqtt(self):
        client = MQTTClient.Client(self.get_mac())
        client.on_message = self.mqtt_process
        client.will_set(self.mqtt_pub_sys, '{{"msg":"OOPS - {} crashed!"}}'.format(self.mac))
        time.sleep(0.1)
        client.connect(self.MQTT_BROKER)
        client.subscribe(self.mqtt_sub_app)
        return client

    @staticmethod
    def get_mac():
        return "AABBCC112233"
        mac_hex = hex(getnode())[2:]
        mac = ''.join(mac_hex[i: i + 2] for i in range(0, 11, 2)).upper()
        return mac

    def get_devices(self):
        pub_data = {}
        pub_data['mac'] = self.mac
        pub_data['cmd'] = 'DEVICE_GET_ALL'
        self.mqtt.publish(self.mqtt_pub_sys, json.dumps(pub_data))

    def mqtt_process(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        print("{}: {}".format(topic, payload))

        data = json.loads(payload)
        pub_data = {}

        channel = topic.split('/')[-1]
        if channel == 'notify':
            mac = data['mac']
            mqtt_pub = ''.join([self.MQTT_SUB, '/', mac])
            if 'cmd' in data:
                if data['cmd'] == 'HELP':
                    pub_data['led'] = 'ON'
                    self.mqtt.publish(mqtt_pub, json.dumps(pub_data))
                elif data['cmd'] == 'CANCEL':
                    pub_data['led'] = 'OFF'
                    self.mqtt.publish(mqtt_pub, json.dumps(pub_data))
        elif channel == self.mac:
            if 'devices' in data:
                self.devices = ast.literal_eval(''.join(['{', data['devices'], '}']))
                log.info("Devices Received: {}".format(self.devices))
                self.gui.remove_device('DEF')

    def mqtt_start(self):
        self.mqtt.loop_start()

    def mqtt_stop(self):
        self.mqtt.loop_stop()
        self.mqtt.disconnect()
        log.info('MQTT for {} has been disconnected.'.format(self.mac))


if __name__ == '__main__':
    try:
        app = AnnounceApp()
    except KeyboardInterrupt:
        print("Ctrl-C pressed")
