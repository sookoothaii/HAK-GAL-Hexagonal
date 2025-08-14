"""
WebSocket Adapter für Hexagonal Architecture - OPTIMIZED VERSION
================================================================
Nach HAK/GAL Verfassung: Real-time Communication Layer
Mit Performance-Optimierungen: Caching, Rate-Limiting, Connection Pooling
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Dict, Any, Optional
import json
import time
from threading import Thread, Lock
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

class RateLimiter:
    """Rate limiter for WebSocket events"""
    def __init__(self, max_requests: int = 10, window_seconds: int = 1):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        with self.lock:
            now = time.time()
            # Clean old requests
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if now - req_time < self.window_seconds
            ]
            
            if len(self.requests[client_id]) < self.max_requests:
                self.requests[client_id].append(now)
                return True
            return False

class CacheManager:
    """Simple cache manager with TTL"""
    def __init__(self):
        self.cache = {}
        self.lock = Lock()
    
    def get(self, key: str, ttl_seconds: int = 30) -> Optional[Any]:
        """Get cached value if not expired"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < ttl_seconds:
                    return value
                else:
                    del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set cached value with current timestamp"""
        with self.lock:
            self.cache[key] = (value, time.time())
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries matching pattern"""
        with self.lock:
            if pattern:
                keys_to_delete = [k for k in self.cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.cache[key]
            else:
                self.cache.clear()

class OptimizedWebSocketAdapter:
    """
    Optimized WebSocket Adapter with Performance Enhancements
    - Connection pooling and management
    - Rate limiting per client
    - Response caching
    - Batch updates
    - Throttled broadcasts
    """
    
    def __init__(self, app=None):
        self.socketio = None
        self.app = app
        self.connected_clients = {}  # client_id -> connection info
        self.fact_repository = None
        self.reasoning_engine = None
        
        # Performance optimizations
        self.rate_limiter = RateLimiter(max_requests=20, window_seconds=1)
        self.cache_manager = CacheManager()
        self.broadcast_lock = Lock()
        self.last_broadcast = {}  # event_name -> timestamp
        self.min_broadcast_interval = 0.5  # seconds between broadcasts
        
        # Connection pool management
        self.max_connections = 100
        self.connection_lock = Lock()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app, fact_repository=None, reasoning_engine=None):
        """Initialize WebSocket with Flask app"""
        self.app = app
        self.fact_repository = fact_repository
        self.reasoning_engine = reasoning_engine
        
        # Initialize Socket.IO with optimized settings
        async_mode = 'threading'
        try:
            import eventlet
            async_mode = 'eventlet'
            # Monkey patch for better performance
            eventlet.monkey_patch()
        except ImportError:
            pass
        
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode=async_mode,
            logger=False,  # Reduce logging overhead
            engineio_logger=False,
            ping_timeout=60,
            ping_interval=25,
            max_http_buffer_size=1000000,  # 1MB buffer
            compression_threshold=1024  # Compress messages > 1KB
        )
        
        self._register_handlers()
        self._start_background_tasks()
        
        print("[OK] Optimized WebSocket Adapter initialized")
        return self.socketio
    
    def _register_handlers(self):
        """Register WebSocket event handlers with optimizations"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection with connection pooling"""
            from flask import request
            client_id = request.sid
            
            with self.connection_lock:
                if len(self.connected_clients) >= self.max_connections:
                    # Reject connection if pool is full
                    emit('error', {'message': 'Connection pool full'})
                    return False
                
                self.connected_clients[client_id] = {
                    'connected_at': datetime.now(),
                    'last_activity': datetime.now(),
                    'request_count': 0
                }
            
            print(f"[CONNECT] Client {client_id[:8]}... (Total: {len(self.connected_clients)})")
            
            # Send cached initial status
            cached_status = self.cache_manager.get('initial_status', ttl_seconds=60)
            if not cached_status:
                cached_status = {
                    'connected': True,
                    'backend': 'hexagonal_optimized',
                    'port': 5001,
                    'timestamp': datetime.now().isoformat(),
                    'max_connections': self.max_connections,
                    'current_connections': len(self.connected_clients)
                }
                self.cache_manager.set('initial_status', cached_status)
            
            emit('connection_status', cached_status)
            
            # Send cached metrics
            self._emit_kb_metrics(use_cache=True)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            from flask import request
            client_id = request.sid
            
            with self.connection_lock:
                if client_id in self.connected_clients:
                    del self.connected_clients[client_id]
            
            print(f"[DISCONNECT] Client {client_id[:8]}... (Remaining: {len(self.connected_clients)})")
        
        @self.socketio.on('request_status')
        def handle_status_request():
            """Handle status request with rate limiting"""
            from flask import request
            client_id = request.sid
            
            if not self.rate_limiter.is_allowed(client_id):
                emit('error', {'message': 'Rate limit exceeded'})
                return
            
            self._emit_system_status(use_cache=True)
        
        @self.socketio.on('kb_metrics_request')
        def handle_kb_metrics_request():
            """Handle KB metrics request with caching"""
            from flask import request
            client_id = request.sid
            
            if not self.rate_limiter.is_allowed(client_id):
                emit('error', {'message': 'Rate limit exceeded'})
                return
            
            self._emit_kb_metrics(use_cache=True)
        
        @self.socketio.on('reasoning_request')
        def handle_reasoning(data):
            """Handle reasoning request with caching"""
            from flask import request
            client_id = request.sid
            
            if not self.rate_limiter.is_allowed(client_id):
                emit('error', {'message': 'Rate limit exceeded'})
                return
            
            query = data.get('query', '')
            
            # Check cache first
            query_hash = hashlib.md5(query.encode()).hexdigest()
            cache_key = f'reasoning_{query_hash}'
            cached_result = self.cache_manager.get(cache_key, ttl_seconds=300)  # 5 min cache
            
            if cached_result:
                emit('reasoning_result', {
                    **cached_result,
                    'cached': True,
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            # Compute if not cached
            if self.reasoning_engine:
                result = self.reasoning_engine.compute_confidence(query)
                
                response = {
                    'query': query,
                    'confidence': result.get('confidence', 0.0),
                    'reasoning_terms': result.get('reasoning_terms', []),
                    'device': result.get('device', 'unknown')
                }
                
                # Cache the result
                self.cache_manager.set(cache_key, response)
                
                emit('reasoning_result', {
                    **response,
                    'cached': False,
                    'timestamp': datetime.now().isoformat()
                })
    
    def _should_broadcast(self, event_name: str) -> bool:
        """Check if broadcast should be throttled"""
        with self.broadcast_lock:
            now = time.time()
            last_time = self.last_broadcast.get(event_name, 0)
            
            if now - last_time >= self.min_broadcast_interval:
                self.last_broadcast[event_name] = now
                return True
            return False
    
    def _emit_system_status(self, use_cache: bool = True):
        """Emit system status with caching"""
        if not self.fact_repository:
            return
        
        if use_cache:
            cached = self.cache_manager.get('system_status', ttl_seconds=5)
            if cached:
                self.socketio.emit('system_status', cached, to=None)
                return
        
        status = {
            'status': 'operational',
            'architecture': 'hexagonal_optimized',
            'fact_count': self.fact_repository.count(),
            'connected_clients': len(self.connected_clients),
            'cache_hits': len(self.cache_manager.cache),
            'timestamp': datetime.now().isoformat()
        }
        
        self.cache_manager.set('system_status', status)
        
        if self._should_broadcast('system_status'):
            self.socketio.emit('system_status', status, to=None)
    
    def _emit_kb_metrics(self, use_cache: bool = True):
        """Emit KB metrics with caching"""
        if not self.fact_repository:
            return
        
        if use_cache:
            cached = self.cache_manager.get('kb_metrics', ttl_seconds=10)
            if cached:
                self.socketio.emit('kb_update', cached, to=None)
                self.socketio.emit('kb_metrics', cached, to=None)
                return
        
        fact_count = self.fact_repository.count()
        
        metrics = {
            'fact_count': fact_count,
            'factCount': fact_count,  # Compatibility
            'vocabulary_size': 729,
            'categories': {
                'Types': 574,
                'Properties': 577,
                'Relationships': 600,
                'Other': max(0, fact_count - 1751)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.cache_manager.set('kb_metrics', metrics)
        
        if self._should_broadcast('kb_metrics'):
            self.socketio.emit('kb_update', metrics, to=None)
            self.socketio.emit('kb_metrics', metrics, to=None)
    
    def _start_background_tasks(self):
        """Start optimized background tasks"""
        
        def emit_batched_updates():
            """Emit batched updates periodically"""
            while True:
                time.sleep(5)  # Less frequent than original
                try:
                    if len(self.connected_clients) > 0:
                        # Only emit if clients connected
                        self._emit_kb_metrics(use_cache=True)
                        self._emit_system_status(use_cache=True)
                        
                        # Clean up stale connections
                        self._cleanup_stale_connections()
                        
                except Exception as e:
                    print(f"[ERROR] Background task: {e}")
        
        def _cleanup_stale_connections():
            """Remove inactive connections"""
            with self.connection_lock:
                now = datetime.now()
                stale_clients = []
                
                for client_id, info in self.connected_clients.items():
                    if now - info['last_activity'] > timedelta(minutes=5):
                        stale_clients.append(client_id)
                
                for client_id in stale_clients:
                    del self.connected_clients[client_id]
                    print(f"[CLEANUP] Removed stale client {client_id[:8]}...")
        
        # Start optimized background thread
        thread = Thread(target=emit_batched_updates, daemon=True)
        thread.start()
        print("[OK] Optimized background tasks started (5s interval)")
    
    def emit_fact_added(self, fact_statement: str, success: bool):
        """Emit fact added event and invalidate cache"""
        event = {
            'statement': fact_statement,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        # Invalidate relevant caches
        self.cache_manager.invalidate('kb_metrics')
        self.cache_manager.invalidate('system_status')
        
        if self._should_broadcast('fact_added'):
            self.socketio.emit('fact_added', event, to=None)
            # Force metrics update
            self._emit_kb_metrics(use_cache=False)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            'connected_clients': len(self.connected_clients),
            'cache_entries': len(self.cache_manager.cache),
            'rate_limited_clients': len(self.rate_limiter.requests),
            'max_connections': self.max_connections
        }

# Helper function for integration
def create_optimized_websocket_adapter(app, fact_repository=None, reasoning_engine=None):
    """Factory function to create optimized WebSocket adapter"""
    adapter = OptimizedWebSocketAdapter()
    socketio = adapter.init_app(app, fact_repository, reasoning_engine)
    return adapter, socketio