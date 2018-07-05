import mqtt2
from time import sleep
import network

# Wait for network connection...
sta_if = network.WLAN(network.STA_IF)
while not sta_if.isconnected():
    sleep(0.5)

announce = mqtt2.Announce()
announce.start()
