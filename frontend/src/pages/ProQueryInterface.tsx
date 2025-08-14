// V3 - DUAL WINDOW VERSION - Symbolic vs Neurologic Responses - IMPROVED FORMATTING
import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useGovernorStore, QueryResponse } from '@/stores/useGovernorStore';
import { useGovernorSocket } from '@/hooks/useGovernorSocket';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, Brain, Terminal, Copy, Check, Cpu, Zap, Timer, Info } from 'lucide-react';
import { toast } from 'sonner';

// Helper function to show raw response without any filtering
const formatResponse = (response: string): string => {
  if (!response) return 'No response available.';
  // Return completely unfiltered response
  return response;
};

// Helper to extract key facts from symbolic response
const extractKeyFacts = (response: string): string[] => {
  const facts = [];
  
  // Extract Result
  const resultMatch = response.match(/Result:\s*([^.]+)/);
  if (resultMatch) facts.push(`Result: ${resultMatch[1].trim()}`);
  
  // Extract Reason
  const reasonMatch = response.match(/Reason:\s*([^.]+)/);
  if (reasonMatch) facts.push(`Reason: ${reasonMatch[1].trim()}`);
  
  // Extract any predicates
  const predicateMatches = response.matchAll(/(\w+)\([^)]+\)/g);
  for (const match of predicateMatches) {
    if (!facts.some(f => f.includes(match[0]))) {
      facts.push(match[0]);
    }
  }
  
  return facts.slice(0, 5); // Max 5 facts
};

// Dual Response Query Result Card
const DualQueryResultCard: React.FC<{ result: QueryResponse; index: number }> = ({ result, index }) => {
  const [copiedSymbolic, setCopiedSymbolic] = useState(false);
  const [copiedNeurologic, setCopiedNeurologic] = useState(false);

  const handleCopy = (text: string, isSymbolic: boolean) => {
    navigator.clipboard.writeText(text);
    if (isSymbolic) {
      setCopiedSymbolic(true);
      setTimeout(() => setCopiedSymbolic(false), 2000);
    } else {
      setCopiedNeurologic(true);
      setTimeout(() => setCopiedNeurologic(false), 2000);
    }
    toast.success('Response copied!');
  };

  const processingTime = result.processingTime || 0;
  const kbFactsUsed = result.kbFactsUsed || 0;
  
  // Extract and format responses
  const symbolicFacts = result.symbolicResponse ? extractKeyFacts(result.symbolicResponse) : [];
  // Get completely raw, unfiltered neurologic response
  const rawNeurologic = result.neurologicResponse || result.naturalLanguageExplanation || '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="mb-6"
    >
      {/* Query Header */}
      <div className="mb-3">
        <p className="font-semibold text-sm text-primary flex items-center justify-between">
          <span><span className="font-mono mr-2">&gt;</span>{result.query}</span>
          <span className="text-xs text-muted-foreground flex items-center gap-2">
            {processingTime > 0 && (
              <span className="flex items-center">
                <Timer className="w-3 h-3 mr-1" />
                {(processingTime / 1000).toFixed(1)}s
              </span>
            )}
            {kbFactsUsed > 0 && (
              <span className="flex items-center">
                <Cpu className="w-3 h-3 mr-1" />
                {kbFactsUsed} facts
              </span>
            )}
          </span>
        </p>
      </div>

      {result.status === 'pending' ? (
        <Card className="border-0 bg-card/50">
          <CardContent className="p-4">
            <div className="flex items-center text-muted-foreground">
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Analyzing query...
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-5 gap-4">
          {/* Symbolic Response - Simplified */}
          <Card className="border-0 bg-card/50 col-span-2">
            <CardHeader className="p-3 pb-2">
              <CardTitle className="text-xs font-semibold uppercase text-muted-foreground flex items-center justify-between">
                <span className="flex items-center">
                  <Cpu className="w-3 h-3 mr-1" />
                  Logic Verified
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-5 w-5"
                  onClick={() => handleCopy(result.symbolicResponse || '', true)}
                >
                  {copiedSymbolic ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-3 pt-0">
              {symbolicFacts.length > 0 ? (
                <ul className="space-y-1">
                  {symbolicFacts.map((fact, i) => (
                    <li key={i} className="text-xs font-mono">
                      {fact.startsWith('Result:') ? (
                        <span className={fact.includes('Yes') ? 'text-green-500' : 'text-yellow-500'}>
                          {fact}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">{fact}</span>
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-muted-foreground">No logical facts found.</p>
              )}
            </CardContent>
          </Card>

          {/* Neurologic Response - Unfiltered */}
          <Card className="border-0 bg-card/50 col-span-3">
            <CardHeader className="p-3 pb-2">
              <CardTitle className="text-xs font-semibold uppercase text-muted-foreground flex items-center justify-between">
                <span className="flex items-center">
                  <Zap className="w-3 h-3 mr-1" />
                  Raw LLM Output (Unfiltered)
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-5 w-5"
                  onClick={() => handleCopy(rawNeurologic, false)}
                >
                  {copiedNeurologic ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-3 pt-0">
              <div className="overflow-auto max-h-[400px] bg-muted/30 p-2 rounded">
                <pre className="text-xs font-mono whitespace-pre-wrap break-words">{rawNeurologic}</pre>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </motion.div>
  );
};

// Main Dual Window Query Interface
const ProQueryInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const wsService = useGovernorSocket();
  const queryHistory = useGovernorStore(state => state.queryHistory);
  const addQueryResponse = useGovernorStore(state => state.addQueryResponse);
  const updateQueryResponse = useGovernorStore(state => state.updateQueryResponse);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query.');
      return;
    }

    const queryId = `query-${Date.now()}`;
    const startTime = Date.now();
    
    // Add pending query
    addQueryResponse({
      id: queryId,
      timestamp: new Date().toISOString(),
      query: query.trim(),
      symbolicResponse: '',
      neurologicResponse: '',
      status: 'pending'
    });

    setIsLoading(true);
    
    // Send dual-response command
    wsService.sendCommand('ask_dual', { 
      query: query.trim(),
      queryId: queryId 
    });
    
    setQuery('');
    
    // Simulate response handling (will be replaced by WebSocket events)
    setTimeout(() => {
      const processingTime = Date.now() - startTime;
      updateQueryResponse(queryId, {
        status: 'success',
        processingTime: processingTime
      });
      setIsLoading(false);
    }, 5000);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && !isLoading) {
        e.preventDefault();
        handleSubmit();
      }
    };
    const textarea = textareaRef.current;
    textarea?.addEventListener('keydown', handleKeyDown);
    return () => textarea?.removeEventListener('keydown', handleKeyDown);
  }, [query, isLoading]);

  // Auto-focus on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  return (
    <div className="h-full flex flex-col p-4">
      <div className="flex-1 flex flex-col min-h-0">
        <ScrollArea className="flex-1 pr-4">
          <AnimatePresence>
            {queryHistory.length > 0 ? (
              queryHistory.map((result, index) => (
                <DualQueryResultCard key={result.id} result={result} index={index} />
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground">
                <Brain className="w-12 h-12 mb-4" />
                <h3 className="text-lg font-semibold">Dual Response Query Interface</h3>
                <p className="text-sm mb-2">Ask questions to see both filtered logic and raw LLM responses.</p>
                <div className="flex gap-8 text-xs mt-4">
                  <div className="flex items-center">
                    <Cpu className="w-4 h-4 mr-2" />
                    <span>Symbolic: Logic-verified & filtered</span>
                  </div>
                  <div className="flex items-center">
                    <Zap className="w-4 h-4 mr-2" />
                    <span>Neurologic: Complete unfiltered LLM output</span>
                  </div>
                </div>
              </div>
            )}
          </AnimatePresence>
        </ScrollArea>
      </div>
      <div className="flex-shrink-0 pt-4 border-t">
        <div className="relative">
          <Textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question... (e.g., Is Socrates mortal?)"
            className="pr-20"
            disabled={isLoading}
          />
          <Button
            onClick={handleSubmit}
            className="absolute right-2 bottom-2"
            size="sm"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Send className="w-4 h-4 mr-2" />
            )}
            Submit
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Ctrl+Enter to submit • Response time target: &lt;2s
        </p>
      </div>
    </div>
  );
};

export default ProQueryInterface;
