// HRM Query Interface
// Uses the new HRM Neural Reasoning endpoint

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useHRMStore } from '@/stores/useHRMStore';
import { useHRMSocket } from '@/hooks/useHRMSocket';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Loader2, 
  Brain, 
  Copy, 
  Check, 
  Cpu, 
  Zap, 
  Timer,
  Package,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { toast } from 'sonner';

// HRM Query Result Card
const HRMQueryResultCard: React.FC<{ 
  result: any; 
  index: number 
}> = ({ result, index }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = `Query: ${result.query}\nConfidence: ${(result.confidence * 100).toFixed(1)}%\nReasoning: ${result.reasoning.join(', ')}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    toast.success('Result copied!');
  };

  // Determine confidence level
  const getConfidenceLevel = (conf: number) => {
    if (conf > 0.8) return { label: 'High', color: 'text-green-500', icon: TrendingUp };
    if (conf > 0.5) return { label: 'Medium', color: 'text-yellow-500', icon: null };
    if (conf > 0.2) return { label: 'Low', color: 'text-orange-500', icon: TrendingDown };
    return { label: 'Very Low', color: 'text-red-500', icon: TrendingDown };
  };

  const confLevel = getConfidenceLevel(result.confidence);
  const Icon = confLevel.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="mb-4"
    >
      <Card className="border-0 bg-card/50">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Brain className="w-4 h-4" />
              {result.query}
            </CardTitle>
            <div className="flex items-center gap-2">
              {result.processingTime > 0 && (
                <Badge variant="outline" className="text-xs">
                  <Timer className="w-3 h-3 mr-1" />
                  {result.processingTime}ms
                </Badge>
              )}
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={handleCopy}
              >
                {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-3">
            {/* Confidence Bar */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-muted-foreground w-20">Confidence:</span>
              <div className="flex-1 bg-muted rounded-full h-2 relative overflow-hidden">
                <motion.div
                  className="absolute left-0 top-0 h-full bg-primary"
                  initial={{ width: 0 }}
                  animate={{ width: `${result.confidence * 100}%` }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                />
              </div>
              <div className={`flex items-center gap-1 ${confLevel.color}`}>
                {Icon && <Icon className="w-3 h-3" />}
                <span className="text-sm font-bold">
                  {(result.confidence * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Verdict */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-muted-foreground w-20">Verdict:</span>
              <Badge 
                variant={result.isTrue ? "default" : "secondary"}
                className={result.isTrue ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"}
              >
                {result.isTrue ? "TRUE" : "FALSE"}
              </Badge>
              <span className="text-xs text-muted-foreground">
                ({confLevel.label} confidence)
              </span>
            </div>

            {/* Reasoning */}
            {result.reasoning && result.reasoning.length > 0 && (
              <div className="space-y-1">
                <span className="text-xs text-muted-foreground">Reasoning:</span>
                <div className="flex flex-wrap gap-1">
                  {result.reasoning.map((term: string, idx: number) => (
                    <Badge key={idx} variant="outline" className="text-xs">
                      {term}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Batch Query Component
const BatchQueryInput: React.FC<{ onSubmit: (queries: string[]) => void }> = ({ onSubmit }) => {
  const [batchText, setBatchText] = useState('');
  
  const handleBatchSubmit = () => {
    const queries = batchText
      .split('\n')
      .map(q => q.trim())
      .filter(q => q.length > 0);
    
    if (queries.length === 0) {
      toast.error('Please enter at least one query');
      return;
    }
    
    if (queries.length > 100) {
      toast.error('Maximum 100 queries per batch');
      return;
    }
    
    onSubmit(queries);
    setBatchText('');
  };

  return (
    <div className="space-y-2">
      <Textarea
        value={batchText}
        onChange={(e) => setBatchText(e.target.value)}
        placeholder="Enter multiple queries (one per line)&#10;IsA(Socrates, Philosopher)&#10;HasPart(Computer, CPU)&#10;LocatedIn(Berlin, Germany)"
        className="min-h-[150px] font-mono text-sm"
      />
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">
          {batchText.split('\n').filter(q => q.trim()).length} queries
        </span>
        <Button onClick={handleBatchSubmit} size="sm">
          <Package className="w-4 h-4 mr-2" />
          Process Batch
        </Button>
      </div>
    </div>
  );
};

// Main HRM Query Interface
const HRMQueryInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const hrm = useHRMStore(state => state.hrm);
  const { sendHRMQuery, sendHRMBatch } = useHRMSocket();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Example queries
  const exampleQueries = [
    "IsA(Socrates, Philosopher)",
    "HasPart(Computer, CPU)",
    "LocatedIn(Berlin, Germany)",
    "Causes(Gravity, Motion)",
    "IsA(Water, Person)",
    "HasPart(Socrates, CPU)"
  ];

  const handleSubmit = () => {
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }
    
    sendHRMQuery(query.trim());
    setQuery('');
  };

  const handleExample = (example: string) => {
    setQuery(example);
    textareaRef.current?.focus();
  };

  const handleBatchSubmit = (queries: string[]) => {
    sendHRMBatch(queries);
    toast.success(`Processing ${queries.length} queries...`);
  };

  // Keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && !hrm.isProcessing) {
        e.preventDefault();
        handleSubmit();
      }
    };
    
    const textarea = textareaRef.current;
    textarea?.addEventListener('keydown', handleKeyDown);
    return () => textarea?.removeEventListener('keydown', handleKeyDown);
  }, [query, hrm.isProcessing]);

  return (
    <div className="h-full flex flex-col p-4">
      <Tabs defaultValue="single" className="flex-1 flex flex-col">
        <TabsList className="mb-4">
          <TabsTrigger value="single">
            <Cpu className="w-4 h-4 mr-2" />
            Single Query
          </TabsTrigger>
          <TabsTrigger value="batch">
            <Package className="w-4 h-4 mr-2" />
            Batch Processing
          </TabsTrigger>
        </TabsList>

        <TabsContent value="single" className="flex-1 flex flex-col">
          {/* Query History */}
          <div className="flex-1 min-h-0 mb-4">
            <ScrollArea className="h-full pr-4">
              <AnimatePresence>
                {hrm.queryHistory.length > 0 ? (
                  hrm.queryHistory.map((result, index) => (
                    <HRMQueryResultCard 
                      key={`${result.query}-${index}`} 
                      result={result} 
                      index={index} 
                    />
                  ))
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground py-8">
                    <Brain className="w-12 h-12 mb-4" />
                    <h3 className="text-lg font-semibold">HRM Neural Reasoning</h3>
                    <p className="text-sm mb-4">
                      Ask logical queries to test the reasoning model
                    </p>
                    <div className="text-xs space-y-1">
                      <p>Model: SimplifiedHRMModel (572K params)</p>
                      <p>Confidence Gap: {(hrm.metrics.confidenceGap * 100).toFixed(1)}%</p>
                      <p>Device: {hrm.metrics.device}</p>
                    </div>
                  </div>
                )}
              </AnimatePresence>
            </ScrollArea>
          </div>

          {/* Query Input */}
          <div className="space-y-3">
            {/* Example Queries */}
            <div className="flex flex-wrap gap-2">
              {exampleQueries.map((example, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  onClick={() => handleExample(example)}
                >
                  {example}
                </Button>
              ))}
            </div>

            {/* Input Area */}
            <div className="relative">
              <Textarea
                ref={textareaRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter a logical query (e.g., IsA(Socrates, Philosopher))"
                className="pr-20 font-mono"
                disabled={hrm.isProcessing}
              />
              <Button
                onClick={handleSubmit}
                className="absolute right-2 bottom-2"
                size="sm"
                disabled={hrm.isProcessing || !query.trim()}
              >
                {hrm.isProcessing ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Press Ctrl+Enter to submit • Target response time: &lt;10ms
            </p>
          </div>
        </TabsContent>

        <TabsContent value="batch" className="flex-1 flex flex-col">
          <div className="flex-1 min-h-0 mb-4">
            <ScrollArea className="h-full pr-4">
              {hrm.batchHistory.length > 0 ? (
                <div className="space-y-4">
                  {hrm.batchHistory.map((batch, idx) => (
                    <Card key={idx} className="border-0 bg-card/50">
                      <CardHeader>
                        <CardTitle className="text-sm flex items-center justify-between">
                          <span>Batch #{hrm.batchHistory.length - idx}</span>
                          <Badge variant="outline">
                            {batch.results.length} queries
                          </Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                          <div>
                            <span className="text-xs text-muted-foreground">Avg Confidence:</span>
                            <p className="font-bold">
                              {(batch.statistics.avgConfidence * 100).toFixed(1)}%
                            </p>
                          </div>
                          <div>
                            <span className="text-xs text-muted-foreground">Processing Time:</span>
                            <p className="font-bold">
                              {batch.statistics.processingTime.toFixed(0)}ms
                            </p>
                          </div>
                          <div>
                            <span className="text-xs text-muted-foreground">High Confidence:</span>
                            <p className="font-bold text-green-500">
                              {batch.statistics.highConfidenceCount}
                            </p>
                          </div>
                          <div>
                            <span className="text-xs text-muted-foreground">Low Confidence:</span>
                            <p className="font-bold text-red-500">
                              {batch.statistics.lowConfidenceCount}
                            </p>
                          </div>
                        </div>
                        <div className="space-y-1">
                          {batch.results.slice(0, 5).map((r, i) => (
                            <div key={i} className="flex items-center justify-between text-xs">
                              <span className="font-mono truncate flex-1">{r.query}</span>
                              <Badge 
                                variant="outline" 
                                className={r.confidence > 0.7 ? 'text-green-500' : r.confidence < 0.3 ? 'text-red-500' : ''}
                              >
                                {(r.confidence * 100).toFixed(0)}%
                              </Badge>
                            </div>
                          ))}
                          {batch.results.length > 5 && (
                            <p className="text-xs text-muted-foreground">
                              +{batch.results.length - 5} more...
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground py-8">
                  <Package className="w-12 h-12 mb-4" />
                  <h3 className="text-lg font-semibold">Batch Processing</h3>
                  <p className="text-sm">
                    Process multiple queries at once for efficiency
                  </p>
                </div>
              )}
            </ScrollArea>
          </div>
          
          <BatchQueryInput onSubmit={handleBatchSubmit} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default HRMQueryInterface;
