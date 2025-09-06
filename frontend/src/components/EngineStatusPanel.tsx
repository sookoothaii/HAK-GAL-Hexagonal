import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { httpClient } from '@/services/api';
import { 
  Activity, Clock, CheckCircle, XCircle, 
  AlertCircle, Loader2, Zap 
} from 'lucide-react';

interface EngineTask {
  id: string;
  engine: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'stopped';
  params: any;
  start_time?: number;
  end_time?: number;
  runtime_seconds?: number;
  result?: any;
  error?: string;
}

export function EngineStatusPanel() {
  const [tasks, setTasks] = useState<EngineTask[]>([]);
  const [isPolling, setIsPolling] = useState(true);

  // Poll for status updates
  useEffect(() => {
    if (!isPolling) return;

    const pollStatus = async () => {
      try {
        const response = await httpClient.get('/api/engines/async/list');
        if (response.data && response.data.tasks) {
          setTasks(response.data.tasks);
        }
      } catch (error) {
        console.error('[EngineStatus] Poll error:', error);
      }
    };

    // Initial poll
    pollStatus();

    // Poll every 2 seconds
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [isPolling]);

  // Get status color and icon
  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'pending':
        return { 
          color: 'bg-yellow-500', 
          icon: <AlertCircle className="w-4 h-4" />,
          text: 'Pending' 
        };
      case 'running':
        return { 
          color: 'bg-blue-500', 
          icon: <Loader2 className="w-4 h-4 animate-spin" />,
          text: 'Running' 
        };
      case 'completed':
        return { 
          color: 'bg-green-500', 
          icon: <CheckCircle className="w-4 h-4" />,
          text: 'Completed' 
        };
      case 'failed':
        return { 
          color: 'bg-red-500', 
          icon: <XCircle className="w-4 h-4" />,
          text: 'Failed' 
        };
      case 'stopped':
        return { 
          color: 'bg-gray-500', 
          icon: <XCircle className="w-4 h-4" />,
          text: 'Stopped' 
        };
      default:
        return { 
          color: 'bg-gray-400', 
          icon: <AlertCircle className="w-4 h-4" />,
          text: 'Unknown' 
        };
    }
  };

  // Calculate progress
  const getProgress = (task: EngineTask) => {
    if (task.status !== 'running') return null;
    
    const duration = task.params?.duration_minutes || 1;
    const elapsed = task.runtime_seconds || 0;
    const totalSeconds = duration * 60;
    const progress = Math.min((elapsed / totalSeconds) * 100, 100);
    
    return {
      percent: progress,
      elapsed: elapsed,
      total: totalSeconds,
      remaining: Math.max(totalSeconds - elapsed, 0)
    };
  };

  // Format time
  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    if (minutes < 60) return `${minutes}m ${secs}s`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  // Get running tasks
  const runningTasks = tasks.filter(t => t.status === 'running');
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const failedTasks = tasks.filter(t => t.status === 'failed');

  return (
    <Card className="p-4 bg-card border">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-violet-500" />
          <h3 className="font-semibold">Engine Status Monitor</h3>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">
            {runningTasks.length} Running
          </Badge>
          <div className={`w-2 h-2 rounded-full ${runningTasks.length > 0 ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
        </div>
      </div>

      {/* Active Tasks */}
      {runningTasks.length > 0 && (
        <div className="space-y-3 mb-4">
          <div className="text-sm font-medium text-muted-foreground">Active Engines</div>
          {runningTasks.map(task => {
            const progress = getProgress(task);
            const status = getStatusDisplay(task.status);
            
            return (
              <div key={task.id} className="space-y-2 p-3 bg-muted/50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {status.icon}
                    <span className="font-medium text-sm">
                      {task.engine.toUpperCase()}
                    </span>
                    <Badge variant="secondary" className="text-xs">
                      {task.params?.duration_minutes || 1} min
                    </Badge>
                  </div>
                  {progress && (
                    <span className="text-xs text-muted-foreground">
                      {formatTime(progress.remaining)} remaining
                    </span>
                  )}
                </div>
                
                {/* Progress Bar */}
                {progress && (
                  <div className="space-y-1">
                    <Progress value={progress.percent} className="h-2" />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>{formatTime(progress.elapsed)} elapsed</span>
                      <span>{Math.round(progress.percent)}%</span>
                    </div>
                  </div>
                )}
                
                {/* Topic/Params */}
                {task.params?.topic && (
                  <div className="text-xs text-muted-foreground">
                    Topic: {task.params.topic}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* No Running Tasks */}
      {runningTasks.length === 0 && (
        <div className="py-8 text-center text-muted-foreground">
          <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <div className="text-sm">No engines running</div>
          <div className="text-xs mt-1">Start a workflow to see engine activity</div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="pt-3 border-t flex items-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <CheckCircle className="w-3 h-3 text-green-500" />
          <span>{completedTasks.length} completed</span>
        </div>
        {failedTasks.length > 0 && (
          <div className="flex items-center gap-1">
            <XCircle className="w-3 h-3 text-red-500" />
            <span>{failedTasks.length} failed</span>
          </div>
        )}
        <div className="flex-1" />
        <button
          onClick={() => setIsPolling(!isPolling)}
          className="text-xs hover:underline"
        >
          {isPolling ? 'Pause' : 'Resume'} updates
        </button>
      </div>
    </Card>
  );
}
