#!/usr/bin/env python
"""
HAK-GAL Real Metrics Monitor
Überwacht tatsächlich verfügbare Metriken aus der API
"""

import requests
import time
import os
from dotenv import load_dotenv
from pathlib import Path

try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Konfiguration
project_root = Path(__file__).parent.parent
dotenv_path = project_root / ".env"
if dotenv_path.exists():
    print(f"📁 Lade .env aus: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path)

API_STATUS = "http://127.0.0.1:5002/api/status?include_metrics=true"
API_METRICS = "http://127.0.0.1:5002/api/metrics"
SENTRY_DSN = "https://48c80acd7769ef02cff4f1987071fd87@o4509639807205376.ingest.de.sentry.io/4509659832189008"
CHECK_INTERVAL_SECONDS = 10

# Schwellwerte (angepasst an reale Metriken)
CPU_THRESHOLD_PERCENT = 80.0      # Alert wenn CPU > 80%
MEMORY_THRESHOLD_PERCENT = 85.0   # Alert wenn Memory > 85%
GPU_THRESHOLD_PERCENT = 90.0      # Alert wenn GPU > 90%
FACT_COUNT_MIN = 5000             # Alert wenn Fakten < 5000

def initialize_sentry():
    """Initialisiert Sentry für Error Tracking"""
    if SENTRY_AVAILABLE and SENTRY_DSN:
        try:
            sentry_sdk.init(
                dsn=SENTRY_DSN.strip(),
                environment="hakgal-monitoring-real",
                traces_sample_rate=1.0
            )
            print("✅ Sentry initialisiert!")
            sentry_sdk.capture_message("HAK-GAL Real Metrics Monitor gestartet", level="info")
            return True
        except Exception as e:
            print(f"⚠️ Sentry-Initialisierung fehlgeschlagen: {e}")
            return False
    return False

def check_real_metrics():
    """Prüft die tatsächlich verfügbaren System-Metriken"""
    try:
        # Status mit System-Metriken abrufen
        response = requests.get(API_STATUS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # System-Metriken extrahieren
        system_metrics = data.get('system_metrics', {})
        
        # CPU-Metriken
        cpu_percent = system_metrics.get('cpu', {}).get('percent', 0)
        cpu_count = system_metrics.get('cpu', {}).get('count', 0)
        
        # Memory-Metriken
        memory = system_metrics.get('memory', {})
        memory_percent = memory.get('percent', 0)
        memory_used_gb = memory.get('used_gb', 0)
        memory_total_gb = memory.get('total_gb', 0)
        
        # GPU-Metriken (falls verfügbar)
        gpu = system_metrics.get('gpu', {})
        gpu_available = gpu.get('available', False)
        gpu_utilization = gpu.get('utilization', 0) if gpu_available else 0
        gpu_memory_percent = gpu.get('memory_percent', 0) if gpu_available else 0
        gpu_temp = gpu.get('temperature', 0) if gpu_available else 0
        
        # Fakten-Anzahl
        fact_count = data.get('fact_count', 0)
        
        # Status ausgeben
        print(f"\n{'='*60}")
        print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        print(f"📊 Fakten: {fact_count:,}")
        print(f"🖥️ CPU: {cpu_percent:.1f}% ({cpu_count} Cores)")
        print(f"💾 RAM: {memory_percent:.1f}% ({memory_used_gb:.1f}/{memory_total_gb:.1f} GB)")
        
        if gpu_available:
            print(f"🎮 GPU: {gpu_utilization}% Auslastung, {gpu_memory_percent:.1f}% VRAM, {gpu_temp}°C")
        
        # Schwellwert-Prüfungen
        alerts = []
        
        if cpu_percent > CPU_THRESHOLD_PERCENT:
            msg = f"⚠️ CPU-Auslastung kritisch: {cpu_percent:.1f}% > {CPU_THRESHOLD_PERCENT}%"
            alerts.append(msg)
            
        if memory_percent > MEMORY_THRESHOLD_PERCENT:
            msg = f"⚠️ Memory-Auslastung kritisch: {memory_percent:.1f}% > {MEMORY_THRESHOLD_PERCENT}%"
            alerts.append(msg)
            
        if gpu_available and gpu_utilization > GPU_THRESHOLD_PERCENT:
            msg = f"⚠️ GPU-Auslastung kritisch: {gpu_utilization}% > {GPU_THRESHOLD_PERCENT}%"
            alerts.append(msg)
            
        if fact_count < FACT_COUNT_MIN:
            msg = f"⚠️ Fakten-Anzahl zu niedrig: {fact_count} < {FACT_COUNT_MIN}"
            alerts.append(msg)
        
        # Alerts ausgeben und an Sentry senden
        if alerts:
            print(f"\n🚨 ALERTS:")
            for alert in alerts:
                print(f"   {alert}")
                if SENTRY_AVAILABLE:
                    sentry_sdk.capture_message(alert, level='warning')
        else:
            print(f"\n✅ Alle Metriken im grünen Bereich")
            
        # Zusätzliche Metriken von /api/metrics
        try:
            metrics_response = requests.get(API_METRICS, timeout=5)
            if metrics_response.status_code == 200:
                metrics_data = metrics_response.json()
                process = metrics_data.get('process', {})
                print(f"\n📈 Prozess-Details:")
                print(f"   PID: {process.get('pid', 'N/A')}")
                print(f"   Threads: {process.get('threads', 'N/A')}")
                print(f"   Memory: {process.get('memory_mb', 0):.1f} MB")
                print(f"   Uptime: {metrics_data.get('uptime_seconds', 0)/60:.1f} Minuten")
        except:
            pass
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API-Fehler: {e}")
        if SENTRY_AVAILABLE:
            sentry_sdk.capture_exception(e)
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        if SENTRY_AVAILABLE:
            sentry_sdk.capture_exception(e)

def main():
    """Haupt-Loop des Monitoring-Agenten"""
    print("\n" + "="*60)
    print("🎯 HAK-GAL Real Metrics Monitor")
    print("="*60)
    
    has_sentry = initialize_sentry()
    
    print(f"📡 Überwache: {API_STATUS}")
    print(f"⏱️ Intervall: {CHECK_INTERVAL_SECONDS} Sekunden")
    print(f"🎚️ Schwellwerte:")
    print(f"   - CPU > {CPU_THRESHOLD_PERCENT}%")
    print(f"   - Memory > {MEMORY_THRESHOLD_PERCENT}%")
    print(f"   - GPU > {GPU_THRESHOLD_PERCENT}%")
    print(f"   - Fakten < {FACT_COUNT_MIN}")
    print("="*60)
    
    print("\n🔄 Starte Monitoring...\n")
    
    while True:
        check_real_metrics()
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
