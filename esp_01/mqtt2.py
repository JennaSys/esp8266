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
        self.led = self.init_led()

        self.rtc = machine.RTC()
        self.init_rtc()

        self.btn = self.init_btn()
        self.prev_btn_press = time.ticks_ms()

    def init_led(self):
        led = machine.Pin(self.PIN_LED, machine.Pin.OUT)
        led.on()
        return led

    def init_btn(self):
        btn = machine.Pin(self.PIN_BTN, machine.Pin.IN, machine.Pin.PULL_UP)  # D2
        btn.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.btn_pushed)
        return btn

    def init_rtc(self):
        self.mqtt.publish(self.mqtt_pub_sys, ''.join(['{"mac":"', self.get_mac(), '", "cmd":"RTC"}']))

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
        # mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode().upper()
        mac = ubinascii.hexlify(network.WLAN().config('mac')).decode().upper()
        return mac

    def mqtt_process_sub(self, topic, msg):
        channel = topic.decode("utf-8")
        payload = msg.decode("utf-8")
        print("{}: {}".format(channel, payload))

        data = json.loads(payload)
        if 'led' in data:
            self.update_display(['led', ' ' + data['led']])
            if data['led'] == 'ON':
                self.led.off()
            elif data['led'] == 'OFF':
                self.led.on()
        elif 'time' in data:
            self.update_display(['time', ' ' + data['time']])
            # temp_time = tuple(int(x) for x in data['time'].split(':'))
            temp_time = tuple(map(int, data['time'].split(':')))
            time.sleep(0.1)
            # print(temp_time)
            # self.rtc.datetime((2017, 8, 23, 1, 12, 48, 0, 0))
            self.rtc.datetime(temp_time)

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
                curr_time = ':'.join(map(str, self.rtc.datetime()))
                if self.led.value():
                    self.mqtt.publish(self.mqtt_pub, ''.join(['{"mac":"', self.get_mac(), '", "cmd":"HELP", "time":"', curr_time, '"}']))
                else:
                    self.mqtt.publish(self.mqtt_pub, ''.join(['{"mac":"', self.get_mac(), '", "cmd":"CANCEL", "time":"', curr_time, '"}']))

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

# TODO: build MQTT data with dictionaries and convert to JSON to send
# TODO: Timer pub on announce/system for heartbeat with mac payload
# TODO: stub out app MQTT controller node
# TODO: add security (user/pwd/cert?)
# TODO: deepsleep mode

"""
import mqtt2
m=mqtt2.Announce()
m.start()
"""
