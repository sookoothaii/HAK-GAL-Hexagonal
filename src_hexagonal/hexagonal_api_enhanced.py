# FIXED VERSION - No import of non-existent module
"""
REST API Adapter with WebSocket, Governor & Sentry - Enhanced Flask Application
==============================================================================
Nach HAK/GAL Verfassung: Complete Hexagonal Architecture Implementation
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, Any, Optional
import sys
import os
import time
from pathlib import Path
import subprocess
from datetime import datetime, timezone
import json
import re
import shutil

# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from application.services import FactManagementService, ReasoningService
from application.policy_guard import PolicyGuard
from application.kill_switch import KillSwitch
from adapters.legacy_adapters import LegacyFactRepository, LegacyReasoningEngine
from adapters.native_adapters import NativeReasoningEngine
from adapters.sqlite_adapter import SQLiteFactRepository
from adapters.websocket_adapter import create_websocket_adapter
from adapters.governor_adapter import get_governor_adapter
from core.domain.entities import Query
from adapters.hrm_feedback_adapter import HRMFeedbackAdapter
from adapters.hrm_feedback_endpoints import register_hrm_feedback_routes
from adapters.llm_providers import get_llm_provider


# Import infrastructure if available
try:
    from infrastructure.sentry_monitoring import SentryMonitoring
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    print("⚠️ Sentry not available - monitoring disabled")

class HexagonalAPI:
    """
    Enhanced REST API Adapter with WebSocket, Governor & Monitoring
    Complete implementation of Hexagonal Architecture
    """
    
    def __init__(self, use_legacy: bool = True, enable_websocket: bool = True, 
                 enable_governor: bool = True, enable_sentry: bool = False):
        self.app = Flask(__name__)
        # Enable permissive CORS for local dev (Frontend on 5173)
        CORS(
            self.app,
            resources={r"/*": {"origins": "*"}},
            supports_credentials=True,
            expose_headers=["*"],
            allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
            methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        )
        
        # Paths setup
        self.hex_root = Path(__file__).resolve().parents[1]
        self.suite_root = (self.hex_root.parent / 'HAK_GAL_SUITE')
        self.graph_public_path = self.suite_root / 'frontend_new' / 'public' / 'knowledge_graph.html'
        self.emergency_generator_path = self.suite_root / 'emergency_graph_generator.py'

        # Load environment
        try:
            env_path = self.suite_root / '.env'
            if env_path.exists():
                try:
                    from dotenv import load_dotenv
                    load_dotenv(dotenv_path=str(env_path), override=False)
                    print(f"[ENV] Loaded environment from {env_path}")
                except Exception:
                    # Manual parser fallback
                    for line in env_path.read_text(encoding='utf-8', errors='ignore').splitlines():
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if line.lower().startswith('export '):
                            line = line[7:].strip()
                        if '=' in line:
                            key, val = line.split('=', 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key and key not in os.environ:
                                os.environ[key] = val
                    print(f"[ENV] Loaded environment (manual) from {env_path}")
        except Exception as e:
            print(f"[ENV] Failed to load .env: {e}")

        # Dependency Injection - Choose Repository Implementation
        if use_legacy:
            print("[INFO] Using Legacy Adapters (Original HAK-GAL)")
            self.fact_repository = LegacyFactRepository()
            self.reasoning_engine = LegacyReasoningEngine()
        else:
            # Modern SQLite adapter
            try:
                print("[INFO] Using SQLite Adapter (hexagonal_kb.db)")
                self.fact_repository = SQLiteFactRepository()
            except Exception as e:
                print(f"[WARN] SQLite adapter error ({e}), attempting JSONL fallback")
                try:
                    from adapters.jsonl_adapter import JsonlFactRepository
                    print("[INFO] Using JSONL Adapter (data/k_assistant.kb.jsonl) [FALLBACK]")
                    self.fact_repository = JsonlFactRepository()
                except Exception as e2:
                    raise RuntimeError(f"No available repository adapters (SQLite/JSONL). Errors: {e} / {e2}")
            self.reasoning_engine = NativeReasoningEngine()
        
        # Initialize Application Services
        self.fact_service = FactManagementService(
            fact_repository=self.fact_repository,
            reasoning_engine=self.reasoning_engine
        )
        
        self.reasoning_service = ReasoningService(
            reasoning_engine=self.reasoning_engine,
            fact_repository=self.fact_repository
        )

        # Initialize Policy Guard and Kill Switch
        self.policy_guard = PolicyGuard()
        self.kill_switch = KillSwitch()
        
        # Initialize WebSocket Support
        self.websocket_adapter = None
        self.socketio = None
        if enable_websocket:
            self.websocket_adapter, self.socketio = create_websocket_adapter(
                self.app, 
                self.fact_repository, 
                self.reasoning_engine
            )
            print("[OK] WebSocket Support enabled")
        
        # Initialize Governor
        self.governor = None
        if enable_governor:
            self.governor = get_governor_adapter()
            print("[OK] Governor initialized (not started - use Frontend to control)")
        
        # Initialize Sentry Monitoring
        self.monitoring = None
        if enable_sentry and SENTRY_AVAILABLE:
            tentative_monitor = SentryMonitoring()
            if tentative_monitor.initialize(self.app):
                self.monitoring = tentative_monitor
                print("[OK] Sentry Monitoring enabled")
            else:
                self.monitoring = None
        
        # Graph configuration state
        self.graph_config: Dict[str, Any] = {
            'auto_update': False,
            'update_interval': 30,
            'last_update': None,
        }

        # Simple in-memory cache
        self._cache: Dict[str, Dict[str, Any]] = {}

        # Mojo adapter
        try:
            from adapters.mojo_kernels_adapter import MojoKernelsAdapter
            self.mojo = MojoKernelsAdapter()
        except Exception:
            self.mojo = None

        # Initialize HRM Feedback Adapter
        self.hrm_feedback = HRMFeedbackAdapter()
        print("[OK] HRM Feedback Learning enabled")

        # Register Routes
        self._register_routes()
        
        # Register HRM Feedback Routes
        if hasattr(self, 'hrm_feedback'):
            register_hrm_feedback_routes(self.app, self.hrm_feedback, self.reasoning_service)
            print("[OK] HRM Feedback endpoints registered")

        self._register_governor_routes()
        self._register_websocket_routes()
        
        # CORS headers on every response
        @self.app.after_request
        def add_cors_headers(response):
            try:
                origin = request.headers.get('Origin', '*')
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Vary'] = 'Origin'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            except Exception:
                pass
            return response
    
    def _register_routes(self):
        """Register all REST endpoints"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health Check"""
            caps = {
                'max_sample_limit': int(os.environ.get('MAX_SAMPLE_LIMIT', '5000')),
                'max_top_k': int(os.environ.get('MAX_TOP_K', '200')),
                'min_threshold': 0.0,
                'max_threshold': 1.0,
            }
            read_only_backend = not (str(os.environ.get('HAKGAL_WRITE_ENABLED', 'false')).lower() == 'true')
            return jsonify({
                'status': 'operational',
                'architecture': 'hexagonal',
                'port': int(os.environ.get('HAKGAL_PORT', '5002')),
                'repository': self.fact_repository.__class__.__name__,
                'read_only': read_only_backend,
                'caps': caps
            })
        
        @self.app.route('/api/status', methods=['GET'])
        def status():
            """System Status"""
            base_status = self.fact_service.get_system_status()
            if request.args.get('light') in ('1', 'true', 'True'):
                return jsonify({
                    'architecture': base_status.get('architecture', 'hexagonal'),
                    'status': base_status.get('status', 'operational')
                })
            
            if self.governor:
                base_status['governor'] = self.governor.get_status()
            
            if self.websocket_adapter:
                base_status['websocket'] = {
                    'enabled': True,
                    'connected_clients': len(self.websocket_adapter.connected_clients)
                }
            
            return jsonify(base_status)

        @self.app.route('/api/facts', methods=['GET'])
        def get_facts():
            """Get all facts"""
            limit = request.args.get('limit', 100, type=int)
            facts = self.fact_service.get_all_facts(limit)
            
            return jsonify({
                'facts': [f.to_dict() for f in facts],
                'count': len(facts),
                'total': self.fact_repository.count()
            })
        
        @self.app.route('/api/facts', methods=['POST'])
        def add_fact():
            """Add new fact"""
            data = request.get_json(silent=True) or {}

            if self.kill_switch.is_safe():
                return jsonify({
                    'error': 'Kill-switch SAFE mode active. Write operations are disabled.',
                    'kill_switch': self.kill_switch.state()
                }), 503

            statement = (data.get('statement') or data.get('query') or data.get('fact') or '').strip()
            if not statement:
                return jsonify({'error': 'Missing statement'}), 400

            if not statement.endswith('.'):
                statement = statement + '.'

            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.$", statement):
                return jsonify({'error': 'Invalid fact format. Expected Predicate(Entity1, Entity2).'}), 400

            context = data.get('context', {})

            decision = self.policy_guard.check(
                action='write_add_fact',
                context={'statement': statement, 'sensitivity': 'write'},
                externally_legal=True,
                sensitivity='write'
            )
            if self.policy_guard.should_block(decision, sensitivity='write'):
                resp = jsonify({'error': 'Policy denied', 'policy': decision})
                resp.headers['X-Policy-Version'] = decision.get('policy_version', 'unknown')
                resp.headers['X-Decision-Id'] = decision.get('decision_id', '')
                return resp, 403

            success, message = self.fact_service.add_fact(statement, context)
            
            if self.websocket_adapter:
                self.websocket_adapter.emit_fact_added(statement, success)
            
            if self.monitoring:
                SentryMonitoring.capture_fact_added(statement, success)
            
            status_code = 201 if success else (409 if isinstance(message, str) and 'exists' in message.lower() else 422)
            response = {
                'success': success,
                'message': message,
                'statement': statement
            }
            response['policy'] = decision
            resp = jsonify(response)
            resp.headers['X-Policy-Version'] = decision.get('policy_version', 'unknown')
            resp.headers['X-Decision-Id'] = decision.get('decision_id', '')
            return resp, status_code

        @self.app.route('/api/facts/count', methods=['GET'])
        def facts_count():
            """Get facts count with 30s TTL cache"""
            now_ts = time.time()
            cached = self._cache.get('facts_count')
            if cached and (now_ts - cached.get('ts', 0) <= 30):
                return jsonify({'count': cached['value'], 'cached': True, 'ttl_sec': 30 - int(now_ts - cached['ts'])})

            try:
                count_val = int(self.fact_repository.count())
            except Exception:
                count_val = None

            self._cache['facts_count'] = {'value': count_val, 'ts': now_ts}
            return jsonify({'count': count_val, 'cached': False, 'ttl_sec': 30})

        @self.app.route('/api/search', methods=['POST', 'OPTIONS'])
        def search_facts():
            """Search facts"""
            if request.method == 'OPTIONS':
                return ('', 204)
            data = request.get_json()
            
            if not data or 'query' not in data:
                return jsonify({'error': 'Missing query'}), 400
            
            query = Query(
                text=data['query'],
                limit=data.get('limit', 10),
                min_confidence=data.get('min_confidence', 0.5)
            )
            
            facts = self.fact_service.search_facts(query)
            
            return jsonify({
                'query': query.text,
                'results': [f.to_dict() for f in facts],
                'count': len(facts)
            })
        
        @self.app.route('/api/reason', methods=['POST', 'OPTIONS'])
        def reason():
            """Reasoning endpoint"""
            if request.method == 'OPTIONS':
                return ('', 204)
            data = request.get_json()
            
            if not data or 'query' not in data:
                return jsonify({'error': 'Missing query'}), 400
            
            query = data['query']
            start_time = time.time()
            
            result = self.reasoning_service.reason(query)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if self.websocket_adapter:
                self.websocket_adapter.emit_reasoning_complete(
                    query, result.confidence, duration_ms
                )
            
            if self.monitoring:
                SentryMonitoring.capture_reasoning_performance(
                    query, result.confidence, duration_ms
                )
            
            response = {
                'query': result.query,
                'confidence': result.confidence,
                'reasoning_terms': result.reasoning_terms,
                'success': result.success,
                'high_confidence': result.is_high_confidence(),
                'duration_ms': duration_ms
            }
            
            if result.metadata and 'device' in result.metadata:
                response['device'] = result.metadata['device']
            
            return jsonify(response)

        @self.app.route('/api/llm/get-explanation', methods=['POST', 'OPTIONS'])
        def get_llm_explanation():
            """Get deep LLM explanation for a topic"""
            if request.method == 'OPTIONS':
                return ('', 204)
            
            data = request.get_json(silent=True) or {}
            topic = data.get('topic', '').strip()
            context_facts = data.get('context_facts', [])
            
            if not topic:
                return jsonify({'error': 'Missing topic'}), 400
            
            # Create prompt for LLM
            prompt = f"""Explain the following topic in detail: {topic}

"""
            
            if context_facts:
                prompt += f"Context from knowledge base:\n"
                for fact in context_facts[:10]:  # Limit to first 10 facts
                    prompt += f"- {fact}\n"
                prompt += "\n"
            
            prompt += """Please provide:
1. A comprehensive explanation
2. Key relationships and concepts
3. Any logical facts that could be derived (in format: Predicate(Entity1, Entity2))

Provide suggested facts in the format: Predicate(Entity1, Entity2)
"""
            
            # Get LLM response
            try:
                llm_provider = get_llm_provider()
                if not llm_provider.is_available():
                    return jsonify({
                        'error': 'No LLM provider available',
                        'explanation': 'LLM service is not configured. Please check API keys.'
                    }), 503
                
                explanation = llm_provider.generate_response(prompt)
                
                # Extract suggested facts from explanation
                suggested_facts = []
                import re
                fact_patterns = re.findall(r'\b[A-Z]\w*\([^)]+\)', explanation)
                
                for pattern in fact_patterns[:20]:  # Limit to 20 suggestions
                    fact = pattern.strip()
                    if not fact.endswith('.'):
                        fact += '.'
                    suggested_facts.append({
                        'fact': fact,
                        'confidence': 0.7,
                        'source': 'LLM'
                    })
                
                # Also check if the topic itself is a valid fact
                if re.match(r'^\w+\([^)]+\)$', topic):
                    topic_fact = topic if topic.endswith('.') else topic + '.'
                    if not any(s['fact'] == topic_fact for s in suggested_facts):
                        suggested_facts.insert(0, {
                            'fact': topic_fact,
                            'confidence': 0.8,
                            'source': 'User Query'
                        })
                
                return jsonify({
                    'success': True,
                    'explanation': explanation,
                    'suggested_facts': suggested_facts,
                    'topic': topic,
                    'context_facts_used': len(context_facts)
                })
                
            except Exception as e:
                print(f"[LLM] Error getting explanation: {e}")
                return jsonify({
                    'error': 'Failed to generate explanation',
                    'message': str(e),
                    'explanation': 'An error occurred while generating the explanation.'
                }), 500

        @self.app.route('/api/command', methods=['POST', 'OPTIONS'])
        def command():
            """Legacy command endpoint for compatibility"""
            if request.method == 'OPTIONS':
                return ('', 204)
            
            data = request.get_json(silent=True) or {}
            command = data.get('command', '')
            query = data.get('query', '')
            
            if command == 'add_fact':
                # Redirect to facts endpoint
                return add_fact()
            elif command == 'explain':
                # Redirect to LLM explanation
                data['topic'] = query
                return get_llm_explanation()
            else:
                return jsonify({'error': f'Unknown command: {command}'}), 400

        @self.app.route('/api/logicalize', methods=['POST', 'OPTIONS'])
        def logicalize():
            """Extract logical facts from text"""
            if request.method == 'OPTIONS':
                return ('', 204)
            
            data = request.get_json(silent=True) or {}
            text = data.get('text', '').strip()
            
            if not text:
                return jsonify({'facts': []})
            
            # Simple extraction of predicate-like patterns
            import re
            facts = []
            patterns = re.findall(r'\b[A-Z]\w*\([^)]+\)', text)
            
            for pattern in patterns:
                fact = pattern.strip()
                if not fact.endswith('.'):
                    fact += '.'
                facts.append(fact)
            
            return jsonify({'facts': facts})

        @self.app.route('/api/architecture', methods=['GET'])
        def architecture():
            """Architecture Information"""
            return jsonify({
                'pattern': 'Hexagonal Architecture',
                'version': '2.0',
                'features': {
                    'core': 'Domain-Driven Design',
                    'websocket': self.websocket_adapter is not None,
                    'governor': self.governor is not None,
                    'monitoring': self.monitoring is not None,
                    'cuda': True,
                    'llm': True
                }
            })

        # Catch-all OPTIONS handler
        @self.app.route('/<path:any_path>', methods=['OPTIONS'])
        def cors_preflight(any_path):
            return ('', 204)

    def _register_governor_routes(self):
        """Register Governor-specific routes"""
        if not self.governor:
            return
        
        @self.app.route('/api/governor/status', methods=['GET'])
        def governor_status():
            return jsonify(self.governor.get_status())
        
        @self.app.route('/api/governor/start', methods=['POST'])
        def governor_start():
            success = self.governor.start()
            
            # CRITICAL FIX: Send WebSocket update to frontend
            if success and self.websocket_adapter:
                governor_status = self.governor.get_status()
                print(f"🔥 [GOVERNOR] Broadcasting status update: {governor_status}")
                self.websocket_adapter.socketio.emit('governor_update', governor_status, to=None)
            
            return jsonify({'success': success})
        
        @self.app.route('/api/governor/stop', methods=['POST'])
        def governor_stop():
            success = self.governor.stop()
            
            # CRITICAL FIX: Send WebSocket update to frontend
            if success and self.websocket_adapter:
                governor_status = self.governor.get_status()
                print(f"🛑 [GOVERNOR] Broadcasting stop status: {governor_status}")
                self.websocket_adapter.socketio.emit('governor_update', governor_status, to=None)
            
            return jsonify({'success': success})
    
    def _register_websocket_routes(self):
        """Register WebSocket-specific routes"""
        if not self.socketio:
            return
        
        @self.socketio.on('governor_control')
        def handle_governor_control(data):
            if not self.governor:
                return {'error': 'Governor not enabled'}
            
            action = data.get('action')
            success = False
            
            if action == 'start':
                success = self.governor.start()
                print(f"🔥 [WebSocket] Governor start: {success}")
            elif action == 'stop':
                success = self.governor.stop()
                print(f"🛑 [WebSocket] Governor stop: {success}")
            
            # Always send status update
            status = self.governor.get_status()
            print(f"📡 [WebSocket] Broadcasting governor status: {status}")
            self.socketio.emit('governor_update', status, to=None)
            
            return {'success': success, 'status': status}
    
    def run(self, host='127.0.0.1', port=5002, debug=True):
        """Start the application"""
        print("=" * 60)
        print("🎯 HAK-GAL HEXAGONAL ARCHITECTURE v2.0")
        print("=" * 60)
        print(f"[START] Starting on http://{host}:{port}")
        print(f"📦 Repository: {self.fact_repository.__class__.__name__}")
        print(f"🧠 Reasoning: {self.reasoning_engine.__class__.__name__}")
        print(f"🔌 WebSocket: {'Enabled' if self.websocket_adapter else 'Disabled'}")
        print(f"[INFO] Governor: {'Enabled' if self.governor else 'Disabled'}")
        print(f"[INFO] Monitoring: {'Enabled' if self.monitoring else 'Disabled'}")
        print("=" * 60)
        
        if self.socketio:
            self.socketio.run(self.app, host=host, port=port, debug=debug, use_reloader=False)
        else:
            self.app.run(host=host, port=port, debug=debug)

def create_app(use_legacy=True, enable_all=True):
    """Factory Function für App Creation"""
    enable_sentry = bool(os.environ.get('SENTRY_DSN'))
    return HexagonalAPI(
        use_legacy=use_legacy,
        enable_websocket=enable_all,
        enable_governor=enable_all,
        enable_sentry=enable_sentry
    )

if __name__ == '__main__':
    api = create_app(use_legacy=False, enable_all=True)
    api.run()
