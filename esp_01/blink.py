import utime
from machine import Pin


led = Pin(2, Pin.OUT)
enabled = False
while True:
    if enabled:
        led.off()
    else:
        led.on()
    utime.sleep_ms(1000)
    enabled = not enabled
