// Enhanced Unified Query Interface with Deep LLM Explanation and Fact Confirmation
// Implements human-in-the-loop learning system - FIXED VERSION WITH VISIBLE FACT BUTTONS

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useHRMStore } from '@/stores/useHRMStore';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, Loader2, Brain, Cpu, Zap, Bot, Database,
  ArrowRight, ChevronDown, ChevronUp, CheckCircle2,
  BookOpen, Shield, Plus, AlertCircle, Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import TrustScoreCard, { TrustBadge, TrustComponents } from '@/components/TrustScoreCard';
import { getActiveBackend } from '@/config/backends';

interface QueryResult {
  id: string;
  query: string;
  timestamp: string;
  hrmConfidence?: number;
  hrmReasoning?: string[];
  searchResponse?: string;
  llmExplanation?: string;
  extractedFacts?: string[];
  suggestedFacts?: Array<{
    fact: string;
    confidence: number;
    source: string;
  }>;
  status: 'pending' | 'processing' | 'complete' | 'error';
  trustComponents?: TrustComponents;
  humanVerified?: boolean;
}

const UnifiedQueryInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<QueryResult[]>([]);
  const [showDetails, setShowDetails] = useState<Record<string, boolean>>({});
  const [confirmingFacts, setConfirmingFacts] = useState<Record<string, boolean>>({});
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const activeBackend = getActiveBackend();
  const baseUrl = activeBackend.apiUrl;
  const isHex = /5001/.test(baseUrl) || /hex/i.test(activeBackend?.name || '');

  const reasonUrl = () => `${baseUrl}/api/reason`;

  const normalizeExplanation = (data: any): string => (
    data?.explanation ??
    data?.result?.explanation ??
    data?.chatResponse?.natural_language_explanation ??
    data?.response ??
    data?.answer ??
    ''
  );

  const logicalizeWithFallback = async (text: string): Promise<string[]> => {
    if (!text || !text.trim()) return [];
    // 1) try active backend
    try {
      const r1 = await fetch(`${baseUrl}/api/logicalize`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      if (r1.ok) {
        const d = await r1.json();
        if (Array.isArray(d.facts)) return d.facts as string[];
      }
    } catch {}
    // 2) fallback to original
      try {
        const r2 = await fetch(`${baseUrl}/api/logicalize`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
        if (r2.ok) {
          const d = await r2.json();
          if (Array.isArray(d.facts)) return d.facts as string[];
        }
      } catch {}
    return [];
  };
  
  // Example queries
  const exampleQueries = [
    "IsA(Socrates, Philosopher)",
    "HasPart(Computer, CPU)",
    "What is machine learning?",
    "Explain the HAK/GAL paradigm",
    "How does neural reasoning work?",
    "What is the relationship between AI and consciousness?"
  ];
  
  const handleSubmit = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }
    
    const queryId = `query-${Date.now()}`;
    console.log('Submitting query:', query);
    
    // Create new result
    const newResult: QueryResult = {
      id: queryId,
      query: query.trim(),
      timestamp: new Date().toISOString(),
      status: 'pending'
    };
    
    setResults(prev => [newResult, ...prev.slice(0, 9)]); // Keep last 10
    setIsProcessing(true);
    
    try {
      // 1. Send to HRM for FAST neural reasoning (should be <10ms)
      console.log('Step 1: HRM Neural Reasoning...');
      const hrmStartTime = Date.now();
      
      try {
        const hrmResponse = await fetch(reasonUrl(), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: query.trim() })
        });
        
        if (hrmResponse.ok) {
          const hrmData = await hrmResponse.json();
          const hrmTime = Date.now() - hrmStartTime;
          console.log(`HRM Response in ${hrmTime}ms:`, hrmData);
          
          // Update with HRM result IMMEDIATELY
          setResults(prev => prev.map(r => 
            r.id === queryId 
              ? {
                  ...r,
                  hrmConfidence: hrmData.confidence || 0,
                  hrmReasoning: hrmData.reasoning_terms || [],
                  status: 'processing'
                }
              : r
          ));
        }
      } catch (hrmError) {
        console.error('HRM Error:', hrmError);
      }
      
      // 2. Search for relevant facts in knowledge base
      console.log('Step 2: Searching knowledge base...');
      const searchStartTime = Date.now();
      let searchOk = false;
      let searchData: any = {};
      let extractedFacts: string[] = [];
      try {
        const respHex = await fetch(`${baseUrl}/api/search`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: query.trim(), limit: 10 })
        });
        if (respHex.ok) {
          const d = await respHex.json();
          searchData = d;
          if (Array.isArray(d.results)) {
            extractedFacts = d.results.map((r: any) => r?.statement).filter(Boolean);
          }
          searchOk = true;
        }
      } catch {}
      
      const searchTime = Date.now() - searchStartTime;
      console.log(`Search completed in ${searchTime}ms`);
      
      if (searchOk) {
        console.log('Search Response:', searchData);
        if (searchData.chatResponse?.relevant_facts) {
          extractedFacts = searchData.chatResponse.relevant_facts;
        }
        const searchText = (
          searchData.chatResponse?.natural_language_explanation ||
          searchData.chatResponse?.symbolic_response ||
          (Array.isArray(extractedFacts) && extractedFacts.length > 0 ? `${extractedFacts.length} facts found` : 'No relevant facts found')
        );
        setResults(prev => prev.map(r => (
          r.id === queryId ? { ...r, searchResponse: searchText, extractedFacts, status: 'processing' } : r
        )));
      }
      
      // 3. Get deep LLM explanation
      console.log('Step 3: Requesting deep LLM explanation...');
      const llmStartTime = Date.now();
      
      try {
        // Prefer Hex explanation proxy
        let llmData: any = null;
        let ok = false;
        try {
          const proxyResp = await fetch(`${baseUrl}/api/llm/get-explanation`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: query.trim(), context_facts: extractedFacts })
          });
          if (proxyResp.ok) { 
            llmData = await proxyResp.json(); 
            ok = true; 
          }
        } catch {}

        const llmTime = Date.now() - llmStartTime;
        console.log(`LLM Explanation generated in ${llmTime}ms`);
        
        if (ok && llmData) {
          console.log('LLM Response data:', llmData);
          
          // Extract suggested facts from various possible locations
          let suggestedFacts = llmData.suggested_facts || 
                               llmData.chatResponse?.suggested_facts || 
                               parseSuggestedFacts(llmData, query.trim());
          
          console.log('Raw suggested facts:', suggestedFacts);

          // Normalize to array of objects
          if (Array.isArray(suggestedFacts)) {
            suggestedFacts = suggestedFacts
              .filter((f: any) => f && (typeof f === 'string' || (typeof f === 'object' && f.fact)))
              .slice(0, 20)  // Cap at 20
              .map((f: any) => {
                if (typeof f === 'string') {
                  const fact = f.trim();
                  return {
                    fact: fact.endsWith('.') ? fact : fact + '.',
                    confidence: 0.7,
                    source: 'LLM'
                  };
                }
                return {
                  fact: f.fact.endsWith('.') ? f.fact : f.fact + '.',
                  confidence: f.confidence || 0.7,
                  source: f.source || 'LLM'
                };
              });
            
            console.log('Normalized suggested facts:', suggestedFacts);
          } else {
            suggestedFacts = [];
          }

          // If still no suggestions, try to extract from explanation text
          if (suggestedFacts.length === 0) {
            const explanationText = normalizeExplanation(llmData);
            console.log('No suggested facts found, extracting from explanation...');
            
            // Look for patterns like Predicate(Entity1, Entity2)
            const factPatterns = explanationText.match(/\b[A-Z]\w*\([^)]+\)/g) || [];
            console.log('Found patterns:', factPatterns);
            
            if (factPatterns.length > 0) {
              suggestedFacts = factPatterns
                .slice(0, 10)
                .map(fact => ({
                  fact: fact.endsWith('.') ? fact : fact + '.',
                  confidence: 0.6,
                  source: 'Extracted'
                }));
            }
            
            // Also check if the original query is a valid fact
            if (query.trim().match(/^\w+\([^)]+\)$/)) {
              suggestedFacts.unshift({
                fact: query.trim().endsWith('.') ? query.trim() : query.trim() + '.',
                confidence: 0.8,
                source: 'User Query'
              });
            }
          }
          
          // Calculate trust components
          const currentResult = results.find(r => r.id === queryId);
          const trustComponents: TrustComponents = {
            neuralConfidence: currentResult?.hrmConfidence || 0.5,
            factualAccuracy: extractedFacts.length > 0 ? 0.8 : 0.3,
            sourceQuality: extractedFacts.length > 0 ? (extractedFacts.length / 10) : 0.1,
            consensus: llmData.chatResponse ? 0.75 : 0.5,
            humanVerified: false,
            ethicalAlignment: 0.7
          };
          
          // Update with full explanation and suggested facts
          setResults(prev => prev.map(r => 
            r.id === queryId 
              ? {
                  ...r,
                  llmExplanation: normalizeExplanation(llmData) || 'Unable to generate explanation',
                  suggestedFacts: suggestedFacts,
                  trustComponents: trustComponents,
                  status: 'complete'
                }
              : r
          ));
          
          console.log('Final result with suggested facts:', {
            id: queryId,
            suggestedFactsCount: suggestedFacts.length,
            suggestedFacts
          });
        }
      } catch (llmError) {
        console.error('LLM Error:', llmError);
        setResults(prev => prev.map(r => 
          r.id === queryId 
            ? { ...r, status: 'complete' }
            : r
        ));
      }
      
    } catch (error) {
      console.error('Request Error:', error);
      setResults(prev => prev.map(r => 
        r.id === queryId 
          ? { ...r, status: 'error' }
          : r
      ));
    } finally {
      setIsProcessing(false);
    }
    
    setQuery('');
  };
  
  // Parse suggested facts from LLM response
  const parseSuggestedFacts = (llmData: any, originalQuery: string) => {
    const suggested = [];
    const text = normalizeExplanation(llmData);
    
    console.log('Parsing facts from text:', text.substring(0, 200));
    
    // Look for logical statements in the response
    const factPatterns = text.match(/\b[A-Z]\w*\([^)]+\)/g) || [];
    
    console.log('Found fact patterns:', factPatterns);
    
    // If the query itself is a valid fact format, suggest it
    if (originalQuery.match(/^\w+\([^)]+\)$/)) {
      const factWithPeriod = originalQuery.endsWith('.') ? originalQuery : originalQuery + '.';
      suggested.push({
        fact: factWithPeriod,
        confidence: 0.8,
        source: 'User Query'
      });
    }
    
    // Add extracted patterns as suggestions
    factPatterns.forEach((fact: string) => {
      const factWithPeriod = fact.endsWith('.') ? fact : fact + '.';
      if (!suggested.some(s => s.fact === factWithPeriod)) {
        suggested.push({
          fact: factWithPeriod,
          confidence: 0.6,
          source: 'Extracted'
        });
      }
    });
    
    return suggested.slice(0, 20); // Max 20 suggestions
  };
  
  // Confirm and add fact to knowledge base
  const confirmFact = async (resultId: string, fact: string) => {
    const key = `${resultId}-${fact}`;
    setConfirmingFacts(prev => ({ ...prev, [key]: true }));
    
    try {
      let ok = false;
      let alreadyExists = false;
      
      if (isHex) {
        // Hex: native add fact endpoint
        try {
          const respHex = await fetch(`${baseUrl}/api/facts`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ statement: fact, context: { source: 'human_verified' } })
          });
          if (respHex.status === 201 || respHex.status === 200) {
            ok = true;
          } else if (respHex.status === 409) {
            alreadyExists = true;
            toast.info('Fact already exists in knowledge base');
          } else {
            const err = await respHex.json().catch(() => ({}));
            toast.error(err?.error || err?.message || 'Failed to add fact');
          }
        } catch (e) {
          console.error('Error adding fact:', e);
        }
      }
      
      if (!ok && !alreadyExists) {
        const response = await fetch(`${baseUrl}/api/command`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            command: 'add_fact',
            query: fact,
            context: {
              source: 'human_verified',
              timestamp: new Date().toISOString(),
              original_query: results.find(r => r.id === resultId)?.query
            }
          })
        });
        
        if (response.status === 201 || response.status === 200) {
          ok = true;
        } else if (response.status === 409) {
          alreadyExists = true;
          toast.info('Fact already exists in knowledge base');
        } else {
          const err = await response.json().catch(() => ({}));
          toast.error(err?.error || err?.message || 'Failed to add fact');
        }
      }
      
      if (ok || alreadyExists) {
        if (ok) {
          toast.success(`Fact added: ${fact}`);
        }
        
        // Remove from suggested facts
        setResults(prev => prev.map(r => 
          r.id === resultId 
            ? {
                ...r,
                suggestedFacts: r.suggestedFacts?.filter(s => s.fact !== fact)
              }
            : r
        ));
      }
    } catch (error) {
      console.error('Error adding fact:', error);
      toast.error('Error adding fact to knowledge base');
    } finally {
      setConfirmingFacts(prev => ({ ...prev, [key]: false }));
    }
  };
  
  const toggleDetails = (id: string) => {
    setShowDetails(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };
  
  // Keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && !isProcessing) {
        e.preventDefault();
        handleSubmit();
      }
    };
    
    const textarea = textareaRef.current;
    textarea?.addEventListener('keydown', handleKeyDown);
    return () => textarea?.removeEventListener('keydown', handleKeyDown);
  }, [query, isProcessing]);
  
  return (
    <div className="h-full flex flex-col p-4">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-3 mb-2">
          <Brain className="w-6 h-6 text-primary" />
          <h2 className="text-xl font-bold">Unified Intelligence Query</h2>
          <Badge variant="outline">Human-in-the-Loop Learning</Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          Neural reasoning + Knowledge search + Deep explanation + Human verification
        </p>
      </div>
      
      {/* Results */}
      <div className="flex-1 min-h-0 mb-4">
        <ScrollArea className="h-full">
          {results.length === 0 ? (
            <div className="h-full flex items-center justify-center text-center py-8">
              <div className="max-w-md">
                <Brain className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">Intelligent Learning System</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Combines multiple intelligence layers with human verification
                </p>
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div className="flex flex-col items-center p-3 border rounded-lg">
                    <Cpu className="w-8 h-8 mb-2 text-blue-500" />
                    <span className="font-medium">Neural Logic</span>
                    <span className="text-muted-foreground">&lt;10ms reasoning</span>
                  </div>
                  <div className="flex flex-col items-center p-3 border rounded-lg">
                    <Database className="w-8 h-8 mb-2 text-green-500" />
                    <span className="font-medium">Knowledge Search</span>
                    <span className="text-muted-foreground">1,230 facts</span>
                  </div>
                  <div className="flex flex-col items-center p-3 border rounded-lg">
                    <BookOpen className="w-8 h-8 mb-2 text-purple-500" />
                    <span className="font-medium">Deep Explanation</span>
                    <span className="text-muted-foreground">LLM analysis</span>
                  </div>
                  <div className="flex flex-col items-center p-3 border rounded-lg">
                    <Shield className="w-8 h-8 mb-2 text-orange-500" />
                    <span className="font-medium">Human Verification</span>
                    <span className="text-muted-foreground">Confirm facts</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <AnimatePresence>
              {results.map((result, index) => (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="mb-4"
                >
                  <Card>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium">{result.query}</CardTitle>
                        <div className="flex items-center gap-2">
                          <Badge variant={
                            result.status === 'complete' ? 'default' :
                            result.status === 'error' ? 'destructive' :
                            'outline'
                          }>
                            {result.status}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => toggleDetails(result.id)}
                          >
                            {showDetails[result.id] ? 
                              <ChevronUp className="h-3 w-3" /> : 
                              <ChevronDown className="h-3 w-3" />
                            }
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      {/* Trust Score Card - Show when we have trust components */}
                      {result.trustComponents && (
                        <div className="mb-4">
                          <TrustScoreCard
                            query={result.query}
                            response={result.llmExplanation || result.searchResponse || 'Processing...'}
                            components={result.trustComponents}
                            sources={result.extractedFacts?.map((fact, idx) => ({
                              fact,
                              confidence: 0.8,
                              id: `fact-${idx}`
                            }))}
                            onVerify={() => {
                              setResults(prev => prev.map(r => 
                                r.id === result.id 
                                  ? {
                                      ...r,
                                      humanVerified: true,
                                      trustComponents: r.trustComponents ? {
                                        ...r.trustComponents,
                                        humanVerified: true
                                      } : undefined
                                    }
                                  : r
                              ));
                              toast.success('Response verified by human');
                            }}
                          />
                        </div>
                      )}
                      
                      {/* Quick Summary */}
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        {/* HRM Confidence */}
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
                            <Cpu className="w-3 h-3" />
                            Neural Confidence
                          </div>
                          {result.hrmConfidence !== undefined ? (
                            <div className="space-y-1">
                              <Progress 
                                value={result.hrmConfidence * 100} 
                                className="h-2"
                              />
                              <div className="flex items-center justify-between text-xs">
                                <span>{(result.hrmConfidence * 100).toFixed(1)}%</span>
                                <Badge variant={result.hrmConfidence > 0.7 ? "default" : "secondary"}>
                                  {result.hrmConfidence > 0.7 ? "HIGH" : "LOW"}
                                </Badge>
                              </div>
                            </div>
                          ) : (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          )}
                        </div>
                        
                        {/* Found Facts */}
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
                            <Database className="w-3 h-3" />
                            Knowledge Base
                          </div>
                          {result.extractedFacts ? (
                            <div className="text-xs">
                              <span className="font-medium">{result.extractedFacts.length}</span> facts found
                              {result.extractedFacts.length > 0 && (
                                <div className="text-muted-foreground mt-1">
                                  {result.searchResponse?.split('.')[0]}
                                </div>
                              )}
                            </div>
                          ) : (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          )}
                        </div>
                        
                        {/* LLM Status */}
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
                            <BookOpen className="w-3 h-3" />
                            Deep Analysis
                          </div>
                          {result.llmExplanation ? (
                            <Badge variant="outline" className="text-xs">
                              <CheckCircle2 className="w-3 h-3 mr-1" />
                              Complete
                            </Badge>
                          ) : result.status === 'processing' ? (
                            <div className="flex items-center gap-1 text-xs">
                              <Loader2 className="w-3 h-3 animate-spin" />
                              Generating...
                            </div>
                          ) : (
                            <span className="text-xs text-muted-foreground">Pending</span>
                          )}
                        </div>
                      </div>
                      
                      {/* IMPORTANT: Suggested Facts for Confirmation - ALWAYS SHOW IF AVAILABLE */}
                      {result.suggestedFacts && result.suggestedFacts.length > 0 && (
                        <Alert className="mb-4 border-primary/50 bg-primary/5">
                          <Sparkles className="w-4 h-4 text-primary" />
                          <AlertDescription>
                            <div className="flex items-center justify-between mb-3">
                              <span className="font-semibold text-sm">
                                🎯 Suggested Facts to Add ({result.suggestedFacts.length})
                              </span>
                              <Badge variant="default" className="text-xs">
                                Click to Add
                              </Badge>
                            </div>
                            <div className="space-y-2 max-h-[300px] overflow-y-auto">
                              {result.suggestedFacts.map((suggestion, idx) => (
                                <div 
                                  key={idx} 
                                  className="flex items-center justify-between p-3 bg-background/80 rounded-lg border hover:border-primary/50 transition-colors"
                                >
                                  <div className="flex-1 pr-2">
                                    <code className="text-sm font-mono text-primary">
                                      {suggestion.fact}
                                    </code>
                                    <div className="flex items-center gap-2 mt-1">
                                      <Badge variant="secondary" className="text-xs">
                                        {(suggestion.confidence * 100).toFixed(0)}% confidence
                                      </Badge>
                                      <span className="text-xs text-muted-foreground">
                                        from {suggestion.source}
                                      </span>
                                    </div>
                                  </div>
                                  <Button
                                    size="sm"
                                    variant="default"
                                    className="ml-2 min-w-[100px]"
                                    disabled={confirmingFacts[`${result.id}-${suggestion.fact}`]}
                                    onClick={() => confirmFact(result.id, suggestion.fact)}
                                  >
                                    {confirmingFacts[`${result.id}-${suggestion.fact}`] ? (
                                      <Loader2 className="w-3 h-3 animate-spin" />
                                    ) : (
                                      <>
                                        <Plus className="w-3 h-3 mr-1" />
                                        Add Fact
                                      </>
                                    )}
                                  </Button>
                                </div>
                              ))}
                            </div>
                          </AlertDescription>
                        </Alert>
                      )}
                      
                      {/* Deep LLM Explanation - ALWAYS VISIBLE */}
                      {result.llmExplanation && (
                        <div className="mt-4 p-4 bg-gradient-to-br from-purple-950/10 to-background border border-purple-500/20 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <BookOpen className="w-4 h-4 text-purple-500" />
                            <span className="font-medium text-sm">Deep Analysis & Explanation</span>
                            <Badge variant="outline" className="text-xs ml-auto">
                              LLM Analysis
                            </Badge>
                          </div>
                          <div className="prose prose-sm dark:prose-invert max-w-none">
                            <p className="text-sm whitespace-pre-wrap leading-relaxed">
                              {result.llmExplanation}
                            </p>
                          </div>
                        </div>
                      )}
                      
                      {/* Detailed View */}
                      {showDetails[result.id] && (
                        <div className="mt-4 pt-4 border-t space-y-4">
                          {/* HRM Reasoning */}
                          {result.hrmReasoning && result.hrmReasoning.length > 0 && (
                            <div>
                              <span className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                                <Cpu className="w-3 h-3" />
                                Neural Reasoning Terms
                              </span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {result.hrmReasoning.map((r, i) => (
                                  <Badge key={i} variant="outline" className="text-xs">
                                    {r}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* Found Facts */}
                          {result.extractedFacts && result.extractedFacts.length > 0 && (
                            <div>
                              <span className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                                <Database className="w-3 h-3" />
                                Facts from Knowledge Base
                              </span>
                              <div className="space-y-1 mt-1">
                                {result.extractedFacts.map((fact, i) => (
                                  <div key={i} className="flex items-center gap-2">
                                    <ArrowRight className="w-3 h-3 text-muted-foreground" />
                                    <code className="text-xs font-mono">{fact}</code>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </ScrollArea>
      </div>
      
      {/* Input */}
      <div className="space-y-3">
        {/* Examples */}
        <div className="flex flex-wrap gap-2">
          {exampleQueries.map((example, idx) => (
            <Button
              key={idx}
              variant="outline"
              size="sm"
              className="text-xs"
              onClick={() => {
                setQuery(example);
                textareaRef.current?.focus();
              }}
            >
              {example}
            </Button>
          ))}
        </div>
        
        {/* Query Input */}
        <div className="relative">
          <Textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything... Get neural validation + knowledge search + deep explanation"
            className="pr-20"
            disabled={isProcessing}
          />
          <Button
            onClick={handleSubmit}
            className="absolute right-2 bottom-2"
            size="sm"
            disabled={isProcessing || !query.trim()}
          >
            {isProcessing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
        
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Press Ctrl+Enter to submit</span>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Cpu className="w-3 h-3" />
              HRM: &lt;10ms
            </span>
            <span className="flex items-center gap-1">
              <Database className="w-3 h-3" />
              Search: ~30ms
            </span>
            <span className="flex items-center gap-1">
              <BookOpen className="w-3 h-3" />
              LLM: ~5s
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnifiedQueryInterface;
