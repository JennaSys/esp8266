from pyb import Switch, LED


led = LED(4)
btn = Switch()


def cb():
    state = btn.value()
    led.toggle()
    print('OFF' if led.intensity() == 0 else 'ON')


btn.callback(cb)
led.on()

