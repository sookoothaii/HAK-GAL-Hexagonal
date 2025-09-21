"""
KNOWLEDGE GRAPH VISUALIZATION SYSTEM
=====================================
Sofort einsatzbereit nach den Test-Fixes!
"""

from flask import Flask, jsonify, request, render_template_string
import sqlite3
import json
import re
from collections import defaultdict
import math

def add_knowledge_graph_features(app, fact_repository):
    """
    Fügt REVOLUTIONÄRE Knowledge Graph Features hinzu!
    """
    
    @app.route('/api/graph/network', methods=['GET'])
    def get_knowledge_network():
        """
        Liefert das komplette Knowledge Network für 3D-Visualisierung
        """
        try:
            limit = request.args.get('limit', 1000, type=int)
            
            with sqlite3.connect(fact_repository.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT statement FROM facts LIMIT ?", (limit,))
                facts = cursor.fetchall()
            
            # Build Network
            nodes = {}
            edges = []
            node_types = defaultdict(int)
            
            # Parse facts
            for fact in facts:
                statement = fact[0]
                # Pattern: Predicate(Entity1, Entity2)
                match = re.match(r'(\w+)\(([^,\)]+)(?:,\s*([^,\)]+))?\)', statement)
                
                if match:
                    predicate = match.group(1)
                    entity1 = match.group(2).strip()
                    entity2 = match.group(3).strip() if match.group(3) else None
                    
                    # Create nodes
                    if entity1 not in nodes:
                        nodes[entity1] = {
                            'id': entity1,
                            'label': entity1,
                            'size': 1,
                            'type': 'entity',
                            'x': math.cos(len(nodes) * 0.5) * 100,
                            'y': math.sin(len(nodes) * 0.5) * 100,
                            'z': (len(nodes) % 10) * 10
                        }
                    nodes[entity1]['size'] += 1
                    
                    if entity2:
                        if entity2 not in nodes:
                            nodes[entity2] = {
                                'id': entity2,
                                'label': entity2,
                                'size': 1,
                                'type': 'entity',
                                'x': math.cos(len(nodes) * 0.5) * 100,
                                'y': math.sin(len(nodes) * 0.5) * 100,
                                'z': (len(nodes) % 10) * 10
                            }
                        nodes[entity2]['size'] += 1
                        
                        # Create edge
                        edges.append({
                            'source': entity1,
                            'target': entity2,
                            'type': predicate,
                            'weight': 1,
                            'color': f'hsl({hash(predicate) % 360}, 70%, 50%)'
                        })
                    
                    node_types[predicate] += 1
            
            # Calculate statistics
            total_nodes = len(nodes)
            total_edges = len(edges)
            avg_degree = (2 * total_edges / total_nodes) if total_nodes > 0 else 0
            
            # Find most connected nodes (hubs)
            node_degrees = defaultdict(int)
            for edge in edges:
                node_degrees[edge['source']] += 1
                node_degrees[edge['target']] += 1
            
            top_hubs = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return jsonify({
                'nodes': list(nodes.values()),
                'edges': edges,
                'statistics': {
                    'total_nodes': total_nodes,
                    'total_edges': total_edges,
                    'average_degree': round(avg_degree, 2),
                    'edge_types': dict(node_types),
                    'top_hubs': [{'node': h[0], 'connections': h[1]} for h in top_hubs],
                    'density': round((2 * total_edges) / (total_nodes * (total_nodes - 1)) if total_nodes > 1 else 0, 4)
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/graph/shortest-path', methods=['POST'])
    def find_shortest_path():
        """
        Findet den kürzesten Pfad zwischen zwei Entitäten im Knowledge Graph
        """
        try:
            data = request.json
            start = data.get('start')
            end = data.get('end')
            
            if not start or not end:
                return jsonify({'error': 'Missing start or end entity'}), 400
            
            # Build graph from facts
            with sqlite3.connect(fact_repository.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT statement FROM facts")
                facts = cursor.fetchall()
            
            # Create adjacency list
            graph = defaultdict(list)
            
            for fact in facts:
                statement = fact[0]
                match = re.match(r'(\w+)\(([^,\)]+)(?:,\s*([^,\)]+))?\)', statement)
                
                if match and match.group(3):
                    entity1 = match.group(2).strip()
                    entity2 = match.group(3).strip()
                    predicate = match.group(1)
                    
                    graph[entity1].append((entity2, predicate))
                    graph[entity2].append((entity1, predicate))  # Bidirectional
            
            # BFS to find shortest path
            from collections import deque
            
            queue = deque([(start, [start], [])])
            visited = {start}
            
            while queue:
                current, path, predicates = queue.popleft()
                
                if current == end:
                    return jsonify({
                        'found': True,
                        'path': path,
                        'predicates': predicates,
                        'length': len(path) - 1
                    })
                
                for neighbor, predicate in graph[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((
                            neighbor,
                            path + [neighbor],
                            predicates + [predicate]
                        ))
            
            return jsonify({
                'found': False,
                'message': f'No path found between {start} and {end}'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/graph/clusters', methods=['GET'])
    def detect_clusters():
        """
        Erkennt Wissens-Cluster mit Community Detection
        """
        try:
            min_size = request.args.get('min_size', 3, type=int)
            
            with sqlite3.connect(fact_repository.db_path) as conn:
                cursor = conn.cursor()
                
                # Group by predicate types
                cursor.execute("""
                    SELECT 
                        SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
                        COUNT(*) as count,
                        GROUP_CONCAT(statement, '|||') as examples
                    FROM facts
                    WHERE INSTR(statement, '(') > 0
                    GROUP BY predicate
                    HAVING count >= ?
                    ORDER BY count DESC
                """, (min_size,))
                
                clusters = []
                
                for pred, count, examples_str in cursor.fetchall():
                    example_list = examples_str.split('|||')[:5]  # First 5 examples
                    
                    # Extract entities from examples
                    entities = set()
                    for ex in example_list:
                        match = re.match(r'\w+\(([^,\)]+)(?:,\s*([^,\)]+))?\)', ex)
                        if match:
                            entities.add(match.group(1).strip())
                            if match.group(2):
                                entities.add(match.group(2).strip())
                    
                    clusters.append({
                        'name': pred,
                        'size': count,
                        'entities': list(entities),
                        'examples': example_list,
                        'density': round(count / len(entities) if entities else 0, 2)
                    })
                
                return jsonify({
                    'clusters': clusters,
                    'total_clusters': len(clusters)
                })
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/graph/recommend-facts', methods=['POST'])
    def recommend_new_facts():
        """
        KI-basierte Empfehlung für neue Facts basierend auf Graph-Struktur
        """
        try:
            data = request.json
            entity = data.get('entity')
            
            if not entity:
                return jsonify({'error': 'Missing entity'}), 400
            
            recommendations = []
            
            with sqlite3.connect(fact_repository.db_path) as conn:
                cursor = conn.cursor()
                
                # Find similar entities
                cursor.execute("""
                    SELECT statement FROM facts
                    WHERE statement LIKE '%' || ? || '%'
                    LIMIT 20
                """, (entity,))
                
                related_facts = cursor.fetchall()
                
                # Extract patterns
                patterns = defaultdict(list)
                for fact in related_facts:
                    statement = fact[0]
                    match = re.match(r'(\w+)\(([^,\)]+)(?:,\s*([^,\)]+))?\)', statement)
                    if match:
                        pred = match.group(1)
                        e1 = match.group(2).strip()
                        e2 = match.group(3).strip() if match.group(3) else None
                        
                        if e1 != entity and e2 != entity:
                            continue
                            
                        patterns[pred].append((e1, e2))
                
                # Generate recommendations
                for pred, instances in patterns.items():
                    # Find common partners
                    partners = [e2 if e1 == entity else e1 for e1, e2 in instances if e2]
                    
                    if partners:
                        # Suggest new connections
                        for partner in partners[:3]:
                            # Check if reverse exists
                            reverse = f"{pred}({partner}, {entity})"
                            cursor.execute(
                                "SELECT COUNT(*) FROM facts WHERE statement = ?",
                                (reverse,)
                            )
                            
                            if cursor.fetchone()[0] == 0:
                                recommendations.append({
                                    'statement': reverse,
                                    'confidence': 0.7,
                                    'reason': f'Symmetric relation suggested based on {pred}({entity}, {partner})'
                                })
                
                # Limit recommendations
                recommendations = recommendations[:10]
                
                return jsonify({
                    'entity': entity,
                    'recommendations': recommendations,
                    'count': len(recommendations)
                })
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

print("""
✅ KNOWLEDGE GRAPH SYSTEM BEREIT!

Neue Endpoints:
- GET  /api/graph/network       - 3D Network Daten
- POST /api/graph/shortest-path - Pfadfindung
- GET  /api/graph/clusters      - Cluster Detection  
- POST /api/graph/recommend-facts - KI Empfehlungen

Integration:
1. Diese Features zur API hinzufügen
2. Frontend mit Three.js/D3.js verbinden
3. Real-time Updates via WebSocket

IMPACT: 
- Visual Knowledge Exploration
- Pattern Discovery
- Automated Knowledge Growth
""")
