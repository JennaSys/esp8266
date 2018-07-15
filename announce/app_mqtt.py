import time
import json
import ast
import logging
import paho.mqtt.client as MQTTClient
from uuid import getnode
from datetime import datetime
from PyQt5.QtCore import QObject

from assist_config import config


logging.basicConfig(format='%(asctime)s %(levelname)s: %(funcName)s() --> %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class AssistanceApp(QObject):

    MQTT_BROKER = config['broker']
    MQTT_SUB = config['topic_root']
    MQTT_APP = config['topic_app']
    MQTT_SYS = config['topic_sys']
    DEVICE_FILE = 'devices.json'

    def __init__(self, cb_status, cb_devices):
        super().__init__()

        self.mqtt_sub_app = ''.join([self.MQTT_SUB, '/+'])
        self.mqtt_pub_app = ''.join([self.MQTT_SUB, '/', self.MQTT_APP])
        self.mqtt_pub_sys = ''.join([self.MQTT_SUB, '/', self.MQTT_SYS])

        self.mac = self.get_mac()

        self.cb_devices = cb_devices
        self.cb_status = cb_status

        self.mqtt = self.init_mqtt()
        time.sleep(0.1)
        self.start()

    def init_mqtt(self):
        client = MQTTClient.Client(self.mac)
        client.on_message = self.process_message
        client.will_set(self.mqtt_pub_sys, '{{"mac":"{}","cmd":"STATUS","sys":"OFFLINE"}}'.format(self.mac))
        time.sleep(0.1)
        client.connect(self.MQTT_BROKER)
        client.subscribe(self.mqtt_sub_app)
        return client

    @staticmethod
    def get_mac():
        mac_hex = hex(getnode())[2:]
        mac = ''.join(mac_hex[i: i + 2] for i in range(0, 11, 2)).upper()
        return mac

    @staticmethod
    def get_time():
        t = datetime.now()
        (dt, micro) = t.strftime('%Y:%m:%d:%H:%M:%S/%f').split('/')
        (ms, us) = str(int(micro) / 1000).split('.')
        return ''.join([dt, ':', ms, ':', us])

    def process_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        log.info("{}: {}".format(topic, payload))

        try:
            data = json.loads(payload)
            pub_data = {}

            channel = topic.split('/')[-1]
            if channel == self.MQTT_APP:
                mac = data['mac']
                if 'cmd' in data:
                    if data['cmd'] == 'HELP':
                        self.cb_status(mac, 'ON')
                    elif data['cmd'] == 'CANCEL':
                        self.cb_status(mac, 'OFF')
            elif channel == self.MQTT_SYS:
                mac = data['mac']
                if 'cmd' in data:
                    if data['cmd'] == 'STATUS':
                        if 'led' in data:
                            self.cb_status(mac, data['led'])
                        if 'sys' in data:
                            self.cb_status(mac, data['sys'])
            elif channel == self.mac:
                if 'devices' in data:
                    devices = ast.literal_eval(''.join(['{', data['devices'], '}']))
                    log.info("Devices Received: {}".format(devices))
                    self.cb_devices(devices)
        except Exception as e:
            log.error("Error: {} -- Payload: [{}]".format(e, payload))

    def device_set_status(self, device_mac, status):
        pub_data = {}
        pub_data['mac'] = device_mac
        pub_data['time'] = self.get_time()
        if status:
            pub_data['cmd'] = 'HELP'
        else:
            pub_data['cmd'] = 'CANCEL'
        self.mqtt.publish(self.mqtt_pub_app, json.dumps(pub_data))

    def device_get_status(self, device_mac):
        pub_data = {}
        pub_data['cmd'] = 'STATUS'
        self.mqtt.publish(''.join([self.MQTT_SUB, '/', device_mac]), json.dumps(pub_data))

    def device_add(self, device_mac, device_name):
        pub_data = {}
        pub_data['mac'] = self.mac
        pub_data['cmd'] = 'DEVICE_ADD'
        pub_data['device_mac'] = device_mac
        pub_data['device_name'] = device_name
        self.mqtt.publish(self.mqtt_pub_sys, json.dumps(pub_data))

    def device_ren(self, device_mac, device_name):
        pub_data = {}
        pub_data['mac'] = self.mac
        pub_data['cmd'] = 'DEVICE_REN'
        pub_data['device_mac'] = device_mac
        pub_data['device_name'] = device_name
        self.mqtt.publish(self.mqtt_pub_sys, json.dumps(pub_data))

    def device_del(self, device_mac):
        pub_data = {}
        pub_data['mac'] = self.mac
        pub_data['cmd'] = 'DEVICE_DEL'
        pub_data['device_mac'] = device_mac
        self.mqtt.publish(self.mqtt_pub_sys, json.dumps(pub_data))

    def device_get(self, device_mac):
        pub_data = {}
        pub_data['mac'] = self.mac
        pub_data['cmd'] = 'DEVICE_GET'
        pub_data['device_mac'] = device_mac
        self.mqtt.publish(self.mqtt_pub_sys, json.dumps(pub_data))

    def device_get_all(self):
        pub_data = {}
        pub_data['mac'] = self.mac
        pub_data['cmd'] = 'DEVICE_GET_ALL'
        self.mqtt.publish(self.mqtt_pub_sys, json.dumps(pub_data))

    def device_reset(self):
        pub_data = {}
        pub_data['mac'] = self.mac
        pub_data['cmd'] = 'DEVICE_RESET'
        self.mqtt.publish(self.mqtt_pub_sys, json.dumps(pub_data))

    def start(self):
        self.mqtt.loop_start()

    def stop(self):
        self.mqtt.loop_stop()
        self.mqtt.disconnect()
        log.info('MQTT for {} has been disconnected.'.format(self.mac))

# TODO: add mqtt security
# TODO: mqtt keepalive setting?
