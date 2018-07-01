from machine import Pin
from time import sleep
import time


led = Pin(5, Pin.OUT)              # D1
btn = Pin(4, Pin.IN, Pin.PULL_UP)  # D2

prev_btn_press = time.ticks_ms()

def cb(p):
    global prev_btn_press

    state = p.value()
    if state:
        prev_btn_press = time.ticks_ms()
    else:
        curr_time = time.ticks_ms()
        delta = time.ticks_diff(curr_time, prev_btn_press)
        prev_btn_press = time.ticks_ms()
        if delta > 20:  # Ignore any triggers < 20ms
            led.value(not led.value())

def cb2(p):
    if p.value():
        led.on()
    else:
        led.off()


def cb_test(p):
    # start = time.ticks_ms()  # get millisecond counter
    # delta = time.ticks_diff(time.ticks_ms(), start)  # compute time difference

    global prev_btn_press
    state = p.value()
    if state:
        prev_btn_press = time.ticks_ms()
    else:
        currentime = time.ticks_ms()

        delta = time.ticks_diff(currentime, prev_btn_press)
        # print('{} from {} to {}'.format(delta, currentime, previousButtonPress))
        prev_btn_press = time.ticks_ms()
        if delta > 20:
            print('Button pressed: {}'.format(delta))
        elif delta <= 20:
            pass
            # print('Delta was too small: {}'.format(delta))
        else:
            print('error: {}'.format(delta))


btn.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=cb)
# btn.irq(trigger=Pin.IRQ_FALLING, handler=cb)
led.on()

try:
    while True:
        sleep(0.5)
except KeyboardInterrupt:
    pass