"""
Application Services - Use Case Implementierungen
==================================================
Nach HAK/GAL Verfassung: Orchestriert Domain Logic und Ports
"""

from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ports.interfaces import (
    FactManagementUseCase,
    ReasoningUseCase,
    FactRepository,
    ReasoningEngine,
    LLMProvider
)
from core.domain.entities import Fact, Query, ReasoningResult

class FactManagementService(FactManagementUseCase):
    """
    Application Service für Fact Management
    Orchestriert zwischen Domain und Infrastructure
    """
    
    def __init__(self, 
                 fact_repository: FactRepository,
                 reasoning_engine: Optional[ReasoningEngine] = None):
        self.repository = fact_repository
        self.reasoning_engine = reasoning_engine
    
    def add_fact(self, statement: str, context: Dict = None) -> tuple[bool, str]:
        """Füge neuen Fact hinzu mit Business Rules"""
        
        # Business Rule: Statement muss mit Punkt enden
        if not statement.endswith('.'):
            statement = statement + '.'
        
        # Prüfe ob bereits existiert (idempotent)
        if self.repository.exists(statement):
            return False, "Fact already exists"
        
        # Erstelle Domain Entity
        fact = Fact(
            statement=statement,
            context=context or {},
            confidence=1.0
        )
        
        # Validiere Business Rules
        if not fact.is_valid():
            return False, "Invalid fact format"
        
        # Speichere über Repository
        success = self.repository.save(fact)
        
        if success:
            return True, f"Fact added: {statement}"
        else:
            return False, "Failed to save fact"
    
    def search_facts(self, query: Query) -> List[Fact]:
        """Suche Facts mit Query"""
        return self.repository.find_by_query(
            query.text, 
            limit=query.limit
        )
    
    def get_all_facts(self, limit: int = 100) -> List[Fact]:
        """Hole alle Facts"""
        return self.repository.find_all(limit)
    
    def get_system_status(self) -> Dict[str, Any]:
        """System Status mit Metriken"""
        fact_count = self.repository.count()
        
        return {
            'status': 'operational',
            'architecture': 'hexagonal',
            'fact_count': fact_count,  # FIXED: fact_count statt facts_count!
            'repository_type': self.repository.__class__.__name__,
            'reasoning_available': self.reasoning_engine is not None
        }

    def delete_fact(self, statement: str) -> tuple[bool, str]:
        """Lösche einen Fact und gib Erfolg zurück."""
        if not self.repository.exists(statement):
            return False, "Fact not found"

        # FIX: Call the correct repository method `delete_by_statement`
        deleted_count = self.repository.delete_by_statement(statement)

        if deleted_count > 0:
            return True, f"Fact deleted: {statement}"
        else:
            return False, "Failed to delete fact or fact not found"

class ReasoningService(ReasoningUseCase):
    """
    Application Service für Reasoning
    """
    
    def __init__(self, 
                 reasoning_engine: ReasoningEngine,
                 fact_repository: Optional[FactRepository] = None):
        self.engine = reasoning_engine
        self.repository = fact_repository
    
    def reason(self, query: str) -> ReasoningResult:
        """Führe Reasoning aus mit Device Info und Feedback Support"""
        
        # Nutze Reasoning Engine
        result = self.engine.compute_confidence(query)
        
        # Map zu Domain Entity
        confidence = result.get('confidence', 0.0)
        base_confidence = result.get('base_confidence', confidence)
        
        # Use original reasoning terms if available, otherwise generate
        reasoning_terms = result.get('reasoning_terms', [])
        if not reasoning_terms:
            # Fallback Business Logic für Reasoning Terms
            if confidence > 0.8:
                reasoning_terms = ["Valid", "Confirmed", "High confidence"]
            elif confidence > 0.5:
                reasoning_terms = ["Plausible", "Likely", "Moderate confidence"]
            elif confidence > 0.2:
                reasoning_terms = ["Uncertain", "Possible", "Low confidence"]
            else:
                reasoning_terms = ["Unlikely", "Doubtful", "Very low confidence"]
        
        # Create result with all metadata
        reasoning_result = ReasoningResult(
            query=query,
            confidence=confidence,
            reasoning_terms=reasoning_terms,
            success=result.get('success', True)
        )
        
        # Add all metadata from engine
        reasoning_result.metadata = {
            'base_confidence': base_confidence,
            'feedback_applied': result.get('feedback_applied', False)
        }
        
        # Add device info if available
        if 'device' in result:
            reasoning_result.metadata['device'] = result['device']
            
        # Add feedback history if available
        if 'feedback_history' in result:
            reasoning_result.metadata['feedback_history'] = result['feedback_history']
        
        return reasoning_result
    
    def get_confidence(self, statement: str) -> float:
        """Hole Confidence für Statement"""
        result = self.engine.compute_confidence(statement)
        return result.get('confidence', 0.0)
