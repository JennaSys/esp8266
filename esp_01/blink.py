import utime
from machine import Pin

# LED_PIN = 1  # ESP-01
LED_PIN = 2  # ESP-12
led = Pin(LED_PIN, Pin.OUT)
enabled = False
while True:
    if enabled:
        led.off()
    else:
        led.on()
    utime.sleep_ms(1000)
    enabled = not enabled
