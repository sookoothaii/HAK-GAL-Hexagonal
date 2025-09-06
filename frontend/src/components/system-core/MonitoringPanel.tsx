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
  Zap, Shield, Eye, BarChart3, TrendingUp, AlertCircle, Info, Server,
  Database, HardDrive, Gauge, Clock, Thermometer, Fan
} from 'lucide-react';
import ApiService from '@/services/apiService';
import { httpClient } from '@/services/api';

const api = new ApiService();

// Real GPU monitoring hook - Fixed to use existing endpoints
const useGPUMonitoring = () => {
  const [gpuData, setGpuData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  
  // Also get GPU info from store if available
  const storeGpuInfo = useGovernorStore(state => state.gpuInfo);
  const systemLoad = useGovernorStore(state => state.systemLoad);
  
  const fetchGPUData = async () => {
    setLoading(true);
    try {
      // First check if we have GPU data in store from WebSocket
      if (storeGpuInfo) {
        setGpuData(storeGpuInfo);
        setLoading(false);
        return;
      }
      
      // Try to get from system status endpoint (this exists)
      try {
        const response = await fetch(`${API_BASE_URL}/api/status`);
        if (response.ok) {
          const data = await response.json();
          if (data.gpu || data.gpu_info) {
            setGpuData(data.gpu || data.gpu_info);
          } else if (systemLoad?.gpu !== undefined) {
            // Fallback to basic GPU load from system load
            setGpuData({
              utilization: systemLoad.gpu,
              memory_percent: systemLoad.gpu_memory,
              name: 'GPU (from system load)',
              available: true
            });
          }
        }
      } catch (error) {
        console.log('GPU info not available from backend');
      }
    } catch (error) {
      console.error('Failed to fetch GPU data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchGPUData();
    const interval = setInterval(fetchGPUData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, [storeGpuInfo, systemLoad]); // Re-run when store updates
  
  return { gpuData: gpuData || storeGpuInfo, loading, refresh: fetchGPUData };
};

// Real monitoring services status
const useMonitoringServices = () => {
  const [services, setServices] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  const checkServices = async () => {
    setLoading(true);
    const serviceChecks = [
      {
        name: 'Database (SQLite)',
        icon: Database,
        color: 'text-blue-500',
        check: async () => {
          try {
            const { data } = await httpClient.get(`/api/facts/count`);
            return { 
              status: data.count > 0 ? 'active' : 'inactive',
              detail: `${data.count || 0} facts`
            };
          } catch { return { status: 'error', detail: 'Connection failed' }; }
        }
      },
      {
        name: 'WebSocket Connection',
        icon: Activity,
        color: 'text-green-500',
        check: async () => {
          const isConnected = useGovernorStore.getState().isConnected;
          return { 
            status: isConnected ? 'active' : 'inactive',
            detail: isConnected ? 'Connected' : 'Disconnected'
          };
        }
      },
      {
        name: 'Kill-Switch Status',
        icon: Shield,
        color: 'text-orange-500',
        check: async () => {
          try {
            const { data } = await httpClient.get(`/api/safety/kill-switch`);
            return { 
              status: data.mode === 'normal' ? 'active' : 'safe',
              detail: `Mode: ${data.mode}`
            };
          } catch { return { status: 'unknown', detail: 'Check failed' }; }
        }
      },
      {
        name: 'Mojo Kernels',
        icon: Zap,
        color: 'text-purple-500',
        check: async () => {
          try {
            const res = await api.mojoStatus();
            return { 
              status: res.mojo?.available ? 'active' : 'inactive',
              detail: res.mojo?.backend || 'Not available'
            };
          } catch { return { status: 'error', detail: 'Check failed' }; }
        }
      }
    ];
    
    const results = await Promise.all(
      serviceChecks.map(async (service) => ({
        ...service,
        ...(await service.check())
      }))
    );
    
    setServices(results);
    setLoading(false);
  };
  
  useEffect(() => {
    checkServices();
    const interval = setInterval(checkServices, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);
  
  return { services, loading, refresh: checkServices };
};

const MonitoringPanel = () => {
  const [activeTab, setActiveTab] = useState('system');
  const [refreshing, setRefreshing] = useState(false);
  
  const systemLoad = useGovernorStore(state => state.systemLoad);
  const systemStatus = useGovernorStore(state => state.systemStatus);
  const kbMetrics = useGovernorStore(state => state.kb.metrics);
  
  // Real GPU monitoring
  const { gpuData, loading: gpuLoading, refresh: refreshGPU } = useGPUMonitoring();
  
  // Real monitoring services
  const { services, loading: servicesLoading, refresh: refreshServices } = useMonitoringServices();
  
  // LLM Explain tester state
  const [explainTopic, setExplainTopic] = useState<string>('quantum entanglement');
  const [explainResult, setExplainResult] = useState<string>('');
  const [explainLoading, setExplainLoading] = useState<boolean>(false);
  const [explainDurationMs, setExplainDurationMs] = useState<number>(0);

  // Backend health/limits/mojo
  const [health, setHealth] = useState<any>(null);
  const [limits, setLimits] = useState<any>(null);
  const [mojo, setMojo] = useState<any>(null);
  const [bench, setBench] = useState<any>(null);
  const [benchLoading, setBenchLoading] = useState<boolean>(false);
  
  // Emergency fixes from backend
  const [emergencyStatus, setEmergencyStatus] = useState<any>(null);
  
  // Performance metrics
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try { const h = await api.health(); if (!cancelled) setHealth(h); } catch {}
      try { const lim = await api.limits(); if (!cancelled) setLimits(lim); } catch {}
      try { const ms = await api.mojoStatus(); if (!cancelled) setMojo(ms); } catch {}
      
      // Fetch emergency status (only if endpoint exists)
      try {
        const res = await httpClient.get(`/api/graph/emergency-status`);
        if (res.status === 200 && !cancelled) setEmergencyStatus(res.data);
      } catch (e) {
        // Emergency endpoints might not exist in all backends
        console.log('Emergency status endpoint not available');
      }
      
      // Fetch performance metrics
      try {
        const res = await httpClient.get(`/api/quality/metrics`, { params: { sample_limit: 100 } });
        if (res.status === 200 && !cancelled) setPerformanceMetrics(res.data);
      } catch {}
    })();
    return () => { cancelled = true; };
  }, []);

  const handleExplainRequest = async () => {
    try {
      setExplainLoading(true);
      setExplainResult('');
      const started = performance.now();
      
      // FIX: Use correct backend URL
      const res = await httpClient.post(`/api/llm/get-explanation`, { topic: explainTopic });
      setExplainResult(res.data.explanation || res.data.error || 'No response');
      setExplainDurationMs(Math.max(0, Math.round(performance.now() - started)));
    } catch (err) {
      setExplainResult(`Error: ${err.message}`);
    } finally {
      setExplainLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    
    // Refresh all data sources
    await Promise.all([
      refreshGPU(),
      refreshServices(),
      (async () => {
        try {
          const [h, lim, ms] = await Promise.allSettled([
            api.health(), api.limits(), api.mojoStatus()
          ]);
          if (h.status === 'fulfilled') setHealth(h.value);
          if (lim.status === 'fulfilled') setLimits(lim.value);
          if (ms.status === 'fulfilled') setMojo(ms.value);
          
          // Refresh emergency status
          const emergRes = await httpClient.get(`/api/graph/emergency-status`);
          if (emergRes.status === 200) setEmergencyStatus(emergRes.data);
          
          // Refresh performance metrics
          const perfRes = await httpClient.get(`/api/quality/metrics`, { params: { sample_limit: 100 } });
          if (perfRes.status === 200) setPerformanceMetrics(perfRes.data);
        } catch {}
      })()
    ]);
    
    setRefreshing(false);
  };

  const runQuickBench = async () => {
    try {
      setBenchLoading(true);
      const res = await api.mojoBench(1000, 0.95);
      setBench(res);
    } catch (e) {
      setBench({ error: 'Bench failed: ' + e.message });
    } finally {
      setBenchLoading(false);
    }
  };
  
  const triggerEmergencyFix = async (action: string) => {
    try {
      const res = await httpClient.post(`/api/graph/emergency-${action}`);
      if (res.status < 200 || res.status >= 300) {
        throw new Error(`Endpoint returned ${res.status}`);
      }
      const data = res.data;
      alert(`${action}: ${data.message || 'Completed'}`);
      // Refresh emergency status
      try {
        const statusRes = await fetch(`${API_BASE_URL}/api/graph/emergency-status`);
        if (statusRes.ok) setEmergencyStatus(await statusRes.json());
      } catch {}
    } catch (err) {
      alert(`Emergency action not available: ${err.message}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'text-green-500';
      case 'degraded': return 'text-yellow-500';
      case 'offline': return 'text-red-500';
      case 'active': return 'text-green-500';
      case 'inactive': return 'text-gray-500';
      case 'safe': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-muted-foreground';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational': 
      case 'active': return <CheckCircle className="w-4 h-4" />;
      case 'degraded':
      case 'safe': return <AlertTriangle className="w-4 h-4" />;
      case 'offline':
      case 'error': return <AlertCircle className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold">System Monitoring</h2>
              <Badge variant="secondary">v3.0 REAL</Badge>
            </div>
            <p className="text-xs text-muted-foreground">Real-time system health and performance metrics</p>
          </div>
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
            <Activity className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="system">System</TabsTrigger>
            <TabsTrigger value="gpu">GPU</TabsTrigger>
            <TabsTrigger value="monitoring">Services</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="emergency">Emergency</TabsTrigger>
          </TabsList>

          {/* System Health Tab - UNCHANGED, works well */}
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
                  <span className={`font-medium ${getStatusColor(systemStatus)}`}>{systemStatus.toUpperCase()}</span>
                  {health?.read_only && (<Badge variant="secondary">READ-ONLY</Badge>)}
                </div>
              </CardContent>
            </Card>

            {/* Backend Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="w-5 h-5" />
                  Backend Info
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-muted-foreground">Port:</span><div className="font-mono">{health?.port ?? '—'}</div></div>
                <div><span className="text-muted-foreground">Repository:</span><div className="font-mono">{health?.repository ?? '—'}</div></div>
                <div><span className="text-muted-foreground">Architecture:</span><div className="font-mono">{health?.architecture ?? 'hexagonal'}</div></div>
                <div><span className="text-muted-foreground">Mojo Backend:</span><div className="font-mono">{health?.mojo?.backend ?? '—'}</div></div>
                <div><span className="text-muted-foreground">Mojo Enabled:</span><div className="font-mono">{String(health?.mojo?.flag_enabled ?? false)}</div></div>
                <div><span className="text-muted-foreground">PPJoin Enabled:</span><div className="font-mono">{String(health?.mojo?.ppjoin_enabled ?? false)}</div></div>
              </CardContent>
            </Card>

            {/* Knowledge Base Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="w-5 h-5" />
                  Knowledge Base Status
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-muted-foreground">Total Facts:</span><div className="font-mono">{kbMetrics?.factCount || 0}</div></div>
                <div><span className="text-muted-foreground">Growth Rate:</span><div className="font-mono">{kbMetrics?.growthRate?.toFixed(2) || '0.00'}/min</div></div>
                <div><span className="text-muted-foreground">Node Count:</span><div className="font-mono">{kbMetrics?.nodeCount || 0}</div></div>
                <div><span className="text-muted-foreground">Edge Count:</span><div className="font-mono">{kbMetrics?.edgeCount || 0}</div></div>
                <div><span className="text-muted-foreground">Connectivity:</span><div className="font-mono">{kbMetrics?.connectivity?.toFixed(2) || '0.00'}</div></div>
                <div><span className="text-muted-foreground">Entropy:</span><div className="font-mono">{kbMetrics?.entropy?.toFixed(2) || '0.00'}</div></div>
              </CardContent>
            </Card>

            {/* Caps & Flags */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Caps & Flags
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-muted-foreground">max_sample_limit:</span><div className="font-mono">{limits?.caps?.max_sample_limit ?? health?.caps?.max_sample_limit ?? '—'}</div></div>
                <div><span className="text-muted-foreground">max_top_k:</span><div className="font-mono">{limits?.caps?.max_top_k ?? health?.caps?.max_top_k ?? '—'}</div></div>
                <div><span className="text-muted-foreground">MOJO_ENABLED:</span><div className="font-mono">{limits?.mojo_flags?.MOJO_ENABLED ?? '—'}</div></div>
                <div><span className="text-muted-foreground">MOJO_DUPES_ENABLED:</span><div className="font-mono">{limits?.mojo_flags?.MOJO_DUPES_ENABLED ?? '—'}</div></div>
                <div><span className="text-muted-foreground">MOJO_VALIDATE_ENABLED:</span><div className="font-mono">{limits?.mojo_flags?.MOJO_VALIDATE_ENABLED ?? '—'}</div></div>
                <div><span className="text-muted-foreground">MOJO_PPJOIN_ENABLED:</span><div className="font-mono">{limits?.mojo_flags?.MOJO_PPJOIN_ENABLED ?? '—'}</div></div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* GPU Monitoring Tab - FIXED with real data */}
          <TabsContent value="gpu" className="space-y-4">
            {gpuLoading ? (
              <Card>
                <CardContent className="text-center py-8">
                  <Activity className="w-8 h-8 mx-auto text-muted-foreground mb-2 animate-spin" />
                  <p className="text-sm text-muted-foreground">Loading GPU information...</p>
                </CardContent>
              </Card>
            ) : gpuData ? (
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
                        <div className="font-mono">{gpuData.name || 'Unknown GPU'}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Driver Version:</span>
                        <div className="font-mono">{gpuData.driver_version || 'N/A'}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Gauge className="w-4 h-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Utilization:</span>
                        <div className="font-mono">{gpuData.utilization || systemLoad?.gpu || 0}%</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <HardDrive className="w-4 h-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Memory:</span>
                        <div className="font-mono">
                          {gpuData.memory_used ? `${(gpuData.memory_used / 1024).toFixed(1)}` : '0'} / 
                          {gpuData.memory_total ? ` ${(gpuData.memory_total / 1024).toFixed(1)}` : ' ?'} GB
                        </div>
                      </div>
                      {gpuData.temperature !== undefined && (
                        <div className="flex items-center gap-2">
                          <Thermometer className="w-4 h-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Temperature:</span>
                          <div className="font-mono">{gpuData.temperature}°C</div>
                        </div>
                      )}
                      {gpuData.power_draw !== undefined && (
                        <div className="flex items-center gap-2">
                          <Zap className="w-4 h-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Power Draw:</span>
                          <div className="font-mono">{gpuData.power_draw}W</div>
                        </div>
                      )}
                      {gpuData.fan_speed !== undefined && (
                        <div className="flex items-center gap-2">
                          <Fan className="w-4 h-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Fan Speed:</span>
                          <div className="font-mono">{gpuData.fan_speed}%</div>
                        </div>
                      )}
                      {gpuData.clock_speed !== undefined && (
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Clock Speed:</span>
                          <div className="font-mono">{gpuData.clock_speed} MHz</div>
                        </div>
                      )}
                    </div>
                    
                    {/* GPU Memory Usage Bar */}
                    {gpuData.memory_percent !== undefined && (
                      <div className="mt-4 space-y-2">
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Memory Usage</span>
                          <span>{gpuData.memory_percent.toFixed(1)}%</span>
                        </div>
                        <Progress value={gpuData.memory_percent} className="h-2" />
                      </div>
                    )}
                    
                    {/* GPU Utilization Bar */}
                    {(gpuData.utilization || systemLoad?.gpu) !== undefined && (
                      <div className="mt-4 space-y-2">
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>GPU Utilization</span>
                          <span>{gpuData.utilization || systemLoad?.gpu || 0}%</span>
                        </div>
                        <Progress value={gpuData.utilization || systemLoad?.gpu || 0} className="h-2" />
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* CUDA Information if available */}
                {gpuData.cuda_version && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Cpu className="w-5 h-5" />
                        CUDA Information
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">CUDA Version:</span>
                          <div className="font-mono">{gpuData.cuda_version}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Compute Capability:</span>
                          <div className="font-mono">{gpuData.compute_capability || 'N/A'}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <Zap className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">No GPU information available</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    GPU monitoring may not be supported on this system
                  </p>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="mt-4"
                    onClick={refreshGPU}
                  >
                    Try Again
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Monitoring Services Tab - FIXED with real service checks */}
          <TabsContent value="monitoring" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="w-5 h-5" />
                  Service Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                {servicesLoading ? (
                  <div className="text-center py-4">
                    <Activity className="w-6 h-6 mx-auto animate-spin text-muted-foreground" />
                    <p className="text-sm text-muted-foreground mt-2">Checking services...</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {services.map((service, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                        <div className="flex items-center gap-2">
                          <service.icon className={`w-4 h-4 ${service.color}`} />
                          <span>{service.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">{service.detail}</span>
                          <Badge variant={service.status === 'active' ? 'default' : service.status === 'error' ? 'destructive' : 'secondary'}>
                            {service.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* LLM Explain Tester - FIXED with correct URL */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  LLM Explain Tester
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <input 
                    value={explainTopic} 
                    onChange={(e) => setExplainTopic(e.target.value)} 
                    className="flex-1 px-3 py-2 rounded border bg-background text-sm" 
                    placeholder="Topic, e.g., quantum entanglement" 
                  />
                  <Button size="sm" onClick={handleExplainRequest} disabled={explainLoading}>
                    {explainLoading ? 'Loading...' : 'Explain'}
                  </Button>
                </div>
                {explainDurationMs > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Duration: {explainDurationMs} ms • Length: {explainResult.length} characters
                  </p>
                )}
                {explainResult && (
                  <pre className="whitespace-pre-wrap text-xs p-3 rounded bg-muted/30 max-h-64 overflow-auto">
                    {explainResult}
                  </pre>
                )}
              </CardContent>
            </Card>

            {/* Mojo Quick Bench - IMPROVED */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Gauge className="w-5 h-5" />
                  Mojo Performance Benchmark
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button size="sm" variant="outline" onClick={runQuickBench} disabled={benchLoading}>
                  {benchLoading ? 'Running benchmark...' : 'Run Benchmark (1000 facts)'}
                </Button>
                {bench && (
                  <div className="space-y-2">
                    {bench.error ? (
                      <p className="text-sm text-red-500">{bench.error}</p>
                    ) : (
                      <>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">Validation Time:</span>
                            <div className="font-mono">{bench?.validate?.duration_ms?.toFixed(2) ?? '—'} ms</div>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Valid Facts:</span>
                            <div className="font-mono">{bench?.validate?.valid_true ?? 0} / {bench?.sample_size ?? 0}</div>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Duplicate Check Time:</span>
                            <div className="font-mono">{bench?.duplicates?.duration_ms?.toFixed(2) ?? '—'} ms</div>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Duplicate Pairs:</span>
                            <div className="font-mono">{bench?.duplicates?.pairs ?? 0}</div>
                          </div>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Backend: {bench?.adapter?.backend ?? 'python_fallback'} | 
                          Threshold: {bench?.duplicates?.threshold ?? 0.95}
                        </div>
                      </>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* NEW: Performance Tab with real metrics */}
          <TabsContent value="performance" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Knowledge Base Quality Metrics
                </CardTitle>
              </CardHeader>
              <CardContent>
                {performanceMetrics ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Total Facts:</span>
                        <div className="font-mono">{performanceMetrics.total || 0}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Checked:</span>
                        <div className="font-mono">{performanceMetrics.checked || 0}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Invalid:</span>
                        <div className="font-mono text-red-500">{performanceMetrics.invalid || 0}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Duplicates:</span>
                        <div className="font-mono text-yellow-500">{performanceMetrics.duplicates || 0}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Isolated:</span>
                        <div className="font-mono">{performanceMetrics.isolated || 0}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Contradictions:</span>
                        <div className="font-mono text-orange-500">{performanceMetrics.contradictions || 0}</div>
                      </div>
                    </div>
                    
                    {performanceMetrics.top_predicates && (
                      <div>
                        <h4 className="text-sm font-medium mb-2">Top Predicates</h4>
                        <div className="space-y-1">
                          {performanceMetrics.top_predicates.slice(0, 5).map((pred: any, idx: number) => (
                            <div key={idx} className="flex justify-between text-xs">
                              <span className="font-mono">{pred.predicate}</span>
                              <Badge variant="secondary">{pred.count}</Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {performanceMetrics.semantic_duplicates && (
                      <div className="p-3 bg-muted/50 rounded">
                        <div className="text-sm">
                          <span className="text-muted-foreground">Semantic Duplicates: </span>
                          <span className="font-mono">{performanceMetrics.semantic_duplicates.pairs_count || 0} pairs</span>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Threshold: {performanceMetrics.semantic_duplicates.threshold}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <BarChart3 className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">Loading performance metrics...</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* System Load History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  System Load
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">CPU:</span>
                    <div className="font-mono text-lg">{systemLoad?.cpu || 0}%</div>
                    <Progress value={systemLoad?.cpu || 0} className="h-1 mt-1" />
                  </div>
                  <div>
                    <span className="text-muted-foreground">Memory:</span>
                    <div className="font-mono text-lg">{systemLoad?.memory || 0}%</div>
                    <Progress value={systemLoad?.memory || 0} className="h-1 mt-1" />
                  </div>
                  <div>
                    <span className="text-muted-foreground">GPU:</span>
                    <div className="font-mono text-lg">{systemLoad?.gpu || 0}%</div>
                    <Progress value={systemLoad?.gpu || 0} className="h-1 mt-1" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Emergency Fixes Tab - FIXED with real data */}
          <TabsContent value="emergency" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Emergency System Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                {emergencyStatus ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Graph Exists:</span>
                        <div className="flex items-center gap-2">
                          {emergencyStatus.graph_exists ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-red-500" />
                          )}
                          <span className="font-mono">{String(emergencyStatus.graph_exists)}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Last Generated:</span>
                        <div className="font-mono text-xs">
                          {emergencyStatus.last_generated ? 
                            new Date(emergencyStatus.last_generated).toLocaleString() : 
                            'Never'}
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Fact Count:</span>
                        <div className="font-mono">{emergencyStatus.fact_count || 0}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">File Size:</span>
                        <div className="font-mono">
                          {emergencyStatus.file_size_bytes ? 
                            `${(emergencyStatus.file_size_bytes / 1024).toFixed(1)} KB` : 
                            'N/A'}
                        </div>
                      </div>
                    </div>
                    
                    <div className="pt-4 border-t">
                      <h4 className="text-sm font-medium mb-3">Emergency Actions</h4>
                      <div className="grid grid-cols-2 gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => triggerEmergencyFix('generate')}
                        >
                          <Activity className="w-4 h-4 mr-2" />
                          Generate Graph
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => triggerEmergencyFix('clean')}
                        >
                          <Shield className="w-4 h-4 mr-2" />
                          Clean Database
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => triggerEmergencyFix('detect')}
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          Detect Corruption
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => triggerEmergencyFix('fix-engines')}
                        >
                          <Cpu className="w-4 h-4 mr-2" />
                          Fix Engines
                        </Button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <Shield className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">Loading emergency status...</p>
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