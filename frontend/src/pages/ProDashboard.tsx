import React from 'react';
import { motion } from 'framer-motion';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Brain, Cpu, Database, Network, Zap, Activity, GitBranch, Sparkles } from 'lucide-react';
import { CURRENT_BACKEND, hasFeature } from '@/config/backends';
import apiService from '@/services/apiService';

const ProDashboard: React.FC = () => {
  const store = useGovernorStore();
  const [hrmStatus, setHrmStatus] = React.useState<any>(null);
  
  React.useEffect(() => {
    // Check HRM status if available
    if (hasFeature('hrm') || hasFeature('neuralReasoning')) {
      apiService.reason("test").then(data => {
        setHrmStatus({ operational: true, confidence: data.confidence || 0 });
      }).catch(() => {
        setHrmStatus({ operational: false });
      });
    }
  }, []);
  
  const neuralMetrics = {
    model: 'SimplifiedHRM (GRU)',
    parameters: '572,673',
    vocabulary: '694 terms',
    device: store.gpuInfo?.name || 'CPU',
    inference: '<10ms'
  };
  
  const symbolicMetrics = {
    facts: store.kb.metrics.factCount || 0,
    predicates: 74,
    rules: 15,
    provers: 4,
    coverage: Math.round((store.kb.metrics.factCount / 1000) * 100)
  };
  
  const learningMetrics = {
    governorMode: store.governor.status,
    learningRate: store.kb.metrics.growthRate || 0,
    decisions: store.governor.decisions.length,
    running: store.governor.running
  };
  
  return (
    <div className="h-full overflow-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          HAK-GAL Neurosymbolic Intelligence Suite
        </h1>
        <p className="text-muted-foreground mt-2">
          Backend: {CURRENT_BACKEND.name} ({CURRENT_BACKEND.port}) | Architecture: {CURRENT_BACKEND.stats.architecture}
        </p>
      </div>
      
      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Neural Component Status */}
        <Card className="border-blue-500/20 bg-gradient-to-br from-blue-950/10 to-background">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-500" />
              Neural Components
            </CardTitle>
            <CardDescription>HRM Neural Reasoning System</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Model</span>
              <Badge variant="outline">{neuralMetrics.model}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Parameters</span>
              <span className="font-mono text-sm">{neuralMetrics.parameters}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Device</span>
              <Badge variant={neuralMetrics.device.includes('NVIDIA') ? 'default' : 'secondary'}>
                {neuralMetrics.device}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Inference</span>
              <span className="text-green-500 font-mono text-sm">{neuralMetrics.inference}</span>
            </div>
          </CardContent>
        </Card>
        
        {/* Symbolic Component Status */}
        <Card className="border-green-500/20 bg-gradient-to-br from-green-950/10 to-background">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-green-500" />
              Symbolic Components
            </CardTitle>
            <CardDescription>Knowledge Base & Logic System</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Facts</span>
              <Badge variant="outline" className="font-mono">
                {symbolicMetrics.facts.toLocaleString()}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Predicates</span>
              <span className="font-mono text-sm">{symbolicMetrics.predicates}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Provers</span>
              <span className="font-mono text-sm">{symbolicMetrics.provers}</span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Coverage</span>
                <span className="text-sm">{symbolicMetrics.coverage}%</span>
              </div>
              <Progress value={symbolicMetrics.coverage} className="h-2" />
            </div>
          </CardContent>
        </Card>
        
        {/* Self-Learning Status */}
        <Card className="border-purple-500/20 bg-gradient-to-br from-purple-950/10 to-background">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              Self-Learning System
            </CardTitle>
            <CardDescription>Autonomous Knowledge Generation</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Governor</span>
              <Badge variant={learningMetrics.running ? 'default' : 'secondary'}>
                {learningMetrics.running ? 'Active' : 'Paused'}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Mode</span>
              <Badge variant="outline">{learningMetrics.governorMode}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Learning Rate</span>
              <span className="font-mono text-sm">
                {learningMetrics.learningRate.toFixed(2)} facts/min
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Decisions</span>
              <span className="font-mono text-sm">{learningMetrics.decisions}</span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* System Integration Status */}
      <Card className="mt-6 border-orange-500/20 bg-gradient-to-br from-orange-950/10 to-background">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5 text-orange-500" />
            Neurosymbolic Integration Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">WebSocket</span>
              </div>
              <Badge variant={store.isConnected ? 'default' : 'destructive'}>
                {store.isConnected ? 'Connected' : 'Disconnected'}
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">CUDA</span>
              </div>
              <Badge variant={store.gpuInfo ? 'default' : 'secondary'}>
                {store.gpuInfo ? 'Active' : 'CPU Mode'}
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <GitBranch className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">Architecture</span>
              </div>
              <Badge variant="outline">
                {CURRENT_BACKEND.type === 'original' ? 'Monolithic' : 'Hexagonal'}
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">Response</span>
              </div>
              <Badge variant="outline">{CURRENT_BACKEND.stats.responseTime}</Badge>
            </div>
          </div>
          
          {/* Feature Grid */}
          <div className="mt-6 pt-6 border-t">
            <h4 className="text-sm font-medium mb-3">System Capabilities</h4>
            <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
              {Object.entries(CURRENT_BACKEND.features).map(([feature, enabled]) => (
                <Badge
                  key={feature}
                  variant={enabled ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {feature.replace(/([A-Z])/g, ' $1').trim()}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProDashboard;
