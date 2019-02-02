import socket
import rgb


class WebServer:
    TITLE = "RGB LED Control"
    HTML_DOC = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jscolor/2.0.4/jscolor.min.js"></script>
</head>
<body>
<div class="container">
    <div class="row">
        <h1>RGB Color Picker</h1>
        <a type="submit" id="change_color" type="button" class="btn btn-primary">Change Color</a>
        <input class="jscolor {onFineChange:'update(this)'}" id="rgb">
    </div>
</div>
<script>
    function update(picker) {
        document.getElementById('rgb').innerHTML = Math.round(picker.rgb[0]) + ', ' +  Math.round(picker.rgb[1]) + ', ' + Math.round(picker.rgb[2]);
        document.getElementById("change_color").href="?r=" + Math.round(picker.rgb[0]*4.0117) + "&g=" +  Math.round(picker.rgb[1]*4.0117) + "&b=" + Math.round(picker.rgb[2]*4.0117);
    }
</script>
</body>
</html>
    """

    def __init__(self):
        self.led = rgb.RGB()
        self.led.setup()

    def ok(self, conn, query):
        conn.send(b"HTTP/1.1 200 OK\r\n")
        conn.send(b"Content-Type: text/html\r\n\r\n")

        if query != "":
            print(query)
            query_str = query.split('&')
            params = dict([param.split('=') for param in query_str])
            # print('r@' + params['r'])
            # print('g@' + params['g'])
            # print('b@' + params['b'])

            self.led.led_val(int(params['r']), int(params['g']), int(params['b']))

        conn.sendall(self.HTML_DOC.encode())
        conn.close()

    @staticmethod
    def err(conn, code, message):
        conn.send(("HTTP/1.1 " + code + " " + message + "\r\n\r\n").encode())
        conn.send(("<h1>" + message + "</h1>").encode())
        conn.close()

    def handle(self, conn):
        try:
            chunk = b""
            while True:
                chunk += conn.recv(1024)
                if chunk[-4:] == b'\r\n\r\n' or chunk == b'' or not chunk:
                    break
        except Exception as e:
            print("recv error...")
            repr(e)

        data = chunk.decode()
        # print(len(data))
        try:
            if len(data) == 0:
                return
            else:
                (method, url, version) = data.split('\r\n')[0].split(' ')
        except ValueError:
            print("Data Error: " + data)
            return

        if "?" in url:
            (path, query) = url.split("?", 2)
        else:
            (path, query) = (url, "")

        # print(method)
        # print(url)
        # print(version)

        if version != "HTTP/1.0" and version != "HTTP/1.1":
            self.err(conn, "505", "Version Not Supported")
        elif method == "GET":
            if path == "/":
                self.ok(conn, query)
            else:
                self.err(conn, "404", "Not Found")
        else:
            self.err(conn, "501", "Not Implemented")

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 80))
        server.listen(5)
        while True:
            try:
                conn = None
                request = server.accept()
                # print(request)
                (conn, addr) = request
                self.handle(conn)
            except Exception as e:
                print(repr(e))
                try:
                    print(conn)
                    conn.send(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
                    conn.send(b"<h1>Internal Server Error</h1>")
                    conn.close()
                except:
                    pass


if __name__ == '__main__':
    ws = WebServer()
    ws.run()
