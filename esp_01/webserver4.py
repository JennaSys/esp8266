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

    def ok(self, sckt, query):
        sckt.write("HTTP/1.1 200 OK\r\n")
        sckt.write("Content-Type: text/html\r\n")
        sckt.write("Connection: close\r\n\r\n")
        if query != b"":
            # print(query)
            query_str = query.decode().split('&')
            params = dict([param.split('=') for param in query_str])
            # print('r@' + params['r'])
            # print('g@' + params['g'])
            # print('b@' + params['b'])

            self.led.led_val(int(params['r']), int(params['g']), int(params['b']))

        sckt.write(self.HTML_DOC)
        sckt.close()

    @staticmethod
    def err(sckt, code, message):
        sckt.write("HTTP/1.1 " + code + " " + message + "\r\n\r\n")
        sckt.write("<h1>" + message + "</h1>")

    def handle(self, sckt):
        (method, url, version) = sckt.readline().split(b" ")
        if b"?" in url:
            (path, query) = url.split(b"?", 2)
        else:
            (path, query) = (url, b"")
        while True:
            header = sckt.readline()
            if header == b"":
                return
            if header == b"\r\n":
                break

        # print(method)
        # print(url)
        # print(version)
        # print(header)

        if version != b"HTTP/1.0\r\n" and version != b"HTTP/1.1\r\n":
            self.err(sckt, "505", "Version Not Supported")
        elif method == b"GET":
            if path == b"/":
                self.ok(sckt, query)
            else:
                self.err(sckt, "404", "Not Found")
        else:
            self.err(sckt, "501", "Not Implemented")

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
