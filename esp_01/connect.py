import network

def start_wifi():
    ap =  network.WLAN(network.AP_IF)
    ap.active(False)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('CASA', '197F991094')
    print('network config:', wlan.ifconfig())
