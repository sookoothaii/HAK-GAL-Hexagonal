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
  Connection
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { WorkflowValidator } from '@/components/WorkflowValidator';
import { LiveExecutor } from '@/components/LiveExecutor';
import { WorkflowErrorBoundary } from '@/components/WorkflowErrorBoundary';

export default function WorkflowPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [palette, setPalette] = useState<any>(null);
  const [uxTexts, setUxTexts] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState('');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [hasWriteOperations, setHasWriteOperations] = useState(false);

  // Load palette from Claude's taxonomy
  useEffect(() => {
    fetch('/workflow/node_palette_taxonomy.json')
      .then(r => {
        if (!r.ok) throw new Error(`Failed to load palette: ${r.status}`);
        return r.json();
      })
      .then(data => {
        console.log('Claude palette loaded:', data);
        setPalette(data);
      })
      .catch(err => {
        console.error('Palette load error:', err);
        // Use fallback palette
        setPalette({
          node_classes: {
            READ_ONLY: { color: '#10B981' },
            WRITE_SENSITIVE: { color: '#EF4444' },
            LLM_DELEGATION: { color: '#8B5CF6' },
            COMPUTATION: { color: '#3B82F6' },
            UTILITY: { color: '#6B7280' }
          },
          node_catalog: []
        });
      });
  }, []);

  // Load UX microtexts from Claude
  useEffect(() => {
    fetch('/workflow/ux_microtexts.json')
      .then(r => {
        if (!r.ok) throw new Error(`Failed to load UX texts: ${r.status}`);
        return r.json();
      })
      .then(data => {
        console.log('Claude UX texts loaded:', data);
        setUxTexts(data);
      })
      .catch(err => {
        console.error('UX texts load error:', err);
        setUxTexts(null);
      });
  }, []);

  // Load workflow
  const loadWorkflow = useCallback(async (path: string) => {
    try {
      const response = await fetch(path);
      if (!response.ok) throw new Error(`Failed to load workflow: ${response.status}`);
      const wf = await response.json();
      
      console.log('Loading workflow:', wf);
      
      // Convert workflow format to ReactFlow nodes
      const flowNodes: Node[] = (wf.nodes || []).map((n: any, idx: number) => {
        // Determine node class and color using Claude's taxonomy
        let nodeClass = 'READ_ONLY';
        let color = '#10B981';
        let nodeShape = 'rounded';
        let icon = 'default';
        
        if (palette?.node_catalog) {
          const catalogEntry = palette.node_catalog.find((c: any) => 
            c.id === n.type || c.id === n.name
          );
          if (catalogEntry && palette.node_classes[catalogEntry.class]) {
            nodeClass = catalogEntry.class;
            color = palette.node_classes[catalogEntry.class].color || color;
            nodeShape = palette.visual_conventions?.node_shape?.[catalogEntry.class] || 'rounded';
            icon = palette.node_classes[catalogEntry.class].icon || 'default';
          }
        }
        
        // Check if this is a utility node
        if (palette?.node_classes?.UTILITY?.types) {
          const utilityType = palette.node_classes.UTILITY.types.find((u: any) => 
            u.name === n.type
          );
          if (utilityType) {
            nodeClass = 'UTILITY';
            color = palette.node_classes.UTILITY.color || '#6B7280';
            nodeShape = 'circle';
            icon = utilityType.icon || 'cog';
          }
        }
        
        // Handle different position formats
        const position = n.position || { x: 100 + idx * 200, y: 100 + (idx % 3) * 100 };
        
        return {
          id: n.id,
          type: 'default',
          data: { 
            label: n.label || n.name || n.type || n.id,
            nodeClass,
            params: n.params
          },
          position,
          style: {
            background: color + '20',
            border: `2px solid ${color}`,
            borderRadius: nodeShape === 'circle' ? '50%' : nodeShape === 'hexagon' ? '0%' : nodeShape === 'diamond' ? '0%' : 8,
            padding: 10,
            fontSize: 12,
            fontWeight: 500,
            color: 'var(--foreground)',
            // Special shapes
            ...(nodeShape === 'hexagon' && {
              clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)'
            }),
            ...(nodeShape === 'diamond' && {
              transform: 'rotate(45deg)',
              width: '80px',
              height: '80px'
            })
          }
        };
      });
      
      // Convert edges
      const flowEdges: Edge[] = (wf.edges || []).map((e: any) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        animated: e.type === 'success',
        style: { stroke: '#64748b', strokeWidth: 2 }
      }));
      
      setNodes(flowNodes);
      setEdges(flowEdges);
      setSelectedWorkflow(path);
      toast.success('Workflow loaded');
      
    } catch (err) {
      console.error('Failed to load workflow:', err);
      toast.error('Failed to load workflow');
      
      // Create demo nodes if loading fails
      setNodes([
        {
          id: '1',
          type: 'default',
          data: { label: 'Start Node' },
          position: { x: 100, y: 100 },
          style: { border: '2px solid #10B981', borderRadius: 8, color: 'var(--foreground)' }
        },
        {
          id: '2',
          type: 'default',
          data: { label: 'Process Node' },
          position: { x: 300, y: 100 },
          style: { border: '2px solid #3B82F6', borderRadius: 8, color: 'var(--foreground)' }
        },
        {
          id: '3',
          type: 'default',
          data: { label: 'End Node' },
          position: { x: 500, y: 100 },
          style: { border: '2px solid #6B7280', borderRadius: 8, color: 'var(--foreground)' }
        }
      ]);
      setEdges([
        { id: 'e1-2', source: '1', target: '2' },
        { id: 'e2-3', source: '2', target: '3' }
      ]);
    }
  }, [palette]);

  // Handle edge connections
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Basic workflow validation for dry run
  const validateWorkflowBasic = (data: any) => {
    const errors: any[] = [];
    
    if (!data.nodes || !Array.isArray(data.nodes)) {
      errors.push({ path: 'nodes', message: 'Workflow must have a nodes array' });
    }
    
    if (!data.edges || !Array.isArray(data.edges)) {
      errors.push({ path: 'edges', message: 'Workflow must have an edges array' });
    }
    
    if (data.nodes && Array.isArray(data.nodes)) {
      data.nodes.forEach((node: any, index: number) => {
        if (!node.id) {
          errors.push({ path: `nodes[${index}]`, message: 'Node must have an ID' });
        }
      });
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  };

  // Dry run simulation
  const handleDryRun = () => {
    // Validate workflow before dry run
    const validationResult = validateWorkflowBasic({ nodes, edges });
    if (!validationResult.isValid) {
      toast.error(`Cannot run workflow: ${validationResult.errors.length} validation errors`);
      return;
    }
    
    setLogs([]);
    const newLogs: string[] = [];
    
    newLogs.push('=== DRY RUN STARTED ===');
    newLogs.push(`Workflow: ${selectedWorkflow || 'Custom'}`);
    newLogs.push(`Nodes: ${nodes.length}`);
    newLogs.push(`Edges: ${edges.length}`);
    newLogs.push('');
    
    // Simulate node execution
    nodes.forEach((node, idx) => {
      setTimeout(() => {
        const log = `[${new Date().toLocaleTimeString()}] Executing: ${node.data.label} (${node.data.nodeClass || 'UNKNOWN'})`;
        setLogs(prev => [...prev, log]);
        
        if (node.data.nodeClass === 'WRITE_SENSITIVE') {
          setLogs(prev => [...prev, `  ⚠️ WRITE OPERATION - Would require approval in live mode`]);
        }
        
        setLogs(prev => [...prev, `  ✓ Success (dry-run)`]);
      }, idx * 500);
    });
    
    setTimeout(() => {
      setLogs(prev => [...prev, '', '=== DRY RUN COMPLETED ===']);
      toast.success('Dry run completed');
    }, nodes.length * 500 + 500);
  };

  // Initial load
  useEffect(() => {
    // Try to load a simple demo workflow instead of complex one
    loadWorkflow('/workflow/examples/simple_demo.json');
  }, [loadWorkflow]);

  return (
    <WorkflowErrorBoundary>
      <div className="h-full w-full flex flex-col">
        {/* Validation Error Banner */}
        {validationErrors.length > 0 && (
          <div className="bg-red-50 border-b border-red-200 p-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span className="text-sm font-medium text-red-800">
                Workflow has validation errors:
              </span>
            </div>
            <div className="mt-1 text-xs text-red-700">
              {validationErrors.join(', ')}
            </div>
          </div>
        )}
        
        {/* Write Operation Warning */}
        {hasWriteOperations && (
          <div className="bg-yellow-50 border-b border-yellow-200 p-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm font-medium text-yellow-800">
                ⚠️ {uxTexts?.info_banners?.approval_pending?.message?.replace('{count}', 'Write operations') || 'Workflow contains write operations'}
              </span>
            </div>
            <div className="mt-1 text-xs text-yellow-700">
              {uxTexts?.info_banners?.execution_mode?.message || 'This workflow will modify data and requires approval before execution.'}
            </div>
          </div>
        )}
        
        {/* Header */}
        <div className="border-b p-3 flex items-center gap-2">
          <h2 className="text-lg font-semibold">Workflow Editor</h2>
          <div className="flex-1" />
                  <Button 
          variant="outline" 
          size="sm"
          onClick={() => loadWorkflow('/workflow/examples/kb_analysis_readonly.json')}
          title={uxTexts?.tooltips?.execution_modes?.dry_run || "Load read-only knowledge base analysis workflow"}
        >
          Load KB Analysis
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => loadWorkflow('/workflow/examples/galileo_validate_batch.json')}
          title={uxTexts?.tooltips?.execution_modes?.dry_run || "Load Galileo hypothesis validation workflow"}
        >
          Load Galileo
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => loadWorkflow('/workflow/examples/delegation_roundtrip.json')}
          title={uxTexts?.tooltips?.execution_modes?.dry_run || "Load multi-agent delegation workflow"}
        >
          Load Delegation
        </Button>
                  <Button 
          onClick={handleDryRun} 
          size="sm"
          disabled={validationErrors.length > 0}
          title={validationErrors.length > 0 ? 
            (uxTexts?.error_messages?.validation_errors?.invalid_workflow?.replace('{details}', `${validationErrors.length} errors`) || "Fix validation errors first") : 
            (uxTexts?.tooltips?.execution_modes?.dry_run || "Run workflow simulation without side effects")
          }
        >
          🔍 Dry Run
        </Button>
        </div>
        
        {/* Main content */}
        <div className="flex-1 flex">
          {/* ReactFlow Canvas */}
          <div className="flex-1">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              fitView
              attributionPosition="top-right"
            >
              <Background color="#aaa" gap={16} />
              <Controls />
              <MiniMap 
                style={{
                  height: 120,
                  backgroundColor: '#f1f5f9'
                }}
                maskColor="rgb(50, 50, 50, 0.8)"
              />
            </ReactFlow>
          </div>
          
          {/* Side panel */}
          <div className="w-96 border-l bg-background p-4 overflow-auto">
                      {/* Workflow Validation */}
          <WorkflowValidator 
            workflowData={{ nodes, edges }}
            onValidationComplete={(result) => {
              // Update validation errors for banner
              setValidationErrors(result.errors.map(e => e.message));
              
              // Check for write operations
              const writeOps = nodes.filter((n: any) => 
                n.data?.nodeClass === 'WRITE_SENSITIVE'
              );
              setHasWriteOperations(writeOps.length > 0);
              
              // Show toast notifications
              if (!result.isValid) {
                toast.error(`Workflow validation failed: ${result.errors.length} errors`);
              } else if (result.warnings.length > 0) {
                toast.warning(`Workflow has ${result.warnings.length} warnings`);
              } else {
                toast.success('Workflow is valid');
              }
            }}
            showDetails={true}
          />
          
          {/* Node Palette */}
          {palette?.node_catalog && (
            <Card className="p-4 mt-4">
              <h3 className="font-semibold mb-2">Available Nodes</h3>
              <div className="space-y-2 max-h-48 overflow-auto">
                {palette.node_catalog.map((node: any) => (
                  <div 
                    key={node.id}
                    className="text-xs p-2 rounded border cursor-pointer hover:bg-muted transition-colors"
                    style={{ borderColor: palette.node_classes[node.class]?.color || '#6B7280' }}
                    title={node.short_help}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{node.label}</span>
                      <span 
                        className="px-1 py-0.5 rounded text-xs"
                        style={{ 
                          background: palette.node_classes[node.class]?.color + '20',
                          color: palette.node_classes[node.class]?.color 
                        }}
                      >
                        {node.class}
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {node.short_help}
                    </div>
                    {node.avg_duration_ms && (
                      <div className="text-xs text-muted-foreground mt-1">
                        ⏱️ ~{node.avg_duration_ms}ms
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}
            
            <Card className="p-4 mt-4">
              <h3 className="font-semibold mb-2">Node Classes</h3>
                          <div className="space-y-1 text-sm">
              {palette?.node_classes && Object.entries(palette.node_classes).map(([className, classInfo]: [string, any]) => (
                <div key={className} className="flex items-center gap-2" title={uxTexts?.tooltips?.node_classes?.[className] || classInfo.description}>
                  <div 
                    className="w-3 h-3" 
                    style={{ 
                      background: classInfo.color,
                      borderRadius: palette.visual_conventions?.node_shape?.[className] === 'circle' ? '50%' : '0%'
                    }} 
                  />
                  <span className="font-medium">{className}</span>
                  <span className="text-xs text-muted-foreground">- {classInfo.description}</span>
                </div>
              ))}
            </div>
            </Card>
            
            <Card className="p-4 mt-4">
              <h3 className="font-semibold mb-2">Execution Log</h3>
              <div className="font-mono text-xs bg-muted p-2 rounded h-64 overflow-auto whitespace-pre-wrap text-foreground">
                {logs.length > 0 ? logs.join('\n') : 'No logs yet. Run a workflow to see output.'}
              </div>
            </Card>
            
            {/* Live Executor */}
            <LiveExecutor
              nodes={nodes}
              edges={edges}
              onExecutionComplete={(results) => {
                console.log('Live execution completed:', results);
                toast.success(`Live execution completed: ${results.filter(r => r.status === 'completed').length}/${results.length} steps successful`);
              }}
              isWriteEnabled={false} // This will be configurable later
            />
          </div>
        </div>
      </div>
    </WorkflowErrorBoundary>
  );
}