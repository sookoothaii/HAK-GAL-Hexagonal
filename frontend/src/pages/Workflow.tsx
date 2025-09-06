import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Panel,
  ReactFlowProvider,
  MarkerType,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';

// Dagre Layout für komplexe Workflows
function dagreLayout(nodes: any[], edges: any[]) {
  const positions = new Map();
  const layers = new Map<number, string[]>();
  const nodeDepths = new Map<string, number>();
  
  // Build adjacency lists
  const graph = new Map<string, { in: string[], out: string[] }>();
  nodes.forEach(n => graph.set(n.id, { in: [], out: [] }));
  
  edges.forEach(e => {
    const src = graph.get(e.source);
    const tgt = graph.get(e.target);
    if (src && tgt) {
      src.out.push(e.target);
      tgt.in.push(e.source);
    }
  });
  
  // Find root nodes and calculate depths
  const roots = nodes.filter(n => graph.get(n.id)?.in.length === 0);
  const visited = new Set<string>();
  
  function calculateDepth(nodeId: string, depth: number = 0) {
    if (visited.has(nodeId)) return;
    visited.add(nodeId);
    
    const currentDepth = nodeDepths.get(nodeId) || 0;
    nodeDepths.set(nodeId, Math.max(currentDepth, depth));
    
    const node = graph.get(nodeId);
    if (node) {
      node.out.forEach(childId => calculateDepth(childId, depth + 1));
    }
  }
  
  roots.forEach(root => calculateDepth(root.id));
  
  // Group nodes by depth
  nodes.forEach(node => {
    const depth = nodeDepths.get(node.id) || 0;
    if (!layers.has(depth)) layers.set(depth, []);
    layers.get(depth)!.push(node.id);
  });
  
  // Position nodes
  const xGap = 200;
  const yGap = 100;
  const startX = 50;
  const startY = 50;
  
  layers.forEach((nodeIds, depth) => {
    const x = startX + depth * xGap;
    nodeIds.forEach((nodeId, index) => {
      const totalInLayer = nodeIds.length;
      const y = startY + index * yGap - (totalInLayer - 1) * yGap / 2 + 200;
      positions.set(nodeId, { x, y });
    });
  });
  
  return nodes.map(node => ({
    ...node,
    position: positions.get(node.id) || { x: 0, y: 0 },
    sourcePosition: Position.Right,
    targetPosition: Position.Left
  }));
}

// Simple Layout für einfache Workflows
function simpleLayout(nodes: any[]) {
  return nodes.map((node, idx) => ({
    ...node,
    position: {
      x: 100 + (idx % 3) * 250,
      y: 100 + Math.floor(idx / 3) * 150
    }
  }));
}

function WorkflowEditor() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState('');
  const [isRunning, setIsRunning] = useState(false);

  // Node-Typ zu Farbe und Icon Mapping
  const getNodeStyle = (type: string, name: string = '') => {
    const combined = `${type} ${name}`.toLowerCase();
    
    if (combined.includes('add') || combined.includes('write') || combined.includes('delete') || combined.includes('save')) {
      return { color: '#EF4444', icon: '⚠️', class: 'WRITE_SENSITIVE' };
    }
    if (combined.includes('delegate') || combined.includes('llm') || combined.includes('claude') || combined.includes('deepseek') || combined.includes('gemini')) {
      return { color: '#8B5CF6', icon: '🤖', class: 'LLM_DELEGATION' };
    }
    if (combined.includes('execute') || combined.includes('compute') || combined.includes('evaluate') || combined.includes('consensus')) {
      return { color: '#3B82F6', icon: '⚙️', class: 'COMPUTATION' };
    }
    if (combined.includes('branch') || combined.includes('parallel') || combined.includes('approval')) {
      return { color: '#F59E0B', icon: '🔀', class: 'UTILITY' };
    }
    if (combined.includes('prepare') || combined.includes('start')) {
      return { color: '#10B981', icon: '🚀', class: 'START' };
    }
    return { color: '#10B981', icon: '📊', class: 'READ_ONLY' };
  };

  // Load workflow - Verbesserte Version
  const loadWorkflow = useCallback(async (path: string) => {
    try {
      const response = await fetch(path);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const wf = await response.json();
      
      console.log('Loading workflow:', path, wf);
      
      // Convert to ReactFlow nodes
      const flowNodes: Node[] = (wf.nodes || []).map((n: any) => {
        const style = getNodeStyle(n.type || '', n.label || n.name || '');
        
        return {
          id: n.id,
          type: 'default',
          data: { 
            label: `${style.icon} ${n.label || n.name || n.type || n.id}`,
            nodeClass: style.class,
            originalData: n
          },
          position: n.position || { x: 0, y: 0 },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
          style: {
            background: 'white',
            border: `2px solid ${style.color}`,
            borderRadius: 8,
            padding: 10,
            fontSize: 12,
            fontWeight: 500,
            minWidth: 140,
            boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
            cursor: 'move'
          }
        };
      });
      
      // Convert edges
      const flowEdges: Edge[] = (wf.edges || []).map((e: any) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label || '',
        type: 'smoothstep',
        animated: true,
        style: { 
          stroke: '#94a3b8', 
          strokeWidth: 2 
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 15,
          height: 15,
          color: '#94a3b8',
        }
      }));
      
      // Apply appropriate layout
      let layoutedNodes;
      if (flowNodes.length <= 5) {
        layoutedNodes = simpleLayout(flowNodes);
      } else {
        layoutedNodes = dagreLayout(flowNodes, flowEdges);
      }
      
      setNodes(layoutedNodes);
      setEdges(flowEdges);
      setSelectedWorkflow(path);
      toast.success('Workflow loaded');
      
    } catch (err) {
      console.error('Load error:', err);
      toast.error(`Failed: ${err}`);
      
      // Demo fallback
      const demoNodes = [
        {
          id: 'start',
          type: 'default',
          data: { label: '🚀 Start', nodeClass: 'START' },
          position: { x: 100, y: 150 },
          style: { 
            background: 'white',
            border: '2px solid #10B981', 
            borderRadius: 8,
            padding: 10,
            minWidth: 140,
            boxShadow: '0 1px 3px rgba(0,0,0,0.12)'
          }
        },
        {
          id: 'process',
          type: 'default',
          data: { label: '⚙️ Process', nodeClass: 'COMPUTATION' },
          position: { x: 350, y: 150 },
          style: { 
            background: 'white',
            border: '2px solid #3B82F6', 
            borderRadius: 8,
            padding: 10,
            minWidth: 140,
            boxShadow: '0 1px 3px rgba(0,0,0,0.12)'
          }
        },
        {
          id: 'end',
          type: 'default',
          data: { label: '✅ Complete', nodeClass: 'SUCCESS' },
          position: { x: 600, y: 150 },
          style: { 
            background: 'white',
            border: '2px solid #10B981', 
            borderRadius: 8,
            padding: 10,
            minWidth: 140,
            boxShadow: '0 1px 3px rgba(0,0,0,0.12)'
          }
        }
      ];
      
      const demoEdges = [
        { 
          id: 'e1', 
          source: 'start', 
          target: 'process', 
          type: 'smoothstep',
          animated: true,
          style: { stroke: '#94a3b8', strokeWidth: 2 }
        },
        { 
          id: 'e2', 
          source: 'process', 
          target: 'end', 
          type: 'smoothstep',
          animated: true,
          style: { stroke: '#94a3b8', strokeWidth: 2 }
        }
      ];
      
      setNodes(demoNodes);
      setEdges(demoEdges);
    }
  }, []);

  // Handle connections
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({
      ...params,
      type: 'smoothstep',
      animated: true,
      style: { stroke: '#94a3b8', strokeWidth: 2 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 15,
        height: 15,
        color: '#94a3b8',
      }
    }, eds)),
    [setEdges]
  );

  // Dry Run
  const handleDryRun = () => {
    if (nodes.length === 0) {
      toast.error('No workflow loaded');
      return;
    }
    
    setLogs([]);
    setIsRunning(true);
    
    const intro = [
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      '    DRY RUN EXECUTION STARTED',
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      `Time: ${new Date().toLocaleString()}`,
      `Workflow: ${selectedWorkflow.split('/').pop()}`,
      `Nodes: ${nodes.length} | Edges: ${edges.length}`,
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      ''
    ];
    setLogs(intro);
    
    // Simulate execution
    let delay = 0;
    nodes.forEach((node, idx) => {
      setTimeout(() => {
        const time = new Date().toLocaleTimeString();
        const nodeInfo = [
          `[${time}] Executing Node ${idx + 1}/${nodes.length}`,
          `├─ Name: ${node.data.label}`,
          `├─ Type: ${node.data.nodeClass}`,
          `└─ Status: ✅ Success (dry-run)`,
          ''
        ];
        
        if (node.data.nodeClass === 'WRITE_SENSITIVE') {
          nodeInfo.splice(3, 0, `├─ ⚠️ Write operation - requires approval`);
        }
        
        setLogs(prev => [...prev, ...nodeInfo]);
        
        if (idx === nodes.length - 1) {
          setTimeout(() => {
            const outro = [
              '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
              '    DRY RUN COMPLETED SUCCESSFULLY',
              '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
              `Duration: ${((nodes.length + 1) * 0.8).toFixed(1)} seconds`,
              `Result: All nodes executed successfully`,
              '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
            ];
            setLogs(prev => [...prev, ...outro]);
            setIsRunning(false);
            toast.success('Dry run completed');
          }, 500);
        }
      }, delay += 800);
    });
  };

  // Auto Layout
  const handleAutoLayout = () => {
    if (nodes.length === 0) return;
    
    const layouted = nodes.length <= 5 
      ? simpleLayout(nodes)
      : dagreLayout(nodes, edges);
    
    setNodes(layouted);
    toast.success('Layout optimized');
  };

  // Clear
  const handleClear = () => {
    setNodes([]);
    setEdges([]);
    setLogs([]);
    setSelectedWorkflow('');
    toast.info('Canvas cleared');
  };

  // Initial load
  useEffect(() => {
    loadWorkflow('/workflows/sample_readonly.json');
  }, [loadWorkflow]);

  return (
    <div className="h-full w-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Enhanced Header */}
      <div className="border-b bg-white dark:bg-gray-800 p-3 shadow-sm">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold">Workflow Editor</h2>
          
          <div className="flex-1" />
          
          {/* Workflow Examples */}
          <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <Button 
              variant={selectedWorkflow.includes('sample') ? 'default' : 'ghost'}
              size="sm"
              onClick={() => loadWorkflow('/workflows/sample_readonly.json')}
              className="text-xs"
            >
              Simple Flow
            </Button>
            <Button 
              variant={selectedWorkflow.includes('kb_analysis') ? 'default' : 'ghost'}
              size="sm"
              onClick={() => loadWorkflow('/workflow/examples/kb_analysis_readonly.json')}
              className="text-xs"
            >
              KB Analysis
            </Button>
            <Button 
              variant={selectedWorkflow.includes('galileo') ? 'default' : 'ghost'}
              size="sm"
              onClick={() => loadWorkflow('/workflow/examples/galileo_validate_batch.json')}
              className="text-xs"
            >
              Galileo Batch
            </Button>
            <Button 
              variant={selectedWorkflow.includes('delegation') ? 'default' : 'ghost'}
              size="sm"
              onClick={() => loadWorkflow('/workflow/examples/delegation_roundtrip_fixed.json')}
              className="text-xs"
            >
              Delegation v2
            </Button>
          </div>
          
          <div className="border-l mx-2 h-6" />
          
          {/* Actions */}
          <Button 
            variant="outline"
            size="sm"
            onClick={handleAutoLayout}
            disabled={nodes.length === 0}
          >
            🔄 Auto Layout
          </Button>
          <Button 
            variant="outline"
            size="sm"
            onClick={handleClear}
            disabled={nodes.length === 0}
          >
            Clear
          </Button>
          <Button 
            onClick={handleDryRun} 
            size="sm"
            disabled={isRunning || nodes.length === 0}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            {isRunning ? '⏳ Running...' : '▶️ Dry Run'}
          </Button>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Canvas */}
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
            fitViewOptions={{ 
              padding: 0.1,
              minZoom: 0.3,
              maxZoom: 1.5
            }}
            attributionPosition="bottom-right"
            defaultZoom={0.8}
            minZoom={0.2}
            maxZoom={2}
          >
            <Background 
              color="#e5e7eb" 
              gap={20} 
              size={1}
            />
            <Controls />
            <MiniMap 
              nodeColor={(n) => {
                const style = n.style as any;
                return style?.border?.split(' ')[2] || '#666';
              }}
              style={{
                height: 120,
                width: 200,
                backgroundColor: 'white',
                border: '1px solid #e5e7eb'
              }}
            />
            <Panel position="top-left" className="bg-white/90 dark:bg-gray-800/90 px-3 py-2 rounded-lg shadow-md">
              <div className="text-xs space-y-1">
                <div className="font-medium">Workflow Stats</div>
                <div className="text-gray-600 dark:text-gray-400">
                  Nodes: {nodes.length} | Edges: {edges.length}
                </div>
              </div>
            </Panel>
          </ReactFlow>
        </div>
        
        {/* Side Panel */}
        <div className="w-80 border-l bg-white dark:bg-gray-800 flex flex-col">
          {/* Legend */}
          <div className="p-4 border-b">
            <h3 className="font-medium mb-3 text-sm">Node Types</h3>
            <div className="space-y-2 text-xs">
              {[
                { color: '#10B981', label: 'READ - Safe operations', icon: '📊' },
                { color: '#3B82F6', label: 'COMPUTE - Calculations', icon: '⚙️' },
                { color: '#8B5CF6', label: 'AI - LLM delegation', icon: '🤖' },
                { color: '#F59E0B', label: 'CONTROL - Flow logic', icon: '🔀' },
                { color: '#EF4444', label: 'WRITE - Needs approval!', icon: '⚠️' }
              ].map(item => (
                <div key={item.color} className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded border-2" 
                    style={{ borderColor: item.color }}
                  />
                  <span>{item.icon}</span>
                  <span className={item.color === '#EF4444' ? 'font-semibold text-red-600' : ''}>
                    {item.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Execution Log */}
          <div className="flex-1 flex flex-col p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-sm">Execution Log</h3>
              {logs.length > 0 && (
                <Button 
                  variant="ghost"
                  size="sm"
                  onClick={() => setLogs([])}
                  className="h-6 px-2 text-xs"
                >
                  Clear
                </Button>
              )}
            </div>
            <div className="flex-1 font-mono text-xs bg-gray-900 text-green-400 p-3 rounded overflow-y-auto">
              <pre className="whitespace-pre-wrap">
                {logs.length > 0 ? logs.join('\n') : 'Ready to execute.\nLoad a workflow and click Dry Run.'}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function WorkflowPage() {
  return (
    <ReactFlowProvider>
      <WorkflowEditor />
    </ReactFlowProvider>
  );
}