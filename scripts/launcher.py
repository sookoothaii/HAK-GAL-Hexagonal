#!/usr/bin/env python3
"""
HAK_GAL Service Launcher - Startet alle Services in Subprozessen
Alternativ zum PowerShell/Batch Script
"""
import subprocess
import time
import os
import sys
from pathlib import Path
import psutil
import socket

# Services konfigurieren
SERVICES = [
    {"name": "Dashboard", "port": 5000, "script": "hakgal_dashboard_ultra.py", "color": "92"},
    {"name": "Prometheus", "port": 8000, "script": "hakgal_prometheus_optimized.py", "color": "93"},
    {"name": "API", "port": 5002, "script": "hexagonal_api_enhanced_clean.py", "color": "94"},
    {"name": "Proxy", "port": 8088, "script": "hakgal_proxy.py", "color": "95"},
    {"name": "Frontend", "port": 5173, "script": "frontend_server.py", "color": "96"},
]

BASE_DIR = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL")
VENV_PYTHON = BASE_DIR / ".venv_hexa/Scripts/python.exe"

def print_colored(text, color="37"):
    """Farbige Ausgabe"""
    print(f"\033[{color}m{text}\033[0m")

def check_port(port):
    """Prüft ob ein Port frei ist"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def start_service(service):
    """Startet einen Service in neuem Fenster"""
    script_path = BASE_DIR / service["script"]
    
    # Windows-spezifischer Start-Command
    cmd = [
        "start",
        f"{service['name']} :{service['port']}",
        "cmd", "/k",
        str(VENV_PYTHON),
        str(script_path)
    ]
    
    subprocess.Popen(cmd, shell=True, cwd=str(BASE_DIR))
    print_colored(f"✅ {service['name']} gestartet auf Port {service['port']}", service["color"])

def main():
    print_colored("🚀 HAK_GAL SYSTEM LAUNCHER", "96")
    print_colored("=" * 50, "96")
    
    os.chdir(BASE_DIR)
    
    # Port-Status prüfen
    print_colored("\n📋 Prüfe Port-Status...", "93")
    blocked_ports = []
    
    for service in SERVICES:
        if check_port(service["port"]):
            print_colored(f"  ⚠️ Port {service['port']} bereits belegt ({service['name']})", "93")
            blocked_ports.append(service["port"])
        else:
            print_colored(f"  ✅ Port {service['port']} frei ({service['name']})", "92")
    
    if blocked_ports:
        print_colored("\n⚠️ Einige Ports sind bereits belegt!", "93")
        response = input("Trotzdem fortfahren? (j/n): ")
        if response.lower() != 'j':
            print_colored("Abgebrochen.", "91")
            return
    
    # Services starten
    print_colored("\n🔧 Starte Services...", "93")
    
    for service in SERVICES:
        start_service(service)
        time.sleep(1)
    
    print_colored("\n✅ Alle Services gestartet!", "92")
    print_colored("\n📊 URLs (WICHTIG: 127.0.0.1 verwenden!):", "96")
    print("  Dashboard:  http://127.0.0.1:5000")
    print("  API:        http://127.0.0.1:5002")
    print("  Frontend:   http://127.0.0.1:5173")
    print("  Prometheus: http://127.0.0.1:8000/metrics")
    print("  Proxy:      http://127.0.0.1:8088")
    print_colored("\n💡 Tipp: Verwenden Sie 127.0.0.1 statt localhost!", "93")
    print_colored("         (localhost hat 2-Sekunden-Delay in Windows)", "93")
    
    # Health-Check
    time.sleep(3)
    print_colored("\n🔍 Health-Check...", "96")
    
    import requests
    for service in SERVICES:
        try:
            response = requests.get(f"http://127.0.0.1:{service['port']}/", timeout=1)
            print_colored(f"  ✅ {service['name']}: ONLINE", "92")
        except:
            print_colored(f"  ⚠️ {service['name']}: Noch nicht bereit", "93")
    
    input("\n✨ System bereit! Drücken Sie Enter zum Beenden...")

if __name__ == "__main__":
    main()
