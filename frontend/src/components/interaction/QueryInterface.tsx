import React, { useState, useRef, useEffect } from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';
import hakgalAPI from '@/services/api';
import wsService from '@/services/websocket';

interface QueryResult {
  id: string;
  query: string;
  response: string;
  metadata: {
    veritasScore: number;
    verificationStatus: 'PROVEN' | 'DISPROVEN' | 'UNCERTAIN';
    prover: string;
    confidence: number;
    processingTime: number;
  };
  timestamp: Date;
}

const QueryInterface = () => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<QueryResult[]>([]);
  const [currentTrace, setCurrentTrace] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const isConnected = useGovernorStore(state => state.isConnected);

  const suggestions = [
    'ask "What is the capital of France?"',
    'analyze physics',
    'status',
    'verify "All birds can fly"',
    'explain quantum entanglement'
  ];

  useEffect(() => {
    // Listen for query results via WebSocket
    const handleQueryResult = (data: any) => {
      const newResult: QueryResult = {
        id: Date.now().toString(),
        query: data.query || query,
        response: data.response || data.answer || '',
        metadata: {
          veritasScore: data.veritas_score || data.pfab_score || 0,
          verificationStatus: data.verification_status || 'UNCERTAIN',
          prover: data.prover || 'UNKNOWN',
          confidence: data.confidence || 0,
          processingTime: data.processing_time || 0
        },
        timestamp: new Date()
      };
      
      setResults(prev => [newResult, ...prev]);
      setCurrentTrace([]);
      setIsProcessing(false);
      setQuery('');
    };

    wsService.on('query_result', handleQueryResult);

    return () => {
      wsService.off('query_result', handleQueryResult);
    };
  }, [query]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isProcessing || !isConnected) return;

    setIsProcessing(true);
    setCurrentTrace(['STEP_1: Parsing query...', 'STEP_2: Routing to appropriate engine...']);

    try {
      // Determine query type and send appropriate request
      if (query.startsWith('ask ')) {
        const question = query.substring(4).replace(/['"]/g, '');
        await hakgalAPI.askQuestion(question);
      } else if (query.startsWith('analyze ')) {
        const text = query.substring(8);
        await hakgalAPI.analyzeText(text);
      } else if (query === 'status') {
        const status = await hakgalAPI.getSystemStatus();
        const newResult: QueryResult = {
          id: Date.now().toString(),
          query: query,
          response: JSON.stringify(status.data, null, 2),
          metadata: {
            veritasScore: 100,
            verificationStatus: 'PROVEN',
            prover: 'SYSTEM',
            confidence: 100,
            processingTime: 0
          },
          timestamp: new Date()
        };
        setResults(prev => [newResult, ...prev]);
        setIsProcessing(false);
        setQuery('');
      } else {
        // General query
        wsService.sendQuery(query);
      }
    } catch (error) {
      console.error('Query error:', error);
      setIsProcessing(false);
      setCurrentTrace([]);
    }
  };

  const getVerificationColor = (status: string) => {
    switch (status) {
      case 'PROVEN': return 'text-success';
      case 'DISPROVEN': return 'text-destructive';
      case 'UNCERTAIN': return 'text-warning';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold">Query Interface</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="p-4 border-b border-border">
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={isConnected ? "Enter your query (e.g., 'ask', 'analyze', 'verify')..." : "Waiting for connection..."}
            className="w-full px-4 py-3 rounded-lg bg-background border border-border focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
            disabled={isProcessing || !isConnected}
          />
          <button
            type="submit"
            disabled={isProcessing || !query.trim() || !isConnected}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? 'Processing...' : 'Submit'}
          </button>
        </div>
        
        {isConnected && (
          <div className="mt-2 flex flex-wrap gap-2">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setQuery(suggestion)}
                className="text-xs px-2 py-1 rounded-full bg-muted hover:bg-muted/80 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </form>
      
      {isProcessing && currentTrace.length > 0 && (
        <div className="p-4 border-b border-border bg-muted/20">
          <h3 className="text-sm font-medium mb-2">Live Reasoning Trace</h3>
          <div className="space-y-1">
            {currentTrace.map((step, idx) => (
              <div key={idx} className="text-xs font-mono text-muted-foreground">
                {step}
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!isConnected && (
          <div className="text-center py-8">
            <p className="text-sm text-muted-foreground">
              Waiting for WebSocket connection...
            </p>
          </div>
        )}
        
        {results.map((result) => (
          <div key={result.id} className="p-4 rounded-lg bg-background border border-border">
            <div className="mb-2">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-primary">Query:</span>
                <span className="text-xs text-muted-foreground">
                  {result.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <div className="text-sm font-mono bg-muted/50 p-2 rounded">{result.query}</div>
            </div>
            
            <div className="mb-3">
              <span className="text-sm font-medium text-primary">Response:</span>
              <div className="text-sm mt-1 whitespace-pre-wrap">{result.response}</div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-3 bg-muted/20 rounded-lg">
              <div>
                <span className="text-xs text-muted-foreground">Veritas Score:</span>
                <div className="text-sm font-semibold">
                  {result.metadata.veritasScore.toFixed(1)}%
                </div>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Verification:</span>
                <div className={`text-sm font-semibold ${getVerificationColor(result.metadata.verificationStatus)}`}>
                  {result.metadata.verificationStatus}
                </div>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Confidence:</span>
                <div className="text-sm font-semibold">
                  {result.metadata.confidence.toFixed(1)}%
                </div>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Time:</span>
                <div className="text-sm font-semibold">
                  {result.metadata.processingTime}ms
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default QueryInterface;
