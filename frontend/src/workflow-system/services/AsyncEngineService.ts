// AsyncEngineService.ts - Manages async engine execution and polling
import { EventEmitter } from '../core/events/EventEmitter';

export interface AsyncEngineTask {
  id: string;
  engine: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'stopped';
  params: Record<string, any>;
  result?: any;
  error?: string;
  start_time?: number;
  end_time?: number;
  runtime_seconds?: number;
}

export class AsyncEngineService extends EventEmitter {
  private apiUrl = 'http://localhost:5002';
  private pollingIntervals: Map<string, NodeJS.Timeout> = new Map();
  private maxPollingAttempts: Map<string, number> = new Map();
  
  async startEngine(
    engine: string, 
    params: Record<string, any>
  ): Promise<string> {
    try {
      const response = await fetch(`${this.apiUrl}/api/engines/async/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engine, ...params })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to start engine: ${response.statusText}`);
      }
      
      const data = await response.json();
      const taskId = data.task_id;
      
      // Calculate max attempts based on duration
      const durationMinutes = params.duration_minutes || 1;
      // Allow 2x the duration + 1 minute buffer for polling
      const maxMinutes = (durationMinutes * 2) + 1;
      const maxAttempts = Math.ceil((maxMinutes * 60) / 5); // 5 second intervals
      
      this.maxPollingAttempts.set(taskId, maxAttempts);
      
      // Start polling for status
      this.startPolling(taskId);
      
      return taskId;
    } catch (error) {
      console.error('Failed to start engine:', error);
      throw error;
    }
  }
  
  private startPolling(taskId: string): void {
    let attemptCount = 0;
    const maxAttempts = this.maxPollingAttempts.get(taskId) || 60; // Default 5 minutes
    
    const interval = setInterval(async () => {
      attemptCount++;
      
      try {
        const task = await this.getTaskStatus(taskId);
        
        // Emit progress event
        this.emit('task:progress', { taskId, task });
        
        // Check if task is complete
        if (task.status === 'completed' || task.status === 'failed' || task.status === 'stopped') {
          this.stopPolling(taskId);
          this.emit('task:complete', { taskId, task });
        } else if (attemptCount >= maxAttempts) {
          // Timeout - but don't stop the task, it might still be running
          console.warn(`Polling timeout for task ${taskId} after ${maxAttempts} attempts`);
          this.stopPolling(taskId);
          
          // Check one more time
          const finalCheck = await this.getTaskStatus(taskId);
          if (finalCheck.status === 'completed') {
            this.emit('task:complete', { taskId, task: finalCheck });
          } else {
            this.emit('task:timeout', { 
              taskId, 
              message: `Task still running after ${Math.floor(maxAttempts * 5 / 60)} minutes. Check status manually.` 
            });
          }
        }
      } catch (error) {
        console.error(`Failed to poll task ${taskId}:`, error);
        attemptCount++; // Still count failed attempts
        
        if (attemptCount >= maxAttempts) {
          this.stopPolling(taskId);
          this.emit('task:error', { taskId, error });
        }
      }
    }, 5000); // Poll every 5 seconds
    
    this.pollingIntervals.set(taskId, interval);
  }
  
  private stopPolling(taskId: string): void {
    const interval = this.pollingIntervals.get(taskId);
    if (interval) {
      clearInterval(interval);
      this.pollingIntervals.delete(taskId);
    }
    this.maxPollingAttempts.delete(taskId);
  }
  
  async getTaskStatus(taskId: string): Promise<AsyncEngineTask> {
    const response = await fetch(`${this.apiUrl}/api/engines/async/status/${taskId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get task status: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async listTasks(): Promise<{
    tasks: AsyncEngineTask[];
    running: number;
    completed: number;
    failed: number;
  }> {
    const response = await fetch(`${this.apiUrl}/api/engines/async/list`);
    
    if (!response.ok) {
      throw new Error(`Failed to list tasks: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async stopTask(taskId: string): Promise<void> {
    const response = await fetch(`${this.apiUrl}/api/engines/async/stop/${taskId}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to stop task: ${response.statusText}`);
    }
    
    this.stopPolling(taskId);
  }
  
  // Clean up all polling intervals
  destroy(): void {
    this.pollingIntervals.forEach(interval => clearInterval(interval));
    this.pollingIntervals.clear();
    this.maxPollingAttempts.clear();
    this.removeAllListeners();
  }
}

export const asyncEngineService = new AsyncEngineService();
