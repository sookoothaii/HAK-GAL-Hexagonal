/**
 * WorkflowEngine - Core execution engine for HAK-GAL Workflow v2.0
 * Fully compatible with existing MCP tools and services
 * FIXED: Browser-compatible EventEmitter implementation
 */

import { MCPWorkflowService } from '../../services/MCPWorkflowService';
import type { WorkflowDefinition, WorkflowNode, WorkflowEdge } from '@/types/workflow';

// Browser-compatible EventEmitter
class EventEmitter {
  private events: Map<string, Set<Function>> = new Map();

  on(event: string, handler: Function): void {
    if (!this.events.has(event)) {
      this.events.set(event, new Set());
    }
    this.events.get(event)!.add(handler);
  }

  off(event: string, handler: Function): void {
    this.events.get(event)?.delete(handler);
  }

  emit(event: string, ...args: any[]): void {
    this.events.get(event)?.forEach(handler => {
      try {
        handler(...args);
      } catch (error) {
        console.error(`Error in event handler for ${event}:`, error);
      }
    });
  }

  removeAllListeners(event?: string): void {
    if (event) {
      this.events.delete(event);
    } else {
      this.events.clear();
    }
  }
}

export interface ExecutionContext {
  workflowId: string;
  executionId: string;
  startTime: number;
  variables: Map<string, any>;
  results: Map<string, any>;
  errors: Map<string, Error>;
  status: 'idle' | 'running' | 'completed' | 'failed' | 'cancelled';
  isDryRun: boolean;
  writeEnabled: boolean;
}

export interface ExecutionOptions {
  dryRun?: boolean;
  writeEnabled?: boolean;
  timeout?: number;
  parallel?: boolean;
  maxParallel?: number;
  checkpoint?: boolean;
  continueOnError?: boolean;
}

export interface ExecutionResult {
  success: boolean;
  executionId: string;
  duration: number;
  nodeResults: Map<string, any>;
  errors: Error[];
  logs: ExecutionLog[];
}

export interface ExecutionLog {
  timestamp: number;
  nodeId: string;
  level: 'info' | 'warn' | 'error' | 'debug';
  message: string;
  data?: any;
}

export interface NodeExecutor {
  execute(node: WorkflowNode, context: ExecutionContext): Promise<any>;
  validate(node: WorkflowNode): { valid: boolean; errors: string[] };
}

export class WorkflowEngine extends EventEmitter {
  private mcpService: MCPWorkflowService;
  private executors: Map<string, NodeExecutor>;
  private activeExecutions: Map<string, ExecutionContext>;

  constructor() {
    super();
    this.mcpService = new MCPWorkflowService();
    this.executors = new Map();
    this.activeExecutions = new Map();
    this.registerDefaultExecutors();
  }

  /**
   * Execute a workflow with full compatibility with existing HAK-GAL tools
   */
  async execute(
    workflow: WorkflowDefinition,
    options: ExecutionOptions = {}
  ): Promise<ExecutionResult> {
    const executionId = `exec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const startTime = Date.now();
    
    // Create execution context
    const context: ExecutionContext = {
      workflowId: workflow.ssotId || 'unknown',
      executionId,
      startTime,
      variables: new Map(),
      results: new Map(),
      errors: new Map(),
      status: 'running',
      isDryRun: options.dryRun || true, // Default to dry run for safety
      writeEnabled: options.writeEnabled || false
    };

    this.activeExecutions.set(executionId, context);
    const logs: ExecutionLog[] = [];

    try {
      // Emit start event
      this.emit('execution:start', { executionId, workflow });
      this.log(logs, 'info', 'system', `Starting workflow execution: ${executionId}`);

      // Validate workflow
      const validation = await this.validateWorkflow(workflow);
      if (!validation.valid) {
        throw new Error(`Workflow validation failed: ${validation.errors.join(', ')}`);
      }

      // Build execution graph (DAG)
      const executionGraph = this.buildExecutionGraph(workflow);
      
      // Execute nodes in topological order
      for (const batch of executionGraph.batches) {
        this.log(logs, 'info', 'system', `Executing batch with ${batch.length} nodes`);
        
        if (options.parallel && batch.length > 1) {
          // Parallel execution within batch
          await this.executeParallelBatch(batch, context, logs, options.maxParallel || 3);
        } else {
          // Sequential execution
          await this.executeSequentialBatch(batch, context, logs);
        }

        // Check if we should continue
        if (context.status === 'cancelled') {
          break;
        }

        // Checkpoint if requested
        if (options.checkpoint) {
          await this.checkpoint(context);
        }
      }

      // Mark as completed - check if we have actual failures
      const hasErrors = context.errors.size > 0;
      const hasFailedNodes = Array.from(context.results.values()).some(
        result => result && typeof result === 'object' && result.success === false
      );
      
      context.status = hasErrors || hasFailedNodes ? 'failed' : 'completed';
      
      // Emit completion
      this.emit('execution:complete', { 
        executionId, 
        results: context.results,
        duration: Date.now() - startTime 
      });

      return {
        success: context.status === 'completed' && context.errors.size === 0 && 
                 !Array.from(context.results.values()).some(r => r?.success === false),
        executionId,
        duration: Date.now() - startTime,
        nodeResults: context.results,
        errors: Array.from(context.errors.values()),
        logs
      };

    } catch (error) {
      context.status = 'failed';
      this.log(logs, 'error', 'system', `Workflow execution failed: ${error}`);
      this.emit('execution:error', { executionId, error });
      
      return {
        success: false,
        executionId,
        duration: Date.now() - startTime,
        nodeResults: context.results,
        errors: [error as Error],
        logs
      };

    } finally {
      this.activeExecutions.delete(executionId);
    }
  }

  /**
   * Cancel an active execution
   */
  async cancel(executionId: string): Promise<boolean> {
    const context = this.activeExecutions.get(executionId);
    if (!context) return false;
    
    context.status = 'cancelled';
    this.emit('execution:cancelled', { executionId });
    return true;
  }

  /**
   * Get execution status
   */
  getExecutionStatus(executionId: string): ExecutionContext | undefined {
    return this.activeExecutions.get(executionId);
  }

  /**
   * Validate workflow structure and node configurations
   */
  private async validateWorkflow(workflow: WorkflowDefinition): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = [];

    // Check basic structure
    if (!workflow.nodes || workflow.nodes.length === 0) {
      errors.push('Workflow must have at least one node');
    }

    // Validate each node
    for (const node of workflow.nodes) {
      if (!node.id) errors.push(`Node missing ID`);
      if (!node.type) errors.push(`Node ${node.id} missing type`);
      if (!node.name) errors.push(`Node ${node.id} missing name`);

      // Check if we have an executor for this node type
      const executor = this.getExecutor(node.type);
      if (executor) {
        const validation = executor.validate(node);
        if (!validation.valid) {
          errors.push(...validation.errors.map(e => `Node ${node.id}: ${e}`));
        }
      }
    }

    // Validate edges
    const nodeIds = new Set(workflow.nodes.map(n => n.id));
    for (const edge of workflow.edges) {
      if (!nodeIds.has(edge.source)) {
        errors.push(`Edge ${edge.id} references unknown source: ${edge.source}`);
      }
      if (!nodeIds.has(edge.target)) {
        errors.push(`Edge ${edge.id} references unknown target: ${edge.target}`);
      }
    }

    return { valid: errors.length === 0, errors };
  }

  /**
   * Build execution graph with topological sorting
   */
  private buildExecutionGraph(workflow: WorkflowDefinition): { batches: WorkflowNode[][] } {
    // Build adjacency list
    const adjacency = new Map<string, Set<string>>();
    const inDegree = new Map<string, number>();
    
    workflow.nodes.forEach(node => {
      adjacency.set(node.id, new Set());
      inDegree.set(node.id, 0);
    });

    workflow.edges.forEach(edge => {
      adjacency.get(edge.source)?.add(edge.target);
      inDegree.set(edge.target, (inDegree.get(edge.target) || 0) + 1);
    });

    // Topological sort with batching
    const batches: WorkflowNode[][] = [];
    const nodeMap = new Map(workflow.nodes.map(n => [n.id, n]));
    
    while (inDegree.size > 0) {
      // Find all nodes with in-degree 0 (can be executed in parallel)
      const batch: WorkflowNode[] = [];
      
      for (const [nodeId, degree] of inDegree.entries()) {
        if (degree === 0) {
          const node = nodeMap.get(nodeId);
          if (node) batch.push(node);
        }
      }

      if (batch.length === 0) {
        throw new Error('Workflow has circular dependencies');
      }

      batches.push(batch);

      // Remove processed nodes and update in-degrees
      batch.forEach(node => {
        inDegree.delete(node.id);
        adjacency.get(node.id)?.forEach(targetId => {
          inDegree.set(targetId, (inDegree.get(targetId) || 1) - 1);
        });
      });
    }

    return { batches };
  }

  /**
   * Execute a batch of nodes in parallel
   */
  private async executeParallelBatch(
    nodes: WorkflowNode[],
    context: ExecutionContext,
    logs: ExecutionLog[],
    maxParallel: number
  ): Promise<void> {
    const promises = nodes.map(node => this.executeNode(node, context, logs));
    await Promise.allSettled(promises);
  }

  /**
   * Execute a batch of nodes sequentially
   */
  private async executeSequentialBatch(
    nodes: WorkflowNode[],
    context: ExecutionContext,
    logs: ExecutionLog[]
  ): Promise<void> {
    for (const node of nodes) {
      await this.executeNode(node, context, logs);
      
      // Check if we should continue after each node
      if (context.status === 'cancelled') {
        break;
      }
    }
  }

  /**
   * Execute a single node
   */
  private async executeNode(
    node: WorkflowNode,
    context: ExecutionContext,
    logs: ExecutionLog[]
  ): Promise<any> {
    const startTime = Date.now();
    this.log(logs, 'info', node.id, `Executing node: ${node.name}`);
    this.emit('node:start', { nodeId: node.id, context });

    try {
      // Check for write operations in dry run mode
      if (context.isDryRun && this.isWriteOperation(node)) {
        this.log(logs, 'warn', node.id, `WRITE OPERATION - Skipped in dry run: ${node.name}`);
        const result = { skipped: true, reason: 'dry run mode' };
        context.results.set(node.id, result);
        this.emit('node:skipped', { nodeId: node.id, reason: 'dry run' });
        return result;
      }

      // Check for approval requirement
      if (node.approvalRequired && !context.writeEnabled) {
        this.log(logs, 'warn', node.id, `APPROVAL REQUIRED - Skipped: ${node.name}`);
        const result = { skipped: true, reason: 'approval required' };
        context.results.set(node.id, result);
        this.emit('node:skipped', { nodeId: node.id, reason: 'approval required' });
        return result;
      }

      // Get executor for node type
      const executor = this.getExecutor(node.type);
      if (!executor) {
        // Fallback to MCP service for unknown node types
        const result = await this.mcpService.executeTool(node.name, node.params || {});
        context.results.set(node.id, result);
        this.log(logs, 'info', node.id, `Node completed via MCP: ${JSON.stringify(result).slice(0, 100)}`);
        this.emit('node:complete', { nodeId: node.id, result, duration: Date.now() - startTime });
        return result;
      }

      // Execute with specific executor
      const result = await executor.execute(node, context);
      context.results.set(node.id, result);
      this.log(logs, 'info', node.id, `Node completed: ${JSON.stringify(result).slice(0, 100)}`);
      this.emit('node:complete', { nodeId: node.id, result, duration: Date.now() - startTime });
      return result;

    } catch (error) {
      const err = error as Error;
      context.errors.set(node.id, err);
      this.log(logs, 'error', node.id, `Node failed: ${err.message}`);
      this.emit('node:error', { nodeId: node.id, error: err });
      throw err; // Re-throw to handle based on continueOnError option
    }
  }

  /**
   * Check if a node performs write operations
   */
  private isWriteOperation(node: WorkflowNode): boolean {
    const writeOperations = [
      'add_fact', 'delete_fact', 'update_fact',
      'write_file', 'create_file', 'delete_file', 'move_file',
      'edit_file', 'multi_edit',
      'db_vacuum', 'db_enable_wal', 'db_checkpoint',
      'backup_kb', 'restore_kb', 'bulk_delete',
      'bulk_translate_predicates', 'project_snapshot'
    ];
    
    return writeOperations.includes(node.name);
  }

  /**
   * Get executor for a node type
   */
  private getExecutor(nodeType: string): NodeExecutor | undefined {
    return this.executors.get(nodeType);
  }

  /**
   * Register default executors
   */
  private registerDefaultExecutors(): void {
    // Tool executor for MCP tools
    this.executors.set('tool', {
      execute: async (node, context) => {
        return this.mcpService.executeTool(node.name, node.params || {});
      },
      validate: (node) => {
        const errors: string[] = [];
        if (!node.name) errors.push('Tool node must have a name');
        return { valid: errors.length === 0, errors };
      }
    });

    // Delegate executor for AI agents
    this.executors.set('delegate', {
      execute: async (node, context) => {
        const { target_agent, task_description, ...params } = node.params || {};
        return this.mcpService.delegateTask(target_agent, task_description, params);
      },
      validate: (node) => {
        const errors: string[] = [];
        if (!node.params?.target_agent) errors.push('Delegate node must have target_agent');
        if (!node.params?.task_description) errors.push('Delegate node must have task_description');
        return { valid: errors.length === 0, errors };
      }
    });

    // Branch executor for conditional logic
    this.executors.set('branch', {
      execute: async (node, context) => {
        const { condition, true_path, false_path } = node.params || {};
        // Evaluate condition using context variables
        const result = this.evaluateCondition(condition, context);
        return { branch: result ? true_path : false_path };
      },
      validate: (node) => {
        const errors: string[] = [];
        if (!node.params?.condition) errors.push('Branch node must have condition');
        return { valid: errors.length === 0, errors };
      }
    });

    // Delay executor
    this.executors.set('delay', {
      execute: async (node, context) => {
        const delay = node.params?.seconds || 1;
        await new Promise(resolve => setTimeout(resolve, delay * 1000));
        return { delayed: delay };
      },
      validate: (node) => {
        const errors: string[] = [];
        if (node.params?.seconds && typeof node.params.seconds !== 'number') {
          errors.push('Delay seconds must be a number');
        }
        return { valid: errors.length === 0, errors };
      }
    });
  }

  /**
   * Evaluate a condition expression
   */
  private evaluateCondition(condition: string, context: ExecutionContext): boolean {
    try {
      // Simple evaluation - in production, use a safe expression evaluator
      // This is a simplified version for demonstration
      const variables = Object.fromEntries(context.variables);
      const results = Object.fromEntries(context.results);
      
      // Create a safe evaluation context
      const evalContext = { ...variables, ...results };
      
      // For now, just check if the condition string contains 'true'
      // In production, use a proper expression evaluator like expr-eval
      return condition.toLowerCase().includes('true');
    } catch (error) {
      console.error('Failed to evaluate condition:', error);
      return false;
    }
  }

  /**
   * Save execution checkpoint
   */
  private async checkpoint(context: ExecutionContext): Promise<void> {
    // Save execution state for recovery
    const checkpoint = {
      executionId: context.executionId,
      workflowId: context.workflowId,
      timestamp: Date.now(),
      variables: Array.from(context.variables.entries()),
      results: Array.from(context.results.entries()),
      status: context.status
    };
    
    // In production, save to persistent storage
    this.emit('checkpoint:saved', checkpoint);
  }

  /**
   * Log helper
   */
  private log(
    logs: ExecutionLog[],
    level: ExecutionLog['level'],
    nodeId: string,
    message: string,
    data?: any
  ): void {
    const log: ExecutionLog = {
      timestamp: Date.now(),
      nodeId,
      level,
      message,
      data
    };
    logs.push(log);
    this.emit('log', log);
  }

  /**
   * Register custom executor
   */
  registerExecutor(nodeType: string, executor: NodeExecutor): void {
    this.executors.set(nodeType, executor);
  }
}