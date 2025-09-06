#!/usr/bin/env python3
"""
Claude Desktop Debug Suite - Erstellt von Gemini AI
Intensive Debugging-Tools für Claude Desktop Integration
"""

import os
import json
import time
import logging
import requests
from pathlib import Path
from datetime import datetime

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('claude_desktop_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClaudeDesktopDebugger:
    def __init__(self):
        self.exchange_dir = Path("claude_desktop_exchange")
        self.api_base = "http://127.0.0.1:5002"
        self.api_key = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
        self.write_token = "515f57956e7bd15ddc3817573598f190"
        
    def check_file_permissions(self):
        """Prüft Datei-Berechtigungen"""
        logger.info("=== DATEI-BERECHTIGUNGEN PRÜFEN ===")
        
        try:
            # Exchange-Verzeichnis prüfen
            if self.exchange_dir.exists():
                permissions = oct(os.stat(self.exchange_dir).st_mode & 0o777)
                logger.info(f"Exchange-Dir: {self.exchange_dir} - Berechtigungen: {permissions}")
                
                # Schreibtest
                test_file = self.exchange_dir / "debug_test.txt"
                try:
                    with open(test_file, 'w') as f:
                        f.write("Debug test")
                    logger.info("✅ Schreibtest erfolgreich")
                    test_file.unlink()  # Löschen
                except Exception as e:
                    logger.error(f"❌ Schreibtest fehlgeschlagen: {e}")
            else:
                logger.error(f"❌ Exchange-Verzeichnis existiert nicht: {self.exchange_dir}")
                
        except Exception as e:
            logger.error(f"❌ Fehler bei Berechtigungsprüfung: {e}")
    
    def check_filesystem_status(self):
        """Prüft Dateisystem-Status"""
        logger.info("=== DATEISYSTEM-STATUS PRÜFEN ===")
        
        try:
            # Freier Speicherplatz
            statvfs = os.statvfs(self.exchange_dir)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            free_space_gb = free_space / (1024**3)
            logger.info(f"Freier Speicherplatz: {free_space_gb:.2f} GB")
            
            if free_space_gb < 1:
                logger.warning("⚠️ Wenig freier Speicherplatz!")
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Dateisystem-Prüfung: {e}")
    
    def list_exchange_files(self):
        """Listet alle Dateien im Exchange-Verzeichnis"""
        logger.info("=== EXCHANGE-DATEIEN LISTEN ===")
        
        try:
            if self.exchange_dir.exists():
                files = list(self.exchange_dir.glob("*"))
                logger.info(f"Anzahl Dateien: {len(files)}")
                
                for file in files:
                    size = file.stat().st_size if file.is_file() else "DIR"
                    modified = datetime.fromtimestamp(file.stat().st_mtime)
                    logger.info(f"  {file.name} - Größe: {size} - Geändert: {modified}")
            else:
                logger.error("❌ Exchange-Verzeichnis existiert nicht")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Auflisten: {e}")
    
    def create_test_response(self):
        """Erstellt eine Test-Response-Datei"""
        logger.info("=== TEST-RESPONSE ERSTELLEN ===")
        
        try:
            test_response = {
                "id": f"debug_test_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "response": "CLAUDE DESKTOP DEBUG TEST - RESPONSE ERSTELLT VON GEMINI",
                "status": "completed",
                "method": "debug_test"
            }
            
            # Verschiedene Formate testen
            formats = [
                ("test_response.json", json.dumps(test_response, indent=2)),
                ("test_response.txt", test_response["response"]),
                ("test_response.md", f"# Debug Test\n\n{test_response['response']}")
            ]
            
            for filename, content in formats:
                test_file = self.exchange_dir / filename
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✅ Test-Response erstellt: {filename}")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen der Test-Response: {e}")
    
    def test_api_integration(self):
        """Testet API-Integration"""
        logger.info("=== API-INTEGRATION TESTEN ===")
        
        try:
            headers = {"X-API-Key": self.api_key}
            
            # Facts Count testen
            response = requests.get(f"{self.api_base}/api/facts/count", headers=headers)
            if response.status_code == 200:
                logger.info(f"✅ API Facts Count: {response.json()}")
            else:
                logger.error(f"❌ API Facts Count Fehler: {response.status_code}")
            
            # Governor Status testen
            response = requests.get(f"{self.api_base}/api/governor/status", headers=headers)
            if response.status_code == 200:
                logger.info(f"✅ API Governor Status: {response.json()}")
            else:
                logger.error(f"❌ API Governor Status Fehler: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ API-Integration Fehler: {e}")

class ExchangeDirectoryMonitor:
    """Überwacht das Exchange-Verzeichnis"""
    
    def __init__(self):
        self.processed_files = set()
        
    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"📁 NEUE DATEI ERSTELLT: {event.src_path}")
            self.processed_files.add(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"📝 DATEI GEÄNDERT: {event.src_path}")
    
    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"🗑️ DATEI GELÖSCHT: {event.src_path}")

def run_full_debug():
    """Führt vollständige Debug-Suite aus"""
    logger.info("🚀 CLAUDE DESKTOP DEBUG SUITE STARTET")
    
    debugger = ClaudeDesktopDebugger()
    
    # Alle Tests ausführen
    debugger.check_file_permissions()
    debugger.check_filesystem_status()
    debugger.list_exchange_files()
    debugger.create_test_response()
    debugger.test_api_integration()
    
    logger.info("✅ DEBUG SUITE ABGESCHLOSSEN")

def start_monitoring():
    """Startet Directory-Monitoring"""
    logger.info("👁️ STARTE EXCHANGE-DIRECTORY MONITORING")
    
    exchange_dir = Path("claude_desktop_exchange")
    event_handler = ExchangeDirectoryMonitor()
    observer = Observer()
    observer.schedule(event_handler, str(exchange_dir), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("⏹️ MONITORING BEENDET")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        start_monitoring()
    else:
        run_full_debug()