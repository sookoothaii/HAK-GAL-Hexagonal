import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Brain, Cpu, Database, Network, Zap, Activity, GitBranch, Sparkles } from 'lucide-react';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { CURRENT_BACKEND, hasFeature } from '@/config/backends';
import apiService from '@/services/apiService';

export const NeuroSymbolicDashboard: React.FC = () => {
  const store = useGovernorStore();
  const [hrmStatus, setHrmStatus] = useState<any>(null);
  const [graphStatus, setGraphStatus] = useState<any>(null);
  
  useEffect(() => {
    // Fetch HRM status if available
    if (hasFeature('hrm')) {
      apiService.hrmReason("test").then(data => {
        setHrmStatus({ operational: true, confidence: data.confidence || 0 });
      }).catch(() => {
        setHrmStatus({ operational: false });
      });
    }
    
    // Fetch graph status
    if (hasFeature('graphGeneration')) {
      apiService.graphStatus().then(data => {
        setGraphStatus(data);
      }).catch(() => {
        setGraphStatus(null);
      });
    }
  }, []);
  
  const neuralMetrics = {
    model: 'SimplifiedHRM (GRU)',
    parameters: '572,673',
    vocabulary: '694 terms',
    trainingGap: '0.802',
    device: store.gpuInfo?.name || 'CPU',
    inference: '<10ms'
  };
  
  const symbolicMetrics = {
    facts: store.kb.metrics.factCount || 0,
    predicates: 74,  // From analysis
    rules: 15,  // Estimated
    provers: 4,  // From architecture
    coverage: Math.round((store.kb.metrics.factCount / 1000) * 100)
  };
  
  const learningMetrics = {
    aethelredStatus: store.engines.find(e => e.name === 'aethelred')?.status || 'stopped',
    thesisStatus: store.engines.find(e => e.name === 'thesis')?.status || 'stopped',
    governorMode: store.governor.status,
    learningRate: store.kb.metrics.growthRate || 0,
    decisions: store.governor.decisions.length
  };
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
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
            <span className="text-sm text-muted-foreground">Vocabulary</span>
            <span className="font-mono text-sm">{neuralMetrics.vocabulary}</span>
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
          {hrmStatus && (
            <div className="pt-2 border-t">
              <div className="flex justify-between items-center">
                <span className="text-sm">HRM Status</span>
                <Badge variant={hrmStatus.operational ? 'default' : 'destructive'}>
                  {hrmStatus.operational ? 'Operational' : 'Offline'}
                </Badge>
              </div>
            </div>
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
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Predicates</span>
            <span className="font-mono text-sm">{symbolicMetrics.predicates}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Rules</span>
            <span className="font-mono text-sm">{symbolicMetrics.rules}</span>
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
            <span className="text-sm text-muted-foreground">Aethelred</span>
            <Badge variant={learningMetrics.aethelredStatus === 'running' ? 'default' : 'secondary'}>
              {learningMetrics.aethelredStatus}
            </Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Thesis</span>
            <Badge variant={learningMetrics.thesisStatus === 'running' ? 'default' : 'secondary'}>
              {learningMetrics.thesisStatus}
            </Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Governor</span>
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
      
      {/* Integration Status */}
      <Card className="border-orange-500/20 bg-gradient-to-br from-orange-950/10 to-background lg:col-span-3">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5 text-orange-500" />
            Neurosymbolic Integration
          </CardTitle>
          <CardDescription>
            Backend: {CURRENT_BACKEND.name} | Architecture: {CURRENT_BACKEND.stats.architecture}
          </CardDescription>
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
                <span className="text-sm">Graph</span>
              </div>
              <Badge variant={graphStatus?.graph_exists ? 'default' : 'secondary'}>
                {graphStatus?.graph_exists ? 'Generated' : 'Pending'}
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

export default NeuroSymbolicDashboard;
