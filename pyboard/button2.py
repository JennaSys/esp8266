from pyb import Switch, Pin


led = Pin('LED_BLUE', Pin.OUT_PP)
btn = Switch()


def cb():
    state = btn.value()
    led.value(not led.value())
    print('ON' if led.value() else 'OFF')


btn.callback(cb)
led.on()


