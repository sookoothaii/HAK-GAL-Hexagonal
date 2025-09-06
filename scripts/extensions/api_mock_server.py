from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class Handler(BaseHTTPRequestHandler):
    def _send(self, code=200, body=None):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        if body is None:
            body = {"ok": True}
        self.wfile.write(json.dumps(body).encode('utf-8'))

    def do_GET(self):
        if self.path.startswith('/api/facts/stats'):
            return self._send(200, {"total": 3776, "top_predicates": ["HasPart", "HasPurpose"]})
        return self._send(200, {"message": "mock ok"})

    def log_message(self, fmt, *args):
        return


def main():
    httpd = HTTPServer(('127.0.0.1', 5999), Handler)
    print('Mock server on http://127.0.0.1:5999')
    httpd.serve_forever()


if __name__ == '__main__':
    main()


