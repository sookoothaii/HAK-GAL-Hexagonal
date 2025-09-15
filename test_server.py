#!/usr/bin/env python3
"""
Test Server für Port 5000
"""

import socket
import threading
import time
import requests

def server():
    s = socket.socket()
    s.bind(('127.0.0.1', 5000))
    s.listen(1)
    print('Server läuft auf Port 5000')
    
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        
        if b'/api/health' in data:
            response = b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"status": "ok"}'
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
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=2)
        print('Status:', response.status_code)
        print('Response:', response.text)
    except Exception as e:
        print('Fehler:', e)
