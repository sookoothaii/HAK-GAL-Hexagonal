#!/usr/bin/env python3
"""
Simple HTTP Server für Health Check
"""

import http.server
import socketserver
import threading
import time
import requests

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "timestamp": "2025-09-13T06:41:00"}')
        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    with socketserver.TCPServer(('127.0.0.1', 5000), HealthHandler) as httpd:
        print('Server gestartet auf Port 5000')
        httpd.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    print('Server Thread gestartet')
    
    time.sleep(2)
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=2)
        print('Server Status:', response.status_code, response.json())
    except Exception as e:
        print('Server Test Fehler:', e)
    
    # Server läuft weiter
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Server gestoppt')


