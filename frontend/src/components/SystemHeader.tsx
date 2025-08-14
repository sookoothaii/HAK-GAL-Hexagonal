import React from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { wsService } from '@/hooks/useGovernorSocket';
import { Button } from '@/components/ui/button';
import { Power } from 'lucide-react';

const SystemHeader = () => {
  const isConnected = useGovernorStore(state => state.isConnected);
  const governorStatus = useGovernorStore(state => state.governor.status);
  const governorRunning = useGovernorStore(state => state.governor.running);
  
  const getSystemStatus = () => {
    if (!isConnected) return { status: 'OFFLINE', color: 'bg-destructive' };
    if (governorStatus === 'ERROR') return { status: 'DEGRADED', color: 'bg-warning' };
    return { status: 'OPERATIONAL', color: 'bg-success' };
  };

  const systemStatus = getSystemStatus();

  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          HAK-GAL Neuro-Symbolic Command Center
        </h1>
        
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${systemStatus.color} animate-pulse`} />
          <span className={`text-sm font-medium ${systemStatus.color.replace('bg-', 'text-')}`}>
            {systemStatus.status}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Governor Control Button */}
        <Button
          onClick={() => wsService.toggleGovernor(!governorRunning)}
          variant={governorRunning ? "destructive" : "default"}
          size="sm"
          disabled={!isConnected}
          className="flex items-center gap-2"
        >
          <Power className="w-4 h-4" />
          {governorRunning ? 'Stop' : 'Start'} Governor
        </Button>
        
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success' : 'bg-destructive'}`} />
          <span className="text-sm text-muted-foreground">
            WebSocket {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </header>
  );
};

export default SystemHeader;
