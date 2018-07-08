import time
from datetime import datetime
import json
import paho.mqtt.client as MQTTClient
from uuid import getnode
import logging

from assistance_config import config

logging.basicConfig(format='%(asctime)s %(levelname)s: %(funcName)s() --> %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class AnnounceController:
    MQTT_BROKER = config['broker']
    MQTT_SUB = config['topic_root']
    MQTT_APP = config['topic_app']
    MQTT_SYS = config['topic_sys']
    DEVICE_FILE = 'devices.json'

    def __init__(self):
        self.mqtt_sub_app = ''.join([self.MQTT_SUB, '/', self.MQTT_APP])
        self.mqtt_sub_sys = ''.join([self.MQTT_SUB, '/', self.MQTT_SYS])

        self.mac = self.get_mac()

        self.mqtt = self.init_mqtt()
        self.device_map = {}
        self.load_devices()

    def init_mqtt(self):
        client = MQTTClient.Client(self.mac)
        client.on_message = self.mqtt_process_sub
        client.will_set(self.mqtt_sub_sys, '{{"mac":"{}", "msg":"OOPS - app controller crashed!"}}'.format(self.mac))
        time.sleep(0.1)
        client.connect(self.MQTT_BROKER)
        client.subscribe(self.mqtt_sub_app)
        client.subscribe(self.mqtt_sub_sys)
        return client

    def mqtt_process_sub(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        print("{}: {}".format(topic, payload))

        try:
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
            elif channel == 'system':
                mac = data['mac']
                mqtt_pub = ''.join([self.MQTT_SUB, '/', mac])
                if 'cmd' in data:
                    # Handle RTC update requests
                    if data['cmd'] == 'RTC':
                        pub_data['time'] = self.get_time()
                        self.mqtt.publish(mqtt_pub, json.dumps(pub_data))

                    # Handle device name requests
                    elif data['cmd'] == 'DEVICE_ADD':
                        self.device_map[data['device_mac']] = data['device_name']
                        self.save_devices()
                    elif data['cmd'] == 'DEVICE_DEL':
                        if data['device_mac'] in self.device_map:
                            del self.device_map[data['device_mac']]
                            self.save_devices()
                    elif data['cmd'] == 'DEVICE_GET':
                        pub_data['device_mac'] = data['device_mac']
                        if data['device_mac'] in self.device_map:
                            pub_data['device_name'] = self.device_map[data['device_mac']]
                        else:  # Return MAC for name if it doesn't exist
                            pub_data['device_name'] = data['device_mac']
                        self.mqtt.publish(mqtt_pub, json.dumps(pub_data))
                    elif data['cmd'] == 'DEVICE_GET_ALL':
                        pub_data['devices'] = str(self.device_map)[1:-1]
                        self.mqtt.publish(mqtt_pub, json.dumps(pub_data))
                        # reconstitute dictionary with   d=ast.literal_eval(''.join(['{', devices, '}']))
                    elif data['cmd'] == 'DEVICE_RESET':
                        self.device_map = {}
                        self.save_devices()
                        pub_data['devices'] = str(self.device_map)[1:-1]
                        self.mqtt.publish(mqtt_pub, json.dumps(pub_data))

                    # Handle STATUS update requests
                    if data['cmd'] == 'STATUS':
                        status = data['led']
                        print('{} status: {}'.format(mac, status))
            else:
                print("Unknown topic: '{}'".format(topic))

        except Exception as e:
            log.error("Error: {} -- Payload: [{}]".format(e, payload))

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

    def load_devices(self):
        try:
            with open(self.DEVICE_FILE) as f:
                self.device_map = json.load(f)
        except FileNotFoundError:
            self.device_map = {}

    def save_devices(self):
        data = json.dumps(self.device_map)
        with open(self.DEVICE_FILE, "w") as f:
            f.write(data)

    def start(self):
        print('Listening for {}...'.format(self.mqtt_sub_app))
        print('Listening for {}...'.format(self.mqtt_sub_sys))
        self.mqtt.loop_start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.mqtt.loop_stop()
            self.mqtt.disconnect()


if __name__ == '__main__':
    announce = AnnounceController()
    announce.start()

# TODO: add mqtt security
