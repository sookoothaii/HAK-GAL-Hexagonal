"""
HRM Feedback Adapter - PROGRESSIVE LEARNING VERSION
====================================================
Implementiert progressives Lernen statt statischer Neuberechnung
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import threading
import math

class HRMFeedbackAdapter:
    """
    Progressive Learning Version - Confidence wächst mit jedem Feedback
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize feedback adapter with persistent storage."""
        if data_path is None:
            self.data_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/hrm_feedback.json")
        else:
            self.data_path = data_path if isinstance(data_path, Path) else Path(data_path)
        
        self.feedback_history: Dict[str, List[Dict]] = {}
        self.confidence_adjustments: Dict[str, float] = {}
        self.lock = threading.RLock()
        
        # Progressive Learning Parameters
        self.base_learning_rate = 0.02  # 2% per positive feedback
        self.max_confidence = 0.95  # Maximum 95% confidence
        self.negative_impact = 0.5  # Negative feedback has half impact
        self.saturation_factor = 0.9  # Learning slows as confidence increases
        self.max_history = 100
        
        # Load existing feedback data
        self._load_feedback()
    
    def _load_feedback(self):
        """Load feedback history from disk."""
        if self.data_path.exists():
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.feedback_history = data.get('history', {})
                    self.confidence_adjustments = data.get('adjustments', {})
            except Exception as e:
                print(f"Error loading feedback data: {e}")
    
    def _save_feedback(self):
        """Save feedback history to disk."""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'history': self.feedback_history,
                    'adjustments': self.confidence_adjustments,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving feedback data: {e}")
    
    def add_feedback(self, query: str, verification_type: str, 
                     original_confidence: float, user_id: Optional[str] = None) -> Dict:
        """
        Add feedback with PROGRESSIVE learning
        """
        with self.lock:
            query_key = self._normalize_query(query)
            
            if query_key not in self.feedback_history:
                self.feedback_history[query_key] = []
            
            # Create feedback entry
            feedback = {
                'timestamp': datetime.now().isoformat(),
                'type': verification_type,
                'original_confidence': original_confidence,
                'user_id': user_id or 'anonymous'
            }
            
            # Add to history
            self.feedback_history[query_key].append(feedback)
            if len(self.feedback_history[query_key]) > self.max_history:
                self.feedback_history[query_key] = self.feedback_history[query_key][-self.max_history:]
            
            # Calculate PROGRESSIVE adjustment
            adjustment = self._calculate_progressive_adjustment(query_key, verification_type, original_confidence)
            
            # Update stored adjustment
            self.confidence_adjustments[query_key] = adjustment
            
            # Save to disk
            self._save_feedback()
            
            # Return updated metrics
            return {
                'query': query,
                'new_confidence': min(1.0, max(0.0, original_confidence + adjustment)),
                'adjustment': adjustment,
                'total_feedback': len(self.feedback_history[query_key]),
                'learning_rate': self.base_learning_rate
            }
    
    def _calculate_progressive_adjustment(self, query_key: str, verification_type: str, 
                                         original_confidence: float) -> float:
        """
        Progressive learning: Each feedback adds to total adjustment
        
        Key innovation: Learning accumulates over time rather than being recalculated
        """
        history = self.feedback_history.get(query_key, [])
        if not history:
            return 0.0
        
        # Start with existing adjustment or 0
        current_adjustment = self.confidence_adjustments.get(query_key, 0.0)
        
        # Calculate total confidence (base + adjustment)
        total_confidence = original_confidence + current_adjustment
        
        # Saturation: Learning slows as confidence approaches limits
        if total_confidence > 0.8:
            # Approaching maximum confidence
            saturation = math.exp(-10 * (total_confidence - 0.8))  # Exponential decay
        elif total_confidence < 0.2:
            # Very low confidence - learn faster
            saturation = 2.0 - 5 * total_confidence  # Boost at low confidence
        else:
            # Normal learning range
            saturation = 1.0
        
        # Calculate incremental change based on this feedback
        if verification_type == 'positive':
            # Positive feedback increases confidence
            increment = self.base_learning_rate * saturation
            
            # Boost for consistent positive feedback
            recent_positive = sum(1 for f in history[-10:] if f['type'] == 'positive')
            if recent_positive >= 8:  # 80% recent positive
                increment *= 1.2
                
        else:  # negative
            # Negative feedback decreases confidence
            increment = -self.base_learning_rate * self.negative_impact * saturation
        
        # Add increment to current adjustment
        new_adjustment = current_adjustment + increment
        
        # Apply bounds
        # Maximum adjustment limited by max_confidence minus base confidence
        max_adjustment = self.max_confidence - original_confidence
        min_adjustment = -original_confidence  # Can't go below 0
        
        new_adjustment = max(min_adjustment, min(max_adjustment, new_adjustment))
        
        return new_adjustment
    
    def get_adjusted_confidence(self, query: str, base_confidence: float) -> Tuple[float, Dict]:
        """Get adjusted confidence for a query."""
        with self.lock:
            query_key = self._normalize_query(query)
            
            # Get stored adjustment
            adjustment = self.confidence_adjustments.get(query_key, 0.0)
            
            # Apply adjustment to base confidence
            adjusted = min(1.0, max(0.0, base_confidence + adjustment))
            
            # Gather metadata
            history = self.feedback_history.get(query_key, [])
            positive_count = sum(1 for h in history if h.get('type') == 'positive')
            negative_count = sum(1 for h in history if h.get('type') == 'negative')
            
            metadata = {
                'base_confidence': base_confidence,
                'adjustment': adjustment,
                'adjusted_confidence': adjusted,
                'feedback_count': len(history),
                'positive_feedback': positive_count,
                'negative_feedback': negative_count,
                'has_history': len(history) > 0
            }
            
            return adjusted, metadata
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for consistent storage."""
        normalized = ' '.join(query.strip().split())
        if not normalized.endswith('.'):
            normalized += '.'
        return normalized.lower()
    
    def get_statistics(self) -> Dict:
        """Get overall feedback statistics."""
        with self.lock:
            total_queries = len(self.feedback_history)
            total_feedback = sum(len(h) for h in self.feedback_history.values())
            
            avg_adjustment = 0.0
            if self.confidence_adjustments:
                avg_adjustment = sum(self.confidence_adjustments.values()) / len(self.confidence_adjustments)
            
            return {
                'total_queries_with_feedback': total_queries,
                'total_feedback_entries': total_feedback,
                'average_adjustment': avg_adjustment,
                'learning_rate': self.base_learning_rate,
                'max_confidence': self.max_confidence
            }
    
    def clear_old_feedback(self, days: int = 30):
        """Clear feedback older than specified days."""
        with self.lock:
            cutoff = datetime.now() - timedelta(days=days)
            
            for query_key in list(self.feedback_history.keys()):
                filtered = []
                for entry in self.feedback_history[query_key]:
                    try:
                        entry_time = datetime.fromisoformat(entry['timestamp'])
                        if entry_time > cutoff:
                            filtered.append(entry)
                    except:
                        filtered.append(entry)
                
                if filtered:
                    self.feedback_history[query_key] = filtered
                else:
                    del self.feedback_history[query_key]
                    if query_key in self.confidence_adjustments:
                        del self.confidence_adjustments[query_key]
            
            self._save_feedback()

# Global instance
hrm_feedback = HRMFeedbackAdapter()
