import time
from datetime import datetime
import json
import paho.mqtt.client as MQTTClient
from uuid import getnode

from announce_config import config


class AnnounceController:
    MQTT_BROKER = config['broker']
    MQTT_SUB = config['topic_root']
    MQTT_APP = config['topic_app']
    MQTT_SYS = config['topic_sys']

    def __init__(self):
        self.mqtt_sub_app = ''.join([self.MQTT_SUB, '/', self.MQTT_APP])
        self.mqtt_sub_sys = ''.join([self.MQTT_SUB, '/', self.MQTT_SYS])

        self.mqtt = self.init_mqtt()

    def init_mqtt(self):
        client = MQTTClient.Client(self.get_mac())
        client.on_message = self.mqtt_process_sub
        client.will_set(self.mqtt_sub_sys, 'OOPS - app controller crashed!')
        time.sleep(0.1)
        client.connect(self.MQTT_BROKER)
        client.subscribe(self.mqtt_sub_app)
        client.subscribe(self.mqtt_sub_sys)
        return client

    def mqtt_process_sub(self, client, userdata, msg):
        channel = msg.topic
        payload = msg.payload
        print("{}: {}".format(channel, payload))

        data = json.loads(payload)

        channel_group = channel.split('/')[-1]
        if channel_group == 'notify':
            mac = data['mac']
            mqtt_pub = ''.join([self.MQTT_SUB, '/', mac])
            if 'cmd' in data:
                if data['cmd'] == 'HELP':
                    self.mqtt.publish(mqtt_pub, '{"led":"ON"}')
                elif data['cmd'] == 'CANCEL':
                    self.mqtt.publish(mqtt_pub, '{"led":"OFF"}')
        elif channel_group == 'system':
            mac = data['mac']
            mqtt_pub = ''.join([self.MQTT_SUB, '/', mac])
            if 'cmd' in data:
                if data['cmd'] == 'RTC':
                    self.mqtt.publish(mqtt_pub, ''.join(['{"time":"', self.get_time(), '"}']))
        else:
            print("Unknown topic: '{}'".format(channel))

    @staticmethod
    def get_mac():
        mac_hex = hex(getnode())[2:]
        mac = ':'.join(hex(getnode())[2:][i : i + 2] for i in range(0, 11, 2)).upper()
        return mac


    @staticmethod
    def get_time():
        t = datetime.now()
        (dt, micro) = t.strftime('%Y:%m:%d:%H:%M:%S/%f').split('/')
        (ms, us) = str(int(micro) / 1000).split('.')
        return ''.join([dt, ':', ms, ':', us])

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


# TODO: Create UI for monitoring, manual updates, and button config
# TODO: add mqtt security
