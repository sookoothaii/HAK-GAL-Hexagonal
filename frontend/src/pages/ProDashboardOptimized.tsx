import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  AlertTriangle, 
  Database, 
  Zap, 
  Activity,
  RefreshCw,
  Info,
  Loader2
} from 'lucide-react';
import { api, getCacheStats } from '@/services/api_optimized';

// REALISTISCHE Performance-Dashboard Komponente
export default function ProDashboardOptimized() {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    factsCount: 0,
    apiPerformance: 0.5, // Gemessene Performance: 0.5 req/s
    cacheHits: 0,
    lastUpdate: null as Date | null
  });
  const [performanceWarning, setPerformanceWarning] = useState(true);

  // Lade initiale Daten mit Cache
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    try {
      const count = await api.getFactsCount();
      const cache = getCacheStats();
      
      setStats(prev => ({
        ...prev,
        factsCount: count,
        cacheHits: cache.size,
        lastUpdate: new Date()
      }));
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearCache = () => {
    api.clearCache();
    setStats(prev => ({ ...prev, cacheHits: 0 }));
  };

  return (
    <div className="p-6 space-y-6">
      {/* Performance Warning Banner */}
      {performanceWarning && (
        <Alert className="border-yellow-500 bg-yellow-500/10">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Performance-Hinweis</AlertTitle>
          <AlertDescription className="mt-2">
            <div className="space-y-2">
              <p>Die API-Performance beträgt aktuell <strong>0.5 req/s</strong> (2000ms pro Request).</p>
              <div className="flex gap-4 text-sm">
                <span>✓ Cache aktiviert (30s TTL)</span>
                <span>✓ Batch-Operations verfügbar</span>
                <span>⚠️ Große Abfragen vermeiden</span>
              </div>
            </div>
          </AlertDescription>
          <Button
            size="sm"
            variant="ghost"
            className="mt-2"
            onClick={() => setPerformanceWarning(false)}
          >
            Verstanden
          </Button>
        </Alert>
      )}

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              <Database className="h-4 w-4 inline mr-2" />
              Knowledge Base
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                stats.factsCount.toLocaleString()
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Facts in Database
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              <Zap className="h-4 w-4 inline mr-2" />
              API Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {stats.apiPerformance} req/s
            </div>
            <Progress value={5} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">
              Sehr langsam (Normal: 100+ req/s)
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">
              <Activity className="h-4 w-4 inline mr-2" />
              Cache Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stats.cacheHits}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Gecachte Responses
            </p>
            <Button
              size="sm"
              variant="outline"
              className="mt-2 w-full"
              onClick={clearCache}
            >
              Cache leeren
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Performance Details */}
      <Card>
        <CardHeader>
          <CardTitle>Performance-Optimierungen</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="current" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="current">Aktueller Status</TabsTrigger>
              <TabsTrigger value="tips">Optimierungs-Tipps</TabsTrigger>
              <TabsTrigger value="alternatives">Alternativen</TabsTrigger>
            </TabsList>
            
            <TabsContent value="current" className="space-y-3">
              <div className="space-y-2">
                <div className="flex justify-between items-center p-2 bg-muted rounded">
                  <span>SQLite Performance</span>
                  <Badge className="bg-green-500">10,000+ queries/s</Badge>
                </div>
                <div className="flex justify-between items-center p-2 bg-muted rounded">
                  <span>Flask/Eventlet API</span>
                  <Badge className="bg-red-500">0.5 req/s</Badge>
                </div>
                <div className="flex justify-between items-center p-2 bg-muted rounded">
                  <span>WebSocket Overhead</span>
                  <Badge className="bg-yellow-500">~1000ms</Badge>
                </div>
                <div className="flex justify-between items-center p-2 bg-muted rounded">
                  <span>Flaschenhals-Faktor</span>
                  <Badge variant="destructive">20,000x</Badge>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="tips" className="space-y-3">
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Nutzen Sie Batch-Operations statt einzelner Requests</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Cache-TTL von 30 Sekunden nutzen</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Vermeiden Sie große Suchanfragen (&gt;100 Facts)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Nutzen Sie Pagination für Listen</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-500">⚠️</span>
                  <span>LLM-Requests können 3-5 Sekunden dauern</span>
                </li>
              </ul>
            </TabsContent>
            
            <TabsContent value="alternatives" className="space-y-3">
              <div className="space-y-3">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertTitle>FastAPI Alternative</AlertTitle>
                  <AlertDescription>
                    Eine FastAPI-Implementation könnte 100-500 req/s erreichen.
                    SQLite ist nicht das Problem - die API-Architektur ist es.
                  </AlertDescription>
                </Alert>
                
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertTitle>Lightweight API (Port 5003)</AlertTitle>
                  <AlertDescription>
                    Eine schlanke Version ohne WebSocket-Overhead wurde vorbereitet.
                    Diese könnte deutlich bessere Performance bieten.
                  </AlertDescription>
                </Alert>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Refresh Button */}
      <div className="flex justify-end">
        <Button
          onClick={loadStats}
          disabled={loading}
          variant="outline"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          Aktualisieren (2s Verzögerung)
        </Button>
      </div>
      
      {/* Last Update Info */}
      {stats.lastUpdate && (
        <p className="text-xs text-muted-foreground text-right">
          Letzte Aktualisierung: {stats.lastUpdate.toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}