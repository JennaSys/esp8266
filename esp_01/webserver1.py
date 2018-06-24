import socket

def webServer():
    s = socket.socket()
    ai = socket.getaddrinfo("192.168.1.171", 8080)
    print("Bind address info:", ai)
    addr = ai[0][-1]
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(2)
    while True:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        # print("Client address:", client_addr)
        # print("Client socket:", client_sock)

        req = client_sock.recv(1024)
        print("Request: %s" % req.decode())

        client_sock.send("HTTP/1.0 200 OK\r\n\r\n'Color: JSON'\r\n")

        client_sock.close()
        print()