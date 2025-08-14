"""
REST API Adapter - Flask Application
=====================================
Nach HAK/GAL Verfassung: Inbound Adapter für HTTP
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, Any
import sys
from pathlib import Path

# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from application.services import FactManagementService, ReasoningService
from adapters.legacy_adapters import LegacyFactRepository, LegacyReasoningEngine
from adapters.sqlite_adapter import SQLiteFactRepository
from core.domain.entities import Query

class HexagonalAPI:
    """
    REST API Adapter - Primary/Driving Adapter
    Übersetzt HTTP Requests zu Application Services
    """
    
    def __init__(self, use_legacy: bool = True):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend
        
        # Dependency Injection - Choose Repository Implementation
        if use_legacy:
            print("🔗 Using Legacy Adapters (Original HAK-GAL)")
            self.fact_repository = LegacyFactRepository()
            self.reasoning_engine = LegacyReasoningEngine()
        else:
            print("💾 Using SQLite Adapters (Development DB)")
            self.fact_repository = SQLiteFactRepository()
            # No SQLite reasoning engine yet, use legacy
            self.reasoning_engine = LegacyReasoningEngine()
        
        # Initialize Application Services
        self.fact_service = FactManagementService(
            fact_repository=self.fact_repository,
            reasoning_engine=self.reasoning_engine
        )
        
        self.reasoning_service = ReasoningService(
            reasoning_engine=self.reasoning_engine,
            fact_repository=self.fact_repository
        )
        
        # Register Routes
        self._register_routes()
    
    def _register_routes(self):
        """Registriere alle REST Endpoints"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health Check Endpoint"""
            return jsonify({
                'status': 'healthy',
                'architecture': 'hexagonal',
                'port': 5001,
                'repository': self.fact_repository.__class__.__name__
            })
        
        @self.app.route('/api/status', methods=['GET'])
        def status():
            """System Status"""
            return jsonify(self.fact_service.get_system_status())
        
        @self.app.route('/api/facts', methods=['GET'])
        def get_facts():
            """GET /api/facts - Hole alle Facts"""
            limit = request.args.get('limit', 100, type=int)
            facts = self.fact_service.get_all_facts(limit)
            
            return jsonify({
                'facts': [f.to_dict() for f in facts],
                'count': len(facts),
                'total': self.fact_repository.count()
            })
        
        @self.app.route('/api/facts', methods=['POST'])
        def add_fact():
            """POST /api/facts - Füge neuen Fact hinzu"""
            data = request.get_json()
            
            if not data or 'statement' not in data:
                return jsonify({'error': 'Missing statement'}), 400
            
            success, message = self.fact_service.add_fact(
                statement=data['statement'],
                context=data.get('context', {})
            )
            
            return jsonify({
                'success': success,
                'message': message
            }), 201 if success else 400
        
        @self.app.route('/api/search', methods=['POST'])
        def search_facts():
            """POST /api/search - Suche Facts"""
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
        
        @self.app.route('/api/reason', methods=['POST'])
        def reason():
            """POST /api/reason - Reasoning Endpoint with Device Info"""
            data = request.get_json()
            
            if not data or 'query' not in data:
                return jsonify({'error': 'Missing query'}), 400
            
            result = self.reasoning_service.reason(data['query'])
            
            response = {
                'query': result.query,
                'confidence': result.confidence,
                'reasoning_terms': result.reasoning_terms,
                'success': result.success,
                'high_confidence': result.is_high_confidence()
            }
            
            # Add device info if available
            if result.metadata and 'device' in result.metadata:
                response['device'] = result.metadata['device']
            
            return jsonify(response)
        
        @self.app.route('/api/architecture', methods=['GET'])
        def architecture():
            """Architecture Information"""
            return jsonify({
                'pattern': 'Hexagonal Architecture',
                'layers': {
                    'core': {
                        'domain': 'Business Entities (Fact, Query, ReasoningResult)',
                        'ports': 'Interfaces (FactRepository, ReasoningEngine)'
                    },
                    'application': 'Use Cases (FactManagementService, ReasoningService)',
                    'adapters': {
                        'inbound': 'REST API (Flask)',
                        'outbound': {
                            'legacy': 'LegacyFactRepository, LegacyReasoningEngine',
                            'sqlite': 'SQLiteFactRepository'
                        }
                    }
                },
                'benefits': [
                    'Testability - Core logic ohne Infrastructure',
                    'Flexibility - Einfacher Wechsel von Adapters',
                    'Maintainability - Klare Trennung der Concerns'
                ]
            })
    
    def run(self, host='127.0.0.1', port=5001, debug=True):
        """Starte Flask Application"""
        print("=" * 60)
        print("🎯 HAK-GAL HEXAGONAL ARCHITECTURE")
        print("=" * 60)
        print(f"🚀 Starting on http://{host}:{port}")
        print(f"📦 Repository: {self.fact_repository.__class__.__name__}")
        print(f"🧠 Reasoning: {self.reasoning_engine.__class__.__name__}")
        print("=" * 60)
        print("Endpoints:")
        print("  GET  /health           - Health Check")
        print("  GET  /api/status       - System Status")
        print("  GET  /api/facts        - List Facts")
        print("  POST /api/facts        - Add Fact")
        print("  POST /api/search       - Search Facts")
        print("  POST /api/reason       - Reasoning")
        print("  GET  /api/architecture - Architecture Info")
        print("=" * 60)
        
        self.app.run(host=host, port=port, debug=debug)

# Main Entry Point
def create_app(use_legacy=False):
    """Factory Function für App Creation"""
    return HexagonalAPI(use_legacy=use_legacy)

if __name__ == '__main__':
    # Start with SQLite/Hex adapters by default
    api = create_app(use_legacy=False)
    api.run()
