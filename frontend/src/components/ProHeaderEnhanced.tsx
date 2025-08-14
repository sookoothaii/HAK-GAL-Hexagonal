import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Database, 
  Network, 
  Zap, 
  Activity,
  Server,
  ChevronDown,
  Check,
  Sparkles
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { BACKENDS, getActiveBackend, setActiveBackend, hasFeature } from '@/config/backends';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

export const ProHeaderEnhanced: React.FC = () => {
  const currentBackend = getActiveBackend();
  const store = useGovernorStore();
  
  const handleSwitch = (backendKey: 'original' | 'hexagonal') => {
    if (backendKey === currentBackend.type) return;
    
    toast.info(`Switching to ${BACKENDS[backendKey].name}...`, {
      description: 'The page will reload to apply changes.',
    });
    
    setTimeout(() => {
      setActiveBackend(backendKey);
    }, 1000);
  };
  
  // Calculate system health score
  const healthScore = React.useMemo(() => {
    let score = 0;
    if (store.isConnected) score += 25;
    if (store.kb.metrics.factCount > 0) score += 25;
    if (store.governor.running) score += 25;
    if (store.gpuInfo) score += 25;
    return score;
  }, [store]);
  
  const healthColor = healthScore >= 75 ? 'text-green-500' : 
                      healthScore >= 50 ? 'text-yellow-500' : 
                      'text-red-500';
  
  return (
    <header className="h-16 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="h-full px-4 flex items-center justify-between">
        {/* Left Section - System Identity */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                HAK-GAL Suite
              </h1>
              <p className="text-xs text-muted-foreground">
                Neurosymbolic Self-Learning System
              </p>
            </div>
          </div>
          
          {/* System Health Badge */}
          <Badge variant="outline" className={cn("gap-1", healthColor)}>
            <Activity className="h-3 w-3" />
            {healthScore}% Health
          </Badge>
        </div>
        
        {/* Center Section - Live Metrics */}
        <div className="hidden lg:flex items-center gap-6">
          {/* Neural Status */}
          <div className="flex items-center gap-2">
            <Brain className="h-4 w-4 text-blue-500" />
            <div className="text-sm">
              <span className="text-muted-foreground">Neural:</span>
              <span className="ml-1 font-mono">
                {hasFeature('hrm') ? 'HRM Active' : 'Bridge Mode'}
              </span>
            </div>
          </div>
          
          {/* Symbolic Status */}
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-green-500" />
            <div className="text-sm">
              <span className="text-muted-foreground">Facts:</span>
              <span className="ml-1 font-mono">
                {store.kb.metrics.factCount || 0}
              </span>
            </div>
          </div>
          
          {/* Learning Status */}
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-purple-500" />
            <div className="text-sm">
              <span className="text-muted-foreground">Learning:</span>
              <span className="ml-1 font-mono">
                {store.governor.running ? 'Active' : 'Paused'}
              </span>
            </div>
          </div>
          
          {/* Performance */}
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-yellow-500" />
            <div className="text-sm">
              <span className="text-muted-foreground">Response:</span>
              <span className="ml-1 font-mono">
                {currentBackend.stats.responseTime}
              </span>
            </div>
          </div>
        </div>
        
        {/* Right Section - Backend Switcher */}
        <div className="flex items-center gap-3">
          {/* Connection Status */}
          <Badge 
            variant={store.isConnected ? 'default' : 'destructive'}
            className="gap-1"
          >
            <Network className="h-3 w-3" />
            {store.isConnected ? 'Connected' : 'Disconnected'}
          </Badge>
          
          {/* Backend Switcher */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="gap-2">
                <Server className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {currentBackend.type === 'original' ? 'Production' : 'Development'}
                </span>
                <Badge variant="secondary" className="ml-1">
                  {currentBackend.port}
                </Badge>
                <ChevronDown className="h-4 w-4 ml-1" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-96">
              <DropdownMenuLabel className="flex items-center gap-2">
                <Network className="h-4 w-4" />
                Backend System Selection
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              
              {Object.entries(BACKENDS).map(([key, backend]) => (
                <DropdownMenuItem
                  key={key}
                  onClick={() => handleSwitch(key as 'original' | 'hexagonal')}
                  className="flex flex-col items-start gap-2 p-3 cursor-pointer"
                >
                  <div className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-2">
                      <Server className="h-4 w-4" />
                      <span className="font-medium">{backend.name}</span>
                      {currentBackend.type === backend.type && (
                        <Check className="h-4 w-4 text-primary" />
                      )}
                    </div>
                    <Badge variant="outline">Port {backend.port}</Badge>
                  </div>
                  
                  <div className="text-xs text-muted-foreground">
                    {backend.stats.architecture}
                  </div>
                  
                  <div className="flex flex-wrap gap-1 mt-1">
                    <Badge variant="secondary" className="text-xs">
                      {backend.stats.facts} facts
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      {backend.stats.responseTime}
                    </Badge>
                    {backend.features.cudaAcceleration && (
                      <Badge variant="secondary" className="text-xs">
                        CUDA
                      </Badge>
                    )}
                    {backend.features.emergencyTools && (
                      <Badge variant="secondary" className="text-xs">
                        Emergency Tools
                      </Badge>
                    )}
                  </div>
                  
                  {/* Feature Indicators */}
                  <div className="flex flex-wrap gap-1 mt-2">
                    {backend.features.websocket && (
                      <div className="w-2 h-2 rounded-full bg-green-500" title="WebSocket" />
                    )}
                    {backend.features.governor && (
                      <div className="w-2 h-2 rounded-full bg-blue-500" title="Governor" />
                    )}
                    {backend.features.neuralReasoning && (
                      <div className="w-2 h-2 rounded-full bg-purple-500" title="Neural" />
                    )}
                    {backend.features.autoLearning && (
                      <div className="w-2 h-2 rounded-full bg-yellow-500" title="Auto-Learn" />
                    )}
                    {backend.features.llmIntegration && (
                      <div className="w-2 h-2 rounded-full bg-orange-500" title="LLM" />
                    )}
                  </div>
                </DropdownMenuItem>
              ))}
              
              <DropdownMenuSeparator />
              <div className="px-3 py-2">
                <p className="text-xs text-muted-foreground">
                  <strong>Production (5000):</strong> Full features, stable, all engines integrated.
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  <strong>Development (5001):</strong> Clean architecture, emergency tools, experimental.
                </p>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};

export default ProHeaderEnhanced;
