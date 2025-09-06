#!/usr/bin/env python3
"""
HAK-GAL Neural Knowledge Network Visualizer
============================================
Erstellt interaktive 3D-Visualisierungen der Knowledge Base
mit Zoom, Clustering und neuronaler Netzwerk-Darstellung
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import random
import math
from collections import defaultdict, Counter

class KnowledgeVisualizer:
    """
    Generiert interaktive 3D Knowledge Graphs im Neural Network Style
    """
    
    def __init__(self, db_path: str = None):
        # Find database
        if db_path:
            self.db_path = db_path
        else:
            # Try standard paths
            for path in [
                Path("hexagonal_kb.db"),
                Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db"),
                Path("../hexagonal_kb.db")
            ]:
                if path.exists():
                    self.db_path = str(path)
                    break
            else:
                raise FileNotFoundError("Database not found!")
        
        print(f"[DB] Using database: {self.db_path}")
        self.colors = {
            'HAK_GAL': '#FF6B6B',      # Red - System Core
            'Backend': '#4ECDC4',       # Teal - Backend
            'Frontend': '#45B7D1',      # Blue - Frontend  
            'Database': '#96CEB4',      # Green - Database
            'AI': '#FFEAA7',           # Yellow - AI/LLM
            'MCP': '#DDA0DD',          # Plum - MCP Tools
            'Network': '#FFB6C1',       # Pink - Network
            'Default': '#95A5A6'       # Gray - Default
        }
        
    def get_category(self, entity: str) -> str:
        """