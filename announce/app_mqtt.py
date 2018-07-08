import time
import json
import ast
import signal
import logging
import sys
import paho.mqtt.client as MQTTClient
from uuid import getnode

from assistance_config import config


logging.basicConfig(format='%(asctime)s %(levelname)s: %(funcName)s() --> %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class AssistanceApp:

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

        self.mqtt = self.init_mqtt()
        time.sleep(0.1)
        self.start()

    def init_mqtt(self):
        client = MQTTClient.Client(self.mac)
        client.on_message = self.process_message
        client.will_set(self.mqtt_pub_sys, '{{"mac":"{}","msg":"OOPS - {} crashed!"}}'.format(self.mac, self.mac))
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

    def process_message(self, client, userdata, msg):
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
                # self.gui.remove_device('DEF')
                # self.gui.update_devices(self.devices)

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


# TODO: test for mqtt id in use and modify if true