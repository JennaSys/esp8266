from umqtt.simple import MQTTClient
from time import sleep
import utils

from mqtt_config import config


MQTT_BROKER = config['broker']
MQTT_SUB = config['topic_sub']
MQTT_PUB = config['topic_pub']

client = MQTTClient(utils.get_mac(), MQTT_BROKER)


def rcv(topic, msg):
    print("{}: {}".format(topic.decode("utf-8"), msg.decode("utf-8")))
    client.publish(MQTT_PUB, '{"rcv":"'+msg.decode("utf-8")+'"}')


client.set_callback(rcv)
client.set_last_will('test/admin', 'OOPS - ' + utils.get_mac() + ' crashed!')
client.connect()
client.subscribe(MQTT_SUB)


def start_loop():
    try:
        while True:
            client.check_msg()
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


def start_loop2():
    try:
        while True:
            client.wait_msg()
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


start_loop2()

