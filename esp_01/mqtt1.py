from umqtt.simple import MQTTClient
from time import sleep
import utils

client=None

def rcv(topic,msg):
    print("{}: {}".format(topic.decode("utf-8"), msg.decode("utf-8")))
    client.publish('test/stuff','{"rcv":"'+msg.decode("utf-8")+'"}')

client = MQTTClient(utils.get_mac(), '192.168.1.166')
client.set_callback(rcv)
client.connect()
client.subscribe('test/junk')

def start_loop():
    while True:
        client.check_msg()
        sleep(1)

start_loop()