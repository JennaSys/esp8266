"""
Helper functions to make life in the micropython REPL a little more pleasant
"""

import os
import network
import ubinascii
import webrepl
import machine
import esp
from flashbdev import bdev

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

def ren(file, newfile):
    os.rename(file, newfile)


# Network utilities
def connect_wifi(loc=None):
    if loc is None:
        loc = input("Enter location key: ")

    STA_SSID = ssids[loc]['SSID']
    STA_PSK = ssids[loc]['PWD']

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

def get_ip():
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.active():
        return sta_if.ifconfig()[0]
    else:
        return '0.0.0.0'

def get_mac():
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode().upper()
    return mac

def webrepl_start():
    webrepl.start()

def webrepl_stop():
    webrepl.stop()

def unique_id():
    uid = ubinascii.hexlify(machine.unique_id()).decode()
    return uid


# machine utils
def set_adc_mode(adc=0):
    ADC_MODE_ADC = 0
    ADC_MODE_VCC = 255

    mode = {0: ADC_MODE_ADC, 1: ADC_MODE_VCC}
    sector_size = bdev.SEC_SIZE
    flash_size = esp.flash_size()  # device dependent
    init_sector = int(flash_size / sector_size - 4)
    data = bytearray(esp.flash_read(init_sector * sector_size, sector_size))
    if data[107] == mode[adc]:
        print("ADC mode is already set in flash!")
        return
    else:
        data[107] = mode[adc]  # re-write flash
        esp.flash_erase(init_sector)
        esp.flash_write(init_sector * sector_size, data)
        print("ADC mode has been changed in flash; restart to use it!")
        return


def get_adc():
    # requires ADC mode set to ADC
    return machine.ADC(0).read()


def get_vcc():
    # requires ADC mode set to VCC
    return machine.ADC(1).read() / 1024