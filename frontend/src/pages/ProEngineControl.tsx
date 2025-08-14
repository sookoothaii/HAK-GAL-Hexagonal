// V3 - Simplified, Read-Only View
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { motion } from 'framer-motion';
import { Zap, Brain, Cpu, AlertTriangle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

// Simplified Engine Card (Read-Only)
const EngineStatusCard: React.FC<{
  engine: { name: string; status: 'running' | 'stopped' | 'error' };
}> = ({ engine }) => {
  const statusColors = {
    running: 'text-green-500 bg-green-500/10 border-green-500/20',
    stopped: 'text-gray-500 bg-gray-500/10 border-gray-500/20',
    error: 'text-red-500 bg-red-500/10 border-red-500/20',
  };

  const getIcon = () => {
    if (engine.name.toLowerCase().includes('aethelred')) return <Brain className="w-5 h-5" />;
    if (engine.name.toLowerCase().includes('thesis')) return <Zap className="w-5 h-5" />;
    return <Cpu className="w-5 h-5" />;
  };

  return (
    <motion.div whileHover={{ scale: 1.02 }}>
      <Card className={cn("border-0 bg-card/50", statusColors[engine.status])}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={cn("p-3 rounded-lg", statusColors[engine.status])}>
                {getIcon()}
              </div>
              <div>
                <CardTitle className="text-lg">{engine.name}</CardTitle>
                <Badge variant="outline" className="mt-1">{engine.status.toUpperCase()}</Badge>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">
            This engine is controlled autonomously by the Bayesian Governor.
          </p>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Main Engine Control Component (Read-Only)
const ProEngineControl: React.FC = () => {
  const isConnected = useGovernorStore(state => state.isConnected);
  const engines = useGovernorStore(state => state.engines);
  const governorRunning = useGovernorStore(state => state.governor.running);
  const governorStatus = useGovernorStore(state => state.governor.status);

  if (!isConnected) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <AlertTriangle className="w-5 h-5 mr-2" /> Not Connected to Backend
      </div>
    );
  }

  return (
    <div className="h-full p-4 space-y-4">
      <Card className="border-0 bg-card/50">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-primary" />
              Governor Status
            </div>
            <Badge variant={governorRunning ? "default" : "secondary"}>
              {governorRunning ? "RUNNING" : "STOPPED"}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Current activity: <span className="font-medium text-foreground">{governorStatus}</span>
          </p>
        </CardContent>
      </Card>

      {engines.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {engines.map((engine) => (
            <EngineStatusCard
              key={engine.name}
              engine={engine}
            />
          ))}
        </div>
      ) : (
        <div className="h-full flex items-center justify-center text-muted-foreground">
          <Loader2 className="w-5 h-5 mr-2 animate-spin" /> Waiting for engine data...
        </div>
      )}
    </div>
  );
};

export default ProEngineControl;
