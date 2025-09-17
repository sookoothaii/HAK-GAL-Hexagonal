// ProDashboardEnhanced - NO-SCROLL VERSION
// Alles auf einem Bildschirm ohne Scrollen!
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
  RefreshCw,
  Play,
  Pause
} from 'lucide-react';

/**
 * NO-SCROLL Dashboard - Wirklich alles auf einem Screen!
 * Nach HAK/GAL Verfassung: Maximale Informationsdichte
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
          const response = await fetch(url, { 
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
      
      const response = await fetch(endpoint, {
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

  // FIXED LAYOUT - Alles in einem Grid ohne Scroll
  return (
    <div className="fixed inset-0 bg-background p-3 overflow-hidden">
      {/* ULTRA-COMPACT HEADER */}
      <div className="flex justify-between items-center h-12 mb-2">
        <div>
          <h1 className="text-xl font-bold">HAK-GAL Neurosymbolic Intelligence Suite</h1>
          <p className="text-xs text-muted-foreground -mt-1">
            Backend: Port 5002 | Mode: {backendStatus.writeMode ? 'WRITE' : 'READ'} | Facts: {backendStatus.facts.toLocaleString()}
          </p>
        </div>
        <Button
          variant={backendStatus.governor?.status === 'running' ? 'destructive' : 'default'}
          size="sm"
          onClick={toggleGovernor}
          className="h-8"
        >
          {backendStatus.governor?.status === 'running' ? 'Stop Governor' : 'Start Governor'}
        </Button>
      </div>

      {/* MAIN GRID - Alles in einer Ansicht */}
      <div className="grid grid-cols-5 gap-2 h-[calc(100vh-80px)]">
        
        {/* Neural Components */}
        <Card className="col-span-1">
          <CardHeader className="pb-2 pt-3">
            <CardTitle className="text-sm flex items-center gap-1">
              <Brain className="w-4 h-4 text-blue-500" />
              Neural Components
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="text-center mb-2">
              <Badge variant={backendStatus.hrm?.status === 'operational' ? 'default' : 'secondary'} className="text-xs mb-1">
                SimplifiedHRM
              </Badge>
              <div className="text-2xl font-bold">1.6M</div>
              <p className="text-xs text-muted-foreground">Parameters (Trained)</p>
            </div>
            <div>
              <div className="text-xs mb-1">Inference</div>
              <Progress value={95} className="h-1" />
              <div className="text-xs text-green-500 mt-1">&lt;10ms</div>
            </div>
          </CardContent>
        </Card>

        {/* Symbolic Components */}
        <Card className="col-span-1">
          <CardHeader className="pb-2 pt-3">
            <CardTitle className="text-sm flex items-center gap-1">
              <Database className="w-4 h-4 text-green-500" />
              Symbolic Components  
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="text-center mb-2">
              <Badge variant="default" className="text-xs mb-1">SQLite</Badge>
              <div className="text-2xl font-bold">{backendStatus.facts.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">Facts</p>
            </div>
            <div>
              <div className="text-xs mb-1">Progress to 5k</div>
              <Progress value={metrics.factProgress} className="h-1" />
              <div className="text-xs text-right mt-1">{metrics.factProgress.toFixed(0)}%</div>
            </div>
          </CardContent>
        </Card>

        {/* Self-Learning System */}
        <Card className="col-span-1">
          <CardHeader className="pb-2 pt-3">
            <CardTitle className="text-sm flex items-center gap-1">
              <Zap className="w-4 h-4 text-yellow-500" />
              Self-Learning
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="text-center mb-2">
              <Badge 
                variant={backendStatus.governor?.status === 'running' ? 'default' : 'secondary'}
                className="text-xs mb-1"
              >
                {backendStatus.governor?.status || 'INACTIVE'}
              </Badge>
              <div className="text-2xl font-bold">{backendStatus.governor?.learning_rate || 0}</div>
              <p className="text-xs text-muted-foreground">facts/min</p>
            </div>
            <div>
              <div className="text-xs mb-1">Learning Progress</div>
              <Progress value={metrics.learningProgress} className="h-1" />
              <div className="text-xs text-right mt-1">{metrics.learningProgress.toFixed(0)}%</div>
            </div>
          </CardContent>
        </Card>

        {/* Trust Score - Vertikal kleiner */}
        <Card className="col-span-1">
          <CardHeader className="pb-2 pt-3">
            <CardTitle className="text-sm flex items-center gap-1">
              <Activity className="w-4 h-4 text-purple-500" />
              System Trust Score
            </CardTitle>
          </CardHeader>
          <CardContent className="pb-3">
            <div className="text-center">
              <div className="text-3xl font-bold">{metrics.trustScore.toFixed(0)}%</div>
              <p className="text-xs text-muted-foreground mb-2">Overall system confidence</p>
              <Progress value={metrics.trustScore} className="h-2 mb-2" />
            </div>
            <div className="space-y-1">
              {Object.entries(metrics.trustFactors).slice(0, 5).map(([factor, value]) => (
                <div key={factor} className="flex items-center gap-1 text-xs">
                  {value > 0 ? (
                    <CheckCircle className="w-3 h-3 text-green-500" />
                  ) : (
                    <XCircle className="w-3 h-3 text-gray-400" />
                  )}
                  <span className="text-xs">{factor.replace(/([A-Z])/g, ' $1').trim()}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Combined System Info - Rechts */}
        <Card className="col-span-1">
          <CardHeader className="pb-2 pt-3">
            <CardTitle className="text-sm">System Capabilities</CardTitle>
          </CardHeader>
          <CardContent className="pb-3 space-y-3">
            {/* Capabilities Grid */}
            <div className="grid grid-cols-3 gap-1">
              {[
                { name: 'WebSocket', status: true, color: 'bg-green-500' },
                { name: 'CUDA', status: false, color: 'bg-gray-400' },
                { name: 'Write Mode', status: backendStatus.writeMode, color: backendStatus.writeMode ? 'bg-green-500' : 'bg-gray-400' },
                { name: 'Governor', status: backendStatus.governor?.status === 'running', color: backendStatus.governor?.status === 'running' ? 'bg-blue-500' : 'bg-gray-400' },
                { name: 'HRM', status: backendStatus.hrm?.status === 'operational', color: backendStatus.hrm?.status === 'operational' ? 'bg-purple-500' : 'bg-gray-400' },
                { name: 'Inactive', status: false, color: 'bg-gray-400' }
              ].map((cap) => (
                <div key={cap.name} className="text-center">
                  <Badge variant={cap.status ? 'default' : 'secondary'} className="text-xs w-full">
                    {cap.name}
                  </Badge>
                </div>
              ))}
            </div>
            
            {/* Backend Health */}
            <Card className="border-0 shadow-none bg-muted/50 p-2">
              <CardTitle className="text-xs flex items-center gap-1 mb-2">
                <Server className="w-3 h-3" />
                Backend Health
              </CardTitle>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span>Port:</span>
                  <Badge className="text-xs h-4">5002</Badge>
                </div>
                <div className="flex justify-between">
                  <span>Repository:</span>
                  <span className="text-xs">SQLiteFactRepository</span>
                </div>
                <div className="flex justify-between">
                  <span>Architecture:</span>
                  <span className="text-xs">Hexagonal v2.0</span>
                </div>
                <div className="flex justify-between">
                  <span>Mode:</span>
                  <Badge variant={backendStatus.writeMode ? 'default' : 'secondary'} className="text-xs h-4">
                    {backendStatus.writeMode ? 'Read-Write' : 'Read-Only'}
                  </Badge>
                </div>
              </div>
            </Card>
          </CardContent>
        </Card>
        
      </div>
    </div>
  );
};

export default ProDashboardEnhanced;