import time
from pyb import Pin

led = Pin('LED_YELLOW', Pin.OUT_PP)
try:
    while True:
        if led.value():
            led.off()
        else:
            led.on()
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
