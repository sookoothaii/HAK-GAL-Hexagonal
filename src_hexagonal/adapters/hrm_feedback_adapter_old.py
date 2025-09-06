"""
HRM Feedback Adapter - Learning through Human Verification
===========================================================
Nach HAK/GAL Verfassung Artikel 1 (Komplementäre Intelligenz)
und Artikel 6 (Empirische Validierung)

Implements a feedback loop for HRM confidence learning based on human verification.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import threading

class HRMFeedbackAdapter:
    """
    Manages HRM confidence feedback and learning.
    Stores feedback history and adjusts confidence based on human verification.
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize feedback adapter with persistent storage."""
        # Use absolute path for data storage
        if data_path is None:
            self.data_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/hrm_feedback.json")
        else:
            self.data_path = data_path if isinstance(data_path, Path) else Path(data_path)
        
        self.feedback_history: Dict[str, List[Dict]] = {}
        self.confidence_adjustments: Dict[str, float] = {}
        self.lock = threading.RLock()
        
        # Learning parameters
        self.base_learning_rate = 0.1  # How much each verification affects confidence
        self.decay_factor = 0.95  # How much old feedback decays
        self.max_history = 100  # Max feedback entries per query
        
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
        Add feedback for a query.
        
        Args:
            query: The query/statement that was verified
            verification_type: 'positive' (confirmed) or 'negative' (rejected)
            original_confidence: The original HRM confidence
            user_id: Optional user identifier
        
        Returns:
            Dict with updated confidence and learning metrics
        """
        with self.lock:
            # Normalize query
            query_key = self._normalize_query(query)
            
            # Initialize history if needed
            if query_key not in self.feedback_history:
                self.feedback_history[query_key] = []
            
            # Create feedback entry
            feedback = {
                'timestamp': datetime.now().isoformat(),
                'type': verification_type,
                'original_confidence': original_confidence,
                'user_id': user_id or 'anonymous'
            }
            
            # Add to history (limit size)
            self.feedback_history[query_key].append(feedback)
            if len(self.feedback_history[query_key]) > self.max_history:
                self.feedback_history[query_key] = self.feedback_history[query_key][-self.max_history:]
            
            # Calculate confidence adjustment
            adjustment = self._calculate_adjustment(query_key, verification_type, original_confidence)
            
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
    
    def _calculate_adjustment(self, query_key: str, verification_type: str, 
                              original_confidence: float) -> float:
        """
        Calculate confidence adjustment based on feedback history.
        
        Uses a weighted average of historical feedback with decay.
        """
        history = self.feedback_history.get(query_key, [])
        if not history:
            return 0.0
        
        # Calculate weighted score based on feedback history
        total_weight = 0.0
        weighted_score = 0.0
        now = datetime.now()
        
        for i, entry in enumerate(reversed(history)):  # Most recent first
            # Calculate age-based weight (exponential decay)
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                age_hours = (now - entry_time).total_seconds() / 3600
                weight = self.decay_factor ** (age_hours / 24)  # Daily decay
            except:
                weight = self.decay_factor ** i  # Fallback to position-based decay
            
            # Add to weighted score
            if entry['type'] == 'positive':
                weighted_score += weight * 1.0
            else:  # negative
                weighted_score += weight * (-0.5)  # Negative feedback has less impact
            
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Calculate adjustment
        average_score = weighted_score / total_weight
        
        # Scale adjustment based on:
        # 1. Learning rate
        # 2. Number of feedback entries (more confident with more data)
        # 3. Recency of feedback (recent feedback matters more)
        
        confidence_factor = min(1.0, len(history) / 10)  # More data = stronger adjustment
        
        # Remove distance_factor or make it work better
        # Option 1: Constant learning regardless of current confidence
        # distance_factor = 1.0  
        
        # Option 2: Boost learning for very low confidence only
        if original_confidence < 0.1:
            distance_factor = 2.0  # Double learning rate for very uncertain queries
        else:
            distance_factor = 1.0  # Normal learning rate otherwise
        
        adjustment = self.base_learning_rate * average_score * confidence_factor * distance_factor
        
        # Allow larger adjustments for consistent positive feedback
        if average_score > 0.8 and len(history) >= 10:
            # Boost adjustment for strongly positive consensus
            adjustment *= 1.5
        
        # Limit adjustment magnitude (increased from 0.3 to 0.5)
        return max(-0.4, min(0.4, adjustment))
    
    def get_adjusted_confidence(self, query: str, base_confidence: float) -> Tuple[float, Dict]:
        """
        Get adjusted confidence for a query based on feedback history.
        
        Returns:
            Tuple of (adjusted_confidence, metadata)
        """
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
        # Remove extra whitespace and standardize
        normalized = ' '.join(query.strip().split())
        # Ensure consistent punctuation
        if not normalized.endswith('.'):
            normalized += '.'
        return normalized.lower()
    
    def get_statistics(self) -> Dict:
        """Get overall feedback statistics."""
        with self.lock:
            total_queries = len(self.feedback_history)
            total_feedback = sum(len(h) for h in self.feedback_history.values())
            
            # Calculate average adjustments
            avg_adjustment = 0.0
            if self.confidence_adjustments:
                avg_adjustment = sum(self.confidence_adjustments.values()) / len(self.confidence_adjustments)
            
            return {
                'total_queries_with_feedback': total_queries,
                'total_feedback_entries': total_feedback,
                'average_adjustment': avg_adjustment,
                'learning_rate': self.base_learning_rate,
                'decay_factor': self.decay_factor
            }
    
    def clear_old_feedback(self, days: int = 30):
        """Clear feedback older than specified days."""
        with self.lock:
            cutoff = datetime.now() - timedelta(days=days)
            
            for query_key in list(self.feedback_history.keys()):
                # Filter out old entries
                filtered = []
                for entry in self.feedback_history[query_key]:
                    try:
                        entry_time = datetime.fromisoformat(entry['timestamp'])
                        if entry_time > cutoff:
                            filtered.append(entry)
                    except:
                        # Keep entries with invalid timestamps
                        filtered.append(entry)
                
                if filtered:
                    self.feedback_history[query_key] = filtered
                else:
                    # Remove query if no feedback remains
                    del self.feedback_history[query_key]
                    if query_key in self.confidence_adjustments:
                        del self.confidence_adjustments[query_key]
            
            self._save_feedback()

# Global instance
hrm_feedback = HRMFeedbackAdapter()
