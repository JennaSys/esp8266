import time
from machine import Pin

# LED_PIN = 1  # ESP-01
LED_PIN = 2  # ESP-12
led = Pin(LED_PIN, Pin.OUT)
while True:
    if led.value():
        led.off()
    else:
        led.on()
    time.sleep(0.5)
    