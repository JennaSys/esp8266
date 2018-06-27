import network
import socket
from machine import Pin

from keys import ssids


class WebServer:
    TITLE = "LED Control"
    GPIO_NUM = 2

    def __init__(self):
        self.pin = Pin(self.GPIO_NUM)
        self.pin.init(Pin.OUT)
        self.led_off()

    def led_off(self):
        self.pin.on()

    def led_on(self):
        self.pin.off()

    def ok(self, socket, query):
        socket.write("HTTP/1.1 OK\r\n\r\n")
        socket.write("<!DOCTYPE html><title>"+self.TITLE+"</title><body>")
        socket.write(self.TITLE+" status: ")
        if not self.pin.value():
            socket.write("<span style='color:green'>ON</span>")
        else:
            socket.write("<span style='color:red'>OFF</span>")

        socket.write("<br>")

        if not self.pin.value():
            socket.write("<form method='POST' action='/off?"+query.decode()+"'>"+
                         "<input type='submit' value='turn OFF'>"+
                         "</form>")
        else:
            socket.write("<form method='POST' action='/on?"+query.decode()+"'>"+
                         "<input type='submit' value='turn ON'>"+
                         "</form>")

    def err(self, socket, code, message):
        socket.write("HTTP/1.1 "+code+" "+message+"\r\n\r\n")
        socket.write("<h1>"+message+"</h1>")

    def handle(self, socket):
        (method, url, version) = socket.readline().split(b" ")
        if b"?" in url:
            (path, query) = url.split(b"?", 2)
        else:
            (path, query) = (url, b"")
        while True:
            header = socket.readline()
            if header == b"":
                return
            if header == b"\r\n":
                break

        if version != b"HTTP/1.0\r\n" and version != b"HTTP/1.1\r\n":
            self.err(socket, "505", "Version Not Supported")
        elif method == b"GET":
            if path == b"/":
                self.ok(socket, query)
            else:
                self.err(socket, "404", "Not Found")
        elif method == b"POST":
            if path == b"/on":
                self.led_on()
                self.ok(socket, query)
            elif path == b"/off":
                self.led_off()
                self.ok(socket, query)
            else:
                self.err(socket, "404", "Not Found")
        else:
            self.err(socket, "501", "Not Implemented")

    def run(self):
        server = socket.socket()
        server.bind(('0.0.0.0', 80))
        server.listen(1)
        while True:
            try:
                (sckt, sockaddr) = server.accept()
                self.handle(sckt)
            except:
                sckt.write("HTTP/1.1 500 Internal Server Error\r\n\r\n")
                sckt.write("<h1>Internal Server Error</h1>")
                sckt.close()


if __name__ == '__main__':
    ws = WebServer()
    ws.run()
