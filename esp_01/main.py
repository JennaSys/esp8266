import mqtt2
from time import sleep
import network

sta_if = network.WLAN(network.STA_IF)
while not sta_if.isconnected():
    sleep(0.5)

m = mqtt2.Announce()
m.start()
