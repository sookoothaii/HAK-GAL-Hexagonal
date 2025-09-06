#!/usr/bin/env python3
"""
Claude Desktop Auto Response Processor - Erstellt von Gemini AI
Verarbeitet automatisch Claude Desktop Responses und integriert sie in HAK/GAL
"""

import json
import os
import time
import requests
from pathlib import Path
from datetime import datetime
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('claude_desktop_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClaudeDesktopAutoProcessor:
    def __init__(self):
        self.response_dir = Path("claude_desktop_exchange")
        self.api_base = "http://127.0.0.1:5002"
        self.api_key = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
        self.write_token = "515f57956e7bd15ddc3817573598f190"
        self.headers = {"X-API-Key": self.api_key}
        self.processed_files = set()
        
    def process_existing_responses(self):
        """Verarbeitet bereits vorhandene Response-Dateien"""
        logger.info("Verarbeite vorhandene Claude Desktop Responses...")
        
        response_files = list(self.response_dir.glob("*_response.json"))
        
        for response_file in response_files:
            if str(response_file) not in self.processed_files:
                self.process_response_file(response_file)
                self.processed_files.add(str(response_file))
    
    def process_response_file(self, response_file):
        """Verarbeitet eine Claude Desktop Response-Datei"""
        try:
            logger.info(f"Verarbeite: {response_file.name}")
            
            with open(response_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Response extrahieren
            response_text = data.get("response", "")
            request_id = data.get("request_id", "unknown")
            timestamp = data.get("timestamp", time.time())
            
            if not response_text:
                logger.warning(f"Keine Response in {response_file.name}")
                return False
            
            # In HAK/GAL System integrieren
            success = self.integrate_to_hakgal(request_id, response_text, timestamp)
            
            if success:
                logger.info(f"✅ Response erfolgreich integriert: {request_id}")
                return True
            else:
                logger.error(f"❌ Fehler bei Integration: {request_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Verarbeiten von {response_file}: {e}")
            return False
    
    def integrate_to_hakgal(self, request_id, response_text, timestamp):
        """Integriert Response in HAK/GAL System"""
        try:
            # Fakt erstellen
            fact = f"ClaudeDesktopResponse({request_id}, {timestamp}, {response_text[:100]}...)."
            
            # An HAK/GAL API senden
            url = f"{self.api_base}/api/facts/add"
            payload = {
                "statement": fact,
                "source": "claude_desktop_auto_processor",
                "tags": ["claude_desktop", "auto_processed", "response"]
            }
            params = {"auth_token": self.write_token}
            
            response = requests.post(url, headers=self.headers, json=payload, params=params)
            
            if response.status_code == 200:
                logger.info(f"Fakt in Wissensdatenbank gespeichert: {fact[:50]}...")
                
                # Response in agent_responses speichern
                self.save_to_agent_responses(request_id, response_text, timestamp)
                
                return True
            else:
                logger.warning(f"Fehler beim Speichern des Fakts: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Fehler bei HAK/GAL Integration: {e}")
            return False
    
    def save_to_agent_responses(self, request_id, response_text, timestamp):
        """Speichert Response in agent_responses Verzeichnis"""
        try:
            response_dir = Path("agent_responses")
            response_dir.mkdir(exist_ok=True)
            
            hakgal_response = {
                "task_id": request_id,
                "agent": "claude_desktop",
                "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
                "status": "completed",
                "result": response_text,
                "method": "auto_processor"
            }
            
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request_id}_claude_desktop.json"
            response_file = response_dir / filename
            
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(hakgal_response, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Response gespeichert: {filename}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Response: {e}")
    
    def monitor_for_new_responses(self):
        """Überwacht auf neue Response-Dateien"""
        logger.info("Starte Monitoring für neue Claude Desktop Responses...")
        
        while True:
            try:
                # Neue Response-Dateien suchen
                response_files = list(self.response_dir.glob("*_response.json"))
                
                for response_file in response_files:
                    if str(response_file) not in self.processed_files:
                        logger.info(f"Neue Response gefunden: {response_file.name}")
                        if self.process_response_file(response_file):
                            self.processed_files.add(str(response_file))
                
                time.sleep(2)  # Alle 2 Sekunden prüfen
                
            except KeyboardInterrupt:
                logger.info("Monitoring beendet.")
                break
            except Exception as e:
                logger.error(f"Fehler im Monitoring: {e}")
                time.sleep(5)

def main():
    """Hauptfunktion"""
    logger.info("🚀 CLAUDE DESKTOP AUTO PROCESSOR STARTET")
    
    processor = ClaudeDesktopAutoProcessor()
    
    # Vorhandene Responses verarbeiten
    processor.process_existing_responses()
    
    # Monitoring starten
    processor.monitor_for_new_responses()

if __name__ == "__main__":
    main()