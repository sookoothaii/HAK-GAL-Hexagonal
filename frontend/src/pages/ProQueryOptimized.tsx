import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Search,
  Brain,
  Plus,
  Clock,
  AlertTriangle,
  Loader2,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { api } from '@/services/api_optimized';
import { toast } from 'sonner';

export default function ProQueryOptimized() {
  const [searchQuery, setSearchQuery] = useState('');
  const [reasonQuery, setReasonQuery] = useState('');
  const [newFact, setNewFact] = useState('');
  const [batchFacts, setBatchFacts] = useState('');
  const [loading, setLoading] = useState({
    search: false,
    reason: false,
    add: false,
    batch: false
  });
  const [results, setResults] = useState<any>({
    search: null,
    reason: null
  });
  const [performanceMetrics, setPerformanceMetrics] = useState({
    lastRequestTime: 0,
    averageTime: 2000 // Realistische 2 Sekunden
  });

  // Zeitmessung für Requests
  const measureTime = async (operation: () => Promise<any>, type: string) => {
    const start = Date.now();
    try {
      const result = await operation();
      const duration = Date.now() - start;
      
      setPerformanceMetrics(prev => ({
        lastRequestTime: duration,
        averageTime: (prev.averageTime + duration) / 2
      }));
      
      if (duration > 3000) {
        toast.warning(`Request dauerte ${(duration/1000).toFixed(1)}s - API ist langsam`);
      }
      
      return result;
    } catch (error) {
      const duration = Date.now() - start;
      setPerformanceMetrics(prev => ({
        ...prev,
        lastRequestTime: duration
      }));
      throw error;
    }
  };

  // Search Facts
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Bitte geben Sie einen Suchbegriff ein');
      return;
    }

    setLoading(prev => ({ ...prev, search: true }));
    toast.info('Suche läuft... (kann 2-3 Sekunden dauern)');

    try {
      const response = await measureTime(
        () => api.searchFacts(searchQuery, 10),
        'search'
      );
      
      setResults(prev => ({ ...prev, search: response.data }));
      toast.success(`${response.data.count} Ergebnisse gefunden`);
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Suche fehlgeschlagen');
    } finally {
      setLoading(prev => ({ ...prev, search: false }));
    }
  };

  // Reasoning
  const handleReason = async () => {
    if (!reasonQuery.trim()) {
      toast.error('Bitte geben Sie eine Anfrage ein');
      return;
    }

    setLoading(prev => ({ ...prev, reason: true }));
    toast.warning('Reasoning kann 2-5 Sekunden dauern...');

    try {
      const response = await measureTime(
        () => api.reason(reasonQuery),
        'reason'
      );
      
      setResults(prev => ({ ...prev, reason: response.data }));
      
      const confidence = response.data.confidence || 0;
      if (confidence > 0.7) {
        toast.success(`Hohe Konfidenz: ${(confidence * 100).toFixed(0)}%`);
      } else {
        toast.warning(`Niedrige Konfidenz: ${(confidence * 100).toFixed(0)}%`);
      }
    } catch (error) {
      console.error('Reasoning failed:', error);
      toast.error('Reasoning fehlgeschlagen');
    } finally {
      setLoading(prev => ({ ...prev, reason: false }));
    }
  };

  // Add Single Fact
  const handleAddFact = async () => {
    if (!newFact.trim()) {
      toast.error('Bitte geben Sie ein Fakt ein');
      return;
    }

    // Validierung
    if (!newFact.match(/^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.?$/)) {
      toast.error('Format: Predicate(Entity1, Entity2)');
      return;
    }

    setLoading(prev => ({ ...prev, add: true }));

    try {
      const factToAdd = newFact.endsWith('.') ? newFact : newFact + '.';
      const response = await measureTime(
        () => api.addFactsBatch([factToAdd]),
        'add'
      );
      
      if (response[0].success) {
        toast.success('Fakt hinzugefügt');
        setNewFact('');
      } else {
        toast.error('Fakt konnte nicht hinzugefügt werden');
      }
    } catch (error) {
      console.error('Add fact failed:', error);
      toast.error('Fehler beim Hinzufügen');
    } finally {
      setLoading(prev => ({ ...prev, add: false }));
    }
  };

  // Batch Add Facts
  const handleBatchAdd = async () => {
    const facts = batchFacts
      .split('\n')
      .filter(f => f.trim())
      .map(f => f.trim());

    if (facts.length === 0) {
      toast.error('Keine Fakten eingegeben');
      return;
    }

    if (facts.length > 10) {
      toast.warning(`${facts.length} Fakten - das dauert ${facts.length * 2} Sekunden!`);
    }

    setLoading(prev => ({ ...prev, batch: true }));
    toast.info(`Füge ${facts.length} Fakten hinzu... (${facts.length * 2}s geschätzt)`);

    try {
      const results = await api.addFactsBatch(facts);
      const successful = results.filter(r => r.success).length;
      const failed = results.filter(r => !r.success).length;

      if (successful > 0) {
        toast.success(`${successful} Fakten hinzugefügt`);
      }
      if (failed > 0) {
        toast.error(`${failed} Fakten fehlgeschlagen`);
      }

      setBatchFacts('');
    } catch (error) {
      console.error('Batch add failed:', error);
      toast.error('Batch-Operation fehlgeschlagen');
    } finally {
      setLoading(prev => ({ ...prev, batch: false }));
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Performance Status Bar */}
      <Alert className="border-yellow-500 bg-yellow-500/10">
        <Clock className="h-4 w-4" />
        <AlertDescription className="flex justify-between items-center">
          <span>API Performance: ~{(performanceMetrics.averageTime/1000).toFixed(1)}s pro Request</span>
          {performanceMetrics.lastRequestTime > 0 && (
            <Badge variant={performanceMetrics.lastRequestTime > 3000 ? "destructive" : "secondary"}>
              Letzter Request: {(performanceMetrics.lastRequestTime/1000).toFixed(1)}s
            </Badge>
          )}
        </AlertDescription>
      </Alert>

      <Tabs defaultValue="search" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="search">Suche</TabsTrigger>
          <TabsTrigger value="reason">Reasoning</TabsTrigger>
          <TabsTrigger value="add">Fakten hinzufügen</TabsTrigger>
        </TabsList>

        {/* Search Tab */}
        <TabsContent value="search">
          <Card>
            <CardHeader>
              <CardTitle>
                <Search className="h-5 w-5 inline mr-2" />
                Knowledge Base durchsuchen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Suchbegriff eingeben..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  disabled={loading.search}
                />
                <Button 
                  onClick={handleSearch}
                  disabled={loading.search}
                >
                  {loading.search ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                </Button>
              </div>

              {results.search && (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {results.search.count} Ergebnisse (gecacht für 30s)
                  </p>
                  <div className="space-y-1 max-h-[300px] overflow-y-auto">
                    {results.search.results?.map((fact: any, i: number) => (
                      <div key={i} className="p-2 bg-muted rounded text-sm">
                        {fact.statement}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reasoning Tab */}
        <TabsContent value="reason">
          <Card>
            <CardHeader>
              <CardTitle>
                <Brain className="h-5 w-5 inline mr-2" />
                HRM Reasoning
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Reasoning-Anfragen dauern typischerweise 2-5 Sekunden
                </AlertDescription>
              </Alert>

              <div className="flex gap-2">
                <Input
                  placeholder="Frage eingeben..."
                  value={reasonQuery}
                  onChange={(e) => setReasonQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleReason()}
                  disabled={loading.reason}
                />
                <Button 
                  onClick={handleReason}
                  disabled={loading.reason}
                >
                  {loading.reason ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Brain className="h-4 w-4" />
                  )}
                </Button>
              </div>

              {results.reason && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm">Konfidenz:</span>
                    <Badge 
                      variant={results.reason.confidence > 0.7 ? "default" : "secondary"}
                    >
                      {(results.reason.confidence * 100).toFixed(0)}%
                    </Badge>
                    {results.reason.success ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                  </div>
                  
                  {results.reason.reasoning_terms && (
                    <div className="space-y-1">
                      <p className="text-sm font-medium">Reasoning Terms:</p>
                      <div className="flex flex-wrap gap-1">
                        {results.reason.reasoning_terms.map((term: string, i: number) => (
                          <Badge key={i} variant="outline">{term}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <p className="text-xs text-muted-foreground">
                    Dauer: {results.reason.duration_ms}ms
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Add Facts Tab */}
        <TabsContent value="add">
          <Card>
            <CardHeader>
              <CardTitle>
                <Plus className="h-5 w-5 inline mr-2" />
                Fakten hinzufügen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Single Fact */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Einzelnes Fakt</label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Predicate(Entity1, Entity2)"
                    value={newFact}
                    onChange={(e) => setNewFact(e.target.value)}
                    disabled={loading.add}
                  />
                  <Button 
                    onClick={handleAddFact}
                    disabled={loading.add}
                  >
                    {loading.add ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      'Hinzufügen'
                    )}
                  </Button>
                </div>
              </div>

              {/* Batch Facts */}
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Batch-Import (ein Fakt pro Zeile)
                </label>
                <Alert>
                  <AlertDescription>
                    Warnung: {batchFacts.split('\n').filter(f => f.trim()).length} Fakten 
                    = ~{batchFacts.split('\n').filter(f => f.trim()).length * 2}s Wartezeit
                  </AlertDescription>
                </Alert>
                <Textarea
                  placeholder="IsA(Cat, Animal)\nHas(Cat, Fur)\nCanDo(Cat, Meow)"
                  value={batchFacts}
                  onChange={(e) => setBatchFacts(e.target.value)}
                  rows={5}
                  disabled={loading.batch}
                />
                <Button 
                  onClick={handleBatchAdd}
                  disabled={loading.batch}
                  className="w-full"
                >
                  {loading.batch ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Batch-Import läuft...
                    </>
                  ) : (
                    'Batch-Import starten'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}