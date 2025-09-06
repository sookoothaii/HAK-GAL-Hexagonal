
import requests
import time
import os
from dotenv import load_dotenv

try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from pathlib import Path

# --- Konfiguration ---
# Lade .env aus dem Projekt-Hauptverzeichnis
project_root = Path(__file__).parent.parent
dotenv_path = project_root / ".env"
if dotenv_path.exists():
    print(f"Lade Umgebungsvariablen aus: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"Warnung: .env-Datei nicht gefunden unter {dotenv_path}")

API_ENDPOINT = "http://127.0.0.1:5002/api/status?include_metrics=true"
# SENTRY DSN DIREKT GESETZT - FUNKTIONIERT GARANTIERT!
SENTRY_DSN = "https://48c80acd7769ef02cff4f1987071fd87@o4509639807205376.ingest.de.sentry.io/4509659832189008"
CHECK_INTERVAL_SECONDS = 15

# Schwellwerte (Empirisch angepasst am 2025-01-03)
# Basierend auf: avg_query=0.475ms, insert_rate=26,827/sec
QUERY_TIME_THRESHOLD_MS = 5  # 10x average (war 20)
INSERT_RATE_THRESHOLD_SEC = 5000  # ~20% der gemessenen Rate (bleibt OK)

def initialize_sentry():
    """Initialisiert Sentry, falls ein DSN vorhanden ist, stürzt aber bei Fehlern nicht ab."""
    if SENTRY_AVAILABLE and SENTRY_DSN:
        try:
            print(f"[DEBUG] Verwende Sentry DSN: {SENTRY_DSN[:50]}...")
            sentry_sdk.init(
                dsn=SENTRY_DSN.strip(),  # Strip whitespace just in case
                environment="hakgal-monitoring-agent",
                traces_sample_rate=1.0  # Enable performance monitoring
            )
            print("[OK] 🚀 Sentry SDK erfolgreich initialisiert!")
            # Test-Event senden
            sentry_sdk.capture_message("HAK-GAL Monitoring Agent gestartet", level="info")
            print("[OK] ✅ Test-Event an Sentry gesendet!")
            return True
        except Exception as e:
            print(f"[WARNING] Sentry-Initialisierung fehlgeschlagen: {e}. Alerts werden nur auf der Konsole ausgegeben.")
            return False
    print("[WARNING] Sentry DSN nicht konfiguriert. Alerts werden nur auf der Konsole ausgegeben.")
    return False

def check_system_performance():
    """Ruft den Status-Endpunkt ab und prüft die Metriken."""
    try:
        response = requests.get(API_ENDPOINT, timeout=10)
        response.raise_for_status() # Löst einen Fehler bei 4xx/5xx Antworten aus
        data = response.json()

        # Debug: Response anzeigen
        print(f"[DEBUG] API Response keys: {list(data.keys())}")
        
        # Metriken extrahieren - verschiedene Möglichkeiten probieren
        metrics = data.get('system_metrics', data.get('metrics', {}))
        if not metrics and 'kb_metrics' in data:
            metrics = data['kb_metrics']
        
        print(f"[DEBUG] Metrics object: {metrics}")
        
        query_time = metrics.get('avg_query_time_ms', metrics.get('query_time', 0))
        insert_rate = metrics.get('inserts_per_second', metrics.get('insert_rate', INSERT_RATE_THRESHOLD_SEC))

        print(f"[INFO] Aktuelle Metriken: Query Time = {query_time:.2f}ms, Insert Rate = {insert_rate}/sec")

        # Schwellwerte prüfen
        if query_time > QUERY_TIME_THRESHOLD_MS:
            message = f"Performance Alert: Query Time überschreitet Schwellwert ({query_time:.2f}ms > {QUERY_TIME_THRESHOLD_MS}ms)"
            print(f"[ALERT] {message}")
            if SENTRY_AVAILABLE:
                sentry_sdk.capture_message(message, level='warning')

        if insert_rate < INSERT_RATE_THRESHOLD_SEC:
            message = f"Performance Alert: Insert Rate unter Schwellwert ({insert_rate} < {INSERT_RATE_THRESHOLD_SEC})"
            print(f"[ALERT] {message}")
            if SENTRY_AVAILABLE:
                sentry_sdk.capture_message(message, level='warning')

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Fehler beim Abrufen der API: {e}")
    except Exception as e:
        print(f"[ERROR] Ein unerwarteter Fehler ist aufgetreten: {e}")

def main():
    """Haupt-Schleife des Monitoring-Agenten."""
    print("="*60)
    print("🚀 HAK/GAL Performance Monitoring Agent mit SENTRY")
    print("="*60)
    has_sentry = initialize_sentry()
    
    if has_sentry:
        print(f"✅ Sentry ist AKTIV!")
        print(f"📡 Überwache Endpunkt: {API_ENDPOINT}")
        print(f"⚠️  Alert-Schwellwerte:")
        print(f"   - Query Time > {QUERY_TIME_THRESHOLD_MS}ms")
        print(f"   - Insert Rate < {INSERT_RATE_THRESHOLD_SEC}/sec")
        print("="*60)
    else:
        print("❌ Sentry ist NICHT aktiv - nur Console-Logging")
    
    print("\n🔄 Starte Monitoring-Loop...\n")
    
    while True:
        check_system_performance()
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
