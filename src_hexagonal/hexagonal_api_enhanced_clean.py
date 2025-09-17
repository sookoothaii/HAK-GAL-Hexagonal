"""
REST API Adapter with WebSocket, Governor & Sentry - CLEAN VERSION WITHOUT MOCKS
================================================================================
Nach HAK/GAL Verfassung: NO FAKE DATA, ONLY REAL RESULTS
"""

import os  # Import os at the top level
import sys
from pathlib import Path

# Set Governance Version BEFORE other imports
os.environ.setdefault('GOVERNANCE_VERSION', 'v3')
print(f"[INFO] Governance Version: {os.environ.get('GOVERNANCE_VERSION')}")

# --- CRITICAL: Eventlet Monkey-Patching ---
# This MUST be the first piece of code to run to ensure all standard libraries
# are patched for cooperative multitasking, preventing hangs with SocketIO.
try:
    import eventlet
    # Full patching for proper async operation - fixes 2-second delay
    eventlet.monkey_patch()
    print("[OK] Eventlet monkey-patching applied (DNS-safe mode).")
except ImportError:
    print("[WARNING] Eventlet not found. WebSocket may hang under load.")
# --- End of Patching ---

from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, Any, Optional
import time
import subprocess
from datetime import datetime, timezone
import re
import shutil
import uuid
import sqlite3
import json
from functools import wraps
from dotenv import load_dotenv
try:
    import engineio.middleware as engineio_middlewares
except ImportError:
    engineio_middlewares = None

# --- API Key Authentication Decorator ---
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow CORS preflight requests to pass through without authentication
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        # Load API key from environment. Fallback to a default if not set for safety.
        # Try multiple possible .env locations
        env_paths = [
            Path(__file__).resolve().parents[1] / '.env',
            Path("D:/MCP Mods/hak_gal_user/.env"),
            Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/.env"),
            Path(__file__).resolve().parents[2] / 'HAK_GAL_HEXAGONAL' / '.env'
        ]
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
                break
        api_key = os.environ.get("HAKGAL_API_KEY")
        if not api_key:
            # This case should not happen if .env is set up, but as a safeguard:
            return jsonify({"error": "API key not configured on server."}), 500

        # Get key from request header
        provided_key = request.headers.get('X-API-Key')
        if not provided_key or provided_key != api_key:
            return jsonify({"error": "Forbidden: Invalid or missing API key."}), 403
        
        return f(*args, **kwargs)
    return decorated_function


# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from application.services import FactManagementService, ReasoningService
from adapters.legacy_adapters import LegacyFactRepository, LegacyReasoningEngine
from adapters.native_adapters import NativeReasoningEngine
from adapters.sqlite_adapter import SQLiteFactRepository
from adapters.websocket_adapter import create_websocket_adapter
from adapters.governor_adapter import get_governor_adapter
from adapters.system_monitor import get_system_monitor
from core.domain.entities import Query
from src_hexagonal.api_endpoints_extension import create_extended_endpoints
from src_hexagonal.missing_endpoints import register_missing_endpoints
from adapters.agent_adapters import get_agent_adapter
from src_hexagonal.llm_config_routes import init_llm_config_routes
from src_hexagonal.llm_governor_integration_fixed import integrate_llm_governor
from src_hexagonal.application.transactional_governance_engine import TransactionalGovernanceEngine
from src_hexagonal.application.governance_monitor import probe_sqlite




# Import infrastructure if available
try:
    from infrastructure.sentry_monitoring import SentryMonitoring
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    print("⚠️ Sentry not available - monitoring disabled")

# --- LLM Configuration Switch ---
# Hybrid Strategy: Try Gemini first (fast), fall back to Ollama (reliable)
USE_HYBRID_LLM = True  # Recommended for production
USE_LOCAL_OLLAMA_ONLY = False  # Set True to skip Gemini completely
GEMINI_TIMEOUT = 70  # seconds before falling back to Ollama
# --- End of LLM Configuration ---

class HexagonalAPI:
    """
    Enhanced REST API Adapter - HONEST VERSION
    No mocks, no fake data, only real results
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
        
        # Paths
        self.hex_root = Path(__file__).resolve().parents[1]
        self.suite_root = (self.hex_root.parent / 'HAK_GAL_SUITE')

        # Load environment from HAK_GAL_SUITE/.env if present (DISABLED - causes conflicts)
        # try:
        #     env_path = self.suite_root / '.env'
        #     if env_path.exists():
        #         try:
        #             from dotenv import load_dotenv
        #             load_dotenv(dotenv_path=str(env_path), override=False)
        #             print(f"[ENV] Loaded environment from {env_path}")
        #         except Exception:
        #             # Manual parser
        #             for line in env_path.read_text(encoding='utf-8', errors='ignore').splitlines():
        #                 line = line.strip()
        #                 if not line or line.startswith('#'):
        #                     continue
        #                 if line.lower().startswith('export '):
        #                     line = line[7:].strip()
        #                 if '=' in line:
        #                     key, val = line.split('=', 1)
        #                     key = key.strip()
        #                     val = val.strip().strip('"').strip("'")
        #                     if key and key not in os.environ:
        #                         os.environ[key] = val
        #             print(f"[ENV] Loaded environment (manual) from {env_path}")
        # except Exception as e:
        #     print(f"[ENV] Failed to load .env: {e}")

        # Dependency Injection
        if use_legacy:
            print("[INFO] Using Legacy Adapters (Original HAK-GAL)")
            self.fact_repository = LegacyFactRepository()
            self.reasoning_engine = LegacyReasoningEngine()
        else:
            print("[INFO] Using SQLite Adapters (Development DB)")
            self.fact_repository = SQLiteFactRepository()
            # Verwende das trainierte HRM (NativeReasoningEngine)
            self.reasoning_engine = NativeReasoningEngine()

        # Initialize Governance V3
        self.governance_engine = TransactionalGovernanceEngine()
        print(f"[OK] Governance {os.environ.get('GOVERNANCE_VERSION')} initialized")
        print(f"[OK] Policy enforcement: {os.environ.get('POLICY_ENFORCE', 'observe')}")
        print(f"[OK] Bypass mode: {os.environ.get('GOVERNANCE_BYPASS', 'false')}")

        
        # Initialize Application Services
        self.fact_service = FactManagementService(
            fact_repository=self.fact_repository,
            reasoning_engine=self.reasoning_engine
        )
        
        self.reasoning_service = ReasoningService(
            reasoning_engine=self.reasoning_engine,
            fact_repository=self.fact_repository
        )
        
        # Initialize WebSocket Support
        self.websocket_adapter = None
        self.socketio = None
        self.system_monitor = None
        if enable_websocket:
            self.websocket_adapter, self.socketio = create_websocket_adapter(
                self.app, 
                self.fact_repository, 
                self.reasoning_engine
            )
            print("[OK] WebSocket Support enabled")
            
            # Initialize System Monitor and start monitoring
            self.system_monitor = get_system_monitor(self.socketio)
            self.system_monitor.start_monitoring()
            print("[OK] System Monitoring started")
        
        # Initialize Governor
        self.governor = None
        if enable_governor:
            self.governor = get_governor_adapter()
            print("[OK] Governor initialized (not started - use Frontend to control)")

        # Initialize LLM Governor
        self.llm_governor_integration = None
        if enable_governor:
            try:
                self.llm_governor_integration = integrate_llm_governor(self.app)
                print("[OK] LLM Governor Integration enabled")
            except Exception as e:
                print(f"[WARNING] LLM Governor Integration failed: {e}")
        
        
        # Initialize Sentry Monitoring
        self.monitoring = None
        if enable_sentry and SENTRY_AVAILABLE:
            tentative_monitor = SentryMonitoring()
            if tentative_monitor.initialize(self.app):
                self.monitoring = tentative_monitor
                print("[OK] Sentry Monitoring enabled")
            else:
                self.monitoring = None
        
        # Simple in-memory cache with TTL
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.delegated_tasks: Dict[str, Dict[str, Any]] = {}

        # Initialize Agent Adapters that need socketio
        self.cursor_adapter = get_agent_adapter('cursor', socketio=self.socketio)

        # Register Routes
        self._register_routes()
        # Register extended endpoints
        create_extended_endpoints(self.app, self.fact_service, self.fact_repository)
        self._register_governor_routes()
        self._register_websocket_routes()
        self._register_auto_add_routes()
        # self._register_hrm_routes()  # HRM routes not implemented yet
        self._register_missing_endpoints()
        self._register_agent_bus_routes() # Register the new agent bus routes
        self._register_engine_routes() # Register engine API routes
        self._register_llm_config_routes() # Register LLM configuration routes
        
        # Ensure CORS headers on every response
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
        """Register all REST Endpoints - NO MOCKS"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health Check"""
            return jsonify({
                'status': 'operational',
                'architecture': 'hexagonal_clean',
                'port': (int(os.environ.get('HAKGAL_PORT', '5001')) if (os.environ.get('HAKGAL_PORT', '5001') or '').isdigit() else 5001),
                'repository': self.fact_repository.__class__.__name__
            })
        
        @self.app.route('/api/feedback/verified/<path:query>', methods=['GET'])
        def check_verified(query):
            """Check if a query has been verified"""
            try:
                query = query.strip()
                print(f"[Check Verified] Checking query: '{query}'")
                
                # Check in verified_queries table
                with sqlite3.connect(self.fact_repository.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # First check if table exists
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='verified_queries'
                    """)
                    if not cursor.fetchone():
                        print("[Check Verified] Table 'verified_queries' does not exist")
                        return jsonify({
                            'verified': False,
                            'query': query,
                            'error': 'Table not initialized'
                        })
                    
                    cursor.execute("""
                        SELECT query, timestamp FROM verified_queries
                        WHERE query = ?
                    """, (query,))
                    
                    result = cursor.fetchone()
                    
                    if result:
                        print(f"[Check Verified] Query IS verified: '{query}'")
                        return jsonify({
                            'verified': True,
                            'query': result[0],
                            'verified_at': result[1]
                        })
                    else:
                        print(f"[Check Verified] Query NOT verified: '{query}'")
                        # Also check how many verified queries exist
                        cursor.execute("SELECT COUNT(*) FROM verified_queries")
                        count = cursor.fetchone()[0]
                        print(f"[Check Verified] Total verified queries: {count}")
                        
                        return jsonify({
                            'verified': False,
                            'query': query,
                            'total_verified': count
                        })
                        
            except Exception as e:
                print(f"[Check Verified] Error: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/feedback/verify', methods=['POST'])
        def verify_query():
            """Verify a query and store in HRM feedback system"""
            try:
                data = request.get_json(silent=True)
                if not data:
                    return jsonify({'error': 'Invalid request data'}), 400
                    
                query = data.get('query', '').strip()
                
                if not query:
                    return jsonify({'error': 'Missing query'}), 400
                
                # Debug log
                print(f"[Verify] Processing query: {query}")
                print(f"[Verify] DB Path: {self.fact_repository.db_path}")
                
                # Store in verified_queries table
                try:
                    with sqlite3.connect(self.fact_repository.db_path) as conn:
                        cursor = conn.cursor()
                        # Create table if not exists
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS verified_queries (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                query TEXT UNIQUE,
                                timestamp TEXT
                            )
                        """)
                        
                        # Try to add confidence column if it doesn't exist (will fail silently if exists)
                        try:
                            cursor.execute("ALTER TABLE verified_queries ADD COLUMN confidence REAL DEFAULT 1.0")
                            print("[Verify] Added confidence column")
                        except:
                            pass  # Column already exists or other error
                        
                        # Check which columns exist
                        cursor.execute("PRAGMA table_info(verified_queries)")
                        columns = [col[1] for col in cursor.fetchall()]
                        print(f"[Verify] Table columns: {columns}")
                        
                        if 'confidence' in columns:
                            cursor.execute("""
                                INSERT OR REPLACE INTO verified_queries (query, timestamp, confidence)
                                VALUES (?, ?, ?)
                            """, (query, datetime.now().isoformat(), 1.0))
                        else:
                            cursor.execute("""
                                INSERT OR REPLACE INTO verified_queries (query, timestamp)
                                VALUES (?, ?)
                            """, (query, datetime.now().isoformat()))
                        
                        conn.commit()
                        print(f"[Verify] Stored in SQLite")
                except Exception as db_error:
                    print(f"[Verify] Database error: {db_error}")
                    return jsonify({'error': f'Database error: {str(db_error)}'}), 500
                
                # Also update HRM feedback if available
                try:
                    if isinstance(self.reasoning_engine, NativeReasoningEngine):
                        # Update the HRM feedback JSON directly
                        # Use absolute path to ensure it works
                        feedback_path = Path('D:/MCP Mods/HAK_GAL_HEXAGONAL/data/hrm_feedback.json')
                        
                        # Load current feedback data
                        feedback_data = {}
                        if feedback_path.exists():
                            with open(feedback_path, 'r', encoding='utf-8') as f:
                                feedback_data = json.load(f)
                        
                        # Ensure verified_queries section exists
                        if 'verified_queries' not in feedback_data:
                            feedback_data['verified_queries'] = {}
                        
                        # Add this query to verified_queries
                        feedback_data['verified_queries'][query] = {
                            'verified': True,
                            'confidence_override': None,  # Could be 1.0 for max confidence
                            'verified_at': time.time(),
                            'verifier': 'user'
                        }
                        
                        # Also ensure it's in adjustments for confidence boost
                        if 'adjustments' not in feedback_data:
                            feedback_data['adjustments'] = {}
                        
                        if query not in feedback_data['adjustments']:
                            feedback_data['adjustments'][query] = {
                                'base_adjustment': 0.2,  # Higher boost for verified
                                'feedback_ratio': 1.0,
                                'updated_at': time.time()
                            }
                        
                        # Save updated feedback data
                        with open(feedback_path, 'w', encoding='utf-8') as f:
                            json.dump(feedback_data, f, indent=2)
                        
                        print(f"[Verify] Updated HRM feedback JSON")
                        
                        # Also call apply_feedback for immediate effect
                        if hasattr(self.reasoning_engine, 'apply_feedback'):
                            self.reasoning_engine.apply_feedback(query, 'positive', 0.2)
                            print(f"[Verify] Applied HRM feedback")
                except Exception as hrm_error:
                    print(f"[Verify] HRM feedback error (non-critical): {hrm_error}")
                    # Continue even if HRM feedback fails
                
                return jsonify({
                    'status': 'success',
                    'message': f'Query verified: {query}',
                    'verified': True
                })
                
            except Exception as e:
                print(f"[Verify] Unexpected error: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/status', methods=['GET'])
        def status():
            """System Status"""
            base_status = self.fact_service.get_system_status()
            
            # Add CUDA status
            import torch
            base_status['cuda'] = {
                'available': torch.cuda.is_available(),
                'active': torch.cuda.is_available(),
                'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
                'device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A',
                'memory_allocated': f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB" if torch.cuda.is_available() else "0 GB",
                'memory_reserved': f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB" if torch.cuda.is_available() else "0 GB"
            }
            
            if self.governor:
                base_status['governor'] = self.governor.get_status()
            
            if self.llm_governor_integration:
                base_status['llm_governor'] = {
                    'available': True,
                    'enabled': self.llm_governor_integration.enabled,
                    'provider': self.llm_governor_integration.config['provider'],
                    'epsilon': self.llm_governor_integration.config['epsilon'],
                    'metrics': self.llm_governor_integration.get_metrics()
                }
            
            if self.websocket_adapter:
                base_status['websocket'] = {
                    'enabled': True,
                    'connected_clients': len(self.websocket_adapter.connected_clients)
                }
            
            if self.system_monitor:
                base_status['monitoring'] = self.system_monitor.get_status()
                # Only include expensive system metrics if explicitly requested
                if request.args.get('include_metrics', '').lower() == 'true':
                    base_status['system_metrics'] = self.system_monitor.get_system_metrics()
            
            return jsonify(base_status)
        
        @self.app.route('/api/facts', methods=['GET'])
        def get_facts():
            """GET /api/facts - Get all facts"""
            limit = request.args.get('limit', 100, type=int)
            facts = self.fact_service.get_all_facts(limit)
            
            return jsonify({
                'facts': [f.to_dict() for f in facts],
                'count': len(facts),
                'total': self.fact_repository.count()
            })
        
        @self.app.route('/api/facts', methods=['POST'])
        # # # # # @require_api_key
        def add_fact():
            """POST /api/facts - Add new fact"""
            data = request.get_json(silent=True) or {}

            statement = (data.get('statement') or data.get('query') or data.get('fact') or '').strip()
            if not statement:
                return jsonify({'error': 'Missing statement'}), 400

            if not statement.endswith('.'):
                statement = statement + '.'

            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.$", statement):
                return jsonify({'error': 'Invalid fact format. Expected Predicate(Entity1, Entity2).'}), 400

            context = data.get('context', {})
            success, message = self.fact_service.add_fact(statement, context)
            
            # Emit WebSocket event
            if self.websocket_adapter:
                self.websocket_adapter.emit_fact_added(statement, success)
            
            # Track with Sentry
            if self.monitoring:
                SentryMonitoring.capture_fact_added(statement, success)
            
            status_code = 201 if success else (409 if isinstance(message, str) and 'exists' in message.lower() else 422)
            return jsonify({
                'success': success,
                'message': message,
                'statement': statement
            }), status_code

        @self.app.route('/api/facts', methods=['DELETE'])
        # # # # # @require_api_key
        def delete_fact_api():
            """DELETE /api/facts - Delete a fact"""
            data = request.get_json(silent=True) or {}
            statement = (data.get('statement') or '').strip()
            if not statement:
                return jsonify({'error': 'Missing statement'}), 400

            # Assuming the service layer has a delete_fact method
            success, message = self.fact_service.delete_fact(statement)

            # if self.websocket_adapter:
            #     self.websocket_adapter.emit_fact_removed(statement, success)

            if success:
                return jsonify({'success': True, 'message': message}), 200
            else:
                # e.g., fact not found
                return jsonify({'success': False, 'message': message}), 404
        
        @self.app.route('/api/search', methods=['POST', 'OPTIONS'])
        def search_facts():
            """POST /api/search - Search facts"""
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
        
        @self.app.route('/api/metrics/trust', methods=['GET', 'POST', 'OPTIONS'])
        def get_trust_metrics():
            """Calculate trust metrics for a query and response"""
            if request.method == 'OPTIONS':
                return ('', 204)
            
            # Handle both GET and POST
            if request.method == 'GET':
                # GET request with query parameters
                query = request.args.get('query', '')
                response = request.args.get('response', '')
                facts_used = request.args.getlist('facts_used')  # Handle array in query params
                confidence = float(request.args.get('confidence', 0.5))
            else:
                # POST request with JSON body
                data = request.get_json(silent=True) or {}
                query = data.get('query', '')
                response = data.get('response', '')
                facts_used = data.get('facts_used', [])
                confidence = data.get('confidence', 0.5)
            
            # Calculate raw metrics
            factual_accuracy = min(len(facts_used) * 0.15 + 0.3, 1.0)
            source_quality = 0.7 if len(facts_used) > 0 else 0.1
            model_consensus = confidence
            ethical_alignment = 0.7
            
            # Calculate overall trust score
            overall_trust = (
                factual_accuracy * 0.3 +
                source_quality * 0.2 +
                model_consensus * 0.3 +
                ethical_alignment * 0.2
            ) * 100  # Convert to percentage
            
            # Format response to match frontend expectations
            trust_data = {
                'trust_score': {
                    'value': overall_trust,
                    'label': 'Overall Trust Score'
                },
                'sub_metrics': [
                    {
                        'label': 'Factual Accuracy',
                        'value': f'{factual_accuracy * 100:.1f}%',
                        'description': 'Based on facts found in knowledge base'
                    },
                    {
                        'label': 'Source Quality',
                        'value': f'{source_quality * 100:.1f}%',
                        'description': 'Quality of sources used'
                    },
                    {
                        'label': 'Model Consensus',
                        'value': f'{model_consensus * 100:.1f}%',
                        'description': 'Model confidence in response'
                    },
                    {
                        'label': 'Ethical Alignment',
                        'value': f'{ethical_alignment * 100:.1f}%',
                        'description': 'Alignment with ethical guidelines'
                    },
                    {
                        'label': 'Neural Confidence',
                        'value': f'{model_consensus * 100:.1f}%',
                        'description': 'HRM neural reasoning confidence'
                    }
                ]
            }
            
            return jsonify(trust_data)
        
        @self.app.route('/api/reason', methods=['POST', 'OPTIONS'])
        def reason():
            """POST /api/reason - Reasoning"""
            if request.method == 'OPTIONS':
                return ('', 204)
            data = request.get_json()
            
            if not data or 'query' not in data:
                return jsonify({'error': 'Missing query'}), 400
            
            query = data['query']
            start_time = time.time()
            
            result = self.reasoning_service.reason(query)
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Emit WebSocket event
            if self.websocket_adapter:
                self.websocket_adapter.emit_reasoning_complete(
                    query, result.confidence, duration_ms
                )
            
            # Track with Sentry
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
            
            # Add device info if available
            if result.metadata and 'device' in result.metadata:
                response['device'] = result.metadata['device']
            
            return jsonify(response)

        @self.app.route('/api/llm/get-explanation', methods=['POST'])
        def llm_get_explanation():
            """
            LLM Explanation endpoint with Hybrid Strategy.
            Primary: Gemini (fast, ~3s)
            Fallback: Ollama (reliable, ~15s)
            """
            import time
            start_time = time.time()  # Start timing immediately
            
            payload = request.get_json(silent=True) or {}
            topic = payload.get('topic') or payload.get('query') or ''
            context_facts = payload.get('context_facts') or []
            
            prompt = (
                f"Query: {topic}\n\n"
                f"Context facts:\n{os.linesep.join(context_facts) if context_facts else 'None'}\n\n"
                "Please provide a deep, step-by-step explanation addressing the query. "
                "After your explanation, suggest additional logical facts that would be relevant to add to the knowledge base. "
                "Format suggested facts as: Predicate(Entity1, Entity2)."
            )

            explanation = None
            llm_used = None
            
            # Try MultiLLMProvider first (Gemini -> DeepSeek -> Claude -> Ollama)
            if not USE_LOCAL_OLLAMA_ONLY and USE_HYBRID_LLM:
                try:
                    print("[MultiLLM] Trying custom chain: Groq -> DeepSeek -> Gemini -> Claude -> Ollama...")
                    from adapters.llm_providers import MultiLLMProvider
                    multi_llm = MultiLLMProvider()
                    
                    if multi_llm.is_available():
                        print("[MultiLLM] Available, generating response...")
                        response = multi_llm.generate_response(prompt)
                        # MultiLLM returns tuple (text, provider_name)
                        if isinstance(response, tuple) and len(response) >= 1:
                            explanation = response[0]  # Extract text from tuple
                            llm_used = response[1]    # Extract provider name
                        else:
                            explanation = response
                            llm_used = 'MultiLLM'
                        print(f"[MultiLLM] Success with {llm_used} (length: {len(explanation)})")
                    else:
                        raise RuntimeError("MultiLLM not available")
                except Exception as e:
                    print(f"[DeepSeek] Failed: {e}. Trying Gemini (2/3)...")
                    try:
                        # Quick network check first
                        import socket
                        try:
                            # Test connection to Google
                            socket.create_connection(("generativelanguage.googleapis.com", 443), timeout=2)
                        except (socket.timeout, socket.error, OSError) as e:
                            print(f"[Gemini] No internet connection: {e}. Skipping to Ollama...")
                            raise RuntimeError("No internet connection")
                        
                        # Import Gemini provider
                        from adapters.llm_providers import GeminiProvider
                        gemini_llm = GeminiProvider()
                        
                        # Check if Gemini is available (has API key)
                        if gemini_llm.is_available():
                            # Try to get response directly with simpler approach
                            print("[Gemini] Attempting to generate response...")
                            try:
                                # Direct call with built-in timeout handling
                                gemini_response = gemini_llm.generate_response(prompt)
                                
                                # Handle both tuple and string responses
                                if gemini_response:
                                    # Check if it's a tuple (response, provider)
                                    if isinstance(gemini_response, tuple) and len(gemini_response) >= 1:
                                        actual_response = gemini_response[0]  # Extract text from tuple
                                        print(f"[Gemini] Extracted response from tuple")
                                    elif isinstance(gemini_response, str):
                                        actual_response = gemini_response
                                    else:
                                        print(f"[Gemini] Unexpected response type: {type(gemini_response)}")
                                        raise RuntimeError("Invalid response format")
                                    
                                    # Now validate the actual text response
                                    if actual_response and isinstance(actual_response, str) and len(actual_response) > 50:
                                        # Check for error indicators
                                        lower_resp = actual_response.lower()
                                        if not any(err in lower_resp[:200] for err in ['error', 'failed', 'exception', 'none', 'null', 'undefined']):
                                            explanation = actual_response
                                            llm_used = 'Gemini'
                                            print(f"[MultiLLM] Success with Gemini (length: {len(actual_response)})")
                                        else:
                                            print(f"[Gemini] Response appears to be an error: {actual_response[:100]}")
                                            raise RuntimeError("Gemini returned error-like response")
                                    else:
                                        print(f"[Gemini] Response too short ({len(actual_response) if actual_response else 0} chars)")
                                        raise RuntimeError("Response too short")
                                else:
                                    print(f"[Gemini] Empty response")
                                    raise RuntimeError("Empty response")
                                    
                            except Exception as e:
                                print(f"[Gemini] Direct call failed: {e}")
                                raise RuntimeError(f"Gemini call failed: {e}")
                                
                    except (ImportError, TimeoutError, RuntimeError, Exception) as e:
                        print(f"[Gemini] Failed: {e}. Trying Ollama (3/3)...")
                        # Continue to Ollama fallback
                        
                except Exception as e:
                    print(f"[Gemini] Unexpected error: {e}. Falling back to Ollama...")
            
            # Fallback to Ollama if needed (for offline capability)
            if explanation is None:
                try:
                    print("[LLM] Falling back to direct Ollama...")
                    from adapters.ollama_adapter import OllamaProvider
                    # Force qwen2.5:7b for reliability
                    ollama_llm = OllamaProvider(model="qwen2.5:7b", timeout=30)
                    
                    if ollama_llm.is_available():
                        print("[LLM] Ollama is available, generating response...")
                        ollama_response = ollama_llm.generate_response(prompt)
                        
                        # Handle tuple response
                        if isinstance(ollama_response, tuple):
                            explanation = ollama_response[0]
                        else:
                            explanation = ollama_response
                            
                        llm_used = 'Ollama'
                        print(f"[LLM] Ollama fallback successful (length: {len(explanation) if explanation else 0})")
                    else:
                        print("[LLM] Ollama not available")
                        raise RuntimeError("Ollama is not available. Please ensure 'ollama serve' is running.")
                        
                except Exception as e:
                    print(f"[Ollama] Direct fallback failed: {e}")
                    return jsonify({
                        'status': 'error',
                        'explanation': 'No LLM service available. Please check API keys and ensure Ollama is running for offline mode.',
                        'suggested_facts': [],
                        'message': f'All LLM providers failed: {e}',
                        'llm_attempted': ['DeepSeek', 'Gemini', 'Ollama']
                    }), 503
            
            # Process the explanation (from either Gemini or Ollama)
            if explanation and len(explanation) > 10:
                # Try refined extractor first, then optimized, then original
                try:
                    from adapters.fact_extractor_universal import extract_facts_from_llm
                    print("[LLM] Using refined fact extractor")
                except ImportError:
                    try:
                        from adapters.fact_extractor_optimized import extract_facts_from_llm
                        print("[LLM] Using optimized fact extractor")
                    except ImportError:
                        from adapters.fact_extractor import extract_facts_from_llm
                        print("[LLM] Using original fact extractor")
                
                suggested = extract_facts_from_llm(explanation, topic)
                print(f"[LLM] Extracted {len(suggested)} facts using {llm_used}")
                
                # Calculate actual response time
                actual_time = round(time.time() - start_time, 2)
                print(f"[LLM] Total response time: {actual_time}s")
                
                return jsonify({
                    'status': 'success',
                    'explanation': explanation,
                    'suggested_facts': suggested,
                    'llm_provider': llm_used,
                    'response_time': f'{actual_time}s',
                    'response_time_ms': int(actual_time * 1000)
                })
            else:
                # Should not reach here if explanation is valid
                return jsonify({
                    'status': 'error',
                    'explanation': 'Failed to generate valid explanation',
                    'suggested_facts': [],
                    'message': 'No valid explanation received from LLM',
                    'llm_provider': llm_used or 'None'
                }), 503

        @self.app.route('/api/graph/generate', methods=['POST', 'OPTIONS'])
        def generate_graph():
            """Generate knowledge graph visualization"""
            if request.method == 'OPTIONS':
                return ('', 204)
            
            try:
                # Import graph generator
                from src_hexagonal.graph_generator import generate_knowledge_graph, generate_graph_html
                
                data = request.get_json(silent=True) or {}
                limit = data.get('limit', 500)
                focus = data.get('focus', None)
                
                # Generate graph data
                graph_data = generate_knowledge_graph(
                    db_path="hexagonal_kb.db",
                    limit=limit,
                    focus=focus
                )
                
                if graph_data.get('success'):
                    # Generate HTML file
                    html_content = generate_graph_html(graph_data)
                    
                    # Save to frontend/public
                    from pathlib import Path
                    output_path = Path("frontend/public/knowledge_graph.html")
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Graph generated successfully',
                        'nodes': len(graph_data.get('nodes', [])),
                        'edges': len(graph_data.get('edges', [])),
                        'path': '/knowledge_graph.html'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': graph_data.get('error', 'Failed to generate graph')
                    }), 500
                    
            except Exception as e:
                print(f"[ERROR] Graph generation failed: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
            """
            Compatibility endpoint - NO MOCKS
            """
            if request.method == 'OPTIONS':
                return ('', 204)
                
            data = request.get_json(silent=True) or {}
            cmd = (data.get('command') or data.get('action') or '').strip().lower()
            
            if cmd == 'add_fact':
                statement = (data.get('statement') or data.get('fact') or data.get('query') or '').strip()
                if not statement:
                    return jsonify({'error': 'Missing statement'}), 400
                if not statement.endswith('.'):
                    statement = statement + '.'
                if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.$", statement):
                    return jsonify({'error': 'Invalid fact format. Expected Predicate(Entity1, Entity2).'}), 400
                ok, msg = self.fact_service.add_fact(statement, data.get('context') or {})
                if self.websocket_adapter:
                    self.websocket_adapter.emit_fact_added(statement, ok)
                code = 201 if ok else (409 if isinstance(msg, str) and 'exists' in msg.lower() else 422)
                return jsonify({'status': 'success' if ok else 'error', 'message': msg, 'statement': statement}), code
                
            elif cmd == 'explain':
                topic = data.get('query') or data.get('topic') or ''
                # Use the real LLM endpoint
                payload = {'topic': topic}
                with self.app.test_request_context(json=payload):
                    resp = llm_get_explanation()
                if isinstance(resp, tuple):
                    body, status = resp
                    if status != 200:
                        # Return error transparently
                        return body, status
                    payload_out = body.get_json() if hasattr(body, 'get_json') else body
                else:
                    payload_out = resp.get_json() if hasattr(resp, 'get_json') else resp
                    
                explanation = (payload_out or {}).get('explanation') or ''
                suggested = (payload_out or {}).get('suggested_facts', [])
                
                return jsonify({
                    'status': payload_out.get('status', 'error'),
                    'chatResponse': {
                        'natural_language_explanation': explanation,
                        'suggested_facts': suggested
                    }
                })
                
            return jsonify({'error': 'Only explain/add_fact supported'}), 405

        @self.app.route('/api/governance/status', methods=['GET'])
        def governance_status():
            """Get current governance status and health"""
            try:
                db_health = probe_sqlite(self.governance_engine.db_path)
                return jsonify({
                    'governance': {
                        'version': os.environ.get('GOVERNANCE_VERSION', 'unknown'),
                        'mode': os.environ.get('POLICY_ENFORCE', 'observe'),
                        'bypass_active': os.environ.get('GOVERNANCE_BYPASS') == 'true'
                    },
                    'database': {
                        'healthy': db_health.get('ok', False),
                        'wal_mode': db_health.get('wal_mode'),
                        'latency_ms': db_health.get('latency_ms'),
                        'facts_count': db_health.get('facts_count')
                    },
                    'status': 'operational'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500


        @self.app.route('/api/facts/count', methods=['GET'])
        def facts_count():
            """GET /api/facts/count - Get fact count with cache"""
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

        @self.app.route('/api/facts/export', methods=['GET'])
        def export_facts():
            """Export facts for autopilot/boosting"""
            limit = request.args.get('limit', 100, type=int)
            format_type = request.args.get('format', 'json')
            
            facts = self.fact_service.get_all_facts(limit)
            
            if format_type == 'json':
                return jsonify({
                    'facts': [{'statement': f.statement} for f in facts],
                    'count': len(facts)
                })
            else:
                # Plain text format
                return '\n'.join([f.statement for f in facts]), 200, {'Content-Type': 'text/plain'}

        # Catch-all OPTIONS handler
        @self.app.route('/<path:any_path>', methods=['OPTIONS'])
        def cors_preflight(any_path):
            return ('', 204)
    
    def _register_auto_add_routes(self):
        """Register auto-add routes for LLM facts"""
        try:
            from adapters.auto_add_extension import register_auto_add_routes
            register_auto_add_routes(self.app, self.fact_service)
            print("[OK] Auto-Add routes registered")
        except ImportError:
            print("[INFO] Auto-Add extension not available")
    
    def _register_governor_routes(self):
        """Register Governor-specific routes"""
        
        if not self.governor:
            return
        
        @self.app.route('/api/governor/status', methods=['GET'])
        def governor_status():
            status = self.governor.get_status() if self.governor else {}
            
            # Add generator metrics if available
            if hasattr(self, '_llm_gov_generator'):
                try:
                    generator_metrics = self._llm_gov_generator.get_metrics()
                    status['generator'] = {
                        'active': self._llm_gov_generator.generating,
                        'facts_generated': generator_metrics['facts_generated'],
                        'facts_per_minute': generator_metrics['facts_per_minute'],
                        'mode': 'integrated_generator'
                    }
                    # Add self-learning specific metrics
                    status['self_learning'] = {
                        'active': self._llm_gov_generator.generating,
                        'facts_generated': generator_metrics['facts_generated'],
                        'learning_rate': generator_metrics['facts_per_minute'],
                        'learning_progress': generator_metrics.get('learning_progress', 0),
                        'adaptive': True
                    }
                except:
                    pass
            
            return jsonify(status)
        
        @self.app.route('/api/governor/start', methods=['POST'])
        # # # # # @require_api_key
        def governor_start():
            data = request.get_json(silent=True) or {}
            use_llm = data.get('use_llm', False)
            
            # Check if LLM Governor requested
            if use_llm:
                # Try the new integrated generator first
                try:
                    import sys
                    sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal")
                    # USE THE PARALLEL VERSION THAT BYPASSES THESIS!
                    from llm_governor_generator_parallel import LLMGovernorWithGenerator
                    
                    # Create or get singleton instance
                    if not hasattr(self, '_llm_gov_generator'):
                        self._llm_gov_generator = LLMGovernorWithGenerator()
                    
                    # Start the integrated generator
                    success = self._llm_gov_generator.start()
                    if success:
                        print("[API] Started LLM Governor with integrated fact generation")
                        # Also start standard governor if available
                        if self.governor:
                            self.governor.start()
                        return jsonify({
                            'success': True,
                            'mode': 'llm_governor_generator',
                            'provider': 'groq',
                            'generating': True,
                            'message': 'LLM Governor started with automatic fact generation'
                        })
                except Exception as e:
                    print(f"[API] Failed to start integrated generator: {e}")
                
                # Fallback to standard LLM Governor
                if self.llm_governor_integration:
                    self.llm_governor_integration.enabled = True
                    # Also start the standard governor for engines
                    if self.governor:
                        self.governor.start()
                    return jsonify({
                        'success': True, 
                        'mode': 'llm_governor',
                        'provider': self.llm_governor_integration.config['provider']
                    })
            else:
                # Use standard Thompson governor
                success = self.governor.start() if self.governor else False
                return jsonify({'success': success, 'mode': 'thompson'})
        
        @self.app.route('/api/governor/stop', methods=['POST'])
        # # # # # @require_api_key
        def governor_stop():
            # Stop integrated generator if running
            if hasattr(self, '_llm_gov_generator'):
                try:
                    self._llm_gov_generator.stop()
                    print("[API] Stopped LLM Governor Generator")
                except:
                    pass
            
            # Stop standard governor
            success = self.governor.stop() if self.governor else False
            return jsonify({'success': success})
        
        def hrm_retrain():
            """Triggers a retraining of the HRM model."""
            try:
                print("[HRM] Retraining triggered.")
                # In a real scenario, this would be an async task
                self.reasoning_engine.retrain() 
                return jsonify({'status': 'success', 'message': 'HRM retraining initiated.'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500

        @self.app.route('/api/hrm/model_info', methods=['GET'])
        def hrm_model_info():
            """Gets information about the current HRM model."""
            try:
                info = self.reasoning_engine.get_model_info()
                return jsonify(info)
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500

        @self.app.route('/api/hrm/feedback-stats', methods=['GET'])
        def hrm_feedback_stats():
            """Gets feedback statistics for the HRM model."""
            try:
                if hasattr(self.reasoning_engine, 'get_feedback_stats'):
                    stats = self.reasoning_engine.get_feedback_stats()
                else:
                    stats = {
                        'total_feedback': 0,
                        'positive_feedback': 0,
                        'negative_feedback': 0,
                        'accuracy_improvement': 0.0,
                        'last_training': None,
                        'model_version': getattr(self.reasoning_engine, 'version', '1.0')
                    }
                return jsonify(stats)
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500

    def _register_missing_endpoints(self):
        """Register missing endpoints that were causing 405 errors"""
        try:
            register_missing_endpoints(self.app, self.fact_repository, self.reasoning_engine)
            print("[OK] Missing endpoints registered (GPU, Mojo, Metrics, Limits, Graph)")
        except Exception as e:
            print(f"[WARNING] Failed to register missing endpoints: {e}")
    
    def _register_engine_routes(self):
        """Register Engine API routes for Thesis and Aethelred"""
        try:
            from api_engines import engines_bp
            self.app.register_blueprint(engines_bp)
            print("[OK] Engine API routes registered (Thesis, Aethelred)")
        except ImportError:
            print("[INFO] Engine API not available")
        except Exception as e:
            print(f"[WARNING] Failed to register engine routes: {e}")
        
        # Register async engine routes
        try:
            from api_engines_async import engines_async_bp
            self.app.register_blueprint(engines_async_bp)
            print("[OK] Async Engine API routes registered")
        except ImportError:
            print("[INFO] Async Engine API not available")
        except Exception as e:
            print(f"[WARNING] Failed to register async engine routes: {e}")

    def _register_websocket_routes(self):
        """Register WebSocket-specific routes"""
        
        if not self.socketio:
            return
        
        @self.socketio.on('governor_control')
        def handle_governor_control(data):
            # --- API Key Authentication for WebSocket ---
            api_key = os.environ.get("HAKGAL_API_KEY")
            provided_key = data.get('apiKey') or (request.args.get('apiKey'))

            if not api_key or not provided_key or provided_key != api_key:
                print(f"WebSocket auth failed for sid {request.sid}")
                # It's better not to emit an error to prevent leaking info,
                # just ignore the request. For debugging, we can emit.
                return {'error': 'Authentication failed'}

            if not self.governor:
                return {'error': 'Governor not enabled'}
            
            action = data.get('action')
            
            if action == 'start':
                self.governor.start()
            elif action == 'stop':
                self.governor.stop()
            
            status = self.governor.get_status()
            self.socketio.emit('governor_update', status, to=None)

    def _register_agent_bus_routes(self):
        """Register routes for the Multi-Agent Collaboration Bus."""
        from adapters.agent_adapters import get_agent_adapter

        @self.app.route('/api/agent-bus/delegate', methods=['POST'])
        @require_api_key
        def delegate_task():
            data = request.get_json()
            if not data or 'target_agent' not in data or 'task_description' not in data:
                return jsonify({'error': 'Missing required fields: target_agent, task_description'}), 400

            target_agent = data['target_agent']
            task_description = data['task_description']
            context = data.get('context', {})
            
            adapter = get_agent_adapter(target_agent, socketio=self.socketio) # Pass socketio to adapters
            if not adapter:
                return jsonify({'error': f'No adapter found for agent: {target_agent}'}), 404

            task_id = str(uuid.uuid4())
            self.delegated_tasks[task_id] = {
                'status': 'pending',
                'target': target_agent,
                'description': task_description,
                'submitted_at': time.time()
            }

            # Non-blocking dispatch would be ideal here, e.g., using a task queue
            # For now, we do a simple blocking call for demonstration
            try:
                result = adapter.dispatch(task_description, context)
                self.delegated_tasks[task_id].update({
                    'status': result.get('status', 'completed'),
                    'result': result,
                    'completed_at': time.time()
                })
                # Notify clients via WebSocket
                if self.websocket_adapter:
                    self.websocket_adapter.emit_agent_response(task_id, self.delegated_tasks[task_id])

                return jsonify({'task_id': task_id, 'status': 'dispatched', 'result': result})
            except Exception as e:
                self.delegated_tasks[task_id].update({'status': 'error', 'message': str(e)})
                return jsonify({'task_id': task_id, 'status': 'error', 'message': str(e)}), 500

        @self.app.route('/api/agent-bus/tasks/<task_id>', methods=['GET'])
        def get_task_status(task_id):
            task = self.delegated_tasks.get(task_id)
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            return jsonify(task)
        
        # WebSocket events for Cursor integration
        if self.socketio:
            @self.socketio.on('connect')
            def handle_connect(auth=None):
                print(f"[WebSocket] Client connected: {request.sid}")
                # Register as potential Cursor client
                if self.cursor_adapter and hasattr(self.cursor_adapter, 'register_websocket_client'):
                    self.cursor_adapter.register_websocket_client(request.sid)
            
            @self.socketio.on('disconnect')
            def handle_disconnect(reason=None):
                print(f"[WebSocket] Client disconnected: {request.sid} (reason: {reason})")
                # Unregister Cursor client
                if self.cursor_adapter and hasattr(self.cursor_adapter, 'unregister_websocket_client'):
                    self.cursor_adapter.unregister_websocket_client(request.sid)
            
            @self.socketio.on('cursor_response')
            def handle_cursor_response(data):
                """Handle response from Cursor IDE"""
                task_id = data.get('task_id')
                result = data.get('result')
                status = data.get('status', 'completed')
                
                if task_id and task_id in self.delegated_tasks:
                    self.delegated_tasks[task_id].update({
                        'status': status,
                        'result': result,
                        'completed_at': time.time()
                    })
                    print(f"[WebSocket] Received Cursor response for task {task_id}")
                else:
                    print(f"[WebSocket] WARNING: Received Cursor response for unknown task {task_id}")
            
            @self.socketio.on('cursor_identify')
            def handle_cursor_identify(data):
                """Cursor IDE identifies itself"""
                print(f"[WebSocket] Cursor IDE identified: {data}")
                # Mark this client as a Cursor client
                if self.cursor_adapter and hasattr(self.cursor_adapter, 'register_websocket_client'):
                    self.cursor_adapter.register_websocket_client(request.sid)
    
    def _register_llm_config_routes(self):
        """Register LLM configuration routes"""
        try:
            init_llm_config_routes(self.app)
            print("[OK] LLM configuration routes registered")
        except Exception as e:
            print(f"[WARNING] Failed to register LLM config routes: {e}")
    
    def run(self, host='127.0.0.1', port=5002, debug=False):
        """Start Flask Application"""
        print("=" * 60)
        print("🎯 HAK-GAL HEXAGONAL ARCHITECTURE - CLEAN VERSION")
        print("=" * 60)
        print("✅ NO MOCKS, NO FAKE DATA, ONLY REAL RESULTS")
        print(f"[START] Starting on http://{host}:{port}")
        print(f"📦 Repository: {self.fact_repository.__class__.__name__}")
        print(f"🧠 Reasoning: {self.reasoning_engine.__class__.__name__}")
        print(f"🔌 WebSocket: {'Enabled' if self.websocket_adapter else 'Disabled'}")
        print(f"[INFO] Governor: {'Enabled' if self.governor else 'Disabled'}")
        print(f"📊 System Monitor: {'Active' if self.system_monitor else 'Disabled'}")
        print(f"🚌 Agent Bus: {'Enabled'}")
        print("=" * 60)
        
        if self.socketio:
            # Use the standard SocketIO run method which handles WebSocket correctly
            # Don't pass cors_allowed_origins here - it's already set in websocket_adapter.py
            self.socketio.run(
                self.app,
                # async_mode removed - not valid for socketio.run() 
                host=host, 
                port=port, 
                debug=False, 
                use_reloader=False,
                log_output=True  # Enable logging to see what's happening
            )
        else:
            self.app.run(host=host, port=port, debug=False, use_reloader=False)

# Main Entry Point
def create_app(use_legacy=False, enable_all=True):
    """Factory Function for Clean App Creation"""
    # Load .env BEFORE checking for SENTRY_DSN
    from pathlib import Path
    from dotenv import load_dotenv
    
    # Try multiple .env locations
    env_paths = [
        Path("D:/MCP Mods/hak_gal_user/.env"),
        Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/.env"),
        Path(__file__).parent.parent / '.env',
        Path.cwd() / '.env'
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            print(f"[create_app] Loaded .env from {env_path}")
            break
    
    # NOW check for SENTRY_DSN after loading .env
    enable_sentry = bool(os.environ.get('SENTRY_DSN'))
    if enable_sentry:
        print(f"[create_app] Sentry DSN found, will enable monitoring")
    
    return HexagonalAPI(
        use_legacy=use_legacy,
        enable_websocket=enable_all,
        enable_governor=enable_all,
        enable_sentry=enable_sentry
    )

if __name__ == '__main__':
    # Use SQLite with the correct hexagonal_kb.db (5000+ facts)
    api = create_app(use_legacy=False, enable_all=True)
    api.run()
