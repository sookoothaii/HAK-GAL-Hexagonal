#!/usr/bin/env python3
"""
HAK-GAL Graph Generator API Endpoint
=====================================
Integriert die Graph-Generierung direkt ins Backend
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from flask import jsonify

def generate_knowledge_graph(db_path="hexagonal_kb.db", limit=500, focus=None):
    """Generate knowledge graph data for API endpoint"""
    
    # Color mapping for categories
    colors = {
        'HAK_GAL': '#FF6B6B',      # Red - System Core
        'Backend': '#4ECDC4',       # Teal - Backend
        'Frontend': '#45B7D1',      # Blue - Frontend  
        'Database': '#96CEB4',      # Green - Database
        'AI': '#FFEAA7',           # Yellow - AI/LLM
        'MCP': '#DDA0DD',          # Plum - MCP Tools
        'Network': '#FFB6C1',       # Pink - Network
        'Default': '#95A5A6'       # Gray - Default
    }
    
    def get_category(entity):
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
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Build query
        if focus:
            query = """
                SELECT DISTINCT statement FROM facts 
                WHERE (statement LIKE ? OR statement LIKE ?)
                AND statement NOT LIKE '%HasFrequency%'
                AND statement NOT LIKE '%Count%'
                AND length(statement) > 10
                LIMIT ?
            """
            cursor.execute(query, (f'%{focus}%', f'%{focus},%', limit))
        else:
            query = """
                SELECT statement FROM facts 
                WHERE statement NOT LIKE '%HasFrequency%'
                AND statement NOT LIKE '%Node[0-9]%'
                AND statement NOT LIKE '%EntityCount%'
                AND statement NOT LIKE '%Count[0-9]%'
                AND length(statement) > 10
                ORDER BY RANDOM()
                LIMIT ?
            """
            cursor.execute(query, (limit,))
        
        facts = cursor.fetchall()
        
        # Build graph structure
        nodes = {}
        edges = []
        node_id_map = {}
        current_id = 0
        
        for (statement,) in facts:
            try:
                if '(' not in statement or ')' not in statement:
                    continue
                    
                pred_end = statement.index('(')
                predicate = statement[:pred_end]
                
                if 'Frequency' in predicate or 'Count' in predicate:
                    continue
                
                args_str = statement[pred_end+1:statement.rindex(')')].strip()
                args = [arg.strip() for arg in args_str.split(',')]
                
                if len(args) >= 2:
                    subject = args[0]
                    obj = args[1]
                    
                    if not subject or not obj or subject == obj:
                        continue
                    if 'Count' in subject or 'Count' in obj:
                        continue
                    if len(subject) < 2 or len(obj) < 2:
                        continue
                    
                    # Create/update nodes
                    for entity in [subject, obj]:
                        if entity not in node_id_map:
                            node_id_map[entity] = current_id
                            current_id += 1
                            
                            category = get_category(entity)
                            nodes[entity] = {
                                'id': node_id_map[entity],
                                'label': entity,
                                'value': 1,
                                'group': category,
                                'color': colors[category],
                                'title': f"{entity}\nConnections: 1"
                            }
                        else:
                            nodes[entity]['value'] += 1
                            nodes[entity]['title'] = f"{entity}\nConnections: {nodes[entity]['value']}"
                    
                    # Create edge
                    edges.append({
                        'from': node_id_map[subject],
                        'to': node_id_map[obj],
                        'label': predicate,
                        'title': f"{predicate}({subject}, {obj})",
                        'color': {
                            'color': 'rgba(150,150,150,0.5)',
                            'highlight': '#4444ff',
                            'hover': '#6666ff'
                        },
                        'width': 2,
                        'arrows': 'to'
                    })
                    
            except Exception:
                continue
        
        conn.close()
        
        # Adjust node sizes
        nodes_list = list(nodes.values())
        for node in nodes_list:
            connections = node['value']
            if connections > 10:
                node['size'] = 30
            elif connections > 5:
                node['size'] = 25
            else:
                node['size'] = 20
        
        return {
            'success': True,
            'nodes': nodes_list,
            'edges': edges,
            'stats': {
                'total_nodes': len(nodes_list),
                'total_edges': len(edges),
                'categories': dict(Counter(n['group'] for n in nodes_list))
            },
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'nodes': [],
            'edges': [],
            'stats': {'total_nodes': 0, 'total_edges': 0}
        }

def generate_graph_html(graph_data):
    """Generate the HTML file with graph data"""
    
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
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            min-width: 250px;
        }
        #controls {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.95);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        .control-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .control-btn:hover {
            background: #2980b9;
            transform: scale(1.05);
        }
        h2 {
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 24px;
        }
        .stat {
            margin: 8px 0;
            color: #555;
            font-size: 14px;
        }
        .stat strong {
            color: #2c3e50;
            font-weight: 600;
        }
        #search {
            width: 100%;
            padding: 8px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .legend {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 13px;
        }
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div id="network"></div>
    
    <div id="info">
        <h2>🧠 HAK-GAL Knowledge Network</h2>
        <div class="stat">Nodes: <strong>''' + str(graph_data.get('stats', {}).get('total_nodes', 0)) + '''</strong></div>
        <div class="stat">Edges: <strong>''' + str(graph_data.get('stats', {}).get('total_edges', 0)) + '''</strong></div>
        <div class="stat">Updated: <strong>''' + datetime.now().strftime('%H:%M:%S') + '''</strong></div>
        
        <input type="text" id="search" placeholder="Search nodes..." onkeyup="searchNodes(this.value)">
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #FF6B6B;"></div>
                <span>HAK-GAL Core</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #4ECDC4;"></div>
                <span>Backend</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #45B7D1;"></div>
                <span>Frontend</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #96CEB4;"></div>
                <span>Database</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFEAA7;"></div>
                <span>AI/LLM</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #DDA0DD;"></div>
                <span>MCP Tools</span>
            </div>
        </div>
    </div>
    
    <div id="controls">
        <button class="control-btn" onclick="network.fit()">🎯 Fit View</button>
        <button class="control-btn" onclick="startSimulation()">▶️ Start Physics</button>
        <button class="control-btn" onclick="stopSimulation()">⏸️ Stop Physics</button>
        <button class="control-btn" onclick="toggleClustering()">🔄 Toggle Cluster</button>
    </div>
    
    <script>
        const graphData = ''' + json.dumps(graph_data) + ''';
        
        const container = document.getElementById('network');
        
        const data = {
            nodes: new vis.DataSet(graphData.nodes || []),
            edges: new vis.DataSet(graphData.edges || [])
        };
        
        const options = {
            nodes: {
                shape: 'dot',
                scaling: {
                    min: 10,
                    max: 40,
                    label: {
                        min: 12,
                        max: 24,
                        drawThreshold: 5,
                        maxVisible: 30
                    }
                },
                font: {
                    size: 14,
                    color: '#ffffff',
                    strokeWidth: 3,
                    strokeColor: '#000000'
                },
                borderWidth: 2,
                borderWidthSelected: 4,
                shadow: true
            },
            edges: {
                smooth: {
                    type: 'continuous',
                    roundness: 0.5
                },
                width: 2,
                selectionWidth: 3,
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.5
                    }
                },
                font: {
                    size: 10,
                    color: '#666',
                    strokeWidth: 2,
                    strokeColor: '#ffffff',
                    align: 'middle'
                }
            },
            physics: {
                enabled: true,
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: 200,
                    springConstant: 0.08,
                    damping: 0.4,
                    avoidOverlap: 0.5
                },
                stabilization: {
                    enabled: true,
                    iterations: 200,
                    updateInterval: 25
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
                zoomView: true,
                dragView: true,
                navigationButtons: true,
                keyboard: true
            },
            layout: {
                improvedLayout: true,
                randomSeed: 42
            }
        };
        
        const network = new vis.Network(container, data, options);
        
        function searchNodes(query) {
            if (!query) {
                data.nodes.forEach(node => {
                    data.nodes.update({id: node.id, hidden: false});
                });
                return;
            }
            
            query = query.toLowerCase();
            data.nodes.forEach(node => {
                const show = node.label.toLowerCase().includes(query);
                data.nodes.update({id: node.id, hidden: !show});
            });
        }
        
        function startSimulation() {
            network.setOptions({physics: {enabled: true}});
        }
        
        function stopSimulation() {
            network.setOptions({physics: {enabled: false}});
        }
        
        let clustered = false;
        function toggleClustering() {
            if (!clustered) {
                const groups = [...new Set(graphData.nodes.map(n => n.group))];
                groups.forEach(group => {
                    network.cluster({
                        joinCondition: function(nodeOptions) {
                            return nodeOptions.group === group;
                        },
                        clusterNodeProperties: {
                            label: group,
                            color: graphData.nodes.find(n => n.group === group)?.color || '#95A5A6',
                            shape: 'square',
                            size: 40
                        }
                    });
                });
                clustered = true;
            } else {
                network.openCluster();
                clustered = false;
            }
        }
        
        network.on("click", function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const connectedNodes = network.getConnectedNodes(nodeId);
                
                const updateArray = [];
                data.nodes.forEach(node => {
                    if (connectedNodes.includes(node.id) || node.id === nodeId) {
                        updateArray.push({id: node.id, opacity: 1});
                    } else {
                        updateArray.push({id: node.id, opacity: 0.3});
                    }
                });
                data.nodes.update(updateArray);
            }
        });
        
        network.on("doubleClick", function(params) {
            const updateArray = [];
            data.nodes.forEach(node => {
                updateArray.push({id: node.id, opacity: 1});
            });
            data.nodes.update(updateArray);
        });
        
        network.once("stabilizationIterationsDone", function() {
            network.setOptions({physics: {enabled: false}});
        });
    </script>
</body>
</html>'''
    
    return html