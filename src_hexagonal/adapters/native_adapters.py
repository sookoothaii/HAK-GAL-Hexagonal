"""
Native Adapters for HEXAGONAL
==============================
No dependency on HAK_GAL_SUITE!
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import time

# Use local modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ports.interfaces import FactRepository, ReasoningEngine
from core.domain.entities import Fact, ReasoningResult
from core.knowledge.k_assistant import get_k_assistant
from core.reasoning.hrm_system import get_hrm_instance
import os

class NativeFactRepository(FactRepository):
    """Native implementation using local KAssistant"""
    
    def __init__(self, db_path: str = "k_assistant_dev.db"):
        self.k_assistant = get_k_assistant(db_path)
        
    def save(self, fact: Fact) -> bool:
        """Save a fact"""
        success, _ = self.k_assistant.add_fact(
            fact.statement,
            fact.confidence,
            fact.context.get('source', 'hexagonal')
        )
        return success
    
    def find_by_query(self, query: str, limit: int = 10) -> List[Fact]:
        """Search for facts"""
        results = self.k_assistant.search_facts(query, limit)
        
        facts = []
        for result in results:
            facts.append(Fact(
                statement=result['statement'],
                confidence=result.get('confidence', 1.0),
                context={'source': 'native'},
                created_at=datetime.now()
            ))
        return facts
    
    def find_all(self, limit: int = 100) -> List[Fact]:
        """Get all facts"""
        statements = self.k_assistant.get_all_facts(limit)
        
        facts = []
        for statement in statements:
            facts.append(Fact(
                statement=statement,
                confidence=1.0,
                context={'source': 'native'},
                created_at=datetime.now()
            ))
        return facts
    
    def exists(self, statement: str) -> bool:
        """Check if fact exists"""
        results = self.k_assistant.search_facts(statement, limit=1)
        return any(r['statement'] == statement for r in results)
    
    def count(self) -> int:
        """Count facts"""
        metrics = self.k_assistant.get_metrics()
        return metrics.get('fact_count', 0)
    
    def delete_by_statement(self, statement: str) -> int:
        """Delete a fact (not implemented in simplified version)"""
        # Would need to add delete method to KAssistant
        return 0
    
    def update_statement(self, old_statement: str, new_statement: str) -> int:
        """Update a fact (not implemented in simplified version)"""
        # Would need to add update method to KAssistant
        return 0

class NativeReasoningEngine(ReasoningEngine):
    """Native implementation using local HRM with feedback support"""
    
    def __init__(self):
        # Optional: spezifischen Modellpfad aus ENV nutzen
        model_path = os.environ.get('HRM_MODEL_PATH') or 'models/hrm_model_v2.pth'
        self.hrm = get_hrm_instance(model_path)
        
        # Initialize feedback data path
        self.feedback_path = Path(__file__).parent.parent.parent / 'data' / 'hrm_feedback.json'
        self.feedback_data = self._load_feedback_data()
        
        # Cache for adjusted confidences
        self.confidence_cache = {}
        self.cache_ttl = 300  # 5 minutes TTL
    
    def _load_feedback_data(self) -> Dict[str, Any]:
        """Load feedback data from persistent storage"""
        if self.feedback_path.exists():
            try:
                with open(self.feedback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Failed to load feedback data: {e}")
        return {'history': {}, 'adjustments': {}, 'statistics': {}, 'verified_queries': {}}
    
    def _save_feedback_data(self):
        """Save feedback data to persistent storage"""
        try:
            self.feedback_path.parent.mkdir(exist_ok=True)
            with open(self.feedback_path, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            print(f"[WARNING] Failed to save feedback data: {e}")
    
    def _apply_feedback_adjustment(self, query: str, base_confidence: float) -> float:
        """Apply feedback adjustments to confidence score"""
        # If already at maximum confidence, no adjustment needed
        if base_confidence >= 0.99:
            return base_confidence
            
        # Check if query has adjustments
        if query in self.feedback_data.get('adjustments', {}):
            adjustment = self.feedback_data['adjustments'][query]
            base_adj = adjustment.get('base_adjustment', 0.0)
            feedback_ratio = adjustment.get('feedback_ratio', 0.5)
            
            # Apply adjustment: increase confidence based on positive feedback ratio
            # Scale the adjustment based on how far from 1.0 we are
            room_to_improve = 1.0 - base_confidence
            adjusted = base_confidence + (base_adj * feedback_ratio * room_to_improve)
            
            # Additional boost if query is verified
            if query in self.feedback_data.get('verified_queries', {}):
                verified_data = self.feedback_data['verified_queries'][query]
                if verified_data.get('verified', False):
                    confidence_override = verified_data.get('confidence_override')
                    if confidence_override is not None:
                        adjusted = confidence_override
                    else:
                        # Add 10% boost for verified queries (scaled)
                        adjusted = min(1.0, adjusted + (0.1 * room_to_improve))
            
            # Ensure confidence stays in [0, 1] range
            return max(0.0, min(1.0, adjusted))
        
        # Check if query is verified even without adjustments
        if query in self.feedback_data.get('verified_queries', {}):
            verified_data = self.feedback_data['verified_queries'][query]
            if verified_data.get('verified', False):
                confidence_override = verified_data.get('confidence_override')
                if confidence_override is not None:
                    return confidence_override
                else:
                    # Add small boost for verified queries (scaled)
                    room_to_improve = 1.0 - base_confidence
                    return min(1.0, base_confidence + (0.06 * room_to_improve))
        
        return base_confidence
    
    def compute_confidence(self, query: str) -> Dict[str, Any]:
        """Compute confidence for a query with feedback adjustments"""
        # Reload feedback data to get latest updates
        self.feedback_data = self._load_feedback_data()
        
        # Get base confidence from HRM
        result = self.hrm.reason(query)
        base_confidence = result.get('confidence', 0.5)
        
        # Apply feedback adjustments
        adjusted_confidence = self._apply_feedback_adjustment(query, base_confidence)
        
        # Update result with adjusted confidence
        result['base_confidence'] = base_confidence
        result['confidence'] = adjusted_confidence
        result['feedback_applied'] = (adjusted_confidence != base_confidence)
        
        # Add feedback history if available
        if query in self.feedback_data.get('history', {}):
            history = self.feedback_data['history'][query]
            result['feedback_history'] = {
                'positive': history.get('positive_count', 0),
                'negative': history.get('negative_count', 0),
                'verified': history.get('verified', False)
            }
        
        return result
    
    def analyze_statement(self, statement: str) -> Dict[str, Any]:
        """Analyze a statement with feedback adjustments"""
        return self.compute_confidence(statement)
    
    def apply_feedback(self, query: str, feedback_type: str, confidence_adjustment: float = 0.0):
        """Apply feedback to adjust future confidence scores"""
        # Reload current data
        self.feedback_data = self._load_feedback_data()
        
        # Initialize query history if not exists
        if 'history' not in self.feedback_data:
            self.feedback_data['history'] = {}
        if query not in self.feedback_data['history']:
            self.feedback_data['history'][query] = {
                'positive_count': 0,
                'negative_count': 0,
                'last_feedback': None,
                'confidence_adjustments': []
            }
        
        # Update feedback counts
        if feedback_type == 'positive':
            self.feedback_data['history'][query]['positive_count'] += 1
        elif feedback_type == 'negative':
            self.feedback_data['history'][query]['negative_count'] += 1
        
        self.feedback_data['history'][query]['last_feedback'] = time.time()
        
        # Calculate and store adjustment
        if 'adjustments' not in self.feedback_data:
            self.feedback_data['adjustments'] = {}
        
        history = self.feedback_data['history'][query]
        total_feedback = history['positive_count'] + history['negative_count']
        if total_feedback > 0:
            feedback_ratio = history['positive_count'] / total_feedback
            self.feedback_data['adjustments'][query] = {
                'base_adjustment': confidence_adjustment if confidence_adjustment != 0 else 0.06,
                'feedback_ratio': feedback_ratio,
                'updated_at': time.time()
            }
        
        # Save updated feedback data
        self._save_feedback_data()
        
        # Clear cache for this query
        if query in self.confidence_cache:
            del self.confidence_cache[query]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information from HRM"""
        info = self.hrm.get_status()
        info['feedback_enabled'] = True
        info['feedback_queries'] = len(self.feedback_data.get('history', {}))
        info['verified_queries'] = len(self.feedback_data.get('verified_queries', {}))
        return info
    
    def retrain(self):
        """Trigger model retraining (not implemented yet)"""
        raise NotImplementedError("HRM retraining not yet implemented")
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        self.feedback_data = self._load_feedback_data()
        stats = self.feedback_data.get('statistics', {})
        
        return {
            'total_feedback': stats.get('total_feedback', 0),
            'positive_feedback': stats.get('positive_feedback', 0),
            'negative_feedback': stats.get('negative_feedback', 0),
            'last_feedback': max(
                [h.get('last_feedback', 0) for h in self.feedback_data.get('history', {}).values() if h.get('last_feedback') is not None],
                default=None
            ),
            'model_version': 'v2',
            'feedback_enabled': True,
            'total_queries_with_feedback': len(self.feedback_data.get('history', {})),
            'total_verified_queries': len(self.feedback_data.get('verified_queries', {}))
        }
