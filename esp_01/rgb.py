from machine import Pin, PWM
from time import sleep


class RGB:
    def __init__(self):
        # Set GPIO pins
        self.pin_r = 12
        self.pin_g = 5
        self.pin_b = 4

    def setup(self):
        pwm_freq = 5000

        self.pwm_r = PWM(Pin(self.pin_r), freq=pwm_freq)
        self.pwm_g = PWM(Pin(self.pin_g), freq=pwm_freq)
        self.pwm_b = PWM(Pin(self.pin_b), freq=pwm_freq)

    def close(self):
        self.pwm_r.deinit()
        self.pwm_g.deinit()
        self.pwm_b.deinit()

    def led_pct(self, r, g, b):
        # Input RGB values are by percentage
        self.pwm_r.duty(int(r * 1023 / 100))
        self.pwm_g.duty(int(g * 1023 / 100))
        self.pwm_b.duty(int(b * 1023 / 100))

    def led_val(self, r, g, b):
        # Input RGB values are by 10-bit value
        self.pwm_r.duty(r)
        self.pwm_g.duty(g)
        self.pwm_b.duty(b)


if __name__ == '__main__':
    led = RGB()
    led.setup()

    for x in range(0, 100):
        led.led_pct(x, x, x)
        sleep(0.1)

    sleep(2)
    led.led_pct(0, 0, 0)
    led.close()
