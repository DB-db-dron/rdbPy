from http.server import BaseHTTPRequestHandler, HTTPServer
from http import HTTPStatus
import json
from urllib.parse import parse_qs, urlparse, unquote_plus


class Request:
    def __init__(self, request: BaseHTTPRequestHandler):
        self._request = request
        self.headers = request.headers
        self.path = request.path
        self.method = request.command
        self.body = self._parseBody()
        self.query = parse_qs(urlparse(self.path).query)

    def log(self):
        print(
            f"""HEADERS
            --------------------
            {self.headers.as_string()}
            Resquest Path: {self.path} 
            Request Method: {self.method}
            Query: {self.query}
            Body: {self.body}
        """.replace(
                " " * 12, ""
            )
        )

    def _parseBody(self):
        if "Content-Length" not in self.headers:
            return None
        length = int(self.headers["Content-Length"])
        if not length:
            return None
        rawString = self._request.rfile.read(length).decode("utf-8")
        rawString = unquote_plus(rawString)

        if self.headers["Content-Type"] == "application/json":
            return json.loads(rawString)
        elif self.headers["Content-Type"] == "text/plain":
            return rawString
        elif self.headers["Content-Type"] == "application/x-www-form-urlencoded":
            return dict([x.split("=") for x in rawString.split("&")])
        else:
            raise TypeError(
                f"Content-Type '${self.headers['Content-Type']}' not supported"
            )

class Response:
    def __init__(self, response: BaseHTTPRequestHandler):
        self.response = response
        self.status = HTTPStatus.OK
        self.sent: bool = False

    def setStatus(self, status: int):
        self.status = status
        return self

    def isSent(self):
        if self.sent == True:
            raise RuntimeError("Cannot send response after response has been sent")

    def finish(self):
        self.sent = True
        # self.response.finish()

    def send(self, data: str):
        self.isSent()
        self.response.send_response(self.status)
        self.response.send_header("Content-type", "text/plain")
        self.response.end_headers()
        self.response.wfile.write(bytes(data, "utf8"))
        self.finish()

    def json(self, data: dict):
        self.isSent()
        self.response.send_response(self.status)
        self.response.send_header("Content-type", "application/json")
        self.response.end_headers()
        self.response.wfile.write(bytes(json.dumps(data), "utf8"))
        self.finish()

    def html(self, data: str):
        self.isSent()
        self.response.send_response(self.status)
        self.response.send_header("Content-type", "text/html")
        self.response.end_headers()
        self.response.wfile.write(data.encode())
        self.finish()

    def redirect(self, path: str):
        self.isSent()
        self.response.send_response(self.status)
        self.response.send_header("Location", path)
        self.response.end_headers()
        self.finish()

class RDB_server:
    def __init__(self):
        self.routes = {}

    def route(self, path: str, method: str = "GET"):
        print("Registered @ROUTE: ", path, method)

        def decorator_handler(handler):
            if (path, method) in self.routes:
                raise RuntimeError(f"Route {path} {method} already registered")
            elif path == "404":
                self.routes[path] = handler
            else:
                self.routes[path, method] = handler
            return None

        return decorator_handler

    def run(self, port=4000, domain="localhost"):
        server = self

        class RDB_request_handler(BaseHTTPRequestHandler):
            def pather(self):
                return urlparse(self.path).path

            def do_GET(self):
                req, res = Request(self), Response(self)
                if (self.pather(), "GET") in server.routes:
                    server.routes[self.pather(), "GET"](req, res)
                else:
                    self.handle404(req, res)

            def do_POST(self):
                req, res = Request(self), Response(self)
                if (self.pather(), "POST") in server.routes:
                    server.routes[self.pather(), "POST"](req, res)
                else:
                    self.handle404(req, res)

            def handle404(self, req, res):
                try:
                    server.routes["404"](req, res)
                except:
                    self.send_response(HTTPStatus.NOT_FOUND)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes("404 Not Found", "utf8"))

        try:
            server_address = (domain, port)
            httpd = HTTPServer(server_address, RDB_request_handler)
            print(f"\nStarting server @ http://{domain}:{httpd.server_address[1]}")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped")
        except Exception as e:
            print(e)
            print("Server stopped")
