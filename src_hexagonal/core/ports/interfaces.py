"""
Hexagonal Ports - Die Interfaces/Contracts
===========================================
Nach HAK/GAL Verfassung: Definiert WAS das System kann, nicht WIE
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.domain.entities import Fact, Query, ReasoningResult

# ========== PRIMARY PORTS (Driving/Inbound) ==========

class FactManagementUseCase(ABC):
    """Primary Port: Use Cases für Fact Management"""
    
    @abstractmethod
    def add_fact(self, statement: str, context: Dict = None) -> tuple[bool, str]:
        """Füge einen neuen Fakt hinzu"""
        pass
    
    @abstractmethod
    def search_facts(self, query: Query) -> List[Fact]:
        """Suche nach Fakten"""
        pass
    
    @abstractmethod
    def get_all_facts(self, limit: int = 100) -> List[Fact]:
        """Hole alle Fakten"""
        pass
    
    @abstractmethod
    def get_system_status(self) -> Dict[str, Any]:
        """Hole System-Status"""
        pass

class ReasoningUseCase(ABC):
    """Primary Port: Use Cases für Reasoning"""
    
    @abstractmethod
    def reason(self, query: str) -> ReasoningResult:
        """Führe Reasoning auf Query aus"""
        pass
    
    @abstractmethod
    def get_confidence(self, statement: str) -> float:
        """Hole Confidence für Statement"""
        pass

# ========== SECONDARY PORTS (Driven/Outbound) ==========

class FactRepository(ABC):
    """Secondary Port: Persistenz für Facts"""
    
    @abstractmethod
    def save(self, fact: Fact) -> bool:
        """Speichere einen Fakt"""
        pass
    
    @abstractmethod
    def find_by_query(self, query: str, limit: int = 10) -> List[Fact]:
        """Finde Facts nach Query"""
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100) -> List[Fact]:
        """Hole alle Facts"""
        pass
    
    @abstractmethod
    def exists(self, statement: str) -> bool:
        """Prüfe ob Fact existiert"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Zähle alle Facts"""
        pass

    @abstractmethod
    def delete_by_statement(self, statement: str) -> int:
        """Lösche Facts mit exakt passendem Statement. Rückgabe: Anzahl gelöschter Zeilen"""
        pass

    @abstractmethod
    def update_statement(self, old_statement: str, new_statement: str) -> int:
        """Ersetze exakt passendes Statement. Rückgabe: Anzahl ersetzter Zeilen"""
        pass

class ReasoningEngine(ABC):
    """Secondary Port: Reasoning Services"""
    
    @abstractmethod
    def compute_confidence(self, query: str) -> Dict[str, Any]:
        """Berechne Confidence für Query"""
        pass
    
    @abstractmethod
    def analyze_statement(self, statement: str) -> Dict[str, Any]:
        """Analysiere ein Statement"""
        pass

class LLMProvider(ABC):
    """Secondary Port: LLM Services"""
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generiere LLM Response"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Prüfe Verfügbarkeit"""
        pass
