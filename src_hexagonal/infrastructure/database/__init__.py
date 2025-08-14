"""
Database Infrastructure for HEXAGONAL
"""

from .knowledge_repository import KnowledgeBaseRepository, get_knowledge_repository

__all__ = [
    'KnowledgeBaseRepository',
    'get_knowledge_repository'
]
