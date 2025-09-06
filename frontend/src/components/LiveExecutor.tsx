import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Play, Pause, Square, RotateCcw, CheckCircle, XCircle, Clock } from 'lucide-react';
import { toast } from 'sonner';

interface ExecutionStep {
  id: string;
  nodeId: string;
  nodeLabel: string;
  nodeClass: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  startTime?: string;
  endTime?: string;
  duration?: number;
  result?: any;
  error?: string;
}

interface LiveExecutorProps {
  nodes: any[];
  edges: any[];
  onExecutionComplete: (results: ExecutionStep[]) => void;
  isWriteEnabled: boolean;
}

export function LiveExecutor({ 
  nodes, 
  edges, 
  onExecutionComplete,
  isWriteEnabled 
}: LiveExecutorProps) {
  const [executionSteps, setExecutionSteps] = useState<ExecutionStep[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);
  const [executionId, setExecutionId] = useState<string>('');

  // Initialize execution steps
  const initializeExecution = useCallback(() => {
    const steps: ExecutionStep[] = nodes.map((node, index) => ({
      id: `step-${index}`,
      nodeId: node.id,
      nodeLabel: node.data.label || node.id,
      nodeClass: node.data.nodeClass || 'UNKNOWN',
      status: 'pending'
    }));
    
    setExecutionSteps(steps);
    setCurrentStepIndex(-1);
    setExecutionId(`exec-${Date.now()}`);
  }, [nodes]);

  // Execute a single step
  const executeStep = useCallback(async (step: ExecutionStep): Promise<ExecutionStep> => {
    const updatedStep = { ...step, status: 'running' as const, startTime: new Date().toISOString() };
    
    try {
      // Simulate MCP tool call (this will be replaced with actual MCP calls)
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      // Check if this is a write operation
      if (step.nodeClass === 'WRITE_SENSITIVE' && !isWriteEnabled) {
        return {
          ...updatedStep,
          status: 'skipped',
          endTime: new Date().toISOString(),
          result: { message: 'Write operation skipped - write not enabled' }
        };
      }
      
      // Simulate success/failure based on node class
      const shouldFail = Math.random() < 0.1; // 10% chance of failure
      
      if (shouldFail) {
        throw new Error(`Simulated failure for ${step.nodeLabel}`);
      }
      
      const result = {
        message: `Successfully executed ${step.nodeLabel}`,
        nodeClass: step.nodeClass,
        timestamp: new Date().toISOString()
      };
      
      return {
        ...updatedStep,
        status: 'completed',
        endTime: new Date().toISOString(),
        result
      };
      
    } catch (error) {
      return {
        ...updatedStep,
        status: 'failed',
        endTime: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }, [isWriteEnabled]);

  // Execute workflow
  const executeWorkflow = useCallback(async () => {
    if (isExecuting) return;
    
    setIsExecuting(true);
    initializeExecution();
    
    try {
      for (let i = 0; i < executionSteps.length; i++) {
        setCurrentStepIndex(i);
        const step = executionSteps[i];
        
        const updatedStep = await executeStep(step);
        
        setExecutionSteps(prev => 
          prev.map(s => s.id === step.id ? updatedStep : s)
        );
        
        // Small delay between steps
        await new Promise(resolve => setTimeout(resolve, 200));
      }
      
      toast.success('Workflow execution completed');
      onExecutionComplete(executionSteps);
      
    } catch (error) {
      console.error('Execution failed:', error);
      toast.error('Workflow execution failed');
    } finally {
      setIsExecuting(false);
      setCurrentStepIndex(-1);
    }
  }, [executionSteps, executeStep, isExecuting, onExecutionComplete, initializeExecution]);

  // Pause execution
  const pauseExecution = useCallback(() => {
    // This will be implemented when we add pause/resume functionality
    toast.info('Pause functionality coming soon');
  }, []);

  // Stop execution
  const stopExecution = useCallback(() => {
    setIsExecuting(false);
    setCurrentStepIndex(-1);
    toast.info('Execution stopped');
  }, []);

  // Reset execution
  const resetExecution = useCallback(() => {
    setExecutionSteps([]);
    setCurrentStepIndex(-1);
    setExecutionId('');
  }, []);

  // Get execution summary
  const getExecutionSummary = () => {
    const completed = executionSteps.filter(s => s.status === 'completed').length;
    const failed = executionSteps.filter(s => s.status === 'failed').length;
    const skipped = executionSteps.filter(s => s.status === 'skipped').length;
    const pending = executionSteps.filter(s => s.status === 'pending').length;
    
    return { completed, failed, skipped, pending };
  };

  const summary = getExecutionSummary();

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">Live Execution</h3>
        <div className="flex items-center gap-2">
          {executionId && (
            <Badge variant="outline" className="text-xs">
              {executionId.slice(-8)}
            </Badge>
          )}
          <Badge 
            variant={isExecuting ? "default" : "secondary"}
            className="text-xs"
          >
            {isExecuting ? "Running" : "Ready"}
          </Badge>
        </div>
      </div>

      {/* Execution Controls */}
      <div className="flex gap-2 mb-3">
        <Button
          onClick={executeWorkflow}
          disabled={isExecuting || nodes.length === 0}
          size="sm"
          className="flex-1"
        >
          <Play className="h-4 w-4 mr-1" />
          {isExecuting ? "Running..." : "Execute"}
        </Button>
        
        <Button
          onClick={pauseExecution}
          disabled={!isExecuting}
          size="sm"
          variant="outline"
        >
          <Pause className="h-4 w-4" />
        </Button>
        
        <Button
          onClick={stopExecution}
          disabled={!isExecuting}
          size="sm"
          variant="outline"
        >
          <Square className="h-4 w-4" />
        </Button>
        
        <Button
          onClick={resetExecution}
          disabled={isExecuting}
          size="sm"
          variant="outline"
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>

      {/* Execution Summary */}
      {executionSteps.length > 0 && (
        <div className="mb-3">
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1">
              <CheckCircle className="h-3 w-3 text-green-600" />
              <span>{summary.completed}</span>
            </div>
            <div className="flex items-center gap-1">
              <XCircle className="h-3 w-3 text-red-600" />
              <span>{summary.failed}</span>
            </div>
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3 text-yellow-600" />
              <span>{summary.skipped}</span>
            </div>
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3 text-gray-600" />
              <span>{summary.pending}</span>
            </div>
          </div>
        </div>
      )}

      {/* Execution Steps */}
      {executionSteps.length > 0 && (
        <div className="space-y-2 max-h-48 overflow-auto">
          {executionSteps.map((step, index) => (
            <div
              key={step.id}
              className={`text-xs p-2 rounded border ${
                index === currentStepIndex && isExecuting
                  ? 'bg-blue-50 border-blue-200'
                  : step.status === 'completed'
                  ? 'bg-green-50 border-green-200'
                  : step.status === 'failed'
                  ? 'bg-red-50 border-red-200'
                  : step.status === 'skipped'
                  ? 'bg-yellow-50 border-yellow-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{step.nodeLabel}</span>
                <Badge 
                  variant={
                    step.status === 'completed' ? 'default' :
                    step.status === 'failed' ? 'destructive' :
                    step.status === 'skipped' ? 'secondary' :
                    step.status === 'running' ? 'default' : 'outline'
                  }
                  className="text-xs"
                >
                  {step.status}
                </Badge>
              </div>
              
              {step.nodeClass && (
                <div className="text-xs text-gray-600 mt-1">
                  Class: {step.nodeClass}
                </div>
              )}
              
              {step.result && (
                <div className="text-xs text-green-700 mt-1">
                  {step.result.message}
                </div>
              )}
              
              {step.error && (
                <div className="text-xs text-red-700 mt-1">
                  Error: {step.error}
                </div>
              )}
              
              {step.duration && (
                <div className="text-xs text-gray-500 mt-1">
                  Duration: {step.duration}ms
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Write Operation Warning */}
      {!isWriteEnabled && nodes.some((n: any) => n.data?.nodeClass === 'WRITE_SENSITIVE') && (
        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
          ⚠️ Write operations will be skipped (write not enabled)
        </div>
      )}
    </Card>
  );
}


