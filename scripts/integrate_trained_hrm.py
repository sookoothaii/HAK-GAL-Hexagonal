#!/usr/bin/env python3
"""
HRM Integration Script - Updates the HRM System with Trained Model
===================================================================
"""

import torch
import torch.nn as nn
from pathlib import Path
import shutil
from datetime import datetime

def update_hrm_system():
    """Update hrm_system.py to use the ImprovedHRM model"""
    
    hrm_system_path = Path("src_hexagonal/core/reasoning/hrm_system.py")
    
    # Backup current file
    backup_path = hrm_system_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
    shutil.copy(hrm_system_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # New HRM system code with trained model support
    new_hrm_code = '''"""
HRM System for HEXAGONAL - Enhanced Version with Trained Model
==============================================================
Neural Reasoning Model with actual training support
"""

import torch
import torch.nn as nn
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class ImprovedHRM(nn.Module):
    """
    Improved HRM Model with GRU and Attention
    """
    def __init__(self, vocab_size: int = 5000, embedding_dim: int = 128, 
                 hidden_dim: int = 256, num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        
        # Embedding layers
        self.entity_embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.predicate_embedding = nn.Embedding(100, embedding_dim)
        
        # GRU for sequence processing
        self.gru = nn.GRU(
            embedding_dim * 2,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(hidden_dim * 2, num_heads=4, batch_first=True)
        
        # Output layers
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, entities, predicates):
        # Embed inputs
        entity_emb = self.entity_embedding(entities)
        pred_emb = self.predicate_embedding(predicates)
        
        # Concatenate embeddings
        combined = torch.cat([entity_emb, pred_emb.unsqueeze(1).expand(-1, entity_emb.size(1), -1)], dim=-1)
        
        # GRU processing
        gru_out, _ = self.gru(combined)
        
        # Self-attention
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)
        
        # Global pooling
        pooled = torch.mean(attn_out, dim=1)
        
        # Classification
        x = self.dropout(pooled)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        output = self.fc2(x)
        
        return self.sigmoid(output).squeeze(-1)


class HRMSystem:
    """Enhanced Hierarchical Reasoning Model System"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize HRM System with trained model support"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.vocab = {'<PAD>': 0, '<UNK>': 1}
        self.predicate_vocab = {'<UNK>': 0}
        self.model_path = model_path or "models/hrm_model_v2.pth"
        
        # Try to load trained model
        if self._load_trained_model():
            logger.info(f"[HRM] Loaded trained model from {self.model_path}")
        else:
            # Fallback to simple model
            logger.warning("[HRM] No trained model found, using fallback")
            self.model = ImprovedHRM().to(self.device)
            self.model.eval()
    
    def _load_trained_model(self) -> bool:
        """Load trained model from checkpoint"""
        model_file = Path(self.model_path)
        
        if not model_file.exists():
            # Try relative path
            model_file = Path(__file__).parent.parent.parent.parent / self.model_path
            
        if model_file.exists():
            try:
                checkpoint = torch.load(model_file, map_location=self.device)
                
                # Load vocabularies
                self.vocab = checkpoint.get('vocab', self.vocab)
                self.predicate_vocab = checkpoint.get('predicate_vocab', self.predicate_vocab)
                
                # Initialize model with correct config
                config = checkpoint.get('model_config', {})
                self.model = ImprovedHRM(
                    vocab_size=config.get('vocab_size', len(self.vocab)),
                    embedding_dim=config.get('embedding_dim', 128),
                    hidden_dim=config.get('hidden_dim', 256),
                    num_layers=config.get('num_layers', 2),
                    dropout=config.get('dropout', 0.2)
                ).to(self.device)
                
                # Load weights
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.model.eval()
                
                # Log metrics
                metrics = checkpoint.get('metrics', {})
                logger.info(f"[HRM] Model metrics: {metrics}")
                
                return True
                
            except Exception as e:
                logger.error(f"[HRM] Error loading model: {e}")
                return False
        
        return False
    
    def _parse_query(self, query: str) -> Optional[Dict]:
        """Parse query into predicate and entities"""
        import re
        
        # Pattern: Predicate(Entity1, Entity2)
        pattern = r'^([A-Z][A-Za-z0-9_]*)\(([^,]+),\s*([^\)]+)\)'
        match = re.match(pattern, query.strip())
        
        if match:
            return {
                'predicate': match.group(1),
                'entities': [match.group(2).strip(), match.group(3).strip()]
            }
        return None
    
    def _encode_query(self, parsed_query: Dict) -> tuple:
        """Encode query for model input"""
        # Encode entities
        entity_ids = []
        for entity in parsed_query['entities']:
            entity_ids.append(self.vocab.get(entity, 1))  # 1 is <UNK>
            
        # Encode predicate
        pred_id = self.predicate_vocab.get(parsed_query['predicate'], 0)
        
        return (
            torch.tensor([entity_ids], dtype=torch.long).to(self.device),
            torch.tensor([pred_id], dtype=torch.long).to(self.device)
        )
    
    def reason(self, query: str) -> Dict[str, Any]:
        """Perform reasoning on a query using trained model"""
        try:
            # Parse query
            parsed = self._parse_query(query)
            
            if not parsed or self.model is None:
                # Fallback to pattern-based reasoning
                confidence = 0.5
                if 'IsA(' in query or 'HasPart(' in query:
                    confidence = 0.85
                elif 'Not' in query or '!' in query:
                    confidence = 0.15
                    
            else:
                # Use trained model
                with torch.no_grad():
                    entities, predicate = self._encode_query(parsed)
                    confidence = self.model(entities, predicate).item()
            
            # Generate reasoning terms based on confidence
            if confidence > 0.7:
                reasoning_terms = ['Valid', 'Confirmed', 'High confidence', 'Supported by model']
            elif confidence < 0.3:
                reasoning_terms = ['Unlikely', 'Low confidence', 'Doubtful', 'Model disagrees']
            else:
                reasoning_terms = ['Possible', 'Uncertain', 'Needs verification', 'Moderate confidence']
            
            return {
                'query': query,
                'confidence': float(confidence),
                'success': True,
                'reasoning_terms': reasoning_terms,
                'device': str(self.device),
                'model_type': 'ImprovedHRM' if self.model else 'Fallback'
            }
            
        except Exception as e:
            logger.error(f"[HRM] Reasoning error: {e}")
            return {
                'query': query,
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def batch_reason(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Perform batch reasoning on multiple queries"""
        results = []
        for query in queries:
            results.append(self.reason(query))
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get HRM system status"""
        return {
            'status': 'operational',
            'device': str(self.device),
            'model_type': 'ImprovedHRM' if self.model else 'Fallback',
            'cuda_available': torch.cuda.is_available(),
            'parameters': sum(p.numel() for p in self.model.parameters()) if self.model else 0,
            'vocab_size': len(self.vocab),
            'predicate_count': len(self.predicate_vocab),
            'model_path': str(self.model_path)
        }
    
    def update_from_feedback(self, query: str, feedback: str):
        """Update model based on user feedback (for future online learning)"""
        # This is a placeholder for future online learning implementation
        logger.info(f"[HRM] Feedback received for '{query}': {feedback}")
        # In future: implement online learning/fine-tuning

# Singleton instance
_hrm_instance = None

def get_hrm_instance(model_path: Optional[str] = None) -> HRMSystem:
    """Get or create HRM instance"""
    global _hrm_instance
    if _hrm_instance is None:
        _hrm_instance = HRMSystem(model_path)
    return _hrm_instance
'''
    
    # Write new code
    with open(hrm_system_path, 'w', encoding='utf-8') as f:
        f.write(new_hrm_code)
    
    print(f"✅ Updated {hrm_system_path}")
    print("\nThe HRM system has been updated to support trained models!")
    print("\nNext steps:")
    print("1. Train the model: python train_hrm_model.py")
    print("2. The trained model will be automatically loaded when backend restarts")
    print("3. HRM will now provide real neural reasoning confidence scores")

if __name__ == "__main__":
    print("="*60)
    print("HRM SYSTEM UPDATE")
    print("="*60)
    
    update_hrm_system()
    
    print("\n" + "="*60)
    print("UPDATE COMPLETE!")
    print("="*60)
