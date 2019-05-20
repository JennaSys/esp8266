from machine import Pin, SPI
import time


MAX7219_DIGITS = 8

MAX7219_REG_NOOP = 0x0
MAX7219_REG_DIGIT0 = 0x1
MAX7219_REG_DIGIT1 = 0x2
MAX7219_REG_DIGIT2 = 0x3
MAX7219_REG_DIGIT3 = 0x4
MAX7219_REG_DIGIT4 = 0x5
MAX7219_REG_DIGIT5 = 0x6
MAX7219_REG_DIGIT6 = 0x7
MAX7219_REG_DIGIT7 = 0x8
MAX7219_REG_DECODEMODE = 0x9
MAX7219_REG_INTENSITY = 0xA
MAX7219_REG_SCANLIMIT = 0xB
MAX7219_REG_SHUTDOWN = 0xC
MAX7219_REG_DISPLAYTEST = 0xF

SPI_BUS = 1  # hardware SPI
SPI_BAUDRATE = 100000
SPI_CS = 0    # D3


class MAX7219:
    def __init__(self, digits=8, cs=SPI_CS, scan_digits=MAX7219_DIGITS):
        """
        Constructor: `digits` should be the number of individual digits being displayed. `cs` is the chip select pin.
        `scan_digits` is the number of digits each max7219 displays
        """

        self.digits = digits
        self.devices = -(-digits // MAX7219_DIGITS)  # ceiling integer division
        self.scan_digits = scan_digits
        self._buffer = [0] * digits
        self._spi = SPI(SPI_BUS, baudrate=SPI_BAUDRATE, polarity=0, phase=0)
        self._cs = Pin(cs, Pin.OUT, value=1)

        self.command(MAX7219_REG_SCANLIMIT, scan_digits-1)    # digits to display on each device  0-7
        self.command(MAX7219_REG_DECODEMODE, 0)   # use segments (not digits)
        self.command(MAX7219_REG_DISPLAYTEST, 0)  # no display test
        self.command(MAX7219_REG_SHUTDOWN, 1)     # not blanking mode
        self.brightness(7)                        # intensity: range: 0..15
        self.clear()

    def command(self, register, data):
        """
        Sets a specific register some data, replicated for all cascaded devices
        """
        self._write([register, data] * self.devices)

    def _write(self, data):
        """
        Send the bytes (which should comprise of alternating command, data values) over the SPI device.
        """
        self._cs.off()
        self._spi.write(bytes(data))
        self._cs.on()

    def clear(self):
        """
        Clears the buffer and flushes the display.
        """
        self._buffer = [0] * self.digits
        self.flush()

    def flush(self):
        """
        For each digit, cascade out the contents of the buffer cells to the SPI device.
        """
        for dev in range(self.devices):
            for pos in range(self.scan_digits):
                self._write([pos + MAX7219_REG_DIGIT0, self._buffer[pos]])

    def brightness(self, intensity):
        """
        Sets the brightness level of all cascaded devices to the same intensity level, ranging from 0..15.
        """
        self.command(MAX7219_REG_INTENSITY, intensity)

    def letter(self, position, char, dot=False, redraw=True):
        """
        Looks up the appropriate character representation for char and updates the buffer, flushes by default
        """
        value = self.CHAR_MAP.get(str(char), self.NOT_IMPLEMENTED) | (dot << 7)
        self._buffer[position] = value

        if redraw:
            self.flush()

    def write_text(self, text):
        """
        Outputs the text (as near as possible) on the specific device.
        """

        self._buffer = [0] * self.digits
        text = text[:self.digits]  # make sure we don't overrun the buffer
        for pos, char in enumerate(text):
            self.letter(pos, char, redraw=False)

        self.flush()

    NOT_IMPLEMENTED = 0x08
    CHAR_MAP = {
        ' ': 0x00,
        '-': 0x01,
        '_': 0x08,
        '0': 0x7e,
        '1': 0x30,
        '2': 0x6d,
        '3': 0x79,
        '4': 0x33,
        '5': 0x5b,
        '6': 0x5f,
        '7': 0x70,
        '8': 0x7f,
        '9': 0x7b,
        'a': 0x7d,
        'b': 0x1f,
        'c': 0x0d,
        'd': 0x3d,
        'e': 0x6f,
        'f': 0x47,
        'g': 0x7b,
        'h': 0x17,
        'i': 0x10,
        'j': 0x18,
        # 'k': cant represent
        'l': 0x06,
        # 'm': cant represent
        'n': 0x15,
        'o': 0x1d,
        'p': 0x67,
        'q': 0x73,
        'r': 0x05,
        's': 0x5b,
        't': 0x0f,
        'u': 0x1c,
        'v': 0x1c,
        # 'w': cant represent
        # 'x': cant represent
        'y': 0x3b,
        'z': 0x6d,
        'A': 0x77,
        'B': 0x7f,
        'C': 0x4e,
        'D': 0x7e,
        'E': 0x4f,
        'F': 0x47,
        'G': 0x5e,
        'H': 0x37,
        'I': 0x30,
        'J': 0x38,
        # 'K': cant represent
        'L': 0x0e,
        # 'M': cant represent
        'N': 0x76,
        'O': 0x7e,
        'P': 0x67,
        'Q': 0x73,
        'R': 0x46,
        'S': 0x5b,
        'T': 0x0f,
        'U': 0x3e,
        'V': 0x3e,
        # 'W': cant represent
        # 'X': cant represent
        'Y': 0x3b,
        'Z': 0x6d,
        ',': 0x80,
        '.': 0x80
    }
