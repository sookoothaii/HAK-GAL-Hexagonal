"""
WebSocket Adapter für Hexagonal Architecture
============================================
Nach HAK/GAL Verfassung: Real-time Communication Layer
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Dict, Any, Optional
import json
import time
from threading import Thread
from datetime import datetime

class WebSocketAdapter:
    """
    WebSocket Adapter für Real-time Updates
    Kompatibel mit Original HAK-GAL Frontend
    """
    
    def __init__(self, app=None):
        self.socketio = None
        self.app = app
        self.connected_clients = set()
        self.fact_repository = None
        self.reasoning_engine = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app, fact_repository=None, reasoning_engine=None):
        """Initialize WebSocket with Flask app"""
        self.app = app
        self.fact_repository = fact_repository
        self.reasoning_engine = reasoning_engine
        
        # Initialize Socket.IO with CORS support
        # Prefer eventlet if available, else fallback to threading
        async_mode = 'threading'
        try:
            import eventlet  # noqa: F401
            async_mode = 'eventlet'
        except Exception:
            async_mode = 'threading'

        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode=async_mode,
            logger=True,
            engineio_logger=False
        )
        
        self._register_handlers()
        
        # Start background tasks
        self._start_background_tasks()
        
        print("✅ WebSocket Adapter initialized")
        return self.socketio
    
    def _register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid if 'request' in globals() else 'unknown'
            self.connected_clients.add(client_id)
            print(f"📱 Client connected: {client_id}")
            
            # Send initial status
            emit('connection_status', {
                'connected': True,
                'backend': 'hexagonal',
                'port': 5001,
                'timestamp': datetime.now().isoformat()
            })
            
            # Send current metrics
            self._emit_kb_metrics()
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid if 'request' in globals() else 'unknown'
            self.connected_clients.discard(client_id)
            print(f"📴 Client disconnected: {client_id}")
        
        @self.socketio.on('request_status')
        def handle_status_request():
            """Handle status request from frontend"""
            self._emit_system_status()
        
        @self.socketio.on('kb_metrics_request')
        def handle_kb_metrics_request():
            """Handle knowledge base metrics request"""
            self._emit_kb_metrics()
        
        @self.socketio.on('governor_status_request')
        def handle_governor_status():
            """Handle governor status request"""
            self._emit_governor_status()
        
        @self.socketio.on('reasoning_request')
        def handle_reasoning(data):
            """Handle reasoning request via WebSocket"""
            query = data.get('query', '')
            
            if self.reasoning_engine:
                result = self.reasoning_engine.compute_confidence(query)
                
                emit('reasoning_result', {
                    'query': query,
                    'confidence': result.get('confidence', 0.0),
                    'reasoning_terms': result.get('reasoning_terms', []),
                    'device': result.get('device', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                })
    
    def _emit_system_status(self):
        """Emit system status to all clients"""
        if not self.fact_repository:
            return
        
        status = {
            'status': 'operational',
            'architecture': 'hexagonal',
            'fact_count': self.fact_repository.count(),
            'connected_clients': len(self.connected_clients),
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('system_status', status, to=None)  # broadcast to all
    
    def _emit_kb_metrics(self):
        """Emit knowledge base metrics"""
        if not self.fact_repository:
            return
        
        fact_count = self.fact_repository.count()
        
        metrics = {
            'fact_count': fact_count,
            'factCount': fact_count,  # Compatibility with frontend
            'vocabulary_size': 729,  # From HRM
            'categories': {
                'Types': 574,
                'Properties': 577,
                'Relationships': 600,
                'Other': fact_count - 1751
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('kb_update', metrics, to=None)  # broadcast to all
        self.socketio.emit('kb_metrics', metrics, to=None)  # Dual emit for compatibility
    
    def _emit_governor_status(self):
        """Emit governor status (placeholder for now)"""
        status = {
            'running': False,
            'mode': 'disabled',
            'decisions_made': 0,
            'last_decision': None,
            'alpha': 1.0,
            'beta': 1.0,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('governor_update', status, to=None)  # broadcast to all
    
    def _emit_llm_status(self):
        """Emit LLM provider status"""
        providers = {
            'deepseek': {
                'status': 'online',
                'model': 'deepseek-chat',
                'tokens_used': 0
            },
            'gemini': {
                'status': 'online', 
                'model': 'gemini-1.5-pro-latest',
                'tokens_used': 0
            },
            'mistral': {
                'status': 'offline',
                'model': 'mistral-large-latest',
                'tokens_used': 0
            }
        }
        
        self.socketio.emit('llm_status', providers, to=None)  # broadcast to all
    
    def _start_background_tasks(self):
        """Start background tasks for periodic updates"""
        
        def emit_periodic_updates():
            """Emit updates every 3 seconds"""
            while True:
                time.sleep(3)
                try:
                    self._emit_kb_metrics()
                    self._emit_system_status()
                    
                    # Every 10 seconds, emit additional status
                    if int(time.time()) % 10 == 0:
                        self._emit_llm_status()
                        self._emit_governor_status()
                        
                except Exception as e:
                    print(f"Error in background task: {e}")
        
        # Start background thread
        # DISABLED: Too much log spam - Option 1 as requested
        # thread = Thread(target=emit_periodic_updates, daemon=True)
        # thread.start()
        print("✅ Background update tasks DISABLED (manual updates only)")
    
    def emit_fact_added(self, fact_statement: str, success: bool):
        """Emit event when fact is added"""
        event = {
            'statement': fact_statement,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('fact_added', event, to=None)  # broadcast to all
        
        # Also update metrics
        self._emit_kb_metrics()
    
    def emit_reasoning_complete(self, query: str, confidence: float, duration_ms: float):
        """Emit event when reasoning completes"""
        event = {
            'query': query,
            'confidence': confidence,
            'duration_ms': duration_ms,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('reasoning_complete', event, to=None)  # broadcast to all

# Helper function for integration
def create_websocket_adapter(app, fact_repository=None, reasoning_engine=None):
    """Factory function to create WebSocket adapter"""
    adapter = WebSocketAdapter()
    socketio = adapter.init_app(app, fact_repository, reasoning_engine)
    return adapter, socketio
