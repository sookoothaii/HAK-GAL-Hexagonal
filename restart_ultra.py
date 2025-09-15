#!/usr/bin/env python3
"""
KILL ALL & RESTART - Beendet alle Services und startet ultra-optimierte Version
"""
import subprocess
import time
import sys
import psutil
import os
import signal

def kill_all_python_services():
    """Beende ALLE Python-Services auf Ports 5000 und 8000"""
    print("🔴 BEENDE ALLE LAUFENDEN SERVICES...")
    print("-" * 60)
    
    killed = []
    
    # Finde alle Python-Prozesse
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                # Prüfe ob es ein HAK/GAL Service ist
                if any(x in cmdline.lower() for x in ['dashboard', 'prometheus', 'hakgal', 'start_']):
                    # Überspringe diesen Prozess selbst
                    if proc.pid == os.getpid():
                        continue
                        
                    print(f"  Beende PID {proc.pid}: {cmdline[:80]}...")
                    try:
                        proc.terminate()
                        killed.append(proc.pid)
                    except:
                        try:
                            proc.kill()
                            killed.append(proc.pid)
                        except:
                            pass
        except:
            pass
    
    # Zusätzlich: Beende alles auf Ports 5000 und 8000
    for conn in psutil.net_connections():
        if conn.laddr.port in [5000, 8000] and conn.status == 'LISTEN':
            try:
                proc = psutil.Process(conn.pid)
                if proc.pid not in killed:
                    print(f"  Beende Port {conn.laddr.port} Prozess (PID {conn.pid})")
                    proc.terminate()
                    time.sleep(0.5)
                    if proc.is_running():
                        proc.kill()
            except:
                pass
    
    print(f"\n✅ {len(killed)} Prozesse beendet")
    print("⏳ Warte 3 Sekunden...")
    time.sleep(3)

def verify_ports_free():
    """Verifiziere dass Ports frei sind"""
    print("\n🔍 VERIFIZIERE PORTS...")
    print("-" * 60)
    
    ports_free = True
    for port in [5000, 8000]:
        in_use = False
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                in_use = True
                print(f"  ❌ Port {port} ist noch belegt!")
                break
        
        if not in_use:
            print(f"  ✅ Port {port} ist frei")
        else:
            ports_free = False
    
    return ports_free

def start_ultra_optimized():
    """Starte die ultra-optimierte Version"""
    print("\n🚀 STARTE ULTRA-OPTIMIERTE SERVICES...")
    print("-" * 60)
    
    # Starte Dashboard
    print("  Starting HAK/GAL Dashboard ULTRA...")
    dashboard_proc = subprocess.Popen(
        [sys.executable, "hakgal_dashboard_ultra.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)
    
    # Starte Prometheus
    print("  Starting Prometheus Exporter...")
    prom_proc = subprocess.Popen(
        [sys.executable, "hakgal_prometheus_optimized.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)
    
    print("\n✅ Services gestartet!")
    return dashboard_proc, prom_proc

def test_performance():
    """Schneller Performance-Test"""
    print("\n⚡ PERFORMANCE-TEST...")
    print("-" * 60)
    
    import requests
    
    # Warte kurz
    time.sleep(1)
    
    # Teste Health-Endpoint
    times = []
    for i in range(5):
        try:
            start = time.perf_counter()
            response = requests.get("http://localhost:5000/api/health", timeout=1)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            
            # Prüfe Cache-Header
            from_cache = response.headers.get('X-From-Cache', 'unknown')
            print(f"  Request {i+1}: {elapsed:.1f}ms (Cache: {from_cache})")
            
            time.sleep(0.5)
        except Exception as e:
            print(f"  Request {i+1}: ERROR - {e}")
    
    if times:
        avg = sum(times) / len(times)
        print(f"\n  📊 Durchschnitt: {avg:.1f}ms")
        
        if avg < 50:
            print("  🚀 EXZELLENT! Performance <50ms erreicht!")
        elif avg < 100:
            print("  ✅ GUT! Performance <100ms")
        else:
            print("  ⚠️ Performance noch nicht optimal")

def main():
    print("=" * 60)
    print("🔧 HAK/GAL SERVICE RESTART - ULTRA OPTIMIZATION")
    print("=" * 60)
    
    # Schritt 1: Alles beenden
    kill_all_python_services()
    
    # Schritt 2: Ports verifizieren
    if not verify_ports_free():
        print("\n⚠️ WARNUNG: Einige Ports sind noch belegt!")
        print("Versuche erneut zu beenden...")
        kill_all_python_services()
    
    # Schritt 3: Neue Services starten
    try:
        dashboard_proc, prom_proc = start_ultra_optimized()
        
        # Schritt 4: Performance testen
        test_performance()
        
        # Schritt 5: Services laufen lassen
        print("\n" + "=" * 60)
        print("✅ ULTRA-OPTIMIERTE SERVICES LAUFEN!")
        print("=" * 60)
        print("\n📊 Verfügbare Endpoints:")
        print("  Dashboard:    http://localhost:5000")
        print("  Health API:   http://localhost:5000/api/health")
        print("  Metrics API:  http://localhost:5000/api/metrics")
        print("  Prometheus:   http://localhost:8000")
        print("\n⚡ Expected Performance: <10ms (cached)")
        print("\n[Drücken Sie Ctrl+C zum Beenden]")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Beende Services...")
        try:
            dashboard_proc.terminate()
            prom_proc.terminate()
        except:
            pass
        print("✅ Services beendet")

if __name__ == "__main__":
    main()