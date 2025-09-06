"""
REAL-TIME BIDIRECTIONAL COMMUNICATION SYSTEM
Ermöglicht echte Echtzeit-Kommunikation zwischen Claude und anderen Agenten
"""
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
import requests
from typing import Dict, Any, Optional

class RealTimeCommunicator:
    """Echte bidirektionale Kommunikation für Claude"""
    
    def __init__(self, api_base="http://127.0.0.1:5002", api_key="hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"):
        self.api_base = api_base
        self.api_key = api_key
        self.response_dir = Path("agent_responses")
        self.response_dir.mkdir(exist_ok=True)
        
    def send_and_wait(self, agent: str, message: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Sende Nachricht und WARTE auf echte Antwort
        Returns: Die tatsächliche Antwort des Agenten
        """
        print(f"📡 Sende an {agent}: {message[:80]}...")
        
        # Sende Request
        task_id = self._send_request(agent, message)
        if not task_id:
            return {"error": "Failed to send request"}
        
        print(f"✅ Task ID: {task_id}")
        print(f"⏳ Warte auf Antwort (max {timeout} Sekunden)...")
        
        # Polling für Response
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check verschiedene Response-Locations
            response = self._check_for_response(agent, task_id)
            if response:
                print(f"✅ ANTWORT ERHALTEN nach {int(time.time() - start_time)} Sekunden!")
                return response
            
            time.sleep(1)  # Poll every second
        
        return {"error": f"Timeout nach {timeout} Sekunden"}
    
    def _send_request(self, agent: str, message: str) -> Optional[str]:
        """Sende Request und gib Task ID zurück"""
        try:
            response = requests.post(
                f"{self.api_base}/api/agent-bus/delegate",
                headers={"X-API-Key": self.api_key},
                json={
                    "target_agent": agent,
                    "task_description": message,
                    "context": {
                        "real_time": True,
                        "sender": "claude",
                        "timestamp": datetime.now().isoformat()
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('task_id')
            
        except Exception as e:
            print(f"❌ Send error: {e}")
        
        return None
    
    def _check_for_response(self, agent: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Prüfe alle möglichen Response-Locations"""
        
        # 1. Check agent_responses directory
        patterns = [
            f"*{task_id}*",
            f"*{agent}*latest*",
            f"*response*"
        ]
        
        for pattern in patterns:
            for file in self.response_dir.rglob(pattern):
                if file.is_file() and file.suffix == '.json':
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Check if this is our response
                        if (data.get('task_id') == task_id or 
                            data.get('timestamp', '') > datetime.now().isoformat()[:19]):
                            
                            response = data.get('response', {})
                            if response.get('status') == 'completed':
                                return {
                                    "task_id": task_id,
                                    "agent": agent,
                                    "result": response.get('result', 'No content'),
                                    "file": str(file)
                                }
                    except:
                        pass
        
        # 2. Special check for Gemini
        if agent == "gemini":
            gemini_file = self.response_dir / "gemini_latest_full_response.txt"
            if gemini_file.exists():
                mod_time = gemini_file.stat().st_mtime
                if time.time() - mod_time < 60:  # Modified in last minute
                    with open(gemini_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if task_id in content or "VOID RESPONSE" in content:
                        return {
                            "task_id": task_id,
                            "agent": "gemini",
                            "result": content,
                            "file": str(gemini_file)
                        }
        
        # 3. Check API endpoint
        try:
            resp = requests.get(
                f"{self.api_base}/api/agent-bus/responses/{task_id}",
                headers={"X-API-Key": self.api_key},
                timeout=2
            )
            if resp.status_code == 200:
                return resp.json()
        except:
            pass
        
        return None
    
    def chat_with_agent(self, agent: str, message: str) -> str:
        """
        High-Level Chat Interface
        Returns: Die Antwort als String
        """
        response = self.send_and_wait(agent, message)
        
        if "error" in response:
            return f"❌ {response['error']}"
        
        return response.get('result', 'Keine Antwort')


# Test-Funktionen
def test_real_time_communication():
    """Teste Echtzeit-Kommunikation mit allen Agenten"""
    
    comm = RealTimeCommunicator()
    
    print("="*80)
    print("🚀 REAL-TIME BIDIRECTIONAL COMMUNICATION TEST")
    print("="*80)
    
    # Test mit Gemini
    print("\n1️⃣ TESTE GEMINI...")
    response = comm.chat_with_agent(
        "gemini",
        "ECHTZEIT-TEST: Antworte sofort mit 'GEMINI ECHTZEIT-ANTWORT: Bidirektionale Kommunikation funktioniert!'"
    )
    print(f"GEMINI SAGT: {response}")
    
    # Test mit Claude CLI
    print("\n2️⃣ TESTE CLAUDE CLI...")
    response = comm.chat_with_agent(
        "claude_cli",
        "ECHTZEIT-TEST: Sage 'CLAUDE CLI ECHTZEIT: Ich bin eine andere Claude-Instanz!'"
    )
    print(f"CLAUDE CLI SAGT: {response}")
    
    # Test mit Cursor
    print("\n3️⃣ TESTE CURSOR...")
    response = comm.chat_with_agent(
        "cursor",
        "ECHTZEIT-TEST: Erstelle eine Datei 'realtime_proof.txt' mit 'CURSOR ECHTZEIT OK'"
    )
    print(f"CURSOR SAGT: {response}")
    
    print("\n✅ TEST ABGESCHLOSSEN!")


# Interactive Chat Mode
def interactive_chat():
    """Interaktiver Chat mit beliebigem Agent"""
    
    comm = RealTimeCommunicator()
    
    print("="*80)
    print("💬 INTERAKTIVER MULTI-AGENT CHAT")
    print("="*80)
    print("Verfügbare Agenten: gemini, claude_cli, cursor, claude_desktop")
    print("Befehle: 'exit' zum Beenden, 'switch <agent>' zum Wechseln")
    print("="*80)
    
    current_agent = "gemini"
    
    while True:
        prompt = input(f"\n[{current_agent}]> ")
        
        if prompt.lower() == 'exit':
            break
        
        if prompt.lower().startswith('switch '):
            new_agent = prompt.split()[1]
            if new_agent in ['gemini', 'claude_cli', 'cursor', 'claude_desktop']:
                current_agent = new_agent
                print(f"✅ Gewechselt zu {current_agent}")
            else:
                print(f"❌ Unbekannter Agent: {new_agent}")
            continue
        
        # Sende Nachricht
        print(f"\n⏳ Warte auf {current_agent}...")
        response = comm.chat_with_agent(current_agent, prompt)
        
        print(f"\n{current_agent.upper()}: {response}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        interactive_chat()
    else:
        test_real_time_communication()
