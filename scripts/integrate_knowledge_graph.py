"""
INTEGRATE KNOWLEDGE GRAPH INTO API - SOFORT!
============================================
"""

import os
import re

api_file = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py"

print("=" * 70)
print("ADDING KNOWLEDGE GRAPH TO API")
print("=" * 70)

# Lese API
with open(api_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Knowledge Graph Code
knowledge_graph_code = '''
        # ============= KNOWLEDGE GRAPH SYSTEM =============
        @self.app.route('/api/graph/network', methods=['GET'])
        def get_knowledge_network():
            """3D Knowledge Network for Visualization"""
            try:
                import math
                from collections import defaultdict
                
                limit = request.args.get('limit', 1000, type=int)
                
                with sqlite3.connect(self.fact_repository.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT statement FROM facts LIMIT ?", (limit,))
                    facts = cursor.fetchall()
                
                nodes = {}
                edges = []
                
                for fact in facts:
                    statement = fact[0]
                    match = re.match(r'(\w+)\(([^,\)]+)(?:,\s*([^,\)]+))?\)', statement)
                    
                    if match:
                        predicate = match.group(1)
                        entity1 = match.group(2).strip()
                        entity2 = match.group(3).strip() if match.group(3) else None
                        
                        if entity1 not in nodes:
                            nodes[entity1] = {
                                'id': entity1,
                                'label': entity1,
                                'size': 1,
                                'x': math.cos(len(nodes) * 0.5) * 100,
                                'y': math.sin(len(nodes) * 0.5) * 100,
                                'z': (len(nodes) % 10) * 10,
                                'color': f'hsl({hash(entity1) % 360}, 70%, 50%)'
                            }
                        nodes[entity1]['size'] += 1
                        
                        if entity2:
                            if entity2 not in nodes:
                                nodes[entity2] = {
                                    'id': entity2,
                                    'label': entity2,
                                    'size': 1,
                                    'x': math.cos(len(nodes) * 0.5) * 100,
                                    'y': math.sin(len(nodes) * 0.5) * 100,
                                    'z': (len(nodes) % 10) * 10,
                                    'color': f'hsl({hash(entity2) % 360}, 70%, 50%)'
                                }
                            nodes[entity2]['size'] += 1
                            
                            edges.append({
                                'source': entity1,
                                'target': entity2,
                                'type': predicate,
                                'weight': 1
                            })
                
                return jsonify({
                    'nodes': list(nodes.values()),
                    'edges': edges,
                    'stats': {
                        'total_nodes': len(nodes),
                        'total_edges': len(edges),
                        'density': round(2*len(edges)/(len(nodes)*(len(nodes)-1)) if len(nodes)>1 else 0, 4)
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/graph/clusters', methods=['GET'])
        def detect_clusters():
            """Detect Knowledge Clusters"""
            try:
                with sqlite3.connect(self.fact_repository.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT 
                            SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
                            COUNT(*) as count
                        FROM facts
                        WHERE INSTR(statement, '(') > 0
                        GROUP BY predicate
                        ORDER BY count DESC
                        LIMIT 20
                    """)
                    
                    clusters = []
                    for pred, count in cursor.fetchall():
                        clusters.append({
                            'name': pred,
                            'size': count,
                            'color': f'hsl({hash(pred) % 360}, 70%, 50%)'
                        })
                    
                    return jsonify({'clusters': clusters, 'total': len(clusters)})
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/graph/path', methods=['POST'])
        def find_knowledge_path():
            """Find shortest path between entities"""
            try:
                from collections import deque, defaultdict
                
                data = request.json
                start = data.get('start')
                end = data.get('end')
                
                if not start or not end:
                    return jsonify({'error': 'Missing start or end'}), 400
                
                with sqlite3.connect(self.fact_repository.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT statement FROM facts")
                    facts = cursor.fetchall()
                
                # Build graph
                graph = defaultdict(list)
                for fact in facts:
                    statement = fact[0]
                    match = re.match(r'(\w+)\(([^,\)]+)(?:,\s*([^,\)]+))?\)', statement)
                    if match and match.group(3):
                        e1 = match.group(2).strip()
                        e2 = match.group(3).strip()
                        pred = match.group(1)
                        graph[e1].append((e2, pred))
                        graph[e2].append((e1, pred))
                
                # BFS
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
                    
                    for neighbor, pred in graph[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, path + [neighbor], predicates + [pred]))
                
                return jsonify({'found': False, 'message': f'No path between {start} and {end}'})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
'''

# Füge Knowledge Graph vor den CORS Options handler ein
if '/api/graph/network' not in content:
    insertion_point = content.find("@self.app.route('/<path:any_path>', methods=['OPTIONS'])")
    if insertion_point > 0:
        content = content[:insertion_point] + knowledge_graph_code + "\n        " + content[insertion_point:]
        print("✅ Knowledge Graph endpoints added!")
    else:
        print("❌ Could not find insertion point")
else:
    print("✅ Knowledge Graph already exists")

# Speichern
with open(api_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 70)
print("✅ KNOWLEDGE GRAPH INTEGRATED!")
print("=" * 70)
print("\nNEUE ENDPOINTS:")
print("  - GET  /api/graph/network")
print("  - GET  /api/graph/clusters")  
print("  - POST /api/graph/path")
print("\n1. Server neu starten")
print("2. curl -X GET http://localhost:5002/api/graph/network")
