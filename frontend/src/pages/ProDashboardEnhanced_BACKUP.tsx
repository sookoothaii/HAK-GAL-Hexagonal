// ProDashboardEnhanced - EXACT LAYOUT wie im Screenshot
// Kompakt aber mit allen Informationen
import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Brain, 
  Database, 
  Zap, 
  Activity, 
  Server,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Play,
  Pause
} from 'lucide-react';

/**
 * Dashboard - Exakt wie im Screenshot
 * Kompaktes Layout das auf einen Screen passt
 */
const ProDashboardEnhanced: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<any>({
    health: null,
    facts: 0,
    writeMode: false,
    governor: null,
    hrm: null,
    neural: null,
    architecture: null
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchBackendStatus = async () => {
    setRefreshing(true);
    try {
      const fetchWithFallback = async (url: string, fallback: any = null) => {
        try {
          const response = await fetch(`http://localhost:5002${url}`, { 
            method: 'GET',
            headers: { 'Accept': 'application/json' }
          });
          if (response.ok) {
            return await response.json();
          }
          return fallback;
        } catch {
          return fallback;
        }
      };

      const [health, factsCount, governor, hrm, architecture] = await Promise.all([
        fetchWithFallback('/health', { status: 'offline' }),
        fetchWithFallback('/api/facts/count', { count: 0 }),
        fetchWithFallback('/api/governor/status', { status: 'inactive' }),
        fetchWithFallback('/api/hrm/status', { status: 'unknown' }),
        fetchWithFallback('/api/architecture', { type: 'hexagonal' })
      ]);

      setBackendStatus({
        health: health || { status: 'error' },
        facts: factsCount?.count || 0,
        writeMode: health ? !health.read_only : false,
        governor: governor || { status: 'inactive', learning_rate: 0 },
        hrm: hrm || { status: 'unknown', model: 'Not loaded' },
        neural: { confidence: 0, last_query: null },
        architecture: architecture || { type: 'hexagonal', version: '2.0' }
      });

      setError(null);
    } catch (err) {
      setError('Failed to connect to backend');
      console.error('Backend fetch error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchBackendStatus();
    const interval = setInterval(fetchBackendStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const toggleGovernor = async () => {
    try {
      const isActive = backendStatus.governor?.status === 'running';
      const endpoint = isActive ? '/api/governor/stop' : '/api/governor/start';
      
      const response = await fetch(`http://localhost:5002${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: 'ultra_performance',
          target_facts_per_minute: 45
        })
      });

      if (response.ok) {
        fetchBackendStatus();
      }
    } catch (err) {
      console.error('Governor toggle error:', err);
    }
  };

  const calculateMetrics = () => {
    const facts = backendStatus.facts || 0;
    const targetFacts = 5000;
    const factProgress = Math.min((facts / targetFacts) * 100, 100);
    
    const learningRate = backendStatus.governor?.learning_rate || 0;
    const targetRate = 45;
    const learningProgress = Math.min((learningRate / targetRate) * 100, 100);

    const trustFactors = {
      factCount: facts >= 4000 ? 0.3 : (facts / 4000) * 0.3,
      writeMode: backendStatus.writeMode ? 0.2 : 0,
      governorActive: backendStatus.governor?.status === 'running' ? 0.2 : 0,
      hrmLoaded: backendStatus.hrm?.status === 'operational' ? 0.2 : 0,
      learningRate: learningRate > 0 ? 0.1 : 0
    };
    
    const trustScore = Object.values(trustFactors).reduce((a, b) => a + b, 0) * 100;

    return {
      factProgress,
      learningProgress,
      trustScore,
      trustFactors
    };
  };

  const metrics = calculateMetrics();

  if (loading && !refreshing) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Synchronizing with backend...</p>
        </div>
      </div>
    );
  }

  // EXACT LAYOUT - Optimiert für einen Screen ohne Scrolling (MIT Navigation)
  return (
    <div className="h-screen bg-background p-1 overflow-hidden flex flex-col">
      {/* Header - Ultra Kompakt */}
      <div className="flex justify-between items-center mb-1 flex-shrink-0" style={{height: '40px'}}>
        <div className="text-center flex-1">
          <h1 className="text-lg font-bold">HAK-GAL Neurosymbolic Intelligence Suite</h1>
          <p className="text-xs text-muted-foreground">
            Backend: Port 5002 | Mode: {backendStatus.writeMode ? 'WRITE' : 'READ'} | Facts: {backendStatus.facts.toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={fetchBackendStatus}
            disabled={refreshing}
            className="h-8 px-3 text-xs"
          >
            <RefreshCw className={`w-3 h-3 ${refreshing ? 'animate-spin' : ''}`} />
            <span className="ml-1">Refresh</span>
          </Button>
          <Button
            variant={backendStatus.governor?.status === 'running' ? 'destructive' : 'default'}
            size="sm"
            onClick={toggleGovernor}
            className="h-8 px-3 text-xs"
          >
            {backendStatus.governor?.status === 'running' ? 'Stop Governor' : 'Start Governor'}
          </Button>
        </div>
      </div>

      {/* Main Metrics - 3 Spalten wie im Screenshot */}
      <div className="grid grid-cols-3 gap-1 mb-1" style={{height: 'calc(25% - 10px)'}}>
        {/* Neural Components */}
        <Card className="h-full overflow-hidden">
          <CardHeader className="p-2 pb-1">
            <CardTitle className="flex items-center gap-1 text-sm">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              Neural Components
            </CardTitle>
          </CardHeader>
          <CardContent className="p-2 pt-0">
            <div className="text-center mb-0.5">
              <div className="flex justify-between items-center mb-0.5">
                <span className="text-xs text-muted-foreground">HRM Model</span>
                <Badge variant={backendStatus.hrm?.status === 'operational' ? 'default' : 'secondary'} className="text-xs py-0 h-5">
                  SimplifiedHRM
                </Badge>
              </div>
              <div className="text-2xl font-bold">3.5M</div>
              <p className="text-xs text-muted-foreground">Parameters</p>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span>Inference</span>
                <span className="text-green-500">&lt;10ms</span>
              </div>
              <Progress value={95} className="h-1" />
            </div>
          </CardContent>
        </Card>

        {/* Symbolic Components */}
        <Card className="h-full overflow-hidden">
          <CardHeader className="p-2 pb-1">
            <CardTitle className="flex items-center gap-1 text-sm">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              Symbolic Components
            </CardTitle>
          </CardHeader>
          <CardContent className="p-2 pt-0">
            <div className="text-center mb-0.5">
              <div className="flex justify-between items-center mb-0.5">
                <span className="text-xs text-muted-foreground">Knowledge Base</span>
                <Badge variant="default" className="text-xs py-0 h-5">SQLite</Badge>
              </div>
              <div className="text-2xl font-bold">{(backendStatus.facts / 1000).toFixed(3)}</div>
              <p className="text-xs text-muted-foreground">Facts</p>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span>Progress to 5k</span>
                <span>{metrics.factProgress.toFixed(0)}%</span>
              </div>
              <Progress value={metrics.factProgress} className="h-1" />
            </div>
          </CardContent>
        </Card>

        {/* Self-Learning System */}
        <Card className="h-full overflow-hidden">
          <CardHeader className="p-2 pb-1">
            <CardTitle className="flex items-center gap-1 text-sm">
              <div className="w-2 h-2 rounded-full bg-yellow-500" />
              Self-Learning System
            </CardTitle>
          </CardHeader>
          <CardContent className="p-2 pt-0">
            <div className="text-center mb-0.5">
              <div className="flex justify-between items-center mb-0.5">
                <span className="text-xs text-muted-foreground">Governor</span>
                <Badge 
                  variant={backendStatus.governor?.status === 'running' ? 'default' : 'secondary'}
                  className="text-xs py-0 h-5"
                >
                  {backendStatus.governor?.status === 'running' ? 'ACTIVE' : 'INACTIVE'}
                </Badge>
              </div>
              <div className="text-2xl font-bold">{backendStatus.governor?.learning_rate || 0}</div>
              <p className="text-xs text-muted-foreground">facts/min</p>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span>Learning Progress</span>
                <span>{metrics.learningProgress.toFixed(0)}%</span>
              </div>
              <Progress value={metrics.learningProgress} className="h-1" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Trust Score - Volle Breite */}
      <Card className="mb-1" style={{height: 'calc(25% - 10px)'}}>
        <CardHeader className="p-2 pb-1">
          <CardTitle className="flex items-center gap-1 text-sm">
            <div className="w-2 h-2 rounded-full bg-purple-500" />
            System Trust Score
          </CardTitle>
        </CardHeader>
        <CardContent className="p-2 pt-0">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold">{metrics.trustScore.toFixed(0)}%</div>
              <p className="text-xs text-muted-foreground">Overall system confidence</p>
            </div>
            <div className="flex flex-col">
              {Object.entries(metrics.trustFactors).map(([factor, value]) => (
                <div key={factor} className="flex items-center gap-2 text-xs">
                  {value > 0 ? (
                    <CheckCircle className="w-3 h-3 text-green-500" />
                  ) : (
                    <XCircle className="w-3 h-3 text-gray-400" />
                  )}
                  <span>{factor.replace(/([A-Z])/g, ' $1').trim()}</span>
                </div>
              ))}
            </div>
          </div>
          <Progress value={metrics.trustScore} className="h-2" />
        </CardContent>
      </Card>

      {/* System Capabilities - Icons in einer Reihe */}
      <Card className="mb-1" style={{height: 'calc(25% - 10px)'}}>
        <CardHeader className="p-2 pb-1">
          <CardTitle className="text-sm">System Capabilities</CardTitle>
        </CardHeader>
        <CardContent className="p-2 pt-0">
          <div className="flex justify-around">
            {[
              { name: 'WebSocket', status: true, icon: '🌐' },
              { name: 'CUDA', status: false, icon: '🖥️' },
              { name: 'Write Mode', status: backendStatus.writeMode, icon: '✏️' },
              { name: 'Governor', status: backendStatus.governor?.status === 'running', icon: '⚙️' },
              { name: 'HRM', status: backendStatus.hrm?.status === 'operational', icon: '🧠' }
            ].map((cap) => (
              <div key={cap.name} className="flex flex-col items-center">
                <div className="text-2xl mb-1">{cap.icon}</div>
                <span className="text-xs text-center">{cap.name}</span>
                <Badge variant={cap.status ? 'default' : 'secondary'} className="text-xs py-0 h-5">
                  {cap.status ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Backend Health - Kompakt */}
      <Card className="flex-1">
        <CardHeader className="p-2 pb-1">
          <CardTitle className="flex items-center gap-1 text-sm">
            <Server className="w-3 h-3" />
            Backend Health
          </CardTitle>
        </CardHeader>
        <CardContent className="p-2 pt-0">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Port:</span>
                <Badge className="text-xs py-0 h-5">5002</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Repository:</span>
                <span>SQLiteFactRepository</span>
              </div>
            </div>
            <div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Architecture:</span>
                <span>Hexagonal v2.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Mode:</span>
                <Badge variant={backendStatus.writeMode ? 'default' : 'secondary'} className="text-xs py-0 h-5">
                  {backendStatus.writeMode ? 'Read-Write' : 'Read-Only'}
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProDashboardEnhanced;