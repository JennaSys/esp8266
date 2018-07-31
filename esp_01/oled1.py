import machine
import ssd1306
from time import sleep

oled_width = 128
oled_height = 64

spi_mode = 1  # hardware SPI
oled_dc = 2    # D4
oled_rst = 5   # D1
oled_cs = 0    # D3
# MOSI = D7
# CLK = D5

i2c_device = 0x3c  # i2c address of oled
oled_scl = 3   # RX
oled_sda = 1   # TX


def oled_i2c():
    i2c = machine.I2C(scl=machine.Pin(oled_scl), sda=machine.Pin(oled_sda))
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c, i2c_device)
    oled_test(oled)


def oled_spi():
    spi = machine.SPI(spi_mode, baudrate=8000000, polarity=0, phase=0)
    oled = ssd1306.SSD1306_SPI(oled_width, oled_height, spi, machine.Pin(oled_dc), machine.Pin(oled_rst), machine.Pin(oled_cs))
    oled_test(oled)


def oled_test(oled):
    oled.fill(1)
    oled.show()
    sleep(1)
    oled.fill(0)
    oled.show()


    oled.pixel(0, 0, 1)
    oled.show()
    sleep(3)

    for y in range(oled_height):
        for x in range(oled_width):
            oled.pixel(x, y, 1)
        oled.show()
    sleep(3)


    oled.fill(0)
    oled.text('Hello', 0, 0)
    oled.text('World', 0, 8)
    oled.show()
    sleep(3)

    oled.fill(0)
    oled.text('Destination', 3, 4)
    oled.text('Los Angeles', 3, 19)
    oled.text('Chicago', 13, 27)
    oled.text('Boston', 23, 35)
    oled.text('Houston', 33, 43)
    oled.text('New York', 43, 51)
    oled.rect(0,0,oled_width,oled_height,1)
    oled.hline(0,15,128,1)
    oled.hline(0,16,128,1)
    oled.line(80,40,120,20,1)
    oled.pixel(10, 50, 1)
    oled.pixel(12, 58, 1)
    oled.pixel(5, 46, 1)
    oled.pixel(20, 52, 1)
    oled.pixel(15, 55, 1)
    oled.fill_rect(100,35,20,10,1)
    oled.show()
    # oled.contrast(0)


def scan_i2c():
    i2c = machine.I2C(scl=machine.Pin(oled_scl), sda=machine.Pin(oled_sda))

    print('Scan i2c bus...')
    devices = i2c.scan()

    if len(devices) == 0:
      print("No i2c device !")
    else:
      print('i2c devices found:',len(devices))

      for device in devices:
        print("Decimal address: ",device," | Hexa address: ",hex(device))
