import time
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 9000
class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        paths = {
            '/foo': {'status': 200},
            '/': {'status': 200},
            '/shi': {'status': 200}
        }
        if self.path in paths:
            self.respond(paths[self.path])
        else:
            self.respond({'status': 500})
    def handle_http(self, status_code, path):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content = '''
        <html><head><title>Hello.</title></head>
        <body><p>Hello SHI!.</p>
        <p>You accessed path: {}, now container ip : {}</p>
        </body></html>
        '''.format(path, socket.gethostbyname(socket.getfqdn()))
        return bytes(content, 'UTF-8')
    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path)
        self.wfile.write(response)
if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))        