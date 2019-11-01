# Mount the SD card
import pyb
import os
sd = pyb.SDCard()
os.mount(sd, '/sd')
os.chdir('/sd')