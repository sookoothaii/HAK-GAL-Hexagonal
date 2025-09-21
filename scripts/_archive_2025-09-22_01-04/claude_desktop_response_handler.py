#!/usr/bin/env python3
"""
Claude Desktop Response Handler für HAK/GAL System
Verarbeitet automatisch Claude Desktop Responses und leitet sie weiter
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClaudeDesktopResponseHandler:
    def __init__(self):
        self.exchange_dir = Path("claude_desktop_exchange")
        self.api_base = "http://127.0.0.1:5002"
        self.api_key = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
        self.write_token = "515f57956e7bd15ddc3817573598f190"
        self.headers = {"X-API-Key": self.api_key}
        
    def monitor_responses(self):
        """Überwacht Claude Desktop Exchange-Verzeichnis für neue Responses"""
        logger.info("Starte Claude Desktop Response Monitor...")
        
        while True:
            try:
                # Suche nach Response-Dateien
                response_files = list(self.exchange_dir.glob("*_response.json"))
                
                for response_file in response_files:
                    if self.process_response_file(response_file):
                        # Response erfolgreich verarbeitet, Datei löschen
                        response_file.unlink(missing_ok=True)
                        logger.info(f"Response verarbeitet und Datei gelöscht: {response_file.name}")
                
                time.sleep(2)  # Alle 2 Sekunden prüfen
                
            except KeyboardInterrupt:
                logger.info("Response Monitor beendet.")
                break
            except Exception as e:
                logger.error(f"Fehler im Response Monitor: {e}")
                time.sleep(5)
    
    def process_response_file(self, response_file):
        """Verarbeitet eine Claude Desktop Response-Datei"""
        try:
            with open(response_file, 'r', encoding='utf-8') as f:
                response_data = json.load(f)
            
            logger.info(f"Verarbeite Response: {response_file.name}")
            
            # Response an HAK/GAL System weiterleiten
            self.forward_to_hakgal(response_data)
            
            # Response in Wissensdatenbank speichern
            self.save_to_knowledge_base(response_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten von {response_file}: {e}")
            return False
    
    def forward_to_hakgal(self, response_data):
        """Leitet Response an HAK/GAL API weiter"""
        try:
            # Erstelle HAK/GAL Response-Format
            hakgal_response = {
                "task_id": response_data.get("id", "unknown"),
                "agent": "claude_desktop",
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "result": response_data.get("response", "Keine Antwort"),
                "method": "claude_desktop_file_exchange"
            }
            
            # Speichere in agent_responses
            response_dir = Path("agent_responses")
            response_dir.mkdir(exist_ok=True)
            
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hakgal_response['task_id']}_claude_desktop.json"
            response_file = response_dir / filename
            
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(hakgal_response, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Response an HAK/GAL weitergeleitet: {filename}")
            
        except Exception as e:
            logger.error(f"Fehler beim Weiterleiten an HAK/GAL: {e}")
    
    def save_to_knowledge_base(self, response_data):
        """Speichert Response in der Wissensdatenbank"""
        try:
            # Fakt erstellen
            fact = f"ClaudeDesktopResponse({response_data.get('id', 'unknown')}, {response_data.get('timestamp', 'unknown')}, completed)."
            
            # An HAK/GAL API senden
            url = f"{self.api_base}/api/facts/add"
            payload = {
                "statement": fact,
                "source": "claude_desktop_response_handler",
                "tags": ["claude_desktop", "response", "automated"]
            }
            params = {"auth_token": self.write_token}
            
            response = requests.post(url, headers=self.headers, json=payload, params=params)
            
            if response.status_code == 200:
                logger.info(f"Fakt in Wissensdatenbank gespeichert: {fact}")
            else:
                logger.warning(f"Fehler beim Speichern des Fakts: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Fehler beim Speichern in Wissensdatenbank: {e}")

def main():
    """Hauptfunktion"""
    handler = ClaudeDesktopResponseHandler()
    handler.monitor_responses()

if __name__ == "__main__":
    main()


