export type WorkflowNodeType = 'tool' | 'delegate' | 'branch' | 'delay';

export interface WorkflowNode {
  id: string;
  type: WorkflowNodeType;
  name: string; // e.g., get_system_status
  params?: Record<string, any>;
  approvalRequired?: boolean; // for write-sensitive nodes
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
}

export interface WorkflowDefinition {
  version: string;
  ssotId?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  retries?: number;
  onError?: 'stop' | 'continue';
}

export interface WorkflowRunResult {
  runId: string;
  ok: boolean;
  logs: { nodeId: string; status: 'planned' | 'executed' | 'skipped' | 'error'; message?: string }[];
}




