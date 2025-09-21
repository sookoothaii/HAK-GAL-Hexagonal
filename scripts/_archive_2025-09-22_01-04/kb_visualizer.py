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
        """Determine category for coloring"""
        entity_lower = entity.lower()
        
        if 'hak' in entity_lower or 'gal' in entity_lower:
            return 'HAK_GAL'
        elif 'backend' in entity_lower or 'api' in entity_lower or 'flask' in entity_lower:
            return 'Backend'
        elif 'frontend' in entity_lower or 'react' in entity_lower or 'ui' in entity_lower:
            return 'Frontend'
        elif 'database' in entity_lower or 'sqlite' in entity_lower or 'db' in entity_lower:
            return 'Database'
        elif 'llm' in entity_lower or 'ai' in entity_lower or 'model' in entity_lower or 'qwen' in entity_lower:
            return 'AI'
        elif 'mcp' in entity_lower or 'tool' in entity_lower:
            return 'MCP'
        elif 'network' in entity_lower or 'port' in entity_lower or 'http' in entity_lower:
            return 'Network'
        else:
            return 'Default'
    
    def extract_graph_data(self, limit: int = 500, focus: str = None) -> dict:
        """Extract knowledge graph from database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        if focus:
            # Focus on specific entity and its connections
            query = """
                SELECT DISTINCT statement FROM facts 
                WHERE statement LIKE ? OR statement LIKE ?
                LIMIT ?
            """
            cursor.execute(query, (f'%{focus}%', f'%{focus},%', limit))
        else:
            # Get most connected facts
            query = """
                SELECT statement FROM facts 
                WHERE statement NOT LIKE '%HasFrequency%'
                AND statement NOT LIKE '%Node[0-9]%'
                AND statement NOT LIKE '%EntityCount%'
                ORDER BY RANDOM()
                LIMIT ?
            """
            cursor.execute(query, (limit,))
        
        facts = cursor.fetchall()
        
        # Build graph structure
        nodes = {}
        edges = []
        node_connections = defaultdict(int)
        node_id_map = {}
        current_id = 0
        
        for (statement,) in facts:
            try:
                # Parse statement
                if '(' not in statement or ')' not in statement:
                    continue
                    
                pred_end = statement.index('(')
                predicate = statement[:pred_end]
                
                args_str = statement[pred_end+1:statement.rindex(')')].strip()
                args = [arg.strip() for arg in args_str.split(',')]
                
                if len(args) >= 2:
                    subject = args[0]
                    obj = args[1]
                    
                    # Skip invalid entities
                    if not subject or not obj or subject == obj:
                        continue
                    
                    # Create/update nodes
                    for entity in [subject, obj]:
                        if entity not in node_id_map:
                            node_id_map[entity] = current_id
                            current_id += 1
                            
                            nodes[entity] = {
                                'id': node_id_map[entity],
                                'label': entity,
                                'value': 1,
                                'group': self.get_category(entity),
                                'color': self.colors[self.get_category(entity)],
                                'title': f"{entity}\nConnections: 1"
                            }
                        else:
                            nodes[entity]['value'] += 1
                            nodes[entity]['title'] = f"{entity}\nConnections: {nodes[entity]['value']}"
                    
                    node_connections[subject] += 1
                    node_connections[obj] += 1
                    
                    # Create edge
                    edges.append({
                        'source': node_id_map[subject],
                        'target': node_id_map[obj],
                        'label': predicate,
                        'value': 1,
                        'title': f"{predicate}({subject}, {obj})"
                    })
                    
            except Exception as e:
                continue
        
        conn.close()
        
        # Apply clustering layout hints
        nodes_list = list(nodes.values())
        
        # Position highly connected nodes centrally
        for node in nodes_list:
            connections = node['value']
            if connections > 10:
                node['mass'] = 5  # Heavy nodes stay central
            elif connections > 5:
                node['mass'] = 3
            else:
                node['mass'] = 1
        
        return {
            'nodes': nodes_list,
            'edges': edges,
            'stats': {
                'total_nodes': len(nodes_list),
                'total_edges': len(edges),
                'categories': dict(Counter(n['group'] for n in nodes_list))
            }
        }
    
    def generate_html(self, output_path: str = None, limit: int = 500, focus: str = None):
        """Generate interactive HTML visualization"""
        
        if not output_path:
            output_path = "frontend/public/knowledge_graph.html"
        
        print(f"[GENERATE] Creating graph with {limit} facts...")
        if focus:
            print(f"[FOCUS] Centering on: {focus}")
        
        graph_data = self.extract_graph_data(limit, focus)
        
        print(f"[STATS] Generated {graph_data['stats']['total_nodes']} nodes, {graph_data['stats']['total_edges']} edges")
        
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HAK-GAL Neural Knowledge Network</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            overflow: hidden;
        }
        #network {
            width: 100vw;
            height: 100vh;
            position: relative;
        }
        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0