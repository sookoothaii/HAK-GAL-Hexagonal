"""
WebSocket Bridge for Real-Time Agent Communication
Ermöglicht echte bidirektionale Echtzeit-Kommunikation
"""
import asyncio
import websockets
import json
import requests
from datetime import datetime
import threading
import queue
from pathlib import Path

class WebSocketBridge:
    """WebSocket Bridge für Echtzeit-Kommunikation"""
    
    def __init__(self, port=8765):
        self.port = port
        self.clients = set()
        self.agent_responses = {}
        self.response_queue = queue.Queue()
        self.api_base = "http://127.0.0.1:5002"
        self.api_key = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
        
    async def handler(self, websocket, path):
        """Handle WebSocket connections"""
        self.clients.add(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_message(data, websocket)
        finally:
            self.clients.remove(websocket)
    
    async def process_message(self, data, websocket):
        """Process incoming WebSocket messages"""
        msg_type = data.get('type')
        
        if msg_type == 'agent_request':
            # Claude sendet Request an anderen Agent
            task_id = await self.delegate_to_agent(data)
            await websocket.send(json.dumps({
                'type': 'request_sent',
                'task_id': task_id,
                'agent': data.get('agent')
            }))
            
            # Warte auf Response
            response = await self.wait_for_response(task_id, data.get('agent'))
            await websocket.send(json.dumps({
                'type': 'agent_response',
                'task_id': task_id,
                'response': response
            }))
            
        elif msg_type == 'agent_response':
            # Agent sendet Response zurück
            task_id = data.get('task_id')
            self.agent_responses[task_id] = data.get('response')
    
    async def delegate_to_agent(self, data):
        """Delegate task to agent via API"""
        agent = data.get('agent')
        message = data.get('message')
        
        response = requests.post(
            f"{self.api_base}/api/agent-bus/delegate",
            headers={"X-API-Key": self.api_key},
            json={
                "target_agent": agent,
                "task_description": message,
                "context": {
                    "websocket_bridge": True,
                    "sender": "claude",
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
        if response.status_code == 200:
            return response.json().get('task_id')
        return None
    
    async def wait_for_response(self, task_id, agent, timeout=30):
        """Wait for agent response"""
        for _ in range(timeout):
            # Check if response arrived via WebSocket
            if task_id in self.agent_responses:
                return self.agent_responses.pop(task_id)
            
            # Check file system
            response = self.check_filesystem_response(task_id, agent)
            if response:
                return response
            
            await asyncio.sleep(1)
        
        return {"error": "Timeout waiting for response"}
    
    def check_filesystem_response(self, task_id, agent):
        """Check filesystem for agent response"""
        response_dir = Path("agent_responses")
        
        # Check for response files
        for file in response_dir.rglob(f"*{task_id}*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('task_id') == task_id:
                    response = data.get('response', {})
                    if response.get('status') == 'completed':
                        return response.get('result')
            except:
                pass
        
        return None
    
    def start(self):
        """Start WebSocket server"""
        print(f"🌐 WebSocket Bridge läuft auf ws://localhost:{self.port}")
        start_server = websockets.serve(self.handler, "localhost", self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


# Client für Claude
class ClaudeWebSocketClient:
    """WebSocket Client für Claude"""
    
    def __init__(self, uri="ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
        
    async def connect(self):
        """Connect to WebSocket server"""
        self.websocket = await websockets.connect(self.uri)
        
    async def send_to_agent(self, agent, message):
        """Send message to agent and wait for response"""
        if not self.websocket:
            await self.connect()
        
        # Send request
        await self.websocket.send(json.dumps({
            'type': 'agent_request',
            'agent': agent,
            'message': message
        }))
        
        # Wait for responses
        while True:
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data['type'] == 'agent_response':
                return data['response']
            elif data['type'] == 'request_sent':
                print(f"✅ Request sent to {agent}, task_id: {data['task_id']}")
    
    async def chat(self, agent, message):
        """High-level chat interface"""
        try:
            response = await self.send_to_agent(agent, message)
            return response
        except Exception as e:
            return f"Error: {str(e)}"


# Test function
async def test_websocket_communication():
    """Test WebSocket communication"""
    
    client = ClaudeWebSocketClient()
    await client.connect()
    
    print("="*80)
    print("🚀 WEBSOCKET REAL-TIME COMMUNICATION TEST")
    print("="*80)
    
    # Test Gemini
    print("\n📡 Teste Gemini...")
    response = await client.chat(
        "gemini",
        "WEBSOCKET TEST: Antworte mit 'GEMINI via WebSocket - Echtzeit funktioniert!'"
    )
    print(f"GEMINI: {response}")
    
    # Test Claude CLI
    print("\n📡 Teste Claude CLI...")
    response = await client.chat(
        "claude_cli",
        "WEBSOCKET TEST: Sage 'CLAUDE CLI via WebSocket - Bidirektional OK!'"
    )
    print(f"CLAUDE CLI: {response}")
    
    print("\n✅ WebSocket Test abgeschlossen!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # Start WebSocket server
        bridge = WebSocketBridge()
        bridge.start()
    else:
        # Run test client
        asyncio.run(test_websocket_communication())
