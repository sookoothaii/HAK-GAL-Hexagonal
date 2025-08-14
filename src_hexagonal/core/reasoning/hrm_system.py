"""
HRM System for HEXAGONAL - Standalone Version
=============================================
Simplified Neural Reasoning Model
"""

import torch
import torch.nn as nn
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SimplifiedHRM(nn.Module):
    """Simplified HRM Model"""
    
    def __init__(self, vocab_size: int = 1000, hidden_dim: int = 256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, batch_first=True)
        self.output = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        output = self.output(lstm_out[:, -1, :])
        return self.sigmoid(output)

class HRMSystem:
    """Hierarchical Reasoning Model System"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize HRM System"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = SimplifiedHRM().to(self.device)
        self.model_path = model_path
        
        # Try to load existing model
        if model_path and Path(model_path).exists():
            try:
                checkpoint = torch.load(model_path, map_location=self.device)
                if 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                logger.info(f"[HRM] Loaded model from {model_path}")
            except Exception as e:
                logger.warning(f"[HRM] Could not load model: {e}")
        else:
            logger.info("[HRM] Using untrained model")
    
    def reason(self, query: str) -> Dict[str, Any]:
        """Perform reasoning on a query"""
        try:
            # Simple pattern-based reasoning (placeholder)
            confidence = 0.5
            
            # Adjust confidence based on query patterns
            if 'IsA(' in query or 'HasPart(' in query:
                confidence = 0.85
            elif 'Not' in query or '!' in query:
                confidence = 0.15
            elif 'Maybe' in query or '?' in query:
                confidence = 0.5
                
            # Determine reasoning terms
            if confidence > 0.7:
                reasoning_terms = ['Valid', 'Confirmed', 'High confidence']
            elif confidence < 0.3:
                reasoning_terms = ['Unlikely', 'Low confidence', 'Doubtful']
            else:
                reasoning_terms = ['Possible', 'Uncertain', 'Needs verification']
            
            return {
                'query': query,
                'confidence': confidence,
                'success': True,
                'reasoning_terms': reasoning_terms,
                'device': str(self.device)
            }
            
        except Exception as e:
            logger.error(f"[HRM] Reasoning error: {e}")
            return {
                'query': query,
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get HRM system status"""
        return {
            'status': 'operational',
            'device': str(self.device),
            'model_type': 'SimplifiedHRM',
            'cuda_available': torch.cuda.is_available(),
            'parameters': sum(p.numel() for p in self.model.parameters())
        }

# Singleton instance
_hrm_instance = None

def get_hrm_instance(model_path: Optional[str] = None) -> HRMSystem:
    """Get or create HRM instance"""
    global _hrm_instance
    if _hrm_instance is None:
        _hrm_instance = HRMSystem(model_path)
    return _hrm_instance
