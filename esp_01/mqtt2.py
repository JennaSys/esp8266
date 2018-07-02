from umqtt.simple import MQTTClient
import time
import machine
import network
import ubinascii
import ssd1306
import json

from mqtt_config import config


class Announce:
    MQTT_BROKER = config['broker']
    MQTT_SUB = config['topic_sub_root']
    MQTT_PUB = config['topic_pub_app']
    MQTT_SYS = config['topic_pub_sys']

    PIN_LED = 5  # D1
    PIN_BTN = 4  # D2

    def __init__(self):
        self.mqtt_sub = ''.join([self.MQTT_SUB, '/', self.get_mac()])
        self.mqtt_pub = ''.join([self.MQTT_SUB, '/', self.MQTT_PUB])
        self.mqtt_pub_sys = ''.join([self.MQTT_SUB, '/', self.MQTT_SYS])
        self.mqtt = self.init_mqtt()
        self.display = self.init_oled()

        self.led = machine.Pin(self.PIN_LED, machine.Pin.OUT)
        self.led.on()

        self.btn = machine.Pin(self.PIN_BTN, machine.Pin.IN, machine.Pin.PULL_UP)  # D2
        self.btn.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.btn_pushed)
        self.prev_btn_press = time.ticks_ms()

    def init_oled(self):
        oled_width = 128
        oled_height = 64
        oled_dc = 2   # D4
        oled_rst = 5  # D1
        oled_cs = 0   # D3

        SPI_MODE = 1  # hardware SPI

        # MOSI = D7
        # CLK = D5

        spi = machine.SPI(SPI_MODE, baudrate=8000000, polarity=0, phase=0)
        oled = ssd1306.SSD1306_SPI(oled_width, oled_height, spi, machine.Pin(oled_dc), machine.Pin(oled_rst), machine.Pin(oled_cs))
        oled.contrast(128)
        oled.fill(0)
        oled.rect(0, 0, oled_width, oled_height, 1)
        oled.hline(0, 15, 128, 1)
        oled.hline(0, 16, 128, 1)
        oled.text(self.mqtt_sub.split('/')[1], 3, 4)
        oled.show()
        return oled

    def init_mqtt(self):
        client = MQTTClient(self.get_mac(), self.MQTT_BROKER)
        client.set_callback(self.mqtt_process_sub)
        client.set_last_will(self.mqtt_pub_sys, 'OOPS - ' + self.get_mac() + ' crashed!')
        time.sleep(0.1)
        client.connect()
        client.subscribe(self.mqtt_sub)
        return client

    @staticmethod
    def get_mac():
        mac = ubinascii.hexlify(network.WLAN().config('mac')).decode().upper()
        # mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode().upper()
        return mac

    def mqtt_process_sub(self, topic, msg):
        payload = msg.decode("utf-8")
        topic = topic.decode("utf-8")
        print("{}: {}".format(topic, payload))

        data = json.loads(payload)
        if 'led' in data:
            self.update_display(['led', ' ' + data['led']])
            if data['led'] == 'ON':
                self.led.off()
            elif data['led'] == 'OFF':
                self.led.on()

    def update_display(self, msg_list):
        line = 20
        self.display.fill_rect(1, 17, 126, 46, 0)
        for msg in msg_list:
            self.display.text(msg, 3, line)
            line += 9
        self.display.show()

    def btn_pushed(self, p):
        state = p.value()
        if state:  # Button UP
            self.prev_btn_press = time.ticks_ms()
        else:  # Button DOWN
            curr_time = time.ticks_ms()
            delta = time.ticks_diff(curr_time, self.prev_btn_press)
            self.prev_btn_press = time.ticks_ms()
            if delta > 20:  # Ignore any triggers < 20ms
                # self.led.value(not self.led.value())
                if self.led.value():
                    self.mqtt.publish(self.mqtt_pub, ''.join(['{"mac":"', self.get_mac(), '", "cmd":"HELP"}']))
                else:
                    self.mqtt.publish(self.mqtt_pub, ''.join(['{"mac":"', self.get_mac(), '", "cmd":"CANCEL"}']))

    def start(self):
        print('Listening for {}...'.format(self.mqtt_sub))
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

# TODO: Timer pub on announce/system for heartbeat with mac payload
# TODO: pub on announce/system with mac and receive on announce/{mac} to set RTC from controller
# TODO: press button again to deactivate LEDs and pub announce/notify with CANCEL

"""
import mqtt2
m=mqtt2.Announce()
m.start()
"""
