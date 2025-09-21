#!/usr/bin/env python3
"""
MULTI-AGENT CHAT TERMINAL
Interaktive Echtzeit-Kommunikation mit allen Agenten
"""

from realtime_communicator import RealTimeCommunicator
import time
from datetime import datetime

class MultiAgentChat:
    """Multi-Agent Chat Interface"""
    
    def __init__(self):
        self.comm = RealTimeCommunicator()
        self.agents = {
            '1': 'gemini',
            '2': 'claude_cli', 
            '3': 'cursor',
            '4': 'claude_desktop'
        }
        self.current_agent = 'gemini'
        self.history = []
        
    def show_header(self):
        """Zeige Chat Header"""
        print("\n" + "="*80)
        print("💬 MULTI-AGENT ECHTZEIT CHAT")
        print("="*80)
        print("Verfügbare Agenten:")
        print("  1. Gemini (Google AI)")
        print("  2. Claude CLI (Andere Claude-Instanz)")
        print("  3. Cursor (IDE)")
        print("  4. Claude Desktop")
        print("\nBefehle:")
        print("  /switch <nummer> - Wechsle zu anderem Agent")
        print("  /history - Zeige Chat-Verlauf")
        print("  /clear - Lösche Bildschirm")
        print("  /test - Teste alle Agenten")
        print("  /exit - Beende Chat")
        print("="*80)
        
    def switch_agent(self, agent_num):
        """Wechsle zu anderem Agent"""
        if agent_num in self.agents:
            self.current_agent = self.agents[agent_num]
            print(f"\n✅ Gewechselt zu {self.current_agent.upper()}")
        else:
            print(f"\n❌ Ungültige Nummer. Wähle 1-4")
            
    def test_all_agents(self):
        """Teste alle Agenten"""
        print("\n🧪 TESTE ALLE AGENTEN...")
        
        test_message = "PING - Bist du online? Antworte mit deinem Namen!"
        
        for num, agent in self.agents.items():
            print(f"\n{num}. Teste {agent}...", end='', flush=True)
            start = time.time()
            
            response = self.comm.chat_with_agent(agent, test_message)
            elapsed = time.time() - start
            
            if "error" not in response.lower():
                print(f" ✅ OK ({elapsed:.1f}s)")
                print(f"   → {response[:60]}...")
            else:
                print(f" ❌ Fehler")
                print(f"   → {response}")
                
    def show_history(self):
        """Zeige Chat-Verlauf"""
        if not self.history:
            print("\n📭 Noch keine Nachrichten")
            return
            
        print(f"\n📜 CHAT-VERLAUF ({len(self.history)} Nachrichten)")
        print("-"*80)
        
        for entry in self.history[-10:]:  # Zeige letzte 10
            print(f"\n[{entry['time']}] {entry['agent'].upper()}")
            print(f"YOU: {entry['message']}")
            print(f"{entry['agent'].upper()}: {entry['response'][:100]}...")
            
    def chat_loop(self):
        """Hauptschleife"""
        self.show_header()
        print(f"\n💬 Chatte mit {self.current_agent.upper()}")
        
        while True:
            try:
                # Input prompt
                prompt = input(f"\n[{self.current_agent}]> ").strip()
                
                if not prompt:
                    continue
                    
                # Handle commands
                if prompt.startswith('/'):
                    if prompt == '/exit':
                        print("\n👋 Auf Wiedersehen!")
                        break
                        
                    elif prompt.startswith('/switch'):
                        parts = prompt.split()
                        if len(parts) > 1:
                            self.switch_agent(parts[1])
                        else:
                            print("\n❌ Verwendung: /switch <1-4>")
                            
                    elif prompt == '/history':
                        self.show_history()
                        
                    elif prompt == '/clear':
                        print("\033[2J\033[H")  # Clear screen
                        self.show_header()
                        print(f"\n💬 Chatte mit {self.current_agent.upper()}")
                        
                    elif prompt == '/test':
                        self.test_all_agents()
                        
                    else:
                        print(f"\n❌ Unbekannter Befehl: {prompt}")
                        
                    continue
                
                # Send message to agent
                print(f"\n⏳ {self.current_agent} denkt nach...", end='', flush=True)
                start_time = time.time()
                
                response = self.comm.chat_with_agent(self.current_agent, prompt)
                elapsed = time.time() - start_time
                
                # Clear waiting message
                print(f"\r{' '*50}\r", end='')
                
                # Show response
                print(f"\n{self.current_agent.upper()} ({elapsed:.1f}s):")
                print("-"*40)
                print(response)
                
                # Save to history
                self.history.append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'agent': self.current_agent,
                    'message': prompt,
                    'response': response
                })
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat beendet!")
                break
            except Exception as e:
                print(f"\n❌ Fehler: {e}")


def main():
    """Starte Multi-Agent Chat"""
    chat = MultiAgentChat()
    
    # Optional: Quick test
    print("🔍 Prüfe Agent-Verfügbarkeit...")
    chat.test_all_agents()
    
    # Start chat
    chat.chat_loop()


if __name__ == "__main__":
    main()
