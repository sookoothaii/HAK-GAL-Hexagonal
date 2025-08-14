import React from 'react';
import { NavLink } from 'react-router-dom';
import { useGovernorStore } from '@/stores/useGovernorStore';

const Navigation = () => {
  const isConnected = useGovernorStore(state => state.isConnected);
  const systemStatus = useGovernorStore(state => state.systemStatus);
  const governorRunning = useGovernorStore(state => state.governorRunning);
  
  // Backend is fixed to hexagonal (5001)

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/query', label: 'Query Interface', icon: '🔍' },
    { path: '/knowledge', label: 'Knowledge Base', icon: '🧠' },
    { path: '/governor', label: 'Governor', icon: '🎯' },
    { path: '/engines', label: 'Engines', icon: '⚙️' },
    { path: '/llm', label: 'LLM Providers', icon: '🤖' },
  ];

  const getStatusColor = () => {
    if (!isConnected) return 'bg-destructive';
    if (systemStatus === 'operational') return 'bg-success';
    if (systemStatus === 'degraded') return 'bg-warning';
    return 'bg-destructive';
  };

  return (
    <nav className="h-full w-full bg-card border-r border-border flex flex-col">
      <div className="p-4 border-b border-border">
         <h1 className="text-lg font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
           HAK-GAL Suite
         </h1>
         <p className="text-xs text-muted-foreground mt-1">
           Neuro-Symbolic Command Center
         </p>
        
        <div className="mt-3 flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
          <span className="text-xs text-muted-foreground">
             {systemStatus.toUpperCase()}
          </span>
          {governorRunning && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">
              Governor Active
            </span>
          )}
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2">
        <div className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-primary/20 text-primary font-medium'
                    : 'hover:bg-muted text-muted-foreground hover:text-foreground'
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>
      </div>
      
      <div className="p-4 border-t border-border space-y-3">
        {/* WebSocket Status */}
        <div className="text-xs text-muted-foreground">
          <div className="flex items-center justify-between">
            <span>WebSocket</span>
            <span className={`flex items-center gap-1 ${isConnected ? 'text-success' : 'text-destructive'}`}>
              <div className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-success' : 'bg-destructive'}`} />
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
