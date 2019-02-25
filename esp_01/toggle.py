from machine import Pin
from time import sleep

import mcp23017

mcp = mcp23017.MCP23017(0x20)
mcp.pullUps(mcp.PORTA, 0xFF)
mcp.pullUps(mcp.PORTB, 0xFF)
mcp.write8(mcp23017.MCP23017_IPOLA, 0xFF)
mcp.write8(mcp23017.MCP23017_IPOLB, 0xFF)

# mirror on, int pin high indicates interrupt
mcp.configSystemInterrupt(mcp.INTMIRROROFF, mcp.INTPOLACTIVEHIGH)
# for the input pin, enable interrupts and compare to previous value rather than default
mcp.configPinInterrupts(mcp.PORTA, 0xFF, 0x00, 0x00)
mcp.configPinInterrupts(mcp.PORTB, 0xFF, 0x00, 0x00)


p_intA = 12  # D6
p_intB = 14  # D5
toggle_intA = Pin(p_intA, Pin.IN)
toggle_intB = Pin(p_intB, Pin.IN)


def cb(p):
    if p == toggle_intA:
        data = mcp.readInterrupt(mcp.PORTA)
    else:
        data = mcp.readInterrupt(mcp.PORTB)
    print("Values: {}".format(data))
    # mcp.clearInterrupts()
    # sleep(0.02)  #debounce


toggle_intA.irq(trigger=Pin.IRQ_RISING, handler=cb)
toggle_intB.irq(trigger=Pin.IRQ_RISING, handler=cb)

mcp.clearInterrupts()

try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    pass
finally:
    mcp.cleanup()
