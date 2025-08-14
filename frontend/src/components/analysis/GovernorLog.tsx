import React from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';

const GovernorLog = () => {
  const governorDecisions = useGovernorStore(state => state.governorDecisions);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'METRIC_ANALYSIS': return 'text-primary';
      case 'KNOWLEDGE_ACQUISITION': return 'text-primary';
      case 'KNOWLEDGE_BALANCE': return 'text-secondary';
      case 'ACTION': return 'text-success';
      case 'DECISION': return 'text-secondary';
      case 'WARNING': return 'text-warning';
      case 'SYSTEM_HEALTH': return 'text-accent';
      case 'QUALITY_IMPROVEMENT': return 'text-primary';

      case 'PROVER_OPTIMIZATION': return 'text-accent';
      default: return 'text-muted-foreground';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'KNOWLEDGE_ACQUISITION': return '📚';
      case 'KNOWLEDGE_BALANCE': return '⚖️';
      case 'METRIC_ANALYSIS': return '📊';
      case 'ACTION': return '⚡';
      case 'DECISION': return '🎯';
      case 'WARNING': return '⚠️';
      case 'SYSTEM_HEALTH': return '💊';
      case 'QUALITY_IMPROVEMENT': return '✨';

      case 'PROVER_OPTIMIZATION': return '🔧';
      default: return '📝';
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold">Governor Decision Log</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-3">
          {governorDecisions.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-sm text-muted-foreground">
                No decisions recorded yet
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                Governor decisions will appear here when the system is active
              </p>
            </div>
          ) : (
            governorDecisions.map((entry, idx) => (
              <div 
                key={idx} 
                className="p-3 rounded-lg bg-background border border-border hover:border-primary/50 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <span className="text-lg mt-0.5">{getTypeIcon(entry.type)}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-muted-foreground font-mono">
                        [{new Date(entry.timestamp).toLocaleTimeString()}]
                      </span>
                      <span className={`text-xs font-medium ${getTypeColor(entry.type)}`}>
                        {entry.type}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        entry.priority === 'high' 
                          ? 'bg-destructive/20 text-destructive' 
                          : entry.priority === 'medium'
                          ? 'bg-primary/20 text-primary'
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        {entry.priority}
                      </span>
                    </div>
                    <div className="text-sm">{entry.reason}</div>
                    <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                      <span>Action: <span className="font-mono">{entry.action}</span></span>
                      <span>Target: <span className="font-mono">{entry.target}</span></span>
                      {entry.executed && (
                        <span className="text-success">✓ Executed</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      
      <div className="p-4 border-t border-border bg-muted/50">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Auto-refresh enabled</span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
            Live
          </span>
        </div>
      </div>
    </div>
  );
};

export default GovernorLog;
