import machine
import ssd1306
from time import sleep

oled_width = 128
oled_height = 64
oled_dc = 2    # D4
oled_rst = 5   # D1
oled_cs = 0    # D3

spi_mode = 1  # hardware SPI

# MOSI = D7
# CLK = D5

spi = machine.SPI(spi_mode, baudrate=8000000, polarity=0, phase=0)
oled = ssd1306.SSD1306_SPI(oled_width, oled_height, spi, machine.Pin(oled_dc), machine.Pin(oled_rst), machine.Pin(oled_cs))

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
oled.text('World', 0, 10)
oled.show()
sleep(3)

oled.fill(0)
oled.text('This is', 3, 3)
oled.text('the end', 13, 13)
oled.text('of the', 23, 23)
oled.text('world', 33, 33)
oled.text('as we', 43, 43)
oled.text('know it!', 53, 53)
oled.rect(0,0,oled_width,oled_height,1)
oled.line(80,30,120,10,1)
oled.show()



