import React from 'react';
import { motion } from 'framer-motion';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Brain, Cpu, Database, Network, Zap, Activity, GitBranch, Sparkles } from 'lucide-react';
import { CURRENT_BACKEND, hasFeature, API_BASE_URL } from '@/config/backends';
import { safeApiCall } from '@/utils/api-helpers';
import { httpClient } from '@/services/api';

const ProDashboard: React.FC = () => {
  const store = useGovernorStore();
  const [hrmStatus, setHrmStatus] = React.useState<any>(null);
  const [systemHealth, setSystemHealth] = React.useState<any>(null);
  
  React.useEffect(() => {
    // Check HRM status with robust error handling
    if (hasFeature('hrm') || hasFeature('neuralReasoning')) {
      safeApiCall(
        async () => {
          const response = await httpClient.post('/api/reason', { query: 'test' });
          return response.data;
        },
        { silent: true }
      ).then(data => {
        if (data) {
          setHrmStatus({ operational: true, confidence: data.confidence || 0 });
        } else {
          setHrmStatus({ operational: false, message: 'HRM endpoint not available' });
        }
      });
    }
    
    // Get system health with fallback
    safeApiCall(
      async () => {
        const response = await httpClient.get('/health');
        return response.data;
      },
      { silent: true }
    ).then(data => {
      if (data) {
        setSystemHealth(data);
      }
    });
  }, []);
  
  const neuralMetrics = {
    model: hrmStatus?.operational ? 'SimplifiedHRM (GRU)' : 'Not Available',
    parameters: hrmStatus?.operational ? '572,673' : 'n/a',
    vocabulary: hrmStatus?.operational ? '694 terms' : 'n/a',
    device: store.gpuInfo?.name || systemHealth?.gpu?.name || 'CPU',
    inference: hrmStatus?.operational ? '<10ms' : 'n/a'
  };
  
  const symbolicMetrics = {
    facts: store.kb.metrics.factCount || 0,
    predicates: store.kb.metrics.uniquePredicates || 74,
    rules: 15,
    provers: 4,
    coverage: store.kb.metrics.factCount > 0 
      ? Math.round((store.kb.metrics.factCount / 10000) * 100) 
      : 0
  };
  
  const learningMetrics = {
    governorMode: store.governor.status || 'Unknown',
    learningRate: store.kb.metrics.growthRate || 0,
    decisions: store.governor.decisions.length || 0,
    running: store.governor.running || false
  };
  
  // Helper component for safe data display
  const MetricRow = ({ label, value, badge = false }: { label: string; value: any; badge?: boolean }) => (
    <div className="flex justify-between items-center">
      <span className="text-sm text-muted-foreground">{label}</span>
      {badge ? (
        <Badge variant="outline" className="font-mono">
          {value ?? 'n/a'}
        </Badge>
      ) : (
        <span className="font-mono text-sm">{value ?? 'n/a'}</span>
      )}
    </div>
  );
  
  return (
    <div className="h-full overflow-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          HAK-GAL Neurosymbolic Intelligence Suite
        </h1>
        <p className="text-muted-foreground mt-2">
          Backend: {CURRENT_BACKEND.name} ({CURRENT_BACKEND.port}) | 
          Architecture: {systemHealth?.architecture || CURRENT_BACKEND.stats.architecture} | 
          Status: {systemHealth?.status || 'Unknown'}
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
            <CardDescription>
              {hrmStatus?.operational ? 'HRM Neural Reasoning System' : 'Neural system unavailable'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <MetricRow label="Model" value={neuralMetrics.model} badge />
            <MetricRow label="Parameters" value={neuralMetrics.parameters} />
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Device</span>
              <Badge variant={neuralMetrics.device.includes('NVIDIA') ? 'default' : 'secondary'}>
                {neuralMetrics.device}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Inference</span>
              <span className={`font-mono text-sm ${hrmStatus?.operational ? 'text-green-500' : 'text-muted-foreground'}`}>
                {neuralMetrics.inference}
              </span>
            </div>
            {hrmStatus?.message && (
              <p className="text-xs text-muted-foreground italic">{hrmStatus.message}</p>
            )}
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
            <MetricRow label="Predicates" value={symbolicMetrics.predicates} />
            <MetricRow label="Provers" value={symbolicMetrics.provers} />
            <div className="space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">KB Coverage</span>
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
            <MetricRow label="Mode" value={learningMetrics.governorMode} badge />
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Learning Rate</span>
              <span className="font-mono text-sm">
                {learningMetrics.learningRate.toFixed(2)} facts/min
              </span>
            </div>
            <MetricRow label="Decisions" value={learningMetrics.decisions} />
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
                {systemHealth?.architecture || 'Hexagonal'}
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">Response</span>
              </div>
              <Badge variant="outline">
                {CURRENT_BACKEND.stats.responseTime}
              </Badge>
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
          
          {/* Health Information */}
          {systemHealth && (
            <div className="mt-6 pt-6 border-t">
              <h4 className="text-sm font-medium mb-3">Backend Health</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div>
                  <span className="text-muted-foreground">Port:</span>
                  <div className="font-mono">{systemHealth.port || 'n/a'}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Repository:</span>
                  <div className="font-mono text-xs">{systemHealth.repository || 'n/a'}</div>
                </div>
                {systemHealth.mojo && (
                  <div>
                    <span className="text-muted-foreground">Mojo:</span>
                    <div className="font-mono">
                      {systemHealth.mojo.available ? 'Available' : 'Disabled'}
                    </div>
                  </div>
                )}
                {systemHealth.read_only !== undefined && (
                  <div>
                    <span className="text-muted-foreground">Mode:</span>
                    <div className="font-mono">
                      {systemHealth.read_only ? 'Read-Only' : 'Read-Write'}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ProDashboard;