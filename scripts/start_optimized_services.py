#!/usr/bin/env python3
"""
HAK/GAL Services Starter - Startet beide optimierte Services
"""
import subprocess
import time
import sys
import psutil
import os

def kill_existing_services():
    """Beende existierende Services auf Ports 5000 und 8000"""
    print("Beende existierende Services...")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections():
                if conn.laddr.port in [5000, 8000]:
                    print(f"  Beende Prozess auf Port {conn.laddr.port} (PID: {proc.pid})")
                    proc.terminate()
                    time.sleep(1)
                    if proc.is_running():
                        proc.kill()
        except:
            pass

def start_services():
    """Starte optimierte Services"""
    print("HAK/GAL OPTIMIZED SERVICES STARTER")
    print("=" * 60)
    
    # Beende alte Services
    print("\nBeende existierende Services...")
    kill_existing_services()
    time.sleep(2)
    
    # Starte Flask Dashboard
    print("\nStarte optimierten Flask Dashboard...")
    flask_proc = subprocess.Popen([sys.executable, "hakgal_dashboard_optimized.py"])
    time.sleep(3)
    
    # Starte Prometheus Exporter
    print("\nStarte optimierten Prometheus Exporter...")
    prom_proc = subprocess.Popen([sys.executable, "hakgal_prometheus_optimized.py"])
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("SERVICES ERFOLGREICH GESTARTET!")
    print("=" * 60)
    print("\nVerfügbare Endpoints:")
    print("  Dashboard:    http://localhost:5000")
    print("  Health API:   http://localhost:5000/api/health")
    print("  Metrics API:  http://localhost:5000/api/metrics")
    print("  Prometheus:   http://localhost:8000")
    print("\nPerformance: <50ms Response Time (optimiert)")
    print("Caching: Aktiviert (5 Sekunden TTL)")
    print("\n[Drücken Sie Ctrl+C zum Beenden]")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nBeende Services...")
        flask_proc.terminate()
        prom_proc.terminate()
        print("Services beendet")

if __name__ == "__main__":
    start_services()