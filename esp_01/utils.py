"""
Helper functions to make life in the micropython REPL a little more pleasant
"""

import os
import network
import webrepl

from keys import ssids


# File utilities
def ls():
    dir_list = os.listdir()
    for f in sorted(dir_list):
        print(f)


def cat(file):
    with open(file, 'r') as f:
        print(f.read())


def rm(file):
    os.remove(file)


# Network utilities
def connect_wifi():
    STA_LOC = 'Pachea'
    STA_SSID = ssids[STA_LOC]['SSID']
    STA_PSK = ssids[STA_LOC]['PWD']

    # Turn off AP mode
    ap_if = network.WLAN(network.AP_IF)
    if ap_if.active():
        ap_if.active(False)

    # Connect to WiFi
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.active():
        sta_if.active(True)
    if not sta_if.isconnected():
        sta_if.connect(STA_SSID, STA_PSK)

    print(sta_if.ifconfig())


def show_ip():
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.active():
        print(sta_if.ifconfig()[0])
    else:
        print("Not Connected")


def webrepl_start():
    webrepl.start()


def webrepl_stop():
    webrepl.stop()
