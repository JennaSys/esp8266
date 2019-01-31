from machine import Pin, PWM
from time import sleep


class RGB:
    def __init__(self):
        self.pin_r = 4
        self.pin_g = 5
        self.pin_b = 2

    def setup(self):
        pwm_freq = 5000

        self.pwm_r = PWM(Pin(self.pin_r), freq=pwm_freq)
        self.pwm_g = PWM(Pin(self.pin_g), freq=pwm_freq)
        self.pwm_b = PWM(Pin(self.pin_b), freq=pwm_freq)

    def close(self):
        self.pwm_r.deinit()
        self.pwm_g.deinit()
        self.pwm_b.deinit()

    def set_leds(self, r, g, b):
        self.pwm_r.duty(int(r * 1023 / 100))
        self.pwm_g.duty(int(g * 1023 / 100))
        self.pwm_b.duty(int(b * 1023 / 100))


if __name__ == '__main__':
    rgb = RGB()
    rgb.setup()

    for x in range(0, 100):
        rgb.set_leds(x, x, x)
        sleep(0.1)

    sleep(2)
    rgb.set_leds(0, 0, 0)
    rgb.close()
