# Adapted for Micropython from https://github.com/GillesC/MCP23017-RPI-Lib

from machine import Pin, I2C
from time import sleep
from math import log

# Register definitions
MCP23017_IODIRA = 0x00
MCP23017_IODIRB = 0x01
MCP23017_IPOLA = 0x02
MCP23017_IPOLB = 0x03
MCP23017_GPINTENA = 0x04
MCP23017_GPINTENB = 0x05
MCP23017_DEFVALA = 0x06
MCP23017_DEFVALB = 0x07
MCP23017_INTCONA = 0x08
MCP23017_INTCONB = 0x09
MCP23017_IOCON = 0x0A  # 0x0B is the same
MCP23017_GPPUA = 0x0C
MCP23017_GPPUB = 0x0D
MCP23017_INTFA = 0x0E
MCP23017_INTFB = 0x0F
MCP23017_INTCAPA = 0x10
MCP23017_INTCAPB = 0x11
MCP23017_GPIOA = 0x12
MCP23017_GPIOB = 0x13
MCP23017_OLATA = 0x14
MCP23017_OLATB = 0x15

# I2C pin defaults
PIN_SCL = 4  # D2
PIN_SDA = 5  # D1

NUM_GPIOS = 16


class MCP23017(object):
    # constants
    OUTPUT = 0
    INPUT = 1
    LOW = 0
    HIGH = 1
    PORTA = 0
    PORTB = 1

    INTMIRRORON = 1
    INTMIRROROFF = 0
    # int pin starts high. when interrupt happens, pin goes low
    INTPOLACTIVELOW = 0
    # int pin starts low. when interrupt happens, pin goes high
    INTPOLACTIVEHIGH = 1
    INTERRUPTON = 1
    INTERRUPTOFF = 0
    INTERRUPTCOMPAREDEFAULT = 1
    INTERRUPTCOMPAREPREVIOUS = 0

    # register values for use below
    IOCONMIRROR = 6
    IOCONINTPOL = 1

    # set defaults
    def __init__(self, address, num_gpios=NUM_GPIOS, pin_scl=PIN_SCL, pin_sda=PIN_SDA):
        assert num_gpios >= 0 and num_gpios <= 16, "Number of GPIOs must be between 0 and 16"
        self.i2c = I2C(scl=Pin(pin_scl), sda=Pin(pin_sda))
        self.address = address
        self.num_gpios = num_gpios

        # set defaults
        self.write8(MCP23017_IODIRA, 0xFF)  # all inputs on port A
        self.write8(MCP23017_IODIRB, 0xFF)  # all inputs on port B
        self.write8(MCP23017_GPIOA, 0x00)  # output register to 0
        self.write8(MCP23017_GPIOB, 0x00)  # output register to 0

        # read the current direction of all pins into instance variable
        # self.direction used for assertions in a few methods methods
        self.direction = self.readU8(MCP23017_IODIRA)
        self.direction |= self.readU8(MCP23017_IODIRB) << 8

        # disable the pull-ups on all ports
        self.write8(MCP23017_GPPUA, 0x00)
        self.write8(MCP23017_GPPUB, 0x00)

        # clear the IOCON configuration register, which is chip default
        self.write8(MCP23017_IOCON, 0x00)

        ##### interrupt defaults
        # disable interrupts on all pins by default
        self.write8(MCP23017_GPINTENA, 0x00)
        self.write8(MCP23017_GPINTENB, 0x00)
        # interrupt on change register set to compare to previous value by default
        self.write8(MCP23017_INTCONA, 0x00)
        self.write8(MCP23017_INTCONB, 0x00)
        # interrupt compare value registers
        self.write8(MCP23017_DEFVALA, 0x00)
        self.write8(MCP23017_DEFVALB, 0x00)
        # clear any interrupts to start fresh
        self.readU8(MCP23017_GPIOA)
        self.readU8(MCP23017_GPIOB)

    def write8(self, register, data):
        self.i2c.writeto_mem(self.address, register, bytes([data]))

    def readU8(self, register):
        return int.from_bytes(self.i2c.readfrom_mem(self.address, register, 1), 'big')

    # change a specific bit in a byte
    def _changeBit(self, bitmap, bit, value):
        assert value == 1 or value == 0, "Value is %s must be 1 or 0" % value
        if value == 0:
            return bitmap & ~(1 << bit)
        elif value == 1:
            return bitmap | (1 << bit)

    # set an output pin to a specific value
    # pin value is relative to a bank, so must be be between 0 and 7
    def _readAndChangePin(self, register, pin, value, curValue=None):
        assert pin >= 0 and pin < 8, "Pin number %s is invalid, only 0-%s are valid" % (pin, 7)
        # if we don't know what the current register's full value is, get it first
        if not curValue:
            curValue = self.readU8(register)
        # set the single bit that corresponds to the specific pin within the full register value
        newValue = self._changeBit(curValue, pin, value)
        # write and return the full register value
        self.write8(register, newValue)
        return newValue

    # used to set the pullUp resistor setting for a pin
    # pin value is relative to the total number of gpio, so 0-15 on mcp23017
    # returns the whole register value
    def pullUp(self, pin, value):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (
            pin, self.num_gpios)
        # if the pin is < 8, use register from first bank
        if (pin < 8):
            return self._readAndChangePin(MCP23017_GPPUA, pin, value)
        else:
            # otherwise use register from second bank
            return self._readAndChangePin(MCP23017_GPPUB, pin - 8, value) << 8

    def pullUps(self, port, values):
        assert port == self.PORTA or port == self.PORTB, "Port to set pullups for must be 0 or 1!"
        # if the port is 0, use register from first bank (A)
        if port == 0:
            self.write8(MCP23017_GPPUA, values)
        else:
            # otherwise use register from second bank (B)
            self.write8(MCP23017_GPPUB, values)
        return values

    # Set pin to either input or output mode
    # pin value is relative to the total number of gpio, so 0-15 on mcp23017
    # returns the value of the combined IODIRA and IODIRB registers
    # def pinMode(self, pin, mode):
    #     assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (
    #         pin, self.num_gpios)
    #     # split the direction variable into bytes representing each gpio bank
    #     gpioa = self.direction & 0xff
    #     gpiob = (self.direction >> 8) & 0xff
    #     # if the pin is < 8, use register from first bank
    #     if (pin < 8):
    #         gpioa = self._readAndChangePin(MCP23017_IODIRA, pin, mode)
    #     else:
    #         # otherwise use register from second bank
    #         # readAndChangePin accepts pin relative to register though, so subtract
    #         gpiob = self._readAndChangePin(MCP23017_IODIRB, pin - 8, mode)
    #         # re-set the direction variable using the new pin modes
    #     self.direction = gpioa + (gpiob << 8)
    #     return self.direction

    def pinModes(self, port, modes):
        assert port == self.PORTA or port == self.PORTB, "Port to set modes from must be 0 or 1!"
        gpioa = self.direction & 0xff
        gpiob = (self.direction >> 8) & 0xff
        # if the port is 0, use register from first bank (A)
        if port == self.PORTA:
            self.write8(MCP23017_IODIRA, modes)
            gpioa = modes
        else:
            # otherwise use register from second bank(B)
            self.write8(MCP23017_IODIRB, modes)
            gpiob = modes
        # re-set the direction variable using the new pin modes
        self.direction = gpioa + (gpiob << 8)
        return self.direction

    # set an output pin to a specific value
    def output(self, pin, value):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (
            pin, self.num_gpios)
        assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin
        # if the pin is < 8, use register from first bank
        if (pin < 8):
            self.outputvalue = self._readAndChangePin(MCP23017_GPIOA, pin, value, self.readU8(MCP23017_OLATA))
        else:
            # otherwise use register from second bank
            # readAndChangePin accepts pin relative to register though, so subtract
            self.outputvalue = self._readAndChangePin(MCP23017_GPIOB, pin - 8, value, self.readU8(MCP23017_OLATB))
        return self.outputvalue

    # read the value of a pin
    # return a 1 or 0
    def input(self, pin):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (
            pin, self.num_gpios)
        assert self.direction & (1 << pin) != 0, "Pin %s not set to input" % pin
        value = 0
        # reads the whole register then compares the value of the specific pin
        if (pin < 8):
            regValue = self.readU8(MCP23017_GPIOA)
            if regValue & (1 << pin) != 0: value = 1
        else:
            regValue = self.readU8(MCP23017_GPIOB)
            if regValue & (1 << pin - 8) != 0: value = 1
        # 1 or 0
        return value
        # Return current value when output mode

    def currentVal(self, pin):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (
            pin, self.num_gpios)
        value = 0
        # reads the whole register then compares the value of the specific pin
        if (pin < 8):
            regValue = self.readU8(MCP23017_GPIOA)
            if regValue & (1 << pin) != 0: value = 1
        else:
            regValue = self.readU8(MCP23017_GPIOB)
            if regValue & (1 << pin - 8) != 0: value = 1
        # 1 or 0
        return value

        # configure system interrupt settings

    # mirror - are the int pins mirrored? 1=yes, 0=INTA associated with PortA, INTB associated with PortB
    # intpol - polarity of the int pin. 1=active-high, 0=active-low
    def configSystemInterrupt(self, mirror, intpol):
        assert mirror == 0 or mirror == 1, "Valid options for MIRROR: 0 or 1"
        assert intpol == 0 or intpol == 1, "Valid options for INTPOL: 0 or 1"
        # get current register settings
        registerValue = self.readU8(MCP23017_IOCON)
        # set mirror bit
        registerValue = self._changeBit(registerValue, self.IOCONMIRROR, mirror)
        self.mirrorEnabled = mirror
        # set the intpol bit
        registerValue = self._changeBit(registerValue, self.IOCONINTPOL, intpol)
        # set ODR pin
        self.write8(MCP23017_IOCON, registerValue)

    # configure interrupt setting for a specific pin. set on or off
    # def configPinInterrupt(self, pin, enabled, compareMode=0, defval=0):
    #     assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (
    #         pin, self.num_gpios)
    #     assert self.direction & (
    #             1 << pin) != 0, "Pin %s not set to input! Must be set to input before you can change interrupt config." % pin
    #     assert enabled == 0 or enabled == 1, "Valid options: 0 or 1"
    #     if (pin < 8):
    #         # first, interrupt on change feature
    #         self._readAndChangePin(MCP23017_GPINTENA, pin, enabled)
    #         # then, compare mode (previous value or default value?)
    #         self._readAndChangePin(MCP23017_INTCONA, pin, compareMode)
    #         # last, the default value. set it regardless if compareMode requires it, in case the requirement has changed since program start
    #         self._readAndChangePin(MCP23017_DEFVALA, pin, defval)
    #     else:
    #         self._readAndChangePin(MCP23017_GPINTENB, pin - 8, enabled)
    #         self._readAndChangePin(MCP23017_INTCONB, pin - 8, compareMode)
    #         self._readAndChangePin(MCP23017_DEFVALB, pin - 8, defval)

    def  configPinInterrupts(self, port, values, compareModes=0, defvals=0):
        assert port == self.PORTA or port == self.PORTB, "Port to set pin interrupts must be 0 or 1!"
        if port == self.PORTA:
            # assert self.direction & values != 0, "Port %s not set to matching inputs! Must be set to matching inputs before you can set interrupt config on port." % port
            # first, interrupt on change feature
            self.write8(MCP23017_GPINTENA, values)
            # then, compare mode (previous value or default value?)
            self.write8(MCP23017_INTCONA, compareModes)
            # last, the default value. set it regardless if compareMode requires it, in case the requirement has changed since program start
            self.write8(MCP23017_DEFVALA, defvals)
        else:
            self.write8(MCP23017_GPINTENB, values)
            # then, compare mode (previous value or default value?)
            self.write8(MCP23017_INTCONB, compareModes)
            # last, the default value. set it regardless if compareMode requires it, in case the requirement has changed since program start
            self.write8(MCP23017_DEFVALB, defvals)

    # private function to return pin and value from an interrupt
    def _readInterruptRegister(self, port):
        assert port == 0 or port == 1, "Port to get interrupts from must be 0 or 1!"
        value = 0
        pin = None
        gpio = None
        if port == 0:
            interruptedA = self.readU8(MCP23017_INTFA)
            if interruptedA != 0:
                pin = int(log(interruptedA, 2))
                # get the value of the pin
                valueRegister = self.readU8(MCP23017_INTCAPA)
                if valueRegister & (1 << pin) != 0: value = 1
                gpio = self.readU8(MCP23017_GPIOA)
            return pin, value, interruptedA, gpio
        if port == 1:
            interruptedB = self.readU8(MCP23017_INTFB)
            if interruptedB != 0:
                pin = int(log(interruptedB, 2))
                # get the value of the pin
                valueRegister = self.readU8(MCP23017_INTCAPB)
                if valueRegister & (1 << pin) != 0: value = 1
                # want return 0-15 pin value, so add 8
                pin = pin + 8
                gpio = self.readU8(MCP23017_GPIOB)
            return pin, value, interruptedB, gpio

    # this function should be called when INTA or INTB is triggered to indicate an interrupt occurred
    # optionally accepts the bank number that caused the interrupt (0 or 1)
    # the function determines the pin that caused the interrupt and gets its value
    # the interrupt is cleared
    # returns pin and the value
    # pin is 0 - 15, not relative to bank
    def readInterrupt(self, port=None):
        assert self.mirrorEnabled == 1 or port != None, "Mirror not enabled and port not specified - call with port (0 or 1) or set mirrored."
        # default value of pin. will be set to 1 if the pin is high
        value = 0
        # if the mirror is enabled, we don't know what port caused the interrupt, so read both
        if self.mirrorEnabled == 1:
            # read 0 first, if no pin, then read and return 1
            pin, value = self._readInterruptRegister(0)
            if pin == None:
                return self._readInterruptRegister(1)
            else:
                return pin, value
        elif port == 0:
            return self._readInterruptRegister(0)
        elif port == 1:
            return self._readInterruptRegister(1)

    # check to see if there is an interrupt pending 3 times in a row (indicating it's stuck)
    # and if needed clear the interrupt without reading values
    # return 0 if everything is ok
    # return 1 if the interrupts had to be forcefully cleared
    def clearInterrupts(self):
        if self.readU8(MCP23017_INTFA) > 0 or self.readU8(MCP23017_INTFB) > 0:
            iterations = 3
            count = 1
            # loop to check multiple times to lower chance of false positive
            while count <= iterations:
                if self.readU8(MCP23017_INTFA) == 0 and self.readU8(MCP23017_INTFB) == 0:
                    return 0
                else:
                    sleep(.5)
                    count += 1
            # if we made it to the end of the loop, reset
            if count >= iterations:
                self.readU8(MCP23017_GPIOA)
                self.readU8(MCP23017_GPIOB)
                return 1

    # cleanup function - set values everything to safe values
    # should be called when program is exiting
    def cleanup(self):
        self.write8(MCP23017_IODIRA, 0xFF)  # all inputs on port A
        self.write8(MCP23017_IODIRB, 0xFF)  # all inputs on port B
        # make sure the output registers are set to off
        self.write8(MCP23017_GPIOA, 0x00)
        self.write8(MCP23017_GPIOB, 0x00)
        # disable the pull-ups on all ports
        self.write8(MCP23017_GPPUA, 0x00)
        self.write8(MCP23017_GPPUB, 0x00)
        # clear the IOCON configuration register, which is chip default
        self.write8(MCP23017_IOCON, 0x00)

        # disable interrupts on all pins
        self.write8(MCP23017_GPINTENA, 0x00)
        self.write8(MCP23017_GPINTENB, 0x00)
        # interrupt on change register set to compare to previous value by default
        self.write8(MCP23017_INTCONA, 0x00)
        self.write8(MCP23017_INTCONB, 0x00)
        # interrupt compare value registers
        self.write8(MCP23017_DEFVALA, 0x00)
        self.write8(MCP23017_DEFVALB, 0x00)
        # clear any interrupts to start fresh
        self.readU8(MCP23017_GPIOA)
        self.readU8(MCP23017_GPIOB)
