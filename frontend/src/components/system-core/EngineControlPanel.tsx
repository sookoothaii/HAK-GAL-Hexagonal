import React from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { wsService } from '@/hooks/useGovernorSocket';

const EngineControlPanel = () => {
  const engines = useGovernorStore(state => state.engines);

  const toggleEngine = async (engineName: string, currentStatus: string) => {
    if (currentStatus === 'running') {
      wsService.stopEngine(engineName);
      console.log(`Stopping engine: ${engineName}`);
    } else {
      wsService.startEngine(engineName);
      console.log(`Starting engine: ${engineName}`);
    }
  };

  // Enhanced: Send engine configuration to backend
  const updateEngineConfig = async (engineName: string, config: any) => {
    wsService.sendMessage('engine_config', {
      engine: engineName,
      config: config
    });
  };

  // Enhanced: Get engine mode options from backend
  const getEngineModes = (engineName: string) => {
    const engine = engines.find(e => e.name === engineName);
    return engine?.modes || ['default', 'performance', 'conservative'];
  };

  // Enhanced: Get comprehensive engine status
  const getEngineStatus = (engine: any) => {
    const status = engine.status || 'unknown';
    const mode = engine.mode || 'default';
    const progress = engine.progress || 0;
    const lastActivity = engine.lastActivity || engine.last_activity;
    const uptime = engine.uptime || 0;
    const memoryUsage = engine.memory_usage || engine.memoryUsage || 0;
    const cpuUsage = engine.cpu_usage || engine.cpuUsage || 0;
    
    return {
      status,
      mode,
      progress,
      lastActivity,
      uptime,
      memoryUsage,
      cpuUsage
    };
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-success';
      case 'stopped': return 'bg-muted';
      case 'error': return 'bg-destructive';
      case 'starting': return 'bg-warning';
      case 'stopping': return 'bg-warning';
      default: return 'bg-muted';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running': return 'Running';
      case 'stopped': return 'Stopped';
      case 'error': return 'Error';
      case 'starting': return 'Starting...';
      case 'stopping': return 'Stopping...';
      default: return 'Unknown';
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold">Engine Control</h2>
        <p className="text-xs text-muted-foreground">
          {engines.filter(e => e.status === 'running').length} of {engines.length} engines active
        </p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {engines.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm text-muted-foreground">
              No engines detected. Waiting for system data...
            </p>
          </div>
        ) : (
          engines.map((engine, idx) => {
            const engineStatus = getEngineStatus(engine);
            return (
              <div key={idx} className="p-4 rounded-lg bg-background border border-border">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(engineStatus.status)} ${
                      engineStatus.status === 'running' ? 'animate-pulse' : ''
                    }`} />
                    <div>
                      <h3 className="font-medium">{engine.name}</h3>
                      <div className="flex items-center gap-2">
                        {engineStatus.mode && (
                          <span className="text-xs text-muted-foreground">Mode: {engineStatus.mode}</span>
                        )}
                        <span className="text-xs text-muted-foreground">
                          {getStatusText(engineStatus.status)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => toggleEngine(engine.name, engineStatus.status)}
                    className={`px-3 py-1 text-sm rounded-md transition-colors hover:opacity-80 ${
                      engineStatus.status === 'running' 
                        ? 'bg-destructive/20 text-destructive' 
                        : 'bg-success/20 text-success'
                    }`}
                    disabled={engineStatus.status === 'starting' || engineStatus.status === 'stopping'}
                  >
                    {engineStatus.status === 'running' ? 'Stop' : 'Start'}
                  </button>
                </div>
                
                {/* Enhanced: Show engine metrics */}
                {engineStatus.status === 'running' && (
                  <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">CPU:</span>
                      <span className="font-mono">{engineStatus.cpuUsage}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Memory:</span>
                      <span className="font-mono">{engineStatus.memoryUsage}%</span>
                    </div>
                    {engineStatus.uptime > 0 && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Uptime:</span>
                        <span className="font-mono">{Math.floor(engineStatus.uptime / 60)}m</span>
                      </div>
                    )}
                  </div>
                )}
                
                {engineStatus.progress !== undefined && engineStatus.status === 'running' && (
                  <div className="mb-2">
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary transition-all duration-500"
                        style={{ width: `${engineStatus.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground">{engineStatus.progress}%</span>
                  </div>
                )}
                
                {engineStatus.lastActivity && (
                  <div className="text-xs text-muted-foreground italic">
                    Last Activity: {new Date(engineStatus.lastActivity).toLocaleTimeString()}
                  </div>
                )}
                
                {/* Enhanced: Show engine errors if any */}
                {engine.error && (
                  <div className="mt-2 p-2 bg-destructive/10 rounded text-xs text-destructive">
                    Error: {engine.error}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default EngineControlPanel;
