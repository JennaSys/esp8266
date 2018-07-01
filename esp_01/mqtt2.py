from umqtt.simple import MQTTClient
import time
import machine
import network
import ubinascii
import ssd1306

from mqtt_config import config


class Announce:
    MQTT_BROKER = config['broker']
    MQTT_SUB = config['topic_sub']
    MQTT_PUB = config['topic_pub']

    def __init__(self):
        self.mqtt = self.init_mqtt()
        self.display = self.init_oled()

    def init_oled(self):
        oled_width = 128
        oled_height = 64
        oled_dc = 2  # D4
        oled_rst = 5  # D1
        oled_cs = 0  # D3

        spi_mode = 1  # hardware SPI

        # MOSI = D7
        # CLK = D5

        spi = machine.SPI(spi_mode, baudrate=8000000, polarity=0, phase=0)
        oled = ssd1306.SSD1306_SPI(oled_width, oled_height, spi, machine.Pin(oled_dc), machine.Pin(oled_rst), machine.Pin(oled_cs))
        oled.contrast(128)
        oled.fill(0)
        oled.rect(0, 0, oled_width, oled_height, 1)
        oled.hline(0, 15, 128, 1)
        oled.hline(0, 16, 128, 1)
        oled.text(self.MQTT_SUB, 3, 4)
        oled.show()
        return oled

    def init_mqtt(self):
        client = MQTTClient(self.get_mac(), self.MQTT_BROKER)
        client.set_callback(self.process)
        client.set_last_will('test/admin', 'OOPS - ' + self.get_mac() + ' crashed!')
        time.sleep(0.1)
        client.connect()
        client.subscribe(self.MQTT_SUB)
        return client

    def get_mac(self):
        mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode().upper()
        return mac

    def process(self, topic, msg):
        print("{}: {}".format(topic.decode("utf-8"), msg.decode("utf-8")))
        self.update_display(msg.decode("utf-8"))
        self.mqtt.publish(self.MQTT_PUB, '{"esp":"' + msg.decode("utf-8") + '"}')

    def update_display(self, msg):
        self.display.fill_rect(1, 17, 126, 46, 0)
        self.display.text(msg, 3, 19)
        self.display.show()

    def start(self):
        try:
            while True:
                self.mqtt.check_msg()
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.mqtt.disconnect()

if __name__ == '__main__':
    announce = Announce()
    announce.start()