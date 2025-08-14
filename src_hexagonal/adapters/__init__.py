"""
Adapters Package - Hexagonal Architecture
=========================================
Nach HAK/GAL Verfassung: Infrastructure Adapters
"""

from .legacy_adapters import LegacyFactRepository, LegacyReasoningEngine
from .sqlite_adapter import SQLiteFactRepository
from .websocket_adapter import WebSocketAdapter, create_websocket_adapter
from .governor_adapter import GovernorAdapter, get_governor_adapter

__all__ = [
    'LegacyFactRepository',
    'LegacyReasoningEngine', 
    'SQLiteFactRepository',
    'WebSocketAdapter',
    'create_websocket_adapter',
    'GovernorAdapter',
    'get_governor_adapter'
]
