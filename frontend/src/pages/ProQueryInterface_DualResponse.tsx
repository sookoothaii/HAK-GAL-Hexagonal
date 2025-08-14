// V3 - DUAL RESPONSE Query Interface
// Shows both Symbolic (Logical) and Neurologic (Raw LLM) responses side by side
import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useGovernorStore, QueryResponse } from '@/stores/useGovernorStore';
import { useGovernorSocket } from '@/hooks/useGovernorSocket';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, Brain, Terminal, Copy, Check, Split, Clock, Database } from 'lucide-react';
import { toast } from 'sonner';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Dual Response Result Card
const DualResponseCard: React.FC<{ result: QueryResponse; index: number }> = ({ result, index }) => {
  const [copiedSymbolic, setCopiedSymbolic] = useState(false);
  const [copiedNeurologic, setCopiedNeurologic] = useState(false);

  const handleCopy = (text: string, type: 'symbolic' | 'neurologic') => {
    navigator.clipboard.writeText(text);
    if (type === 'symbolic') {
      setCopiedSymbolic(true);
      setTimeout(() => setCopiedSymbolic(false), 2000);
    } else {
      setCopiedNeurologic(true);
      setTimeout(() => setCopiedNeurologic(false), 2000);
    }
    toast.success(`${type} response copied!`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="mb-6"
    >
      {/* Query Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <p className="font-semibold text-sm text-primary">
            <span className="font-mono mr-2">&gt;</span>{result.query}
          </p>
          {result.processingTime && (
            <div className="flex items-center text-xs text-muted-foreground">
              <Clock className="w-3 h-3 mr-1" />
              {result.processingTime.toFixed(2)}s
            </div>
          )}
        </div>
        {result.kbFactsUsed !== undefined && (
          <div className="flex items-center text-xs text-muted-foreground mt-1">
            <Database className="w-3 h-3 mr-1" />
            {result.kbFactsUsed} facts available
          </div>
        )}
      </div>

      {/* Dual Response Content */}
      {result.status === 'pending' ? (
        <Card className="border-0 bg-card/50">
          <CardContent className="p-6 flex items-center justify-center">
            <Loader2 className="w-6 h-6 mr-3 animate-spin text-primary" />
            <span className="text-muted-foreground">Processing query...</span>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Symbolic Response */}
          <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center justify-between">
                <div className="flex items-center">
                  <Terminal className="w-4 h-4 mr-2" />
                  Symbolic Response
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => handleCopy(result.symbolicResponse || '', 'symbolic')}
                >
                  {copiedSymbolic ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-3 rounded bg-black/50 font-mono text-xs overflow-x-auto">
                <pre className="whitespace-pre-wrap text-green-400">
                  {result.symbolicResponse || 'No symbolic response available'}
                </pre>
              </div>
              {result.naturalLanguageExplanation && (
                <div className="mt-3 p-3 rounded bg-muted/50">
                  <p className="text-xs text-muted-foreground mb-1">Explanation:</p>
                  <p className="text-sm">{result.naturalLanguageExplanation}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Neurologic Response */}
          <Card className="border-secondary/20 bg-gradient-to-br from-secondary/5 to-transparent">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center justify-between">
                <div className="flex items-center">
                  <Brain className="w-4 h-4 mr-2" />
                  Neurologic Response
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => handleCopy(result.neurologicResponse || '', 'neurologic')}
                >
                  {copiedNeurologic ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-3 rounded bg-muted/30">
                <p className="text-sm whitespace-pre-wrap">
                  {result.neurologicResponse || 'No neurologic response available'}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </motion.div>
  );
};

// Main Dual Query Interface
const ProQueryInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [viewMode, setViewMode] = useState<'split' | 'tabs'>('split');
  const wsService = useGovernorSocket();
  const queryHistory = useGovernorStore(state => state.queryHistory);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!query.trim()) {
      toast.error('Please enter a query.');
      return;
    }
    wsService.sendCommand('ask', query.trim());
    setQuery('');
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        handleSubmit();
      }
    };
    const textarea = textareaRef.current;
    textarea?.addEventListener('keydown', handleKeyDown);
    return () => textarea?.removeEventListener('keydown', handleKeyDown);
  }, [query]);

  return (
    <div className="h-full flex flex-col p-4">
      {/* Header with View Mode Toggle */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold">Dual Response Query Interface</h2>
          <p className="text-sm text-muted-foreground">
            Compare symbolic logic with raw neural responses
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === 'split' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('split')}
          >
            <Split className="w-4 h-4 mr-2" />
            Split View
          </Button>
          <Button
            variant={viewMode === 'tabs' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('tabs')}
          >
            Tabs
          </Button>
        </div>
      </div>

      {/* Query History */}
      <div className="flex-1 flex flex-col min-h-0">
        <ScrollArea className="flex-1 pr-4">
          <AnimatePresence>
            {queryHistory.length > 0 ? (
              viewMode === 'split' ? (
                // Split View
                queryHistory.map((result, index) => (
                  <DualResponseCard key={result.id} result={result} index={index} />
                ))
              ) : (
                // Tabs View
                queryHistory.map((result, index) => (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="mb-6"
                  >
                    <div className="mb-3">
                      <p className="font-semibold text-sm text-primary">
                        <span className="font-mono mr-2">&gt;</span>{result.query}
                      </p>
                    </div>
                    <Tabs defaultValue="symbolic" className="w-full">
                      <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="symbolic">Symbolic</TabsTrigger>
                        <TabsTrigger value="neurologic">Neurologic</TabsTrigger>
                      </TabsList>
                      <TabsContent value="symbolic">
                        <Card>
                          <CardContent className="pt-6">
                            <div className="p-3 rounded bg-black/50 font-mono text-xs">
                              <pre className="whitespace-pre-wrap text-green-400">
                                {result.symbolicResponse}
                              </pre>
                            </div>
                          </CardContent>
                        </Card>
                      </TabsContent>
                      <TabsContent value="neurologic">
                        <Card>
                          <CardContent className="pt-6">
                            <p className="text-sm whitespace-pre-wrap">
                              {result.neurologicResponse}
                            </p>
                          </CardContent>
                        </Card>
                      </TabsContent>
                    </Tabs>
                  </motion.div>
                ))
              )
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground">
                <div className="flex items-center mb-4">
                  <Terminal className="w-8 h-8 mr-4 text-primary" />
                  <Brain className="w-8 h-8 text-secondary" />
                </div>
                <h3 className="text-lg font-semibold">Dual Response Query Interface</h3>
                <p className="text-sm max-w-md">
                  Ask questions to see both the logical verification (symbolic) 
                  and the raw LLM interpretation (neurologic) side by side.
                </p>
              </div>
            )}
          </AnimatePresence>
        </ScrollArea>
      </div>

      {/* Query Input */}
      <div className="flex-shrink-0 pt-4 border-t">
        <div className="relative">
          <Textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question... (e.g., Is Socrates mortal?)"
            className="pr-24 min-h-[80px]"
          />
          <Button
            onClick={handleSubmit}
            className="absolute right-2 bottom-2"
            size="sm"
          >
            <Send className="w-4 h-4 mr-2" />
            Submit
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Ctrl+Enter to submit
        </p>
      </div>
    </div>
  );
};

export default ProQueryInterface;
