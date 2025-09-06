import React, { useState, useEffect } from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, AlertTriangle, CheckCircle, Cpu, 
  Zap, Shield, Eye, BarChart3, TrendingUp, AlertCircle, Info, Server,
  Database, HardDrive, Gauge, Clock, Thermometer, Fan, XCircle
} from 'lucide-react';
import { httpClient, getApiBaseUrl } from '@/services/api';

// Robust API wrapper with fallback handling
const safeApiCall = async <T,>(
  apiCall: () => Promise<T>,
  fallback: T | null = null,
  onError?: (error: any) => void
): Promise<T | null> => {
  try {
    return await apiCall();
  } catch (error: any) {
    if (error?.response?.status === 405 || error?.response?.status === 404) {
      // Silently handle expected missing endpoints
      console.debug(`Endpoint not available: ${error?.config?.url}`);
    } else if (onError) {
      onError(error);
    } else {
      console.error('API call failed:', error);
    }
    return fallback;
  }
};

// GPU monitoring hook with robust error handling
const useGPUMonitoring = () => {
  const [gpuData, setGpuData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  
  // Also get GPU info from store if available
  const storeGpuInfo = useGovernorStore(state => state.gpuInfo);
  const systemLoad = useGovernorStore(state => state.systemLoad);
  
  const fetchGPUData = async () => {
    setLoading(true);
    
    // First check store data
    if (storeGpuInfo) {
      setGpuData(storeGpuInfo);
      setLoading(false);
      return;
    }
    
    // Try various endpoints with fallbacks
    const gpuEndpoints = [
      '/api/system/gpu',
      '/api/status',
      '/api/metrics'
    ];
    
    for (const endpoint of gpuEndpoints) {
      const data = await safeApiCall(async () => {
        const res = await httpClient.get(endpoint);
        return res.data?.gpu || res.data?.gpu_info || null;
      });
      
      if (data) {
        setGpuData(data);
        setLoading(false);
        return;
      }
    }
    
    // Final fallback to system load
    if (systemLoad?.gpu !== undefined) {
      setGpuData({
        utilization: systemLoad.gpu,
        memory_percent: systemLoad.gpu_memory,
        name: 'GPU (from system metrics)',
        available: true
      });
    }
    
    setLoading(false);
  };
  
  useEffect(() => {
    fetchGPUData();
    const interval = setInterval(fetchGPUData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [storeGpuInfo, systemLoad]);
  
  return { gpuData: gpuData || storeGpuInfo, loading, refresh: fetchGPUData };
};

// Monitoring services with robust checks
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
          const data = await safeApiCall(
            async () => (await httpClient.get('/api/facts/count')).data,
            { count: 0 }
          );
          return { 
            status: data && data.count > 0 ? 'active' : 'inactive',
            detail: `${data?.count || 0} facts`
          };
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
        name: 'Backend Health',
        icon: Server,
        color: 'text-purple-500',
        check: async () => {
          const data = await safeApiCall(
            async () => (await httpClient.get('/health')).data,
            null
          );
          return { 
            status: data ? 'active' : 'unknown',
            detail: data ? `Port ${data.port}` : 'Check failed'
          };
        }
      },
      {
        name: 'Mojo Kernels',
        icon: Zap,
        color: 'text-yellow-500',
        check: async () => {
          const data = await safeApiCall(
            async () => (await httpClient.get('/api/mojo/status')).data,
            null
          );
          return { 
            status: data?.mojo?.available ? 'active' : 'inactive',
            detail: data?.mojo?.backend || 'Not available'
          };
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
    const interval = setInterval(checkServices, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);
  
  return { services, loading, refresh: checkServices };
};

const MonitoringPanelRobust = () => {
  const [activeTab, setActiveTab] = useState('system');
  const [refreshing, setRefreshing] = useState(false);
  
  // Store data
  const systemLoad = useGovernorStore(state => state.systemLoad);
  const systemStatus = useGovernorStore(state => state.systemStatus);
  const kbMetrics = useGovernorStore(state => state.kb.metrics);
  const isConnected = useGovernorStore(state => state.isConnected);
  
  // Hooks
  const { gpuData, loading: gpuLoading, refresh: refreshGPU } = useGPUMonitoring();
  const { services, loading: servicesLoading, refresh: refreshServices } = useMonitoringServices();
  
  // Backend info states
  const [health, setHealth] = useState<any>(null);
  const [limits, setLimits] = useState<any>(null);
  const [mojo, setMojo] = useState<any>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);
  const [emergencyStatus, setEmergencyStatus] = useState<any>(null);
  
  // Benchmark state
  const [bench, setBench] = useState<any>(null);
  const [benchLoading, setBenchLoading] = useState(false);
  
  // Load initial data with robust error handling
  useEffect(() => {
    let cancelled = false;
    
    const loadData = async () => {
      // Health check
      const healthData = await safeApiCall(
        async () => (await httpClient.get('/health')).data
      );
      if (!cancelled && healthData) setHealth(healthData);
      
      // Limits - may not exist
      const limitsData = await safeApiCall(
        async () => (await httpClient.get('/api/limits')).data
      );
      if (!cancelled && limitsData) setLimits(limitsData);
      
      // Mojo status
      const mojoData = await safeApiCall(
        async () => (await httpClient.get('/api/mojo/status')).data
      );
      if (!cancelled && mojoData) setMojo(mojoData);
      
      // Performance metrics - may not exist
      const perfData = await safeApiCall(
        async () => (await httpClient.get('/api/quality/metrics', { 
          params: { sample_limit: 100 } 
        })).data
      );
      if (!cancelled && perfData) setPerformanceMetrics(perfData);
      
      // Emergency status - may not exist
      const emergData = await safeApiCall(
        async () => (await httpClient.get('/api/graph/emergency-status')).data
      );
      if (!cancelled && emergData) setEmergencyStatus(emergData);
    };
    
    loadData();
    
    return () => { cancelled = true; };
  }, []);
  
  const handleRefresh = async () => {
    setRefreshing(true);
    
    await Promise.all([
      refreshGPU(),
      refreshServices(),
      (async () => {
        // Re-fetch all data with error handling
        const [h, l, m, p, e] = await Promise.all([
          safeApiCall(async () => (await httpClient.get('/health')).data),
          safeApiCall(async () => (await httpClient.get('/api/limits')).data),
          safeApiCall(async () => (await httpClient.get('/api/mojo/status')).data),
          safeApiCall(async () => (await httpClient.get('/api/quality/metrics', { 
            params: { sample_limit: 100 } 
          })).data),
          safeApiCall(async () => (await httpClient.get('/api/graph/emergency-status')).data)
        ]);
        
        if (h) setHealth(h);
        if (l) setLimits(l);
        if (m) setMojo(m);
        if (p) setPerformanceMetrics(p);
        if (e) setEmergencyStatus(e);
      })()
    ]);
    
    setRefreshing(false);
  };
  
  const runQuickBench = async () => {
    setBenchLoading(true);
    
    const benchData = await safeApiCall(
      async () => (await httpClient.post('/api/mojo/bench', {
        sample_size: 1000,
        threshold: 0.95
      })).data,
      null,
      (error) => {
        setBench({ error: `Benchmark not available: ${error?.message || 'Unknown error'}` });
      }
    );
    
    if (benchData) {
      setBench(benchData);
    }
    
    setBenchLoading(false);
  };
  
  const triggerEmergencyFix = async (action: string) => {
    const result = await safeApiCall(
      async () => (await httpClient.post(`/api/graph/emergency-${action}`)).data,
      null,
      (error) => {
        alert(`Emergency action not available: ${error?.message || 'Endpoint missing'}`);
      }
    );
    
    if (result) {
      alert(`${action}: ${result.message || 'Completed'}`);
      // Refresh emergency status
      const newStatus = await safeApiCall(
        async () => (await httpClient.get('/api/graph/emergency-status')).data
      );
      if (newStatus) setEmergencyStatus(newStatus);
    }
  };
  
  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'operational': return 'text-green-500';
      case 'degraded': return 'text-yellow-500';
      case 'offline': return 'text-red-500';
      case 'active': return 'text-green-500';
      case 'inactive': return 'text-gray-500';
      case 'unknown': return 'text-gray-400';
      case 'error': return 'text-red-500';
      default: return 'text-muted-foreground';
    }
  };
  
  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'operational': 
      case 'active': return <CheckCircle className="w-4 h-4" />;
      case 'degraded': return <AlertTriangle className="w-4 h-4" />;
      case 'offline':
      case 'error': return <AlertCircle className="w-4 h-4" />;
      case 'unknown': return <Info className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };
  
  // Helper component for displaying "N/A" when data is missing
  const DataField = ({ label, value, fallback = 'n/a' }: { label: string; value: any; fallback?: string }) => (
    <div>
      <span className="text-muted-foreground">{label}:</span>
      <div className="font-mono">{value ?? fallback}</div>
    </div>
  );
  
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold">System Monitoring</h2>
              <Badge variant="secondary">v3.1 ROBUST</Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Real-time metrics with graceful fallbacks
            </p>
          </div>
          <div className="flex items-center gap-2">
            {!isConnected && (
              <Badge variant="destructive" className="flex items-center gap-1">
                <XCircle className="w-3 h-3" />
                Disconnected
              </Badge>
            )}
            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
              <Activity className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="system">System</TabsTrigger>
            <TabsTrigger value="gpu">GPU</TabsTrigger>
            <TabsTrigger value="services">Services</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="emergency">Emergency</TabsTrigger>
          </TabsList>
          
          {/* System Tab */}
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
                  {getStatusIcon(systemStatus || 'unknown')}
                  <span className={`font-medium ${getStatusColor(systemStatus || 'unknown')}`}>
                    {(systemStatus || 'UNKNOWN').toUpperCase()}
                  </span>
                  {health?.read_only && <Badge variant="secondary">READ-ONLY</Badge>}
                  {isConnected && <Badge variant="default">CONNECTED</Badge>}
                </div>
              </CardContent>
            </Card>
            
            {/* Backend Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="w-5 h-5" />
                  Backend Information
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4 text-sm">
                <DataField label="Port" value={health?.port} />
                <DataField label="Repository" value={health?.repository} />
                <DataField label="Architecture" value={health?.architecture || 'hexagonal'} />
                <DataField label="Mojo Backend" value={health?.mojo?.backend || mojo?.mojo?.backend} />
                <DataField label="Mojo Enabled" value={String(health?.mojo?.flag_enabled ?? false)} />
                <DataField label="API Base" value={getApiBaseUrl()} />
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
                <DataField label="Total Facts" value={kbMetrics?.factCount || 0} />
                <DataField label="Growth Rate" value={`${kbMetrics?.growthRate?.toFixed(2) || '0.00'}/min`} />
                <DataField label="Node Count" value={kbMetrics?.nodeCount || 0} />
                <DataField label="Edge Count" value={kbMetrics?.edgeCount || 0} />
                <DataField label="Connectivity" value={kbMetrics?.connectivity?.toFixed(2) || '0.00'} />
                <DataField label="Entropy" value={kbMetrics?.entropy?.toFixed(2) || '0.00'} />
              </CardContent>
            </Card>
            
            {/* Caps & Flags - only show if data exists */}
            {(limits || health?.caps) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Caps & Flags
                  </CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-4 text-sm">
                  <DataField label="Max Sample Limit" value={limits?.caps?.max_sample_limit || health?.caps?.max_sample_limit} />
                  <DataField label="Max Top K" value={limits?.caps?.max_top_k || health?.caps?.max_top_k} />
                  <DataField label="MOJO_ENABLED" value={limits?.mojo_flags?.MOJO_ENABLED} />
                  <DataField label="MOJO_DUPES_ENABLED" value={limits?.mojo_flags?.MOJO_DUPES_ENABLED} />
                  <DataField label="MOJO_VALIDATE_ENABLED" value={limits?.mojo_flags?.MOJO_VALIDATE_ENABLED} />
                  <DataField label="MOJO_PPJOIN_ENABLED" value={limits?.mojo_flags?.MOJO_PPJOIN_ENABLED} />
                </CardContent>
              </Card>
            )}
          </TabsContent>
          
          {/* GPU Tab */}
          <TabsContent value="gpu" className="space-y-4">
            {gpuLoading ? (
              <Card>
                <CardContent className="text-center py-8">
                  <Activity className="w-8 h-8 mx-auto text-muted-foreground mb-2 animate-spin" />
                  <p className="text-sm text-muted-foreground">Loading GPU information...</p>
                </CardContent>
              </Card>
            ) : gpuData ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5" />
                    GPU Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <DataField label="Name" value={gpuData.name || 'GPU Available'} />
                    <DataField label="Driver Version" value={gpuData.driver_version} />
                    
                    {(gpuData.utilization !== undefined || systemLoad?.gpu !== undefined) && (
                      <>
                        <div className="col-span-2">
                          <div className="flex items-center gap-2 mb-1">
                            <Gauge className="w-4 h-4 text-muted-foreground" />
                            <span className="text-muted-foreground">GPU Utilization</span>
                            <span className="ml-auto font-mono">{gpuData.utilization || systemLoad?.gpu || 0}%</span>
                          </div>
                          <Progress value={gpuData.utilization || systemLoad?.gpu || 0} className="h-2" />
                        </div>
                      </>
                    )}
                    
                    {gpuData.memory_percent !== undefined && (
                      <div className="col-span-2">
                        <div className="flex items-center gap-2 mb-1">
                          <HardDrive className="w-4 h-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Memory Usage</span>
                          <span className="ml-auto font-mono">{gpuData.memory_percent.toFixed(1)}%</span>
                        </div>
                        <Progress value={gpuData.memory_percent} className="h-2" />
                      </div>
                    )}
                    
                    {gpuData.temperature !== undefined && (
                      <div className="flex items-center gap-2">
                        <Thermometer className="w-4 h-4 text-muted-foreground" />
                        <DataField label="Temperature" value={`${gpuData.temperature}°C`} />
                      </div>
                    )}
                    
                    {gpuData.power_draw !== undefined && (
                      <div className="flex items-center gap-2">
                        <Zap className="w-4 h-4 text-muted-foreground" />
                        <DataField label="Power Draw" value={`${gpuData.power_draw}W`} />
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <Zap className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">No GPU information available</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    GPU monitoring may not be supported
                  </p>
                  <Button variant="outline" size="sm" className="mt-4" onClick={refreshGPU}>
                    Try Again
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>
          
          {/* Services Tab */}
          <TabsContent value="services" className="space-y-4">
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
                          <Badge 
                            variant={
                              service.status === 'active' ? 'default' : 
                              service.status === 'error' ? 'destructive' : 
                              'secondary'
                            }
                          >
                            {service.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
            
            {/* Mojo Benchmark */}
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
                      <p className="text-sm text-muted-foreground">{bench.error}</p>
                    ) : (
                      <>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <DataField label="Validation Time" value={`${bench?.validate?.duration_ms?.toFixed(2) ?? 'n/a'} ms`} />
                          <DataField label="Valid Facts" value={`${bench?.validate?.valid_true ?? 0} / ${bench?.sample_size ?? 0}`} />
                          <DataField label="Duplicate Check Time" value={`${bench?.duplicates?.duration_ms?.toFixed(2) ?? 'n/a'} ms`} />
                          <DataField label="Duplicate Pairs" value={bench?.duplicates?.pairs ?? 0} />
                        </div>
                        {bench?.adapter?.backend && (
                          <div className="text-xs text-muted-foreground">
                            Backend: {bench.adapter.backend} | Threshold: {bench?.duplicates?.threshold ?? 0.95}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-4">
            {performanceMetrics ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Knowledge Base Quality Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <DataField label="Total Facts" value={performanceMetrics.total || 0} />
                      <DataField label="Checked" value={performanceMetrics.checked || 0} />
                      <DataField label="Invalid" value={performanceMetrics.invalid || 0} />
                      <DataField label="Duplicates" value={performanceMetrics.duplicates || 0} />
                      <DataField label="Isolated" value={performanceMetrics.isolated || 0} />
                      <DataField label="Contradictions" value={performanceMetrics.contradictions || 0} />
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
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <BarChart3 className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">Performance metrics not available</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    This endpoint may not be implemented in the current backend
                  </p>
                </CardContent>
              </Card>
            )}
            
            {/* System Load */}
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
          
          {/* Emergency Tab */}
          <TabsContent value="emergency" className="space-y-4">
            {emergencyStatus ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5" />
                    Emergency System Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
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
                      <DataField 
                        label="Last Generated" 
                        value={emergencyStatus.last_generated ? 
                          new Date(emergencyStatus.last_generated).toLocaleString() : 
                          'Never'} 
                      />
                      <DataField label="Fact Count" value={emergencyStatus.fact_count || 0} />
                      <DataField 
                        label="File Size" 
                        value={emergencyStatus.file_size_bytes ? 
                          `${(emergencyStatus.file_size_bytes / 1024).toFixed(1)} KB` : 
                          'N/A'} 
                      />
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
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <Shield className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">Emergency features not available</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    These endpoints may not be implemented in the current backend
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default MonitoringPanelRobust;
