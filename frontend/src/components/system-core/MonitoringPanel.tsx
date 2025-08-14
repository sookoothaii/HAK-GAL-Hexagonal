import React, { useState, useEffect } from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { wsService } from '@/hooks/useGovernorSocket';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, AlertTriangle, CheckCircle, Cpu, 
  Zap, Shield, Eye, BarChart3, TrendingUp, AlertCircle, Info
} from 'lucide-react';

const MonitoringPanel = () => {
  const [activeTab, setActiveTab] = useState('system');
  const [refreshing, setRefreshing] = useState(false);
  
  const systemLoad = useGovernorStore(state => state.systemLoad);
  const gpuInfo = useGovernorStore(state => state.gpuInfo);
  const systemStatus = useGovernorStore(state => state.systemStatus);
  const monitoringMetrics = useGovernorStore(state => state.monitoringMetrics);
  const emergencyFixes = useGovernorStore(state => state.emergencyFixes);

  // LLM Explain tester state
  const [explainTopic, setExplainTopic] = useState<string>('quantum entanglement');
  const [explainResult, setExplainResult] = useState<string>('');
  const [explainLoading, setExplainLoading] = useState<boolean>(false);
  const [explainDurationMs, setExplainDurationMs] = useState<number>(0);

  const handleExplainRequest = async () => {
    try {
      setExplainLoading(true);
      setExplainResult('');
      const started = performance.now();
      const res = await fetch('/api/llm/get-explanation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ topic: explainTopic })
      });
      const text = await res.text();
      setExplainResult(text || '');
      setExplainDurationMs(Math.max(0, Math.round(performance.now() - started)));
    } catch (err) {
      setExplainResult('Fehler beim Abrufen der Erklärung.');
    } finally {
      setExplainLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    wsService.requestSystemStatus();
    wsService.requestEmergencyStatus();
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'text-green-500';
      case 'degraded': return 'text-yellow-500';
      case 'offline': return 'text-red-500';
      default: return 'text-muted-foreground';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational': return <CheckCircle className="w-4 h-4" />;
      case 'degraded': return <AlertTriangle className="w-4 h-4" />;
      case 'offline': return <AlertCircle className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">System Monitoring</h2>
            <p className="text-xs text-muted-foreground">
              Real-time system health and performance metrics
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <Activity className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="system">System</TabsTrigger>
            <TabsTrigger value="gpu">GPU</TabsTrigger>
            <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
            <TabsTrigger value="emergency">Emergency</TabsTrigger>
          </TabsList>

          {/* System Health Tab */}
          <TabsContent value="system" className="space-y-4">
            {/* Overall Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Overall System Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  {getStatusIcon(systemStatus)}
                  <span className={`font-medium ${getStatusColor(systemStatus)}`}>
                    {systemStatus.toUpperCase()}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Resource Usage */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Resource Usage
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-blue-500" />
                      <span className="text-sm">CPU Usage</span>
                    </div>
                    <span className="text-sm font-mono">{systemLoad?.cpu || 0}%</span>
                  </div>
                  <Progress value={systemLoad?.cpu || 0} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-green-500" />
                      <span className="text-sm">Memory Usage</span>
                    </div>
                    <span className="text-sm font-mono">{systemLoad?.memory || 0}%</span>
                  </div>
                  <Progress value={systemLoad?.memory || 0} className="h-2" />
                </div>

                {systemLoad?.gpu !== undefined && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Zap className="w-4 h-4 text-purple-500" />
                        <span className="text-sm">GPU Usage</span>
                      </div>
                      <span className="text-sm font-mono">{systemLoad.gpu}%</span>
                    </div>
                    <Progress value={systemLoad.gpu} className="h-2" />
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* GPU Monitoring Tab */}
          <TabsContent value="gpu" className="space-y-4">
            {gpuInfo ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5" />
                      GPU Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Name:</span>
                        <div className="font-mono">{gpuInfo.name || 'Unknown'}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Utilization:</span>
                        <div className="font-mono">{gpuInfo.utilization || 0}%</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Memory Used:</span>
                        <div className="font-mono">
                          {gpuInfo.memory_used ? `${(gpuInfo.memory_used / 1024).toFixed(1)} GB` : 'N/A'}
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Memory Total:</span>
                        <div className="font-mono">
                          {gpuInfo.memory_total ? `${(gpuInfo.memory_total / 1024).toFixed(1)} GB` : 'N/A'}
                        </div>
                      </div>
                      {gpuInfo.temperature && (
                        <div>
                          <span className="text-muted-foreground">Temperature:</span>
                          <div className="font-mono">{gpuInfo.temperature}°C</div>
                        </div>
                      )}
                      {gpuInfo.power_draw && (
                        <div>
                          <span className="text-muted-foreground">Power Draw:</span>
                          <div className="font-mono">{gpuInfo.power_draw}W</div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {gpuInfo.metrics && gpuInfo.metrics.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="w-5 h-5" />
                        GPU Metrics History
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {gpuInfo.metrics.slice(-10).map((metric: any, idx: number) => (
                          <div key={idx} className="flex justify-between text-xs">
                            <span>{metric.timestamp}</span>
                            <span className="font-mono">{metric.utilization}%</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <Zap className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">
                    No GPU information available
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Monitoring Services Tab */}
          <TabsContent value="monitoring" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="w-5 h-5" />
                  Monitoring Services
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-blue-500" />
                      <span>Prometheus Metrics</span>
                    </div>
                    <Badge variant="default">Active</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-orange-500" />
                      <span>Sentry Error Tracking</span>
                    </div>
                    <Badge variant="default">Active</Badge>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-green-500" />
                      <span>System Load Monitoring</span>
                    </div>
                    <Badge variant="default">Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {monitoringMetrics && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Performance Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {Object.entries(monitoringMetrics).map(([key, value]: [string, any]) => (
                      <div key={key}>
                        <span className="text-muted-foreground">{key}:</span>
                        <div className="font-mono">{typeof value === 'number' ? value.toFixed(2) : String(value)}</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* LLM Explain Tester */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  LLM Explain Tester (Auto-Learning Sicht)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    value={explainTopic}
                    onChange={(e) => setExplainTopic(e.target.value)}
                    className="flex-1 px-3 py-2 rounded border bg-background text-sm"
                    placeholder="Topic, z.B. quantum entanglement"
                  />
                  <Button size="sm" onClick={handleExplainRequest} disabled={explainLoading}>
                    {explainLoading ? 'Lädt…' : 'Abrufen'}
                  </Button>
                </div>
                {explainDurationMs > 0 && (
                  <p className="text-xs text-muted-foreground">Dauer: {explainDurationMs} ms • Länge: {explainResult.length} Zeichen</p>
                )}
                {explainResult && (
                  <pre className="whitespace-pre-wrap text-xs p-3 rounded bg-muted/30 max-h-64 overflow-auto">
{explainResult}
                  </pre>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Emergency Fixes Tab */}
          <TabsContent value="emergency" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Emergency Fixes Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                {emergencyFixes && emergencyFixes.length > 0 ? (
                  <div className="space-y-2">
                    {emergencyFixes.map((fix: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-2 bg-muted/30 rounded">
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="text-sm">{fix.name}</span>
                        </div>
                        <Badge variant={fix.active ? "default" : "secondary"}>
                          {fix.active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <Shield className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">
                      No emergency fixes currently active
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default MonitoringPanel;
