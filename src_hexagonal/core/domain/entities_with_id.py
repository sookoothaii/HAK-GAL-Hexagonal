"""
Domain Entities - Das Herz der Hexagonal Architecture
======================================================
Nach HAK/GAL Verfassung: Pure Business Logic ohne Dependencies
ENHANCED: ID support for frontend compatibility
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class Fact:
    """Core Domain Entity - Ein Fakt in der Wissensbasis"""
    statement: str
    confidence: float = 1.0
    context: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def is_valid(self) -> bool:
        """Business Rule: Fact muss mit Punkt enden"""
        return self.statement.endswith('.')
    
    def to_dict(self) -> Dict:
        """Convert to dict - ENHANCED with ID support"""
        result = {
            'statement': self.statement,
            'confidence': self.confidence,
            'context': self.context,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Extract ID from metadata if present and add as top-level field
        if self.metadata and 'id' in self.metadata:
            result['id'] = self.metadata['id']
        
        return result

@dataclass
class Query:
    """Domain Entity für Suchanfragen"""
    text: str
    limit: int = 10
    min_confidence: float = 0.5
    
@dataclass
class ReasoningResult:
    """Domain Entity für Reasoning-Ergebnisse"""
    query: str
    confidence: float
    reasoning_terms: List[str]
    success: bool
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_high_confidence(self) -> bool:
        """Business Rule: High confidence ist > 0.8"""
        return self.confidence > 0.8
