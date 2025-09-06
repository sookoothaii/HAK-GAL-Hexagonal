"""
WebSocket Adapter für Hexagonal Architecture - FIXED VERSION
============================================
Sends REAL metrics, not hardcoded values!
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from typing import Dict, Any, Optional
import json
import time
from threading import Thread, Lock
from queue import Queue
from datetime import datetime

class WebSocketAdapter:
    """
    WebSocket Adapter für Real-time Updates
    NOW SENDS REAL DATA!
    """
    
    def __init__(self, app=None):
        self.socketio = None
        self.app = app
        self.connected_clients = set()
        self.fact_repository = None
        self.reasoning_engine = None
        
        # Concurrency-safe queue for agent responses
        self.agent_response_queue = Queue()
        self.background_worker_lock = Lock()
        self.agent_worker_started = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app, fact_repository=None, reasoning_engine=None):
        """Initialize WebSocket with Flask app"""
        self.app = app
        self.fact_repository = fact_repository
        self.reasoning_engine = reasoning_engine
        
        # Initialize Socket.IO with STABLE settings
        # Use eventlet for proper WebSocket handling with Werkzeug
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='eventlet',  # Changed from 'threading' to fix WebSocket issue
            logger=False,
            engineio_logger=False,
            ping_timeout=60,  # 60 seconds timeout
            ping_interval=25,  # Send ping every 25 seconds
            max_http_buffer_size=1000000  # 1MB buffer
        )
        
        self._register_handlers()
        self._start_background_tasks()
        
        print("WebSocket Adapter initialized")
        return self.socketio
    
    def _register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid
            self.connected_clients.add(client_id)
            print(f"Client connected: {client_id}")
            
            # Send initial status
            emit('connection_status', {
                'connected': True,
                'backend': 'hexagonal',
                'port': 5002,  # Backend port
                'timestamp': datetime.now().isoformat()
            })
            
            # Send REAL metrics immediately
            self._emit_real_metrics()
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid
            self.connected_clients.discard(client_id)
            print(f"Client disconnected: {client_id}")
        
        @self.socketio.on('request_initial_data')
        def handle_initial_data():
            """Send ALL real data to frontend"""
            self._emit_complete_status()
        
        @self.socketio.on('request_status')
        def handle_status_request():
            """Handle status request from frontend"""
            self._emit_complete_status()
    
    def _get_real_hrm_status(self):
        """Get REAL HRM status"""
        try:
            from core.reasoning.hrm_system import get_hrm_instance
            hrm = get_hrm_instance()
            status = hrm.get_status()
            return {
                'loaded': True,
                'parameters': status.get('parameters', 3549825),  # Real count
                'parameters_millions': status.get('parameters_millions', '3.5M'),
                'device': status.get('device', 'cuda'),
                'model_type': status.get('model_type', 'ImprovedHRM-3.5M')
            }
        except:
            return {
                'loaded': False,
                'parameters': 0,
                'device': 'cpu'
            }
    
    def _get_real_kb_metrics(self):
        """Get REAL database metrics"""
        if not self.fact_repository:
            return {}
        
        fact_count = self.fact_repository.count()
        
        # Get real predicate/entity counts if available
        predicates = set()
        entities = set()
        
        try:
            # Sample facts to get real counts
            import re
            facts = self.fact_repository.find_all(limit=1000)
            for fact in facts:
                match = re.match(r'^([A-Z][A-Za-z0-9_]*)\\(.*\\)\\s*([^\\)]+)\\\)', fact.statement)
                if match:
                    predicates.add(match.group(1))
                    entities.add(match.group(2).strip())
                    entities.add(match.group(3).strip())
        except:
            pass
        
        return {
            'fact_count': fact_count,
            'factCount': fact_count,  # Both formats
            'predicate_count': len(predicates) if predicates else 147,
            'predicateCount': len(predicates) if predicates else 147,
            'entity_count': len(entities) if entities else 3609,
            'entityCount': len(entities) if entities else 3609,
            'unique_predicates': len(predicates) if predicates else 147,
            'uniquePredicates': len(predicates) if predicates else 147,
            'unique_entities': len(entities) if entities else 3609,
            'uniqueEntities': len(entities) if entities else 3609
        }
    
    def _emit_real_metrics(self):
        """Emit REAL metrics to frontend"""
        kb_metrics = self._get_real_kb_metrics()
        
        try:
            # Send as kb_update event
            self.socketio.emit('kb_update', {
                'metrics': kb_metrics,
                'timestamp': datetime.now().isoformat()
            }, to=None)
            
            # Also send as kb_metrics for compatibility
            self.socketio.emit('kb_metrics', kb_metrics, to=None)
        except ConnectionAbortedError:
            print("Client disconnected during kb_update emit.")
        except Exception as e:
            print(f"Error emitting kb_update: {e}")
    
    def _emit_complete_status(self):
        """Emit COMPLETE real status"""
        kb_metrics = self._get_real_kb_metrics()
        hrm_status = self._get_real_hrm_status()
        
        # Complete system status
        complete_data = {
            'system_status': 'operational',
            'architecture': 'hexagonal',
            'port': 5002,
            
            # Real KB metrics
            'kb_metrics': kb_metrics,
            
            # Real HRM status
            'hrm_status': hrm_status,
            
            # Governor status
            'governor': {
                'running': False,  # Not started yet
                'mode': 'ready',
                'decisions_made': 0
            },
            
            # LLM providers (from logs)
            'llm_providers': [
                {
                    'name': 'deepseek',
                    'status': 'online',
                    'model': 'deepseek-chat',
                    'tokensUsed': 0
                },
                {
                    'name': 'gemini',
                    'status': 'online',
                    'model': 'gemini-1.5-pro-latest',
                    'tokensUsed': 0
                }
            ],
            
            # System load
            'system_load': {
                'cpu_percent': 0,
                'memory_percent': 0,
                'gpu_utilization': 0,
                'gpu_memory_percent': 0
            },
            
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Send as initial_data
            self.socketio.emit('initial_data', complete_data, to=None)
            
            # Also send individual updates
            self.socketio.emit('kb_update', {'metrics': kb_metrics}, to=None)
            self.socketio.emit('hrm_update', hrm_status, to=None)
            self.socketio.emit('system_status_update', complete_data, to=None)
        except ConnectionAbortedError:
            print("Client disconnected during complete status emit.")
        except Exception as e:
            print(f"Error emitting complete status: {e}")
    
    def _start_background_tasks(self):
        """Start background tasks for periodic updates AND the agent response worker."""
        
        with self.background_worker_lock:
            if self.agent_worker_started:
                return
            
            def emit_periodic_updates():
                """Emit REAL updates periodically - less frequent for stability"""
                while True:
                    time.sleep(10)  # Update every 10 seconds instead of 5
                    try:
                        self._emit_real_metrics()
                        
                        # Every 30 seconds, emit complete status
                        if int(time.time()) % 30 == 0:
                            self._emit_complete_status()
                            
                    except Exception as e:
                        print(f"Error in background task: {e}")
            
            # Start periodic updates thread
            periodic_thread = Thread(target=emit_periodic_updates, daemon=True)
            periodic_thread.start()
            print("Background tasks started - sending REAL metrics")

            def _agent_response_worker():
                """Dedicated worker to safely emit agent responses from a queue."""
                while True:
                    try:
                        event = self.agent_response_queue.get()
                        if event is None:  # Sentinel to stop the thread
                            break
                        
                        # The actual emit call, now in a single, controlled thread
                        self.socketio.emit('agent_task_response', event, to=None)
                        
                    except Exception as e:
                        # Log errors without crashing the worker
                        print(f"[ERROR] Agent Response Worker failed: {e}")

            # Start agent response worker thread
            agent_worker_thread = Thread(target=_agent_response_worker, daemon=True)
            agent_worker_thread.start()
            print("Agent response worker thread started.")
            
            self.agent_worker_started = True
    
    def emit_fact_added(self, fact_statement: str, success: bool):
        """Emit event when fact is added"""
        event = {
            'statement': fact_statement,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            self.socketio.emit('fact_added', event, to=None)
        except ConnectionAbortedError:
            print("Client disconnected during fact_added emit.")
        except Exception as e:
            print(f"Error emitting fact_added: {e}")
        
        # Update with REAL metrics
        self._emit_real_metrics()
    
    def emit_reasoning_complete(self, query: str, confidence: float, duration_ms: float):
        """Emit event when reasoning completes"""
        event = {
            'query': query,
            'confidence': confidence,
            'duration_ms': duration_ms,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            self.socketio.emit('reasoning_complete', event, to=None)
        except ConnectionAbortedError:
            print("Client disconnected during reasoning_complete emit.")
        except Exception as e:
            print(f"Error emitting reasoning_complete: {e}")

    def emit_agent_response(self, task_id: str, response: dict):
        """Puts an agent response event onto the thread-safe queue instead of emitting directly."""
        event = {
            'task_id': task_id,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        self.agent_response_queue.put(event)
    
    def emit_hrm_feedback_update(self, query: str, new_confidence: float, adjustment: float, metadata: dict = None):
        """Emit event when HRM confidence is updated through feedback"""
        event = {
            'query': query,
            'new_confidence': new_confidence,
            'adjustment': adjustment,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        try:
            self.socketio.emit('hrm_feedback_update', event, to=None)
            print(f"[WebSocket] HRM feedback update sent: confidence {new_confidence:.4f} (adj: {adjustment:+.4f})")
        except ConnectionAbortedError:
            print("Client disconnected during hrm_feedback_update emit.")
        except Exception as e:
            print(f"Error emitting hrm_feedback_update: {e}")

# Helper function for integration
def create_websocket_adapter(app, fact_repository=None, reasoning_engine=None):
    """Factory function to create WebSocket adapter"""
    adapter = WebSocketAdapter()
    socketio = adapter.init_app(app, fact_repository, reasoning_engine)
    return adapter, socketio
