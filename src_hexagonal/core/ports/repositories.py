# Repository Interfaces
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src_hexagonal.core.domain.entities import Fact, FactGroup


class FactRepositoryInterface(ABC):
    """Port for fact storage operations"""
    
    @abstractmethod
    def add(self, fact: Fact) -> bool:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Fact]:
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Fact]:
        pass
    
    @abstractmethod
    def delete(self, statement: str) -> bool:
        pass
    
    @abstractmethod
    def update(self, old_statement: str, new_statement: str) -> bool:
        pass
    
    @abstractmethod
    def get_count(self) -> int:
        pass
    
    @abstractmethod
    def get_recent(self, limit: int = 10) -> List[Fact]:
        pass


class FactGroupRepositoryInterface(ABC):
    """Port for fact group operations"""
    
    @abstractmethod
    def create_group(self, name: str, facts: List[str]) -> FactGroup:
        pass
    
    @abstractmethod
    def get_group(self, group_id: str) -> Optional[FactGroup]:
        pass
    
    @abstractmethod
    def list_groups(self) -> List[FactGroup]:
        pass
    
    @abstractmethod
    def add_to_group(self, group_id: str, facts: List[str]) -> bool:
        pass


class LearningRepositoryInterface(ABC):
    """Port for HRM learning data"""
    
    @abstractmethod
    def save_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def load_feedback(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_model_performance(self) -> Dict[str, float]:
        pass
