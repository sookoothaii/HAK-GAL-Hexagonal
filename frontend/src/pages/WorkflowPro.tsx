/**
 * WorkflowPro - Professional Workflow Page (n8n-style)
 * Enterprise-grade workflow editor with full HAK-GAL integration
 */

import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
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
  NodeTypes,
  EdgeTypes,
  ReactFlowProvider,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { 
  Play, Pause, Square, RotateCcw, Save, Upload, Download,
  Zap, Database, Brain, Code, Shield, GitBranch, 
  Clock, AlertCircle, CheckCircle, XCircle,
  FolderGit2, Library, AlertTriangle,
  Search, Star, FileText, Sparkles, BookOpen,
  Globe
} from 'lucide-react';
import { Input } from '@/components/ui/input';

// Import our workflow system
import { WorkflowEngine, ExecutionOptions, ExecutionResult } from '@/workflow-system/core/engine/WorkflowEngine';
import { MCPWorkflowService } from '@/workflow-system/services/MCPWorkflowService';
import type { WorkflowDefinition, WorkflowNode as WFNode } from '@/types/workflow';

// Import Engine Status Panel
import { EngineStatusPanel } from '@/components/EngineStatusPanel';

// Professional color scheme
const NODE_COLORS = {
  READ_ONLY: '#10b981',      // Emerald
  WRITE_SENSITIVE: '#ef4444', // Red
  LLM_DELEGATION: '#8b5cf6',  // Purple
  COMPUTATION: '#3b82f6',     // Blue
  UTILITY: '#6b7280',         // Gray
  SYSTEM: '#f59e0b',          // Amber
  DATABASE: '#06b6d4',        // Cyan
};

// Node categories with metadata
const NODE_CATALOG = {
  KNOWLEDGE_BASE: {
    label: 'Knowledge Base',
    icon: Database,
    color: NODE_COLORS.READ_ONLY,
    tools: [
      { id: 'search_knowledge', label: 'Search Knowledge', params: { query: '', limit: 10 }},
      { id: 'get_facts_count', label: 'Get Facts Count', params: {}},
      { id: 'add_fact', label: 'Add Fact', params: { statement: '', source: 'workflow' }, write: true},
      { id: 'delete_fact', label: 'Delete Fact', params: { statement: '' }, write: true },
      { id: 'update_fact', label: 'Update Fact', params: { old_statement: '', new_statement: '' }, write: true },
      { id: 'bulk_add_facts', label: 'Bulk Add Facts', params: { statements: [] }, write: true },
      { id: 'bulk_delete', label: 'Bulk Delete Facts', params: { statements: [] }, write: true },
      { id: 'bulk_translate_predicates', label: 'Translate Predicates', params: { mapping: {} }, write: true },
      { id: 'get_recent_facts', label: 'Get Recent Facts', params: { count: 10 } },
      { id: 'get_predicates_stats', label: 'Get Predicate Stats', params: {} },
      { id: 'get_system_status', label: 'Get System Status', params: {} },
      { id: 'kb_stats', label: 'Get KB Stats', params: {} },
      { id: 'list_audit', label: 'List Audit Trail', params: { limit: 20 } },
      { id: 'export_facts', label: 'Export Facts', params: { count: 50, direction: 'tail' } },
      { id: 'growth_stats', label: 'Get Growth Stats', params: { days: 30 } },
      { id: 'semantic_similarity', label: 'Find Similar', params: { statement: '', threshold: 0.8 }},
      { id: 'consistency_check', label: 'Check Consistency', params: { limit: 1000 }},
      { id: 'validate_facts', label: 'Validate Facts Syntax', params: { limit: 1000 } },
      { id: 'get_entities_stats', label: 'Get Entity Stats', params: { min_occurrences: 2 } },
      { id: 'search_by_predicate', label: 'Search by Predicate', params: { predicate: '' } },
      { id: 'get_fact_history', label: 'Get Fact History', params: { statement: '' } },
      { id: 'query_related', label: 'Query Related Facts', params: { entity: '' } },
      { id: 'analyze_duplicates', label: 'Analyze Duplicates', params: { threshold: 0.9 } },
      { id: 'get_knowledge_graph', label: 'Get Knowledge Graph', params: { entity: '', depth: 2 } },
      { id: 'find_isolated_facts', label: 'Find Isolated Facts', params: { limit: 50 } },
      { id: 'inference_chain', label: 'Get Inference Chain', params: { start_fact: '' } },
    ]
  },
  DB_ADMIN: {
    label: 'DB Admin',
    icon: Database,
    color: NODE_COLORS.DATABASE,
    tools: [
      { id: 'db_get_pragma', label: 'Get DB PRAGMAs', params: {} },
      { id: 'db_enable_wal', label: 'Enable WAL Mode', params: { synchronous: 'NORMAL' }, write: true },
      { id: 'db_vacuum', label: 'Vacuum Database', params: {}, write: true },
      { id: 'db_checkpoint', label: 'Force DB Checkpoint', params: { mode: 'TRUNCATE' }, write: true },
      { id: 'db_backup_now', label: 'Create DB Backup', params: {}, write: true },
      { id: 'db_backup_rotate', label: 'Rotate DB Backups', params: { keep_last: 10 }, write: true },
    ]
  },
  PROJECT_HUB: {
    label: 'Project Hub',
    icon: FolderGit2,
    color: NODE_COLORS.COMPUTATION,
    tools: [
      { id: 'project_snapshot', label: 'Create Project Snapshot', params: { title: '', description: '' }, write: true },
      { id: 'project_list_snapshots', label: 'List Project Snapshots', params: { limit: 20 } },
      { id: 'project_hub_digest', label: 'Create Hub Digest', params: { limit_files: 3 } },
    ]
  },
  NICHE_SYSTEM: {
    label: 'Niche System',
    icon: Library,
    color: '#a855f7',
    tools: [
      { id: 'niche_list', label: 'List All Niches', params: {} },
      { id: 'niche_stats', label: 'Get Niche Stats', params: { niche_name: '' } },
      { id: 'niche_query', label: 'Query a Niche', params: { niche_name: '', query: '' } },
    ]
  },
  SENTRY_MONITORING: {
    label: 'Sentry Monitoring',
    icon: AlertTriangle,
    color: NODE_COLORS.SYSTEM,
    tools: [
      { id: 'sentry_test_connection', label: 'Test Sentry Connection', params: {} },
      { id: 'sentry_whoami', label: 'Sentry Who Am I', params: {} },
      { id: 'sentry_find_organizations', label: 'Find Sentry Orgs', params: {} },
      { id: 'sentry_find_projects', label: 'Find Sentry Projects', params: { organization_slug: '' } },
      { id: 'sentry_search_issues', label: 'Search Sentry Issues', params: { query: 'is:unresolved' } },
    ]
  },
  AI_DELEGATION: {
    label: 'AI Agents',
    icon: Brain,
    color: NODE_COLORS.LLM_DELEGATION,
    tools: [
      { id: 'delegate_task', label: 'Delegate to AI', params: { target_agent: 'Gemini:gemini-1.5-flash', task_description: '' }},
      { id: 'consensus_evaluator', label: 'Consensus Eval', params: { task_id: '', outputs: [], method: 'semantic_similarity' }},
      { id: 'delegation_optimizer', label: 'Optimize Delegation', params: { task_description: '', available_tools: [] }},
      { id: 'reliability_checker', label: 'Check Tool Reliability', params: { tool_name: '', task: '' } },
      { id: 'bias_detector', label: 'Detect Tool Bias', params: { tool_outputs: {} } },
    ]
  },
  ENGINES: {
    label: 'HAK-GAL Engines',
    icon: Zap,
    color: '#a855f7', // Violet for engines
    tools: [
      { id: 'thesis_pattern_analysis', label: 'THESIS Pattern Analysis', params: { duration_minutes: 1 }, type: 'engine'},
      { id: 'aethelred_fact_gen', label: 'Aethelred Fact Gen', params: { topic: 'knowledge systems', duration_minutes: 1 }, type: 'engine'},
      { id: 'governor_decision', label: 'Governor Decision', params: { strategy: 'thompson_sampling' }, type: 'engine'},
    ]
  },
  FILE_OPERATIONS: {
    label: 'File Operations',
    icon: Code,
    color: NODE_COLORS.COMPUTATION,
    tools: [
      { id: 'read_file', label: 'Read File', params: { path: '' }},
      { id: 'write_file', label: 'Write File', params: { path: '', content: '' }, write: true},
      { id: 'list_files', label: 'List Files', params: { path: '.', pattern: '*' }},
      { id: 'get_file_info', label: 'Get File Info', params: { path: '' } },
      { id: 'directory_tree', label: 'Get Directory Tree', params: { path: '.', maxDepth: 3 } },
      { id: 'create_file', label: 'Create File', params: { path: '', content: '' }, write: true },
      { id: 'delete_file', label: 'Delete File', params: { path: '' }, write: true },
      { id: 'move_file', label: 'Move/Rename File', params: { source: '', destination: '' }, write: true },
      { id: 'grep', label: 'Search in Files', params: { pattern: '', path: '.' }},
      { id: 'find_files', label: 'Find Files', params: { pattern: '*' } },
      { id: 'search', label: 'Unified Search', params: { query: '' } },
      { id: 'edit_file', label: 'Edit File', params: { path: '', oldText: '', newText: '' }, write: true },
      { id: 'multi_edit', label: 'Multi-Edit File', params: { path: '', edits: [] }, write: true },
    ]
  },
  EXECUTION: {
    label: 'Execution',
    icon: Zap,
    color: NODE_COLORS.SYSTEM,
    tools: [
      { id: 'execute_code', label: 'Execute Code', params: { code: '', language: 'python', timeout: 30 }},
      { id: 'health_check', label: 'Health Check', params: {}},
      { id: 'health_check_json', label: 'Health Check (JSON)', params: {}},
      { id: 'db_benchmark_inserts', label: 'Benchmark DB', params: { rows: 5000, batch: 1000 }},
    ]
  },
  ERROR_HANDLING: {
    label: 'Error Handling',
    icon: AlertTriangle,
    color: '#ef4444',
    tools: [
      { id: 'try_catch', label: 'Try/Catch Block', params: { try_nodes: [], catch_nodes: [], finally_nodes: [] }, type: 'try_catch'},
      { id: 'retry_with_backoff', label: 'Retry with Backoff', params: { max_retries: 3, backoff_ms: 1000, exponential: true }},
      { id: 'circuit_breaker', label: 'Circuit Breaker', params: { failure_threshold: 5, timeout_ms: 30000, reset_timeout_ms: 60000 }},
      { id: 'fallback_chain', label: 'Fallback Chain', params: { fallback_nodes: [], default_value: null }},
      { id: 'error_transform', label: 'Error to Success', params: { error_map: {}, default_success: true }}
    ]
  },
  DATA_TRANSFORMATION: {
    label: 'Data Transform',
    icon: FileText,
    color: '#06b6d4',
    tools: [
      { id: 'json_parse', label: 'Parse JSON', params: { json_string: '', safe_mode: true, default_on_error: {} }},
      { id: 'json_stringify', label: 'Stringify JSON', params: { object: {}, pretty: true, replacer: null }},
      { id: 'string_template', label: 'String Template', params: { template: 'Hello {{name}}!', variables: { name: 'World' } }},
      { id: 'regex_extract', label: 'Regex Extract', params: { pattern: '(\\d+)', input: '', flags: 'g' }},
      { id: 'data_validator', label: 'Validate Data', params: { schema: { type: 'object' }, strict: true }},
      { id: 'csv_to_json', label: 'CSV to JSON', params: { csv_string: '', delimiter: ',', headers: true }},
      { id: 'set_fields', label: 'Set/Edit Fields', params: { fields: { new_field: 'value' }, mode: 'merge' }}
    ]
  },
  ITERATION: {
    label: 'Loops & Iteration',
    icon: RotateCcw,
    color: '#8b5cf6',
    tools: [
      { id: 'for_each', label: 'For Each Item', params: { array_field: 'items', item_name: 'item', batch_size: 1 }, type: 'for_each'},
      { id: 'split_in_batches', label: 'Split In Batches', params: { batch_size: 10, reset: false }},
      { id: 'loop_over_items', label: 'Loop Over Items', params: { max_iterations: 100, break_condition: '' }},
      { id: 'map_transform', label: 'Map Transform', params: { transform_expression: '{{ $item.field * 2 }}' }},
      { id: 'reduce_aggregate', label: 'Reduce/Aggregate', params: { accumulator: 0, operation: 'sum', field: 'value' }}
    ]
  },
  HTTP_REQUESTS: {
    label: 'HTTP Requests',
    icon: Globe,
    color: '#10b981',
    tools: [
      { id: 'http_request', label: 'HTTP Request', params: { method: 'GET', url: '', headers: {}, body: '', timeout: 30000 }},
      { id: 'webhook_send', label: 'Send Webhook', params: { url: '', method: 'POST', payload: {}, headers: {} }},
      { id: 'api_call', label: 'Generic API Call', params: { base_url: '', endpoint: '', auth_type: 'none' }},
      { id: 'rest_client', label: 'REST Client', params: { service: 'custom', operation: 'GET', path: '/' }}
    ]
  },
  ADVANCED_LOGIC: {
    label: 'Advanced Logic',
    icon: GitBranch,
    color: '#f59e0b',
    tools: [
      { id: 'switch_case', label: 'Switch/Case', params: { switch_value: '{{ $json.status }}', cases: { success: 'path1', error: 'path2' } }, type: 'switch'},
      { id: 'if_condition', label: 'IF Condition', params: { condition: '{{ $json.value > 10 }}', true_path: '', false_path: '' }, type: 'if'},
      { id: 'merge_data', label: 'Merge Data', params: { mode: 'append', clashing_fields: 'add_suffix' }},
      { id: 'filter_items', label: 'Filter Items', params: { condition: '{{ $json.active === true }}' }},
      { id: 'sort_items', label: 'Sort Items', params: { field: 'created_at', order: 'ascending' }}
    ]
  },
  FLOW_CONTROL: {
    label: 'Flow Control',
    icon: GitBranch,
    color: NODE_COLORS.UTILITY,
    tools: [
      { id: 'branch', label: 'Branch', params: { condition: '', true_path: '', false_path: '' }, type: 'branch'},
      { id: 'delay', label: 'Delay', params: { seconds: 1 }, type: 'delay'},
      { id: 'parallel', label: 'Parallel', params: { node_ids: [] }, type: 'parallel'},
      { id: 'wait_for_webhook', label: 'Wait for Webhook', params: { timeout_ms: 300000 }, type: 'wait'},
      { id: 'schedule_trigger', label: 'Schedule Trigger', params: { cron: '0 9 * * *', timezone: 'UTC' }, type: 'trigger'}
    ]
  },
  STATE_MANAGEMENT: {
    label: 'State & Context',
    icon: Database,
    color: '#a855f7',
    tools: [
      { id: 'get_global_state', label: 'Get Global State', params: { key: '', default: null }},
      { id: 'set_global_state', label: 'Set Global State', params: { key: '', value: '' }, write: true},
      { id: 'get_workflow_context', label: 'Get Workflow Context', params: { context_path: '' }},
      { id: 'set_workflow_context', label: 'Set Workflow Context', params: { context_path: '', value: '' }, write: true},
      { id: 'incr_counter', label: 'Increment Counter', params: { counter_name: '', step: 1 }, write: true},
      { id: 'atomic_transaction', label: 'Atomic Transaction', params: { keys: [], operations: [] }, write: true}
    ]
  },
  DEBUGGING: {
    label: 'Debug & Test',
    icon: AlertCircle,
    color: '#84cc16',
    tools: [
      { id: 'breakpoint', label: 'Breakpoint', params: { enabled: true, message: 'Debug checkpoint' }},
      { id: 'log_node_input', label: 'Log Input', params: { log_level: 'DEBUG', prefix: 'INPUT' }},
      { id: 'log_node_output', label: 'Log Output', params: { log_level: 'DEBUG', prefix: 'OUTPUT' }},
      { id: 'mock_data', label: 'Mock Data', params: { mock_response: {}, enabled: true }},
      { id: 'assert_condition', label: 'Assert Condition', params: { condition: '', error_message: 'Assertion failed' }},
      { id: 'test_trigger', label: 'Manual Test Trigger', params: { test_data: {}, description: 'Test execution' }}
    ]
  },
  TIME_SCHEDULING: {
    label: 'Time & Scheduling',
    icon: Clock,
    color: '#6366f1',
    tools: [
      { id: 'timer_trigger', label: 'Timer Trigger', params: { interval_ms: 5000, repeat: true, max_executions: 0 }},
      { id: 'rate_limiter', label: 'Rate Limiter', params: { max_calls: 100, window_ms: 60000, burst_limit: 10 }},
      { id: 'timeout_handler', label: 'Timeout Handler', params: { timeout_ms: 30000, on_timeout: 'fail' }},
      { id: 'schedule_task', label: 'Schedule Task', params: { cron_expression: '0 0 * * *', timezone: 'UTC', enabled: true }}
    ]
  }
};

export default function WorkflowPro() {
  return (
    <ReactFlowProvider>
      <WorkflowProContent />
    </ReactFlowProvider>
  );
}

function WorkflowProContent() {
  // ReactFlow state
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  // Workflow state
  const [workflow, setWorkflow] = useState<WorkflowDefinition | null>(null);
  const [engine] = useState(() => new WorkflowEngine());
  const [mcpService] = useState(() => new MCPWorkflowService());
  
  // Execution state
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [executionLogs, setExecutionLogs] = useState<string[]>([]);
  
  // UI state
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isDryRun, setIsDryRun] = useState(true); // Default to safe dry-run
  const [writeEnabled, setWriteEnabled] = useState(false);
  
  // NEW: Parameter Modal state
  const [showParameterModal, setShowParameterModal] = useState(false);
  const [editingNode, setEditingNode] = useState<Node | null>(null);
  
  // Node ID counter
  const [nodeIdCounter, setNodeIdCounter] = useState(1);
  
  // NEW: Enhanced UI features
  const [searchQuery, setSearchQuery] = useState('');
  const [favorites, setFavorites] = useState<string[]>(() => {
    const saved = localStorage.getItem('workflowPro_favorites');
    return saved ? JSON.parse(saved) : [];
  });
  const [showTemplates, setShowTemplates] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Custom node types
  const nodeTypes = useMemo<NodeTypes>(() => ({
    tool: ToolNode,
    delegate: DelegateNode,
    branch: BranchNode,
    delay: DelayNode,
    engine: EngineNode,
  }), []);
  
  // Workflow Templates
  const WORKFLOW_TEMPLATES = [
    {
      id: 'kb-analysis',
      name: 'Knowledge Base Analysis',
      description: 'Analyze KB consistency and find duplicates',
      icon: Brain,
      nodes: [
        { tool: 'consistency_check', params: { limit: 1000 }, position: { x: 100, y: 100 }},
        { tool: 'analyze_duplicates', params: { threshold: 0.9 }, position: { x: 100, y: 250 }},
        { tool: 'semantic_similarity', params: { statement: 'SystemKnowledge(HAK_GAL, advanced).', threshold: 0.8 }, position: { x: 350, y: 175 }},
      ]
    },
    {
      id: 'daily-maintenance',
      name: 'Daily Maintenance',
      description: 'Backup, vacuum and checkpoint database',
      icon: Database,
      nodes: [
        { tool: 'db_backup_now', params: {}, position: { x: 100, y: 100 }},
        { tool: 'db_vacuum', params: {}, position: { x: 300, y: 100 }},
        { tool: 'db_checkpoint', params: { mode: 'TRUNCATE' }, position: { x: 500, y: 100 }},
      ]
    },
    {
      id: 'research-pipeline',
      name: 'Research Pipeline',
      description: 'Run THESIS and Aethelred engines with AI analysis',
      icon: Sparkles,
      nodes: [
        { tool: 'thesis_pattern_analysis', params: { duration_minutes: 2 }, position: { x: 100, y: 100 }},
        { tool: 'aethelred_fact_gen', params: { topic: 'system optimization', duration_minutes: 2 }, position: { x: 100, y: 250 }},
        { tool: 'delegate_task', params: { target_agent: 'Gemini', task_description: 'Analyze the patterns and facts generated' }, position: { x: 400, y: 175 }},
      ]
    },
    {
      id: 'code-execution',
      name: 'Code Execution Pipeline',
      description: 'Execute Python code and analyze results',
      icon: Code,
      nodes: [
        { tool: 'execute_code', params: { code: 'print("Hello HAK-GAL!")', language: 'python' }, position: { x: 100, y: 150 }},
        { tool: 'health_check_json', params: {}, position: { x: 350, y: 150 }},
      ]
    }
  ];
  
  // Toggle favorite
  const toggleFavorite = (toolId: string) => {
    const newFavorites = favorites.includes(toolId)
      ? favorites.filter(f => f !== toolId)
      : [...favorites, toolId];
    setFavorites(newFavorites);
    localStorage.setItem('workflowPro_favorites', JSON.stringify(newFavorites));
  };
  
  // Filter tools based on search
  const getFilteredTools = (category: any) => {
    if (!searchQuery) return category.tools;
    return category.tools.filter((tool: any) => 
      tool.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tool.id.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };
  
  // Load template
  const loadTemplate = (template: any) => {
    const newNodes: Node[] = template.nodes.map((node: any, idx: number) => ({
      id: `node-${nodeIdCounter + idx}`,
      type: node.type || 'tool',
      data: {
        label: NODE_CATALOG[Object.keys(NODE_CATALOG).find(cat => 
          NODE_CATALOG[cat as keyof typeof NODE_CATALOG].tools.some((t: any) => t.id === node.tool)
        ) as keyof typeof NODE_CATALOG]?.tools.find((t: any) => t.id === node.tool)?.label || node.tool,
        tool: node.tool,
        params: node.params,
        category: Object.keys(NODE_CATALOG).find(cat => 
          NODE_CATALOG[cat as keyof typeof NODE_CATALOG].tools.some((t: any) => t.id === node.tool)
        ),
      },
      position: node.position
    }));
    
    // Auto-connect nodes in sequence
    const newEdges: Edge[] = [];
    for (let i = 0; i < newNodes.length - 1; i++) {
      if (template.nodes[i].position.y === template.nodes[i + 1].position.y) {
        newEdges.push({
          id: `e${newNodes[i].id}-${newNodes[i + 1].id}`,
          source: newNodes[i].id,
          target: newNodes[i + 1].id,
          animated: true
        });
      }
    }
    
    setNodes([...nodes, ...newNodes]);
    setEdges([...edges, ...newEdges]);
    setNodeIdCounter(nodeIdCounter + template.nodes.length);
    setShowTemplates(false);
    toast.success(`Loaded template: ${template.name}`);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Ctrl+F or Cmd+F for search
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      // Escape to clear search
      if (e.key === 'Escape' && searchQuery) {
        setSearchQuery('');
      }
      // Ctrl+T for templates
      if ((e.ctrlKey || e.metaKey) && e.key === 't') {
        e.preventDefault();
        setShowTemplates(!showTemplates);
      }
    };
    
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [searchQuery, showTemplates]);
  
  // Initialize with demo workflow and help
  useEffect(() => {
    loadDemoWorkflow();
    
    // Show initial help
    setTimeout(() => {
      toast(
        <div>
          <strong>👋 Welcome to Workflow Pro!</strong>
          <br /><br />
          <strong>Quick Start:</strong>
          <ol style={{ marginLeft: '20px', marginTop: '5px', fontSize: '12px' }}>
            <li><strong>Connect nodes:</strong> Drag from right edge to left edge</li>
            <li><strong>Add nodes:</strong> Click items in left palette</li>
            <li><strong>Execute:</strong> Click play button (safe dry-run)</li>
            <li><strong>View results:</strong> Check right panel tabs</li>
          </ol>
          <br />
          <strong>💡 Tip:</strong> The demo workflow is ready to run!
        </div>,
        { 
          duration: 15000,
          position: 'top-center',
          style: {
            maxWidth: '400px'
          }
        }
      );
    }, 1500);
    
    // Subscribe to engine events
    engine.on('log', (log) => {
      setExecutionLogs(prev => [...prev, `[${log.level}] ${log.nodeId}: ${log.message}`]);
    });
    
    engine.on('node:start', ({ nodeId }) => {
      highlightNode(nodeId, 'running');
    });
    
    engine.on('node:complete', ({ nodeId }) => {
      highlightNode(nodeId, 'completed');
    });
    
    engine.on('node:error', ({ nodeId }) => {
      highlightNode(nodeId, 'error');
    });
    
    engine.on('node:skipped', ({ nodeId }) => {
      highlightNode(nodeId, 'skipped');
    });
    
    return () => {
      engine.removeAllListeners();
    };
  }, [engine]);

  // Load demo workflow with better example
  const loadDemoWorkflow = () => {
    const demoNodes: Node[] = [
      {
        id: 'node-1',
        type: 'tool',
        data: { 
          label: '1. Count Facts',
          tool: 'get_facts_count',
          category: 'KNOWLEDGE_BASE',
          params: {}
        },
        position: { x: 50, y: 200 }
      },
      {
        id: 'node-2',
        type: 'tool',
        data: {
          label: '2. Search "workflow"',
          tool: 'search_knowledge',
          category: 'KNOWLEDGE_BASE',
          params: { query: 'workflow', limit: 5 }
        },
        position: { x: 250, y: 100 }
      },
      {
        id: 'node-3',
        type: 'tool',
        data: {
          label: '3. System Health',
          tool: 'health_check',
          category: 'EXECUTION',
          params: {}
        },
        position: { x: 250, y: 300 }
      },
      {
        id: 'node-4',
        type: 'delegate',
        data: {
          label: '4. AI Analysis',
          tool: 'delegate_task',
          category: 'AI_DELEGATION',
          params: { 
            target_agent: 'Gemini:gemini-1.5-flash',
            task_description: 'Analyze the system health and knowledge base status. Summarize findings.'
          }
        },
        position: { x: 500, y: 200 }
      },
      {
        id: 'node-5',
        type: 'tool',
        data: {
          label: '5. Save Report (Optional)',
          tool: 'add_fact',
          category: 'KNOWLEDGE_BASE',
          params: { 
            statement: 'SystemReport({{timestamp}}, health_ok, facts_analyzed).',
            source: 'workflow_demo'
          },
          isWriteOperation: true
        },
        position: { x: 750, y: 200 }
      }
    ];
    
    const demoEdges: Edge[] = [
      { 
        id: 'e1-4', 
        source: 'node-1', 
        target: 'node-4', 
        sourceHandle: 'output',
        targetHandle: 'input',
        animated: true, 
        label: 'facts count' 
      },
      { 
        id: 'e2-4', 
        source: 'node-2', 
        target: 'node-4', 
        sourceHandle: 'output',
        targetHandle: 'input',
        animated: true, 
        label: 'search results' 
      },
      { 
        id: 'e3-4', 
        source: 'node-3', 
        target: 'node-4', 
        sourceHandle: 'output',
        targetHandle: 'input',
        animated: true, 
        label: 'health status' 
      },
      { 
        id: 'e4-5', 
        source: 'node-4', 
        target: 'node-5', 
        sourceHandle: 'output',
        targetHandle: 'input',
        animated: true, 
        label: 'AI report', 
        style: { stroke: '#ef4444', strokeDasharray: '5 5' } 
      }
    ];
    
    setNodes(demoNodes);
    setEdges(demoEdges);
    
    // Show tutorial toast
    toast.info(
      <div>
        <strong>Demo Workflow Loaded!</strong>
        <br />
        This workflow:
        <ol style={{ marginLeft: '20px', marginTop: '5px' }}>
          <li>Counts facts in the knowledge base</li>
          <li>Searches for "workflow" topics</li>
          <li>Checks system health</li>
          <li>AI analyzes all results</li>
          <li>Optionally saves report (requires approval)</li>
        </ol>
        <br />
        <strong>Try:</strong> Click "Execute" to run in dry-run mode!
      </div>,
      { duration: 10000 }
    );
    
    // Highlight the execute button
    setTimeout(() => {
      const executeBtn = document.querySelector('button:has(svg)');
      if (executeBtn && executeBtn.textContent?.includes('Execute')) {
        executeBtn.classList.add('animate-pulse');
        setTimeout(() => {
          executeBtn.classList.remove('animate-pulse');
        }, 3000);
      }
    }, 1000);
  };

  // Add node from catalog
  const addNode = useCallback((tool: any, category: string) => {
    const newNode: Node = {
      id: `node-${nodeIdCounter}`,
      type: tool.type || 'tool',
      data: {
        label: tool.label,
        tool: tool.id,
        category,
        params: tool.params || {},
        isWriteOperation: tool.write || false
      },
      position: {
        x: 100 + (nodeIdCounter % 5) * 200,
        y: 100 + Math.floor(nodeIdCounter / 5) * 150
      }
    };
    
    setNodes(prev => [...prev, newNode]);
    setNodeIdCounter(prev => prev + 1);
    toast.success(`Added ${tool.label} node`);
  }, [nodeIdCounter, setNodes]);

  // Handle connection
  const onConnect = useCallback((params: Connection) => {
    setEdges(eds => addEdge({ ...params, animated: true }, eds));
  }, [setEdges]);

  // Handle node click - for selection and modal opening
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
    
    // Double-click or Ctrl+Click opens parameter modal
    if (event.detail === 2 || event.ctrlKey) {
      setEditingNode(node);
      setShowParameterModal(true);
    }
  }, []);

  // Update node parameters
  const updateNodeParameters = useCallback((nodeId: string, newParams: any) => {
    setNodes(nds => 
      nds.map(node => 
        node.id === nodeId 
          ? { ...node, data: { ...node.data, params: newParams } }
          : node
      )
    );
    toast.success('Node parameters updated');
  }, [setNodes]);

  // Handle edge click - for selection
  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    console.log('Edge selected:', edge.id);
  }, []);

  // Right-click context menu for deletion
  const onNodeContextMenu = useCallback((event: React.MouseEvent, node: Node) => {
    event.preventDefault();
    
    const menu = document.createElement('div');
    menu.className = 'absolute bg-card border rounded shadow-lg p-2 z-50';
    menu.style.left = `${event.clientX}px`;
    menu.style.top = `${event.clientY}px`;
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'flex items-center gap-2 px-3 py-2 hover:bg-accent rounded text-sm w-full text-left';
    deleteBtn.innerHTML = '🗑️ Delete Node';
    deleteBtn.onclick = () => {
      if (confirm(`Delete node "${node.data.label}"?`)) {
        setNodes(nds => nds.filter(n => n.id !== node.id));
        // Also remove connected edges
        setEdges(eds => eds.filter(e => e.source !== node.id && e.target !== node.id));
        toast.info(`Deleted node: ${node.data.label}`);
      }
      document.body.removeChild(menu);
    };
    
    menu.appendChild(deleteBtn);
    document.body.appendChild(menu);
    
    // Remove menu on click outside
    const removeMenu = (e: MouseEvent) => {
      if (!menu.contains(e.target as Node)) {
        document.body.removeChild(menu);
        document.removeEventListener('click', removeMenu);
      }
    };
    setTimeout(() => document.addEventListener('click', removeMenu), 100);
  }, [setNodes, setEdges]);

  // Handle key press for deletion
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Delete or Backspace key
      if (event.key === 'Delete' || event.key === 'Backspace') {
        // Check if we're not typing in an input field
        if ((event.target as HTMLElement).tagName !== 'INPUT' && 
            (event.target as HTMLElement).tagName !== 'TEXTAREA') {
          
          // Get selected elements from ReactFlow
          const selectedNodes = nodes.filter(n => n.selected);
          const selectedEdges = edges.filter(e => e.selected);
          
          if (selectedNodes.length > 0 || selectedEdges.length > 0) {
            // Confirm deletion for safety
            if (selectedNodes.length > 0) {
              const nodeNames = selectedNodes.map(n => n.data.label).join(', ');
              if (confirm(`Delete node(s): ${nodeNames}?`)) {
                setNodes(nds => nds.filter(n => !n.selected));
                toast.info(`Deleted ${selectedNodes.length} node(s)`);
              }
            }
            
            if (selectedEdges.length > 0) {
              setEdges(eds => eds.filter(e => !e.selected));
              toast.info(`Deleted ${selectedEdges.length} connection(s)`);
            }
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [nodes, edges, setNodes, setEdges]);

  // Convert ReactFlow to WorkflowDefinition
  const buildWorkflowDefinition = useCallback((): WorkflowDefinition => {
    const wfNodes: WFNode[] = nodes.map(node => ({
      id: node.id,
      type: node.data.type || 'tool',
      name: node.data.tool,
      params: node.data.params,
      approvalRequired: node.data.isWriteOperation
    }));
    
    return {
      version: '2.0',
      ssotId: `wf-${Date.now()}`,
      nodes: wfNodes,
      edges: edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target
      })),
      retries: 1,
      onError: 'stop'
    };
  }, [nodes, edges]);

  // Execute workflow with better feedback
  const executeWorkflow = useCallback(async () => {
    if (isExecuting) return;
    
    // Check if there are nodes to execute
    if (nodes.length === 0) {
      toast.error('No nodes to execute! Add some nodes first or click "Demo" for an example.');
      return;
    }
    
    // Check if nodes are connected
    if (edges.length === 0 && nodes.length > 1) {
      toast.warning('Nodes are not connected! Drag from output to input to create connections.');
      return;
    }
    
    setIsExecuting(true);
    setExecutionLogs([]);
    setExecutionResult(null);
    
    try {
      const workflowDef = buildWorkflowDefinition();
      
      // Show execution start with visual feedback
      toast.info('🚀 Starting workflow execution...', { duration: 2000 });
      
      // Define execution options FIRST
      const options: ExecutionOptions = {
        dryRun: isDryRun,
        writeEnabled: writeEnabled && !isDryRun,
        parallel: true,
        maxParallel: 3,
        continueOnError: false,
        checkpoint: true
      };
      
      // Log execution start with accurate mode information
      const actualMode = options.dryRun !== false ? 'DRY RUN (Safe - No actual changes)' : 
                         options.writeEnabled ? 'LIVE MODE with WRITE ACCESS' : 'LIVE MODE (Write Protected)';
      
      setExecutionLogs([
        `=== WORKFLOW EXECUTION STARTED ===`,
        `Time: ${new Date().toLocaleTimeString()}`,
        `Mode: ${actualMode}`,
        `Total Nodes: ${workflowDef.nodes.length}`,
        `Total Connections: ${workflowDef.edges.length}`,
        ``,
        `--- EXECUTION FLOW ---`
      ]);
      
      // Execute workflow
      const result = await engine.execute(workflowDef, options);
      
      setExecutionResult(result);
      
      // Log results with emoji indicators
      setExecutionLogs(prev => [
        ...prev, 
        '',
        `--- EXECUTION ${result.success ? '✅ COMPLETED' : '❌ FAILED'} ---`,
        `Total Duration: ${result.duration}ms`,
        `Nodes Executed: ${result.nodeResults.size}/${workflowDef.nodes.length}`,
        `Status: ${result.success ? 'All operations successful' : 'Some operations failed'}`
      ]);
      
      if (result.errors.length > 0) {
        setExecutionLogs(prev => [
          ...prev,
          '',
          `--- ERRORS ---`
        ]);
        result.errors.forEach(err => {
          setExecutionLogs(prev => [...prev, `❌ ${err.message}`]);
        });
      }
      
      // Show results summary
      if (result.success) {
        toast.success(
          <div>
            <strong>✅ Workflow completed successfully!</strong>
            <br />
            Duration: {result.duration}ms | Nodes: {result.nodeResults.size}
            <br />
            {isDryRun && <em>This was a dry run - no actual changes were made.</em>}
          </div>,
          { duration: 5000 }
        );
      } else {
        toast.error(
          <div>
            <strong>❌ Workflow execution failed</strong>
            <br />
            Check the logs for details.
          </div>,
          { duration: 5000 }
        );
      }
      
    } catch (error: any) {
      console.error('Workflow execution error:', error);
      toast.error(`Execution failed: ${error.message}`);
      setExecutionLogs(prev => [...prev, `❌ CRITICAL ERROR: ${error.message}`]);
    } finally {
      setIsExecuting(false);
      
      // Reset node highlights after delay
      setTimeout(() => {
        nodes.forEach(node => {
          highlightNode(node.id, 'idle');
        });
      }, 3000);
    }
  }, [isExecuting, isDryRun, writeEnabled, buildWorkflowDefinition, engine, nodes, edges]);

  // Highlight node during execution
  const highlightNode = (nodeId: string, status: 'idle' | 'running' | 'completed' | 'error' | 'skipped') => {
    setNodes(nds =>
      nds.map(node => {
        if (node.id === nodeId) {
          const statusColors = {
            idle: '#e5e7eb',
            running: '#fbbf24',
            completed: '#10b981',
            error: '#ef4444',
            skipped: '#6b7280'
          };
          
          return {
            ...node,
            style: {
              ...node.style,
              backgroundColor: statusColors[status] + '20',
              borderColor: statusColors[status],
              borderWidth: 2,
              transition: 'all 0.3s ease'
            }
          };
        }
        return node;
      })
    );
  };

  // Save workflow
  const saveWorkflow = () => {
    const wf = buildWorkflowDefinition();
    const blob = new Blob([JSON.stringify(wf, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `workflow-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Workflow saved');
  };

  // Load workflow
  const loadWorkflow = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const wf = JSON.parse(e.target?.result as string) as WorkflowDefinition;
        
        // Convert to ReactFlow nodes/edges
        const flowNodes: Node[] = wf.nodes.map((n, idx) => ({
          id: n.id,
          type: n.type || 'tool',
          data: {
            label: n.name,
            tool: n.name,
            params: n.params,
            isWriteOperation: n.approvalRequired
          },
          position: { x: 100 + (idx % 5) * 200, y: 100 + Math.floor(idx / 5) * 150 }
        }));
        
        const flowEdges: Edge[] = wf.edges.map(e => ({
          id: e.id,
          source: e.source,
          target: e.target,
          animated: true
        }));
        
        setNodes(flowNodes);
        setEdges(flowEdges);
        setWorkflow(wf);
        toast.success('Workflow loaded');
      } catch (error) {
        toast.error('Failed to load workflow');
      }
    };
    reader.readAsText(file);
  };

  // NodeParameterModal Component
  const NodeParameterModal = () => {
    const [localParams, setLocalParams] = useState(editingNode?.data.params || {});
    
    useEffect(() => {
      if (editingNode) {
        setLocalParams(editingNode.data.params || {});
      }
    }, [editingNode]);
    
    const handleSave = () => {
      if (editingNode) {
        updateNodeParameters(editingNode.id, localParams);
        setShowParameterModal(false);
        setEditingNode(null);
      }
    };
    
    const handleCancel = () => {
      setShowParameterModal(false);
      setEditingNode(null);
      setLocalParams({});
    };
    
    const updateParam = (key: string, value: any) => {
      setLocalParams(prev => ({ ...prev, [key]: value }));
    };
    
    if (!editingNode) return null;
    
    const toolInfo = Object.values(NODE_CATALOG)
      .flatMap(cat => cat.tools)
      .find(tool => tool.id === editingNode.data.tool);
    
    return (
      <Dialog open={showParameterModal} onOpenChange={setShowParameterModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {toolInfo && (
                <div 
                  className="w-4 h-4 rounded" 
                  style={{ backgroundColor: NODE_CATALOG[editingNode.data.category as keyof typeof NODE_CATALOG]?.color }}
                />
              )}
              {editingNode.data.label}
              {editingNode.data.isWriteOperation && (
                <Badge variant="destructive" className="text-xs">
                  <Shield className="w-3 h-3 mr-1" />
                  Write Operation
                </Badge>
              )}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground">
              <strong>Tool:</strong> {editingNode.data.tool}
            </div>
            
            {/* Dynamic Parameter Form */}
            <div className="space-y-4">
              {Object.entries(localParams).map(([key, value]) => (
                <div key={key} className="space-y-2">
                  <Label htmlFor={key} className="text-sm font-medium capitalize">
                    {key.replace(/_/g, ' ')}
                  </Label>
                  
                  {/* Different input types based on value type */}
                  {typeof value === 'boolean' ? (
                    <div className="flex items-center space-x-2">
                      <Switch
                        id={key}
                        checked={value}
                        onCheckedChange={(checked) => updateParam(key, checked)}
                      />
                      <Label htmlFor={key} className="text-sm">
                        {value ? 'Enabled' : 'Disabled'}
                      </Label>
                    </div>
                  ) : typeof value === 'number' ? (
                    <Input
                      id={key}
                      type="number"
                      value={value}
                      onChange={(e) => updateParam(key, parseFloat(e.target.value) || 0)}
                      className="w-full"
                    />
                  ) : Array.isArray(value) ? (
                    <Textarea
                      id={key}
                      value={JSON.stringify(value, null, 2)}
                      onChange={(e) => {
                        try {
                          const parsed = JSON.parse(e.target.value);
                          updateParam(key, parsed);
                        } catch {
                          // Invalid JSON, keep as string for now
                        }
                      }}
                      placeholder="Enter JSON array..."
                      className="font-mono text-xs"
                      rows={3}
                    />
                  ) : typeof value === 'object' && value !== null ? (
                    <Textarea
                      id={key}
                      value={JSON.stringify(value, null, 2)}
                      onChange={(e) => {
                        try {
                          const parsed = JSON.parse(e.target.value);
                          updateParam(key, parsed);
                        } catch {
                          // Invalid JSON, keep as string for now
                        }
                      }}
                      placeholder="Enter JSON object..."
                      className="font-mono text-xs"
                      rows={4}
                    />
                  ) : key.includes('mode') || key.includes('method') || key.includes('type') ? (
                    <Select value={value} onValueChange={(newValue) => updateParam(key, newValue)}>
                      <SelectTrigger>
                        <SelectValue placeholder={`Select ${key}`} />
                      </SelectTrigger>
                      <SelectContent>
                        {/* Common options based on parameter name */}
                        {key.includes('method') && [
                          <SelectItem key="GET" value="GET">GET</SelectItem>,
                          <SelectItem key="POST" value="POST">POST</SelectItem>,
                          <SelectItem key="PUT" value="PUT">PUT</SelectItem>,
                          <SelectItem key="DELETE" value="DELETE">DELETE</SelectItem>
                        ]}
                        {key.includes('mode') && [
                          <SelectItem key="merge" value="merge">Merge</SelectItem>,
                          <SelectItem key="replace" value="replace">Replace</SelectItem>,
                          <SelectItem key="append" value="append">Append</SelectItem>
                        ]}
                        {key.includes('level') && [
                          <SelectItem key="DEBUG" value="DEBUG">DEBUG</SelectItem>,
                          <SelectItem key="INFO" value="INFO">INFO</SelectItem>,
                          <SelectItem key="WARN" value="WARN">WARN</SelectItem>,
                          <SelectItem key="ERROR" value="ERROR">ERROR</SelectItem>
                        ]}
                      </SelectContent>
                    </Select>
                  ) : String(value).length > 50 || key.includes('template') || key.includes('query') || key.includes('code') ? (
                    <Textarea
                      id={key}
                      value={String(value)}
                      onChange={(e) => updateParam(key, e.target.value)}
                      placeholder={`Enter ${key.replace(/_/g, ' ')}...`}
                      className={key.includes('code') ? 'font-mono text-xs' : ''}
                      rows={key.includes('code') ? 6 : 3}
                    />
                  ) : (
                    <Input
                      id={key}
                      value={String(value)}
                      onChange={(e) => updateParam(key, e.target.value)}
                      placeholder={`Enter ${key.replace(/_/g, ' ')}...`}
                      className="w-full"
                    />
                  )}
                  
                  {/* Help text for common parameters */}
                  {key === 'timeout' && (
                    <p className="text-xs text-muted-foreground">Timeout in milliseconds</p>
                  )}
                  {key === 'max_retries' && (
                    <p className="text-xs text-muted-foreground">Maximum number of retry attempts</p>
                  )}
                  {key === 'url' && (
                    <p className="text-xs text-muted-foreground">Full URL including protocol (https://)</p>
                  )}
                </div>
              ))}
              
              {/* Add new parameter */}
              <div className="border-t pt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const key = prompt('Parameter name:');
                    if (key && !localParams.hasOwnProperty(key)) {
                      updateParam(key, '');
                    }
                  }}
                >
                  + Add Parameter
                </Button>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={handleCancel}>
              Cancel
            </Button>
            <Button onClick={handleSave}>
              Save Parameters
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  };

  return (
    <div className="h-full w-full flex flex-col bg-background">
      {/* Header Bar */}
      <div className="border-b px-4 py-2 flex items-center gap-3 bg-card">
        <h1 className="text-lg font-semibold">Workflow Pro</h1>
        
        <div className="flex-1" />
        
        {/* Execution Controls */}
        <div className="flex items-center gap-2 border-r pr-3">
          <Button
            size="sm"
            variant={isDryRun ? 'outline' : 'default'}
            onClick={() => setIsDryRun(!isDryRun)}
          >
            {isDryRun ? 'Dry Run' : 'Live Mode'}
          </Button>
          
          {!isDryRun && (
            <Button
              size="sm"
              variant={writeEnabled ? 'destructive' : 'outline'}
              onClick={() => setWriteEnabled(!writeEnabled)}
            >
              <Shield className="w-4 h-4 mr-1" />
              {writeEnabled ? 'Writes ON' : 'Writes OFF'}
            </Button>
          )}
          
          <Button
            size="sm"
            variant="default"
            onClick={executeWorkflow}
            disabled={isExecuting}
          >
            {isExecuting ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2" />
                Executing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-1" />
                Execute
              </>
            )}
          </Button>
        </div>
        
        {/* File Operations */}
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={saveWorkflow}>
            <Download className="w-4 h-4 mr-1" />
            Save
          </Button>
          
          <label className="cursor-pointer">
            <Button size="sm" variant="outline" asChild>
              <span>
                <Upload className="w-4 h-4 mr-1" />
                Load
              </span>
            </Button>
            <input
              type="file"
              accept=".json"
              className="hidden"
              onChange={loadWorkflow}
            />
          </label>
          
          <Button size="sm" variant="outline" onClick={() => {
            if (confirm('Clear canvas and start fresh?')) {
              setNodes([]);
              setEdges([]);
              setExecutionLogs([]);
              setExecutionResult(null);
              setSelectedNode(null);
              toast.info('Canvas cleared');
            }
          }}>
            <RotateCcw className="w-4 h-4 mr-1" />
            Clear
          </Button>
          
          <Button size="sm" variant="outline" onClick={loadDemoWorkflow}>
            <Zap className="w-4 h-4 mr-1" />
            Demo
          </Button>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex min-h-0">
        {/* Left Sidebar - Node Palette */}
        <div className="w-64 border-r bg-card p-3 flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-sm">Node Palette</h2>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowTemplates(!showTemplates)}
              className="h-7 px-2"
            >
              <BookOpen className="w-3 h-3 mr-1" />
              Templates
            </Button>
          </div>
          
          {/* Search Bar */}
          <div className="relative mb-3">
            <Search className="absolute left-2 top-2 h-4 w-4 text-muted-foreground" />
            <Input
              ref={searchInputRef}
              type="text"
              placeholder="Search nodes... (Ctrl+F)"
              className="pl-8 h-8 text-xs"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-2 text-muted-foreground hover:text-foreground"
              >
                <XCircle className="h-4 w-4" />
              </button>
            )}
          </div>
          
          {/* Templates Panel */}
          {showTemplates && (
            <div className="mb-4 p-3 bg-accent/50 rounded-lg border">
              <h3 className="font-semibold text-xs mb-2">Workflow Templates</h3>
              <div className="space-y-2">
                {WORKFLOW_TEMPLATES.map(template => {
                  const Icon = template.icon;
                  return (
                    <div
                      key={template.id}
                      className="p-2 bg-card rounded border cursor-pointer hover:bg-accent transition-colors"
                      onClick={() => loadTemplate(template)}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Icon className="w-3 h-3" />
                        <span className="text-xs font-medium">{template.name}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">{template.description}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
          
          {/* Connection Help */}
          <div className="mb-4 p-2 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded text-xs">
            <div className="flex items-center gap-1 mb-1">
              <Zap className="w-3 h-3" />
              <strong>How to connect:</strong>
            </div>
            <ol className="ml-4 space-y-1 text-xs">
              <li>1. Hover over node edge</li>
              <li>2. Click & drag from dot</li>
              <li>3. Drop on target node</li>
            </ol>
            <div className="mt-2 text-xs text-muted-foreground">
              Output (right) → Input (left)
            </div>
          </div>
          
          {/* Deletion Help */}
          <div className="mb-4 p-2 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded text-xs">
            <div className="flex items-center gap-1 mb-1">
              <XCircle className="w-3 h-3" />
              <strong>How to delete:</strong>
            </div>
            <ul className="ml-4 space-y-1 text-xs">
              <li>• Click to select (blue outline)</li>
              <li>• Press <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">Delete</kbd> or <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">Backspace</kbd></li>
              <li>• Confirm deletion</li>
            </ul>
            <div className="mt-2 text-xs text-muted-foreground">
              <strong>Multi-select:</strong> Hold <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">Shift</kbd> + Click
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            {/* Favorites Section */}
            {favorites.length > 0 && !searchQuery && (
              <div className="mb-4 pb-4 border-b">
                <div className="flex items-center gap-2 mb-2">
                  <Star className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-medium">Favorites</span>
                </div>
                <div className="space-y-1">
                  {favorites.map(toolId => {
                    const category = Object.keys(NODE_CATALOG).find(cat =>
                      NODE_CATALOG[cat as keyof typeof NODE_CATALOG].tools.some((t: any) => t.id === toolId)
                    );
                    if (!category) return null;
                    const tool = NODE_CATALOG[category as keyof typeof NODE_CATALOG].tools.find((t: any) => t.id === toolId);
                    if (!tool) return null;
                    const data = NODE_CATALOG[category as keyof typeof NODE_CATALOG];
                    return (
                      <div
                        key={tool.id}
                        className="p-2 rounded border text-xs cursor-move hover:bg-accent transition-colors bg-yellow-50 dark:bg-yellow-950"
                        style={{ borderColor: data.color + '60' }}
                        draggable
                        onDragEnd={() => addNode(tool, category)}
                        onClick={() => addNode(tool, category)}
                      >
                        <div className="flex items-center justify-between">
                          <span>{tool.label}</span>
                          <div className="flex items-center gap-1">
                            {tool.write && <Shield className="w-3 h-3 text-destructive" />}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleFavorite(tool.id);
                              }}
                              className="hover:bg-accent p-0.5 rounded"
                            >
                              <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            
            {/* Regular Categories */}
            {Object.entries(NODE_CATALOG).map(([category, data]) => {
              const Icon = data.icon;
              const filteredTools = getFilteredTools(data);
              
              // Skip category if no tools match search
              if (searchQuery && filteredTools.length === 0) return null;
              
              return (
                <div key={category} className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className="w-4 h-4" style={{ color: data.color }} />
                    <span className="text-sm font-medium">{data.label}</span>
                    {searchQuery && filteredTools.length > 0 && (
                      <Badge variant="secondary" className="text-xs ml-auto">
                        {filteredTools.length}
                      </Badge>
                    )}
                  </div>
                  
                  <div className="space-y-1">
                    {filteredTools.map((tool: any) => {
                      const isFavorite = favorites.includes(tool.id);
                      return (
                        <div
                          key={tool.id}
                          className="p-2 rounded border text-xs cursor-move hover:bg-accent transition-colors"
                          style={{ 
                            borderColor: data.color + '60',
                            backgroundColor: searchQuery && tool.label.toLowerCase().includes(searchQuery.toLowerCase()) 
                              ? 'rgba(59, 130, 246, 0.1)' 
                              : undefined
                          }}
                          draggable
                          onDragEnd={() => addNode(tool, category)}
                          onClick={() => addNode(tool, category)}
                        >
                          <div className="flex items-center justify-between">
                            <span>{tool.label}</span>
                            <div className="flex items-center gap-1">
                              {tool.write && <Shield className="w-3 h-3 text-destructive" />}
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleFavorite(tool.id);
                                }}
                                className="hover:bg-accent p-0.5 rounded"
                              >
                                <Star className={`w-3 h-3 ${isFavorite ? 'fill-yellow-500 text-yellow-500' : 'text-gray-400'}`} />
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
            
            {/* No results message */}
            {searchQuery && Object.entries(NODE_CATALOG).every(([_, data]) => getFilteredTools(data).length === 0) && (
              <div className="text-center text-sm text-muted-foreground py-4">
                No tools found for "{searchQuery}"
              </div>
            )}
          </div>
        </div>
        
        {/* Center - Canvas */}
        <div className="flex-1 h-full">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onNodeContextMenu={onNodeContextMenu}
            onEdgeClick={onEdgeClick}
            nodeTypes={nodeTypes}
            deleteKeyCode={['Delete', 'Backspace']}
            selectionOnDrag
            multiSelectionKeyCode="Shift"
            fitView
            attributionPosition="bottom-right"
          >
            <Background variant="dots" gap={12} size={1} />
            <Controls />
            <MiniMap
              nodeColor={node => {
                const category = node.data?.category;
                return NODE_COLORS[category as keyof typeof NODE_COLORS] || '#6b7280';
              }}
              style={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))'
              }}
            />
          </ReactFlow>
        </div>
        
        {/* Right Sidebar - Properties & Logs */}
        <div className="w-96 border-l bg-card p-3">
          <Tabs defaultValue="status" className="h-full flex flex-col">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="status">Status</TabsTrigger>
              <TabsTrigger value="properties">Props</TabsTrigger>
              <TabsTrigger value="logs">Logs</TabsTrigger>
              <TabsTrigger value="results">Results</TabsTrigger>
            </TabsList>
            
            <TabsContent value="status" className="flex-1 overflow-auto">
              <EngineStatusPanel />
            </TabsContent>
            
            <TabsContent value="properties" className="flex-1 overflow-auto">
              {selectedNode ? (
                <Card className="p-3">
                  <h3 className="font-semibold text-sm mb-2">Node Properties</h3>
                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="font-medium">ID:</span> {selectedNode.id}
                    </div>
                    <div>
                      <span className="font-medium">Type:</span> {selectedNode.type}
                    </div>
                    <div>
                      <span className="font-medium">Tool:</span> {selectedNode.data.tool}
                    </div>
                    <div>
                      <span className="font-medium">Parameters:</span>
                      <pre className="mt-1 p-2 bg-muted rounded text-xs">
                        {JSON.stringify(selectedNode.data.params, null, 2)}
                      </pre>
                    </div>
                    {selectedNode.data.isWriteOperation && (
                      <Badge variant="destructive" className="text-xs">
                        Write Operation - Requires Approval
                      </Badge>
                    )}
                  </div>
                </Card>
              ) : (
                <div className="text-sm text-muted-foreground">
                  Select a node to view properties
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="logs" className="flex-1 overflow-auto">
              <Card className="p-3 h-full">
                <h3 className="font-semibold text-sm mb-2">Execution Logs</h3>
                <ScrollArea className="h-full">
                  <div className="font-mono text-xs whitespace-pre-wrap">
                    {executionLogs.length > 0 
                      ? executionLogs.join('\n')
                      : 'No execution logs yet. Run the workflow to see logs.'}
                  </div>
                </ScrollArea>
              </Card>
            </TabsContent>
            
            <TabsContent value="results" className="flex-1 overflow-auto">
              {executionResult ? (
                <Card className="p-3">
                  <h3 className="font-semibold text-sm mb-2">Execution Results</h3>
                  <div className="space-y-2 text-xs">
                    <div className="flex items-center gap-2">
                      {executionResult.success ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                      <span className="font-medium">
                        {executionResult.success ? 'Success' : 'Failed / Partial Success'}
                      </span>
                    </div>
                    
                    <div>
                      <span className="font-medium">Duration:</span> {executionResult.duration}ms
                    </div>
                    
                    <div>
                      <span className="font-medium">Nodes Executed:</span> {executionResult.nodeResults.size}
                    </div>
                    
                    {/* Show summary of results */}
                    <div>
                      <span className="font-medium">Results Summary:</span>
                      <div className="mt-1 space-y-1">
                        {Array.from(executionResult.nodeResults.entries()).map(([nodeId, result]) => (
                          <div key={nodeId} className="flex items-center gap-2 ml-2">
                            {result?.success === false ? (
                              <XCircle className="w-3 h-3 text-red-500" />
                            ) : result?.skipped ? (
                              <AlertCircle className="w-3 h-3 text-yellow-500" />
                            ) : (
                              <CheckCircle className="w-3 h-3 text-green-500" />
                            )}
                            <span className="text-xs">
                              {nodeId}: {
                                result?.success === false ? 'Failed' :
                                result?.skipped ? 'Skipped' : 'Success'
                              }
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {executionResult.errors.length > 0 && (
                      <div>
                        <span className="font-medium">Errors:</span>
                        <ul className="list-disc list-inside mt-1">
                          {executionResult.errors.map((err, idx) => (
                            <li key={idx} className="text-red-500">
                              {err.message}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    <div>
                      <span className="font-medium">Node Results:</span>
                      <ScrollArea className="h-64 mt-1">
                        <pre className="p-2 bg-muted rounded text-xs">
                          {JSON.stringify(
                            Object.fromEntries(executionResult.nodeResults),
                            null,
                            2
                          )}
                        </pre>
                      </ScrollArea>
                    </div>
                  </div>
                </Card>
              ) : (
                <div className="text-sm text-muted-foreground">
                  No execution results yet. Run the workflow to see results.
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
      
      {/* Status Bar */}
      <div className="border-t px-4 py-1 flex items-center gap-4 text-xs bg-card">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span>System Ready</span>
        </div>
        <div>Nodes: {nodes.length}</div>
        <div>Edges: {edges.length}</div>
        <div className="flex items-center gap-1">
          <span>Tools: 122</span>
        </div>
        {favorites.length > 0 && (
          <div className="flex items-center gap-1">
            <Star className="w-3 h-3 text-yellow-500" />
            <span>{favorites.length}</span>
          </div>
        )}
        <div className="flex-1" />
        <div className="flex items-center gap-4 text-muted-foreground">
          <div className="flex items-center gap-2">
            <kbd className="px-1.5 py-0.5 text-xs bg-muted rounded">Ctrl+F</kbd>
            <span>Search</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="px-1.5 py-0.5 text-xs bg-muted rounded">Ctrl+T</kbd>
            <span>Templates</span>
          </div>
          <div className="border-l pl-4">HAK-GAL Workflow v2.1</div>
        </div>
      </div>
      
      {/* Parameter Modal */}
      <NodeParameterModal />
    </div>
  );
}

// Custom Node Components with proper ReactFlow Handles
function ToolNode({ data }: { data: any }) {
  const Icon = NODE_CATALOG[data.category as keyof typeof NODE_CATALOG]?.icon || Zap;
  const color = NODE_CATALOG[data.category as keyof typeof NODE_CATALOG]?.color || '#6b7280';
  
  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        style={{ background: '#555' }}
      />
      <div 
        className="px-3 py-2 rounded border-2 bg-card min-w-[140px]"
        style={{ borderColor: color }}
      >
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4" style={{ color }} />
          <span className="text-xs font-medium">{data.label}</span>
          {data.isWriteOperation && (
            <Shield className="w-3 h-3 text-destructive ml-auto" />
          )}
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        style={{ background: '#555' }}
      />
    </>
  );
}

function DelegateNode({ data }: { data: any }) {
  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        style={{ background: NODE_COLORS.LLM_DELEGATION }}
      />
      <div 
        className="px-3 py-2 rounded-lg border-2 bg-card min-w-[120px]"
        style={{ 
          borderColor: NODE_COLORS.LLM_DELEGATION,
          borderStyle: 'dashed'
        }}
      >
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4" style={{ color: NODE_COLORS.LLM_DELEGATION }} />
          <span className="text-xs font-medium">{data.label}</span>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        style={{ background: NODE_COLORS.LLM_DELEGATION }}
      />
    </>
  );
}

function BranchNode({ data }: { data: any }) {
  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        style={{ background: NODE_COLORS.UTILITY }}
      />
      <div 
        className="px-3 py-2 rounded border-2 bg-card min-w-[120px]"
        style={{ 
          borderColor: NODE_COLORS.UTILITY,
          clipPath: 'polygon(10% 0%, 100% 0%, 90% 100%, 0% 100%)'
        }}
      >
        <div className="flex items-center gap-2">
          <GitBranch className="w-4 h-4" style={{ color: NODE_COLORS.UTILITY }} />
          <span className="text-xs font-medium">{data.label}</span>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="output-true"
        style={{ top: '30%', background: NODE_COLORS.UTILITY }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="output-false"
        style={{ top: '70%', background: NODE_COLORS.UTILITY }}
      />
    </>
  );
}

function DelayNode({ data }: { data: any }) {
  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        style={{ background: NODE_COLORS.UTILITY }}
      />
      <div 
        className="px-3 py-2 rounded-full border-2 bg-card min-w-[120px] text-center"
        style={{ borderColor: NODE_COLORS.UTILITY }}
      >
        <div className="flex items-center justify-center gap-2">
          <Clock className="w-4 h-4" style={{ color: NODE_COLORS.UTILITY }} />
          <span className="text-xs font-medium">{data.label}</span>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        style={{ background: NODE_COLORS.UTILITY }}
      />
    </>
  );
}

function EngineNode({ data }: { data: any }) {
  const Icon = Zap;
  const color = '#a855f7'; // Violet

  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        style={{ background: color }}
      />
      <div
        className="px-3 py-2 rounded-lg border-2 bg-card min-w-[140px]"
        style={{
          borderColor: color,
          borderStyle: 'solid'
        }}
      >
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4" style={{ color }} />
          <span className="text-xs font-medium">{data.label}</span>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        style={{ background: color }}
      />
    </>
  );
}