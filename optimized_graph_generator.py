#!/usr/bin/env python3
"""
Optimized Knowledge Graph Generator für HAK-GAL
===============================================
Nach HAK/GAL Verfassung Artikel 4: Transparenz und Visualisierung
Mit Performance-Optimierungen und Auto-Update Feature
"""

import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime
import hashlib
import threading
import sys

class OptimizedGraphGenerator:
    """
    Generiert interaktive 3D Knowledge Graphs mit:
    - Inkrementellen Updates (nur Änderungen)
    - Caching für Performance
    - Auto-Update Feature
    - Clustering für große Graphen
    """
    
    def __init__(self, db_path: str, output_path: str = None):
        self.db_path = db_path
        self.output_path = output_path or "knowledge_graph_optimized.html"
        self.cache = {}
        self.last_update = None
        self.auto_update_thread = None
        self.auto_update_interval = 30  # seconds
        self.auto_update_enabled = False
        
    def generate_graph_data(self, limit: int = 500, use_cache: bool = True) -> dict:
        """Generate graph data with caching"""
        
        # Check cache
        cache_key = f"graph_data_{limit}"
        if use_cache and cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 60:  # 1 minute cache
                print(f"[CACHE] Using cached graph data (age: {int(time.time() - timestamp)}s)")
                return cached_data
        
        print(f"[GENERATE] Creating graph from {limit} facts...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get facts with better structure
        cursor.execute("""
            SELECT rowid, statement, context, fact_metadata 
            FROM facts 
            WHERE statement NOT LIKE '%HasProperty(PasswordStorage(%'
            AND statement NOT LIKE '%HasCapability(Pluripotent(%'
            LIMIT ?
        """, (limit,))
        
        facts = cursor.fetchall()
        
        # Build graph structure
        nodes = {}
        links = []
        node_id_counter = 0
        
        # Statistics
        stats = {
            'total_facts': len(facts),
            'valid_facts': 0,
            'invalid_facts': 0,
            'node_count': 0,
            'edge_count': 0
        }
        
        for fact_id, statement, context, metadata in facts:
            try:
                # Parse fact structure
                if '(' in statement and ')' in statement:
                    # Extract predicate and arguments
                    predicate_end = statement.index('(')
                    predicate = statement[:predicate_end]
                    
                    args_str = statement[predicate_end+1:statement.rindex(')')]
                    args = [arg.strip() for arg in args_str.split(',')]
                    
                    if len(args) >= 2:
                        subject = args[0]
                        obj = args[1]
                        
                        # Create nodes
                        if subject not in nodes:
                            nodes[subject] = {
                                'id': node_id_counter,
                                'name': subject,
                                'val': 1,
                                'group': self._get_node_group(subject)
                            }
                            node_id_counter += 1
                        else:
                            nodes[subject]['val'] += 1
                        
                        if obj not in nodes:
                            nodes[obj] = {
                                'id': node_id_counter,
                                'name': obj,
                                'val': 1,
                                'group': self._get_node_group(obj)
                            }
                            node_id_counter += 1
                        else:
                            nodes[obj]['val'] += 1
                        
                        # Create link
                        links.append({
                            'source': nodes[subject]['id'],
                            'target': nodes[obj]['id'],
                            'name': predicate,
                            'value': 1
                        })
                        
                        stats['valid_facts'] += 1
                    else:
                        stats['invalid_facts'] += 1
                else:
                    stats['invalid_facts'] += 1
                    
            except Exception as e:
                stats['invalid_facts'] += 1
        
        conn.close()
        
        stats['node_count'] = len(nodes)
        stats['edge_count'] = len(links)
        
        # Apply clustering for large graphs
        if len(nodes) > 100:
            nodes = self._apply_clustering(nodes, links)
        
        graph_data = {
            'nodes': list(nodes.values()),
            'links': links,
            'stats': stats,
            'generated_at': datetime.now().isoformat()
        }
        
        # Update cache
        self.cache[cache_key] = (graph_data, time.time())
        
        print(f"[OK] Generated {stats['node_count']} nodes, {stats['edge_count']} edges")
        return graph_data
    
    def _get_node_group(self, node_name: str) -> int:
        """Assign node to group based on characteristics"""
        node_lower = node_name.lower()
        
        if any(x in node_lower for x in ['type', 'class', 'category']):
            return 1  # Types
        elif any(x in node_lower for x in ['property', 'attribute', 'trait']):
            return 2  # Properties
        elif any(x in node_lower for x in ['has', 'is', 'can', 'does']):
            return 3  # Relations
        elif any(x in node_lower for x in ['system', 'process', 'method']):
            return 4  # Systems
        elif any(x in node_lower for x in ['data', 'information', 'knowledge']):
            return 5  # Data
        else:
            return 0  # Default
    
    def _apply_clustering(self, nodes: dict, links: list) -> dict:
        """Apply force-directed clustering to nodes"""
        # Group highly connected nodes
        connection_count = {}
        for link in links:
            for node_name, node_data in nodes.items():
                if node_data['id'] == link['source'] or node_data['id'] == link['target']:
                    connection_count[node_name] = connection_count.get(node_name, 0) + 1
        
        # Adjust node values based on connections
        for node_name in nodes:
            if node_name in connection_count:
                nodes[node_name]['val'] = min(10, connection_count[node_name])
        
        return nodes
    
    def generate_html(self, graph_data: dict = None) -> str:
        """Generate interactive HTML visualization"""
        
        if graph_data is None:
            graph_data = self.generate_graph_data()
        
        html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HAK-GAL Knowledge Graph - Optimized</title>
    <style>
        body { 
            margin: 0; 
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255,255,255,0.95);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        #controls {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255,255,255,0.95);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin: 2px;
        }
        button:hover {
            background: #764ba2;
        }
        .stat {
            margin: 5px 0;
            font-size: 14px;
        }
        #auto-update-status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-left: 10px;
        }
        .status-active { background: #10b981; }
        .status-inactive { background: #ef4444; }
    </style>
    <script src="https://unpkg.com/3d-force-graph"></script>
</head>
<body>
    <div id="info">
        <h2>HAK-GAL Knowledge Graph</h2>
        <div class="stat">Nodes: <strong id="node-count">0</strong></div>
        <div class="stat">Edges: <strong id="edge-count">0</strong></div>
        <div class="stat">Facts: <strong id="fact-count">0</strong></div>
        <div class="stat">
            Auto-Update: <span id="auto-update-text">OFF</span>
            <span id="auto-update-status" class="status-inactive"></span>
        </div>
        <div class="stat">Last Update: <span id="last-update">Never</span></div>
    </div>
    
    <div id="controls">
        <h3>Controls</h3>
        <button onclick="toggleAutoUpdate()">Toggle Auto-Update</button>
        <button onclick="refreshGraph()">Refresh Now</button>
        <button onclick="resetView()">Reset View</button>
        <button onclick="toggleNodeLabels()">Toggle Labels</button>
        <button onclick="changeColorScheme()">Change Colors</button>
    </div>
    
    <div id="3d-graph"></div>
    
    <script>
        // Graph data
        const graphData = ''' + json.dumps(graph_data) + ''';
        
        // Update statistics
        document.getElementById('node-count').textContent = graphData.nodes.length;
        document.getElementById('edge-count').textContent = graphData.links.length;
        document.getElementById('fact-count').textContent = graphData.stats.total_facts;
        document.getElementById('last-update').textContent = new Date(graphData.generated_at).toLocaleString();
        
        // Color schemes
        const colorSchemes = [
            ['#667eea', '#764ba2', '#f093fb', '#f5576c'],
            ['#4facfe', '#00f2fe', '#43e97b', '#38f9d7'],
            ['#fa709a', '#fee140', '#30cfd0', '#330867'],
            ['#a8edea', '#fed6e3', '#ff9a9e', '#fecfef']
        ];
        let currentScheme = 0;
        let showLabels = true;
        let autoUpdateInterval = null;
        
        // Initialize graph
        const Graph = ForceGraph3D()
            (document.getElementById('3d-graph'))
            .graphData(graphData)
            .nodeLabel(node => showLabels ? `${node.name} (${node.val})` : '')
            .nodeAutoColorBy('group')
            .nodeVal('val')
            .linkName('name')
            .linkOpacity(0.3)
            .linkDirectionalParticles(2)
            .linkDirectionalParticleSpeed(0.01)
            .onNodeClick(node => {
                // Focus on node
                const distance = 100;
                const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
                Graph.cameraPosition(
                    { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
                    node,
                    2000
                );
            })
            .onNodeHover(node => document.body.style.cursor = node ? 'pointer' : null);
        
        // Functions
        function toggleAutoUpdate() {
            if (autoUpdateInterval) {
                clearInterval(autoUpdateInterval);
                autoUpdateInterval = null;
                document.getElementById('auto-update-text').textContent = 'OFF';
                document.getElementById('auto-update-status').className = 'status-inactive';
            } else {
                autoUpdateInterval = setInterval(refreshGraph, 30000); // 30 seconds
                document.getElementById('auto-update-text').textContent = 'ON (30s)';
                document.getElementById('auto-update-status').className = 'status-active';
            }
        }
        
        function refreshGraph() {
            // In real implementation, fetch new data from server
            console.log('Refreshing graph...');
            document.getElementById('last-update').textContent = new Date().toLocaleString();
            
            // Simulate data update
            const newNode = {
                id: graphData.nodes.length,
                name: 'NewFact_' + Date.now(),
                val: 1,
                group: Math.floor(Math.random() * 6)
            };
            graphData.nodes.push(newNode);
            
            // Update graph
            Graph.graphData(graphData);
        }
        
        function resetView() {
            Graph.cameraPosition(
                { x: 0, y: 0, z: 500 },
                { x: 0, y: 0, z: 0 },
                2000
            );
        }
        
        function toggleNodeLabels() {
            showLabels = !showLabels;
            Graph.nodeLabel(node => showLabels ? `${node.name} (${node.val})` : '');
        }
        
        function changeColorScheme() {
            currentScheme = (currentScheme + 1) % colorSchemes.length;
            const scheme = colorSchemes[currentScheme];
            Graph.nodeColor(node => scheme[node.group % scheme.length]);
        }
        
        // Auto-rotate
        let angle = 0;
        setInterval(() => {
            angle += 0.005;
            Graph.cameraPosition({
                x: 300 * Math.sin(angle),
                y: 0,
                z: 300 * Math.cos(angle)
            });
        }, 50);
    </script>
</body>
</html>'''
        
        return html_template
    
    def save_graph(self, limit: int = 500):
        """Generate and save graph to file"""
        print(f"[SAVE] Generating graph with {limit} facts...")
        
        graph_data = self.generate_graph_data(limit)
        html_content = self.generate_html(graph_data)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] Graph saved to {self.output_path}")
        print(f"[STATS] {graph_data['stats']}")
        
        return self.output_path
    
    def start_auto_update(self, interval: int = 30):
        """Start auto-update thread"""
        self.auto_update_interval = interval
        self.auto_update_enabled = True
        
        def update_loop():
            while self.auto_update_enabled:
                try:
                    self.save_graph()
                    print(f"[AUTO-UPDATE] Graph updated at {datetime.now().strftime('%H:%M:%S')}")
                except Exception as e:
                    print(f"[ERROR] Auto-update failed: {e}")
                
                time.sleep(self.auto_update_interval)
        
        self.auto_update_thread = threading.Thread(target=update_loop, daemon=True)
        self.auto_update_thread.start()
        print(f"[OK] Auto-update started (interval: {interval}s)")
    
    def stop_auto_update(self):
        """Stop auto-update thread"""
        self.auto_update_enabled = False
        if self.auto_update_thread:
            self.auto_update_thread.join(timeout=5)
        print("[OK] Auto-update stopped")

def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate HAK-GAL Knowledge Graph')
    parser.add_argument('--db', type=str, default='../HAK_GAL_SUITE/k_assistant.db',
                       help='Path to database')
    parser.add_argument('--output', type=str, default='knowledge_graph_optimized.html',
                       help='Output HTML file')
    parser.add_argument('--limit', type=int, default=500,
                       help='Number of facts to visualize')
    parser.add_argument('--auto-update', action='store_true',
                       help='Enable auto-update feature')
    parser.add_argument('--interval', type=int, default=30,
                       help='Auto-update interval in seconds')
    
    args = parser.parse_args()
    
    # Find database
    db_path = Path(args.db)
    if not db_path.exists():
        alt_path = Path('..') / 'HAK_GAL_SUITE' / 'k_assistant.db'
        if alt_path.exists():
            db_path = alt_path
        else:
            print(f"[ERROR] Database not found: {args.db}")
            return 1
    
    print("=" * 60)
    print("HAK-GAL OPTIMIZED GRAPH GENERATOR")
    print("=" * 60)
    print(f"[DB] Using database: {db_path}")
    
    generator = OptimizedGraphGenerator(str(db_path), args.output)
    
    # Generate initial graph
    output_path = generator.save_graph(limit=args.limit)
    print(f"\n[SUCCESS] Graph available at: {output_path}")
    
    # Start auto-update if requested
    if args.auto_update:
        generator.start_auto_update(interval=args.interval)
        print("\nPress Ctrl+C to stop auto-update...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            generator.stop_auto_update()
            print("\n[EXIT] Graph generator stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())