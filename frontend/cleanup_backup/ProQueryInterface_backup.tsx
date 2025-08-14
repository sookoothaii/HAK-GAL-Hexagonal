// V2 - Simplified, Real-Data Driven
import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useGovernorStore, QueryResponse } from '@/stores/useGovernorStore';
import { useGovernorSocket } from '@/hooks/useGovernorSocket';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, Brain, Terminal, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';

// Simplified Query Result Card
const QueryResultCard: React.FC<{ result: QueryResponse; index: number }> = ({ result, index }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Response copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group"
    >
      <div className="mb-4">
        <p className="font-semibold text-sm mb-2 text-primary">
          <span className="font-mono mr-2">&gt;</span>{result.query}
        </p>
        <Card className="border-0 bg-card/50">
          <CardContent className="p-4">
            {result.status === 'pending' ? (
              <div className="flex items-center text-muted-foreground">
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">Symbolic Response</h4>
                  <div className="relative p-3 rounded bg-muted/50 font-mono text-xs">
                    <pre className="whitespace-pre-wrap">{result.symbolicResponse}</pre>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute top-1 right-1 h-6 w-6"
                      onClick={() => handleCopy(result.symbolicResponse)}
                    >
                      {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    </Button>
                  </div>
                </div>
                {result.naturalLanguageExplanation && (
                  <div>
                    <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">LLM Explanation</h4>
                    <p className="text-sm">{result.naturalLanguageExplanation}</p>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
};

// Main Query Interface
const ProQueryInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const wsService = useGovernorSocket();
  const queryHistory = useGovernorStore(state => state.queryHistory);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!query.trim()) {
      toast.error('Please enter a query.');
      return;
    }
    // The command is now hardcoded to 'ask' for simplicity, can be expanded later
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
      <div className="flex-1 flex flex-col min-h-0">
        <ScrollArea className="flex-1 pr-4">
          <AnimatePresence>
            {queryHistory.length > 0 ? (
              queryHistory.map((result, index) => (
                <QueryResultCard key={result.id} result={result} index={index} />
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground">
                <Brain className="w-12 h-12 mb-4" />
                <h3 className="text-lg font-semibold">Query Interface</h3>
                <p className="text-sm">Ask questions to the knowledge base.</p>
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
      </div>
    </div>
  );
};

export default ProQueryInterface;
