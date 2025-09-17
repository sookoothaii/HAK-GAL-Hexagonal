#!/usr/bin/env python3
"""
Prometheus Server für Port 8000
"""

import socket
import threading
import time
import requests

def server():
    s = socket.socket()
    s.bind(('127.0.0.1', 8000))
    s.listen(1)
    print('Prometheus Server läuft auf Port 8000')
    
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        
        if b'/metrics' in data:
            response = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n# HELP test_metric Test metric\ntest_metric 1.0'
            conn.send(response)
            conn.close()
            break
        else:
            conn.close()

if __name__ == "__main__":
    t = threading.Thread(target=server, daemon=True)
    t.start()
    
    time.sleep(1)
    
    try:
        response = requests.get('http://127.0.0.1:8000/metrics', timeout=2)
        print('Prometheus Status:', response.status_code)
        print('Response:', response.text)
    except Exception as e:
        print('Fehler:', e)


