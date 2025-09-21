#!/usr/bin/env python3
"""
Cursor File Watcher für HAK/GAL Multi-Agent System
Überwacht das cursor_exchange-Verzeichnis und leitet Tasks an Cursor weiter
"""

import os
import json
import time
import logging
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import webbrowser
import urllib.parse

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cursor_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CursorTaskHandler(FileSystemEventHandler):
    """Handler für neue Task-Dateien im cursor_exchange-Verzeichnis"""
    
    def __init__(self, exchange_dir: Path):
        self.exchange_dir = exchange_dir
        self.processed_files = set()
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix != '.json':
            return
            
        # Verzögerung um sicherzustellen, dass die Datei vollständig geschrieben ist
        time.sleep(0.5)
        self.process_task_file(file_path)
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix != '.json':
            return
            
        # Nur verarbeiten wenn noch nicht verarbeitet
        if str(file_path) not in self.processed_files:
            time.sleep(0.5)
            self.process_task_file(file_path)
    
    def process_task_file(self, task_file: Path):
        """Verarbeite eine Task-Datei und leite sie an Cursor weiter"""
        try:
            logger.info(f"Verarbeite Task-Datei: {task_file.name}")
            
            # Task-Daten lesen
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            task_id = task_data.get('task_id', 'unknown')
            task_description = task_data.get('task', '')
            context = task_data.get('context', {})
            
            logger.info(f"Task ID: {task_id}")
            logger.info(f"Task: {task_description[:100]}...")
            
            # Methode 1: URL Scheme (öffnet Cursor mit Task)
            self.open_cursor_with_task(task_description, context, task_id)
            
            # Methode 2: Response-Datei erstellen (für sofortige Rückmeldung)
            self.create_immediate_response(task_file, task_id)
            
            # Als verarbeitet markieren
            self.processed_files.add(str(task_file))
            
        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten von {task_file}: {e}")
    
    def open_cursor_with_task(self, task_description: str, context: dict, task_id: str):
        """Öffne Cursor mit der Task über URL Scheme"""
        try:
            # Vollständigen Prompt erstellen
            full_prompt = f"HAK/GAL Multi-Agent Task (ID: {task_id}):\n\n{task_description}"
            
            if context:
                full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2, ensure_ascii=False)}"
            
            full_prompt += "\n\nBitte bearbeite diese Aufgabe und speichere das Ergebnis."
            
            # URL-encode
            prompt_encoded = urllib.parse.quote(full_prompt)
            
            # Verschiedene Cursor URL-Schemes versuchen
            url_schemes = [
                f"cursor://open?prompt={prompt_encoded}",
                f"cursor://new?prompt={prompt_encoded}",
                f"cursor-ide://task?description={prompt_encoded}"
            ]
            
            for url in url_schemes:
                try:
                    webbrowser.open(url)
                    logger.info(f"Cursor geöffnet mit URL: {url[:50]}...")
                    return True
                except Exception as e:
                    logger.debug(f"URL Scheme {url} fehlgeschlagen: {e}")
                    continue
            
            logger.warning("Kein Cursor URL-Scheme funktioniert")
            return False
            
        except Exception as e:
            logger.error(f"Fehler beim Öffnen von Cursor: {e}")
            return False
    
    def create_immediate_response(self, task_file: Path, task_id: str):
        """Erstelle eine sofortige Response-Datei"""
        try:
            response_file = task_file.parent / f"response_{task_id}.json"
            
            response_data = {
                "id": task_id,
                "status": "pending",
                "message": "Task wurde an Cursor weitergeleitet",
                "timestamp": time.time(),
                "method": "file_watcher",
                "result": "Task in Cursor geöffnet - bitte manuell bearbeiten"
            }
            
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Response-Datei erstellt: {response_file.name}")
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Response: {e}")

def process_existing_tasks(exchange_dir: Path):
    """Verarbeite bereits vorhandene Task-Dateien"""
    handler = CursorTaskHandler(exchange_dir)
    
    for task_file in exchange_dir.glob("task_*.json"):
        if task_file.is_file():
            logger.info(f"Verarbeite bestehende Task: {task_file.name}")
            handler.process_task_file(task_file)

def main():
    """Hauptfunktion"""
    exchange_dir = Path("cursor_exchange")
    
    if not exchange_dir.exists():
        logger.error(f"Verzeichnis {exchange_dir} existiert nicht!")
        return
    
    logger.info(f"Starte Cursor File Watcher für: {exchange_dir.absolute()}")
    
    # Bestehende Tasks verarbeiten
    process_existing_tasks(exchange_dir)
    
    # File-Watcher starten
    event_handler = CursorTaskHandler(exchange_dir)
    observer = Observer()
    observer.schedule(event_handler, str(exchange_dir), recursive=False)
    observer.start()
    
    try:
        logger.info("File-Watcher läuft... Drücke Ctrl+C zum Beenden")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Beende File-Watcher...")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()


