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
import { useGovernorStore } from '@/stores/useGovernorStore';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, Loader2, Brain, Cpu, Zap, Bot, Database,
  ArrowRight, ChevronDown, ChevronUp, CheckCircle2,
  BookOpen, Shield, Plus, AlertCircle, Sparkles,
  Microscope, Heart
} from 'lucide-react';
import { toast } from 'sonner';
import TrustScoreCard, { TrustBadge, TrustComponents } from '@/components/TrustScoreCard';
import { getApiBaseUrl, httpClient } from '@/services/api';
import llmClient from '@/services/llmService'; // Import the LLM client with extended timeout

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
  const [explanationMode, setExplanationMode] = useState<'simple' | 'scientific' | 'friendly'>('simple');
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const baseUrl = getApiBaseUrl();
  const isHex = true;
  
  const kbFactCount = useGovernorStore(state => state.kb.metrics.factCount);

  const reasonUrl = () => `${baseUrl}/api/reason`;

  const normalizeExplanation = (data: any): string => {
    console.log('Normalizing explanation from data:', data);
    const explanation = 
      data?.explanation ??
      data?.result?.explanation ??
      data?.chatResponse?.natural_language_explanation ??
      data?.response ??
      data?.answer ??
      data?.text ??
      data?.output ??
      data?.content ??
      '';
    console.log('Extracted explanation:', explanation ? explanation.substring(0, 100) + '...' : 'EMPTY');
    return explanation;
  };

  const logicalizeWithFallback = async (text: string): Promise<string[]> => {
    if (!text || !text.trim()) return [];
    try {
      const r1 = await httpClient.post(`/api/logicalize`, { text });
      if (r1.status === 200) {
        const d = r1.data;
        if (Array.isArray(d.facts)) return d.facts as string[];
      }
    } catch {}
      try {
        const r2 = await httpClient.post(`/api/logicalize`, { text });
        if (r2.status === 200) {
          const d = r2.data;
          if (Array.isArray(d.facts)) return d.facts as string[];
        }
      } catch {}
    return [];
  };
  
  const exampleQueries = [
    "IsA(Socrates, Philosopher).",
    "HasPart(Computer, CPU).",
    "What is machine learning?",
    "RelatesTo(HAK_GAL, NeurosymbolicAI).",
    "Explain quantum computing",
    "What is the relationship between AI and consciousness?"
  ];
  
  const handleSubmit = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }
    
    const queryId = `query-${Date.now()}`;
    console.log('Submitting query:', query);
    
    const newResult: QueryResult = {
      id: queryId,
      query: query.trim(),
      timestamp: new Date().toISOString(),
      status: 'pending'
    };
    
    setResults(prev => [newResult, ...prev.slice(0, 9)]);
    setIsProcessing(true);
    
    let storedHrmConfidence = 0.001;
    
    try {
      console.log('Step 1: HRM Neural Reasoning...');
      const hrmStartTime = Date.now();
      
      try {
        const hrmResponse = await httpClient.post(`/api/reason`, { query: query.trim() });
        if (hrmResponse.status === 200 || hrmResponse.data) {
          const hrmData = hrmResponse.data;
          const hrmTime = Date.now() - hrmStartTime;
          console.log(`HRM Response in ${hrmTime}ms:`, hrmData);
          storedHrmConfidence = Math.max(hrmData.confidence || 0.5, 0.5); // Minimum 50% confidence
          setResults(prev => prev.map(r => 
            r.id === queryId 
              ? { ...r, hrmConfidence: storedHrmConfidence, hrmReasoning: hrmData.reasoning_terms || [], status: 'processing' }
              : r
          ));
        }
      } catch (hrmError) {
        console.error('HRM Error:', hrmError);
      }
      
      console.log('Step 2: Searching knowledge base...');
      const searchStartTime = Date.now();
      let searchOk = false;
      let searchData: any = {};
      let extractedFacts: string[] = [];
      try {
        const respHex = await httpClient.post(`/api/search`, { query: query.trim(), limit: 10 });
        if (respHex.status === 200) {
          const d = respHex.data;
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
        if (searchData.chatResponse?.relevant_facts) {
          extractedFacts = searchData.chatResponse.relevant_facts;
        }
        const searchText = (searchData.chatResponse?.natural_language_explanation || searchData.chatResponse?.symbolic_response || (Array.isArray(extractedFacts) && extractedFacts.length > 0 ? `${extractedFacts.length} facts found` : 'No relevant facts found'));
        setResults(prev => prev.map(r => (r.id === queryId ? { ...r, searchResponse: searchText, extractedFacts, status: 'processing' } : r)));
      }
      
      console.log('Step 3: Requesting deep LLM explanation...');
      const llmStartTime = Date.now();
      
      try {
        let llmData: any = null;
        let ok = false;
        try {
          const proxyResp = await llmClient.getExplanation({ topic: query.trim(), context_facts: extractedFacts, hrm_confidence: storedHrmConfidence });
          if (proxyResp.status === 200) { 
            llmData = proxyResp.data; 
            ok = true; 
          }
        } catch {}

        const llmTime = Date.now() - llmStartTime;
        console.log(`LLM Explanation generated in ${llmTime}ms`);
        
        if (ok && llmData) {
          console.log('LLM Response data:', llmData);
          let suggestedFacts = llmData.suggested_facts || llmData.chatResponse?.suggested_facts || parseSuggestedFacts(llmData, query.trim());
          
          if (Array.isArray(suggestedFacts)) {
            suggestedFacts = suggestedFacts.filter((f: any) => f && (typeof f === 'string' || (typeof f === 'object' && f.fact))).slice(0, 20).map((f: any) => {
                if (typeof f === 'string') {
                  const fact = f.trim();
                  return { fact: fact.endsWith('.') ? fact : fact + '.', confidence: 0.7, source: 'LLM' };
                }
                return { fact: f.fact.endsWith('.') ? f.fact : f.fact + '.', confidence: f.confidence || 0.7, source: f.source || 'LLM' };
              });
          } else {
            suggestedFacts = [];
          }

          if (suggestedFacts.length === 0) {
            const explanationText = normalizeExplanation(llmData);
            console.log('No suggested facts found, extracting from explanation...');
            const factPatterns = explanationText.match(/\b[A-Z]\w*\([^)]+\)/g) || [];
            if (factPatterns.length > 0) {
              suggestedFacts = factPatterns.slice(0, 10).map(fact => ({ fact: fact.endsWith('.') ? fact : fact + '.', confidence: 0.6, source: 'Extracted' }));
            }
            if (query.trim().match(/^\w+\([^)]+\)$/)) {
              suggestedFacts.unshift({ fact: query.trim().endsWith('.') ? query.trim() : query.trim() + '.', confidence: 0.8, source: 'User Query' });
            }
          }
          
          // Check if this query was previously verified
          let isVerified = false;
          
          // First check localStorage as fallback
          const verifiedQueries = JSON.parse(localStorage.getItem('verifiedQueries') || '{}');
          if (verifiedQueries[query.trim()]) {
            isVerified = true;
            console.log('Query verified in localStorage');
          }
          
          // Then try backend check
          try {
            console.log('Checking if query is verified:', query.trim());
            const verifyCheckResponse = await httpClient.get(`/api/feedback/verified/${encodeURIComponent(query.trim())}`);
            console.log('Verify check response:', verifyCheckResponse.data);
            if (verifyCheckResponse.status === 200 && verifyCheckResponse.data.verified) {
              isVerified = true;
              // Also save to localStorage
              verifiedQueries[query.trim()] = true;
              localStorage.setItem('verifiedQueries', JSON.stringify(verifiedQueries));
              console.log('Query was previously verified!');
            }
          } catch (e) {
            console.error('Error checking verification status:', e);
            // Backend not available, rely on localStorage
          }
          
          // Calculate dynamic trust components based on actual data
          const factsUsedCount = llmData.context_facts_used || extractedFacts.length || 0;
          
          const trustComponents: TrustComponents = {
            neuralConfidence: llmData.trustComponents?.neuralConfidence || storedHrmConfidence,
            // Dynamic calculation based on facts found
            factualAccuracy: llmData.trustComponents?.factualAccuracy || Math.min(0.3 + (factsUsedCount * 0.15), 1.0), // 30% base + 15% per fact, max 100%
            sourceQuality: llmData.trustComponents?.sourceQuality || (factsUsedCount > 0 ? 0.7 : 0.1), // 70% if facts used, 10% otherwise
            consensus: llmData.trustComponents?.consensus || storedHrmConfidence, // Use actual model confidence
            humanVerified: isVerified,  // ALWAYS use our verified status, never the LLM's!
            ethicalAlignment: llmData.trustComponents?.ethicalAlignment || 0.7
          };
          
          // No need for boosts anymore - verified queries get 100% in TrustScoreCard
          if (isVerified) {
            console.log('Query is verified - will show 100% trust');
          }
          
          const extractedExplanation = normalizeExplanation(llmData) || 'Unable to generate explanation';
          console.log('Setting LLM explanation:', extractedExplanation.substring(0, 100) + '...');
          
          setResults(prev => prev.map(r => {
            if (r.id === queryId) {
              const updated = { 
                ...r, 
                llmExplanation: extractedExplanation, 
                suggestedFacts: suggestedFacts, 
                trustComponents: trustComponents, 
                status: 'complete',
                // 🔧 FIX: Add backend context facts for Trust Analysis
                contextFactsUsed: llmData.context_facts_used || 0,
                contextFacts: llmData.context_facts || []
              };
              console.log('Updated result:', updated);
              return updated;
            }
            return r;
          }));
        }
      } catch (llmError) {
        console.error('LLM Error:', llmError);
        setResults(prev => prev.map(r => r.id === queryId ? { ...r, status: 'complete' } : r));
      }
    } catch (error) {
      console.error('Request Error:', error);
      setResults(prev => prev.map(r => r.id === queryId ? { ...r, status: 'error' } : r));
    } finally {
      setIsProcessing(false);
    }
    setQuery('');
  };
  
  const parseSuggestedFacts = (llmData: any, originalQuery: string) => {
    const suggested = [];
    const text = normalizeExplanation(llmData);
    console.log('Parsing facts from text:', text.substring(0, 200));
    const factPatterns = text.match(/\b[A-Z]\w*\([^)]+\)/g) || [];
    console.log('Found fact patterns:', factPatterns);
    if (originalQuery.match(/^\w+\([^)]+\)$/)) {
      const factWithPeriod = originalQuery.endsWith('.') ? originalQuery : originalQuery + '.';
      suggested.push({ fact: factWithPeriod, confidence: 0.8, source: 'User Query' });
    }
    factPatterns.forEach((fact: string) => {
      const factWithPeriod = fact.endsWith('.') ? fact : fact + '.';
      if (!suggested.some(s => s.fact === factWithPeriod)) {
        suggested.push({ fact: factWithPeriod, confidence: 0.6, source: 'Extracted' });
      }
    });
    return suggested.slice(0, 20);
  };
  
  const confirmFact = async (resultId: string, fact: string) => {
    const key = `${resultId}-${fact}`;
    setConfirmingFacts(prev => ({ ...prev, [key]: true }));
    try {
      let ok = false;
      let alreadyExists = false;
      if (isHex) {
        try {
          const respHex = await httpClient.post(`/api/facts`, { statement: fact, context: { source: 'human_verified' } });
          if (respHex.status === 201 || respHex.status === 200) { ok = true; }
          else if (respHex.status === 409) { alreadyExists = true; toast.info('Fact already exists in knowledge base'); }
          else { const err = await respHex.json().catch(() => ({})); toast.error(err?.error || err?.message || 'Failed to add fact'); }
        } catch (e) { console.error('Error adding fact:', e); }
      }
      if (!ok && !alreadyExists) {
        const response = await httpClient.post(`/api/command`, { command: 'add_fact', query: fact, context: { source: 'human_verified', timestamp: new Date().toISOString(), original_query: results.find(r => r.id === resultId)?.query } });
        if (response.status === 201 || response.status === 200) { ok = true; }
        else if (response.status === 409) { alreadyExists = true; toast.info('Fact already exists in knowledge base'); }
        else { const err = response.data || {}; toast.error(err?.error || err?.message || 'Failed to add fact'); }
      }
      if (ok || alreadyExists) {
        if (ok) { toast.success(`Fact added: ${fact}`); }
        setResults(prev => prev.map(r => r.id === resultId ? { ...r, suggestedFacts: r.suggestedFacts?.filter(s => s.fact !== fact) } : r));
      }
    } catch (error) {
      console.error('Error adding fact:', error);
      toast.error('Error adding fact to knowledge base');
    } finally {
      setConfirmingFacts(prev => ({ ...prev, [key]: false }));
    }
  };
  
  const toggleDetails = (id: string) => {
    setShowDetails(prev => ({ ...prev, [id]: !prev[id] }));
  };
  
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
      <div className="mb-4">
        <div className="flex items-center gap-3 mb-2">
          <Brain className="w-6 h-6 text-primary" />
          <h2 className="text-xl font-bold">Unified Intelligence Query</h2>
          <Badge variant="outline">Human-in-the-Loop Learning</Badge>
        </div>
        <p className="text-sm text-muted-foreground">Neural reasoning + Knowledge search + Deep explanation + Human verification</p>
      </div>
      {results.length === 0 && (
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <Button variant={explanationMode === 'simple' ? 'default' : 'outline'} size="sm" className="text-xs" onClick={() => setExplanationMode('simple')}><Brain className="w-3 h-3 mr-1" />Simple</Button>
          <Button variant={explanationMode === 'scientific' ? 'default' : 'outline'} size="sm" className="text-xs" onClick={() => setExplanationMode('scientific')}><Microscope className="w-3 h-3 mr-1" />Scientific</Button>
          <Button variant={explanationMode === 'friendly' ? 'default' : 'outline'} size="sm" className="text-xs" onClick={() => setExplanationMode('friendly')}><Heart className="w-3 h-3 mr-1" />Friendly</Button>
        </div>
        <AnimatePresence mode="wait">
          <motion.div key={explanationMode} initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} transition={{ duration: 0.2 }}>
            {explanationMode === 'simple' && (<Alert className="border-blue-500/30 bg-blue-950/10"><Brain className="w-4 h-4" /><AlertDescription><div className="text-sm space-y-2"><p className="font-medium">🎯 Dual Query System - Bridging Neural and Symbolic AI</p><p className="text-xs text-muted-foreground">This interface combines <strong>neural reasoning</strong> (fast pattern matching) with <strong>symbolic knowledge</strong> (precise facts) to provide comprehensive answers. Ask questions in <strong>English</strong> - natural language or symbolic logic.</p><div className="grid grid-cols-2 gap-2 mt-2 text-xs"><div><strong>Symbolic queries:</strong> End with period (.)<br />Example: IsA(Python, Language).</div><div><strong>Natural queries:</strong> English<br />Example: What is Python?</div></div></div></AlertDescription></Alert>)}
            {explanationMode === 'scientific' && (<Alert className="border-primary/30 bg-primary/5"><Sparkles className="w-4 h-4" /><AlertDescription><div className="text-sm space-y-3"><p className="font-semibold">🧠 Neurosymbolic Dual Query Architecture</p><p className="text-xs leading-relaxed">This system implements a <strong>hybrid AI approach</strong> that unifies:</p><div className="grid grid-cols-2 gap-3 text-xs"><div className="p-2 bg-background/50 rounded"><strong className="text-blue-400">Neural Component:</strong><ul className="mt-1 space-y-0.5 text-[11px] text-muted-foreground"><li>• Sub-10ms pattern recognition</li><li>• Confidence scoring (0-1)</li><li>• Fuzzy concept matching</li></ul></div><div className="p-2 bg-background/50 rounded"><strong className="text-green-400">Symbolic Component:</strong><ul className="mt-1 space-y-0.5 text-[11px] text-muted-foreground"><li>• Precise fact retrieval</li><li>• Logic-based reasoning</li><li>• Triple store: (S, P, O)</li></ul></div></div><p className="text-[11px] text-muted-foreground italic">Query in any format: Natural language (English) or Symbolic logic Predicate(Subject, Object).</p></div></AlertDescription></Alert>)}
            {explanationMode === 'friendly' && (<Alert className="border-purple-500/20 bg-gradient-to-r from-purple-950/10 to-blue-950/10"><Zap className="w-4 h-4 text-purple-400" /><AlertDescription><div className="space-y-3"><div className="flex items-center justify-between"><p className="font-semibold text-sm">🌍 Universal Intelligence Interface</p><Badge variant="outline" className="text-xs">HAK-GAL v4</Badge></div><div className="text-xs space-y-2"><p>Ask questions naturally or symbolically - the system understands both!</p><div className="flex gap-2"><Badge variant="secondary" className="text-[10px]">🇬🇧 English only</Badge><Badge variant="outline" className="text-[10px]">Currently supports English queries</Badge></div><div className="bg-background/60 rounded p-2 space-y-1"><div className="flex items-center gap-2"><Brain className="w-3 h-3 text-blue-400" /><span className="text-[11px]"><strong>Natural:</strong> "What is artificial intelligence?"</span></div><div className="flex items-center gap-2"><Cpu className="w-3 h-3 text-green-400" /><span className="text-[11px]"><strong>Symbolic:</strong> "IsA(AI, Technology)." (note the period!)</span></div></div></div></div></AlertDescription></Alert>)}
          </motion.div>
        </AnimatePresence>
      </div>
      )}
      <div className="flex-1 min-h-0 mb-4">
        <ScrollArea className="h-full">
          {results.length === 0 ? (
            <div className="h-full flex items-center justify-center text-center py-8"><div className="max-w-md"><Brain className="w-12 h-12 mx-auto mb-4 text-muted-foreground" /><h3 className="text-lg font-semibold mb-2">Intelligent Learning System</h3><p className="text-sm text-muted-foreground mb-4">Combines multiple intelligence layers with human verification</p><div className="grid grid-cols-2 gap-4 text-xs"><div className="flex flex-col items-center p-3 border rounded-lg"><Cpu className="w-8 h-8 mb-2 text-blue-500" /><span className="font-medium">Neural Logic</span><span className="text-muted-foreground">&lt;10ms reasoning</span></div><div className="flex flex-col items-center p-3 border rounded-lg"><Database className="w-8 h-8 mb-2 text-green-500" /><span className="font-medium">Knowledge Search</span><span className="text-muted-foreground">{kbFactCount.toLocaleString()} facts</span></div><div className="flex flex-col items-center p-3 border rounded-lg"><BookOpen className="w-8 h-8 mb-2 text-purple-500" /><span className="font-medium">Deep Explanation</span><span className="text-muted-foreground">LLM analysis</span></div><div className="flex flex-col items-center p-3 border rounded-lg"><Shield className="w-8 h-8 mb-2 text-orange-500" /><span className="font-medium">Human Verification</span><span className="text-muted-foreground">Confirm facts</span></div></div></div></div>
          ) : (
            <AnimatePresence>
              {results.map((result, index) => (
                <motion.div key={result.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }} className="mb-4">
                  <Card>
                    <CardHeader className="pb-3"><div className="flex items-center justify-between"><CardTitle className="text-sm font-medium">{result.query}</CardTitle><div className="flex items-center gap-2"><Badge variant={result.status === 'complete' ? 'default' : result.status === 'error' ? 'destructive' : 'outline'}>{result.status}</Badge><Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => toggleDetails(result.id)}>{showDetails[result.id] ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}</Button></div></div></CardHeader>
                    <CardContent className="pt-0">
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
                            onVerify={async () => { 
                              const currentResult = results.find(r => r.id === result.id); 
                              if (!currentResult) return; 
                              
                              try { 
                                const response = await httpClient.post(`/api/feedback/verify`, { 
                                  query: currentResult.query 
                                }); 
                                
                                if (response.status === 200) { 
                                  toast.success('Response successfully verified and recorded!'); 
                                  
                                  // Save to localStorage immediately
                                  const verifiedQueries = JSON.parse(localStorage.getItem('verifiedQueries') || '{}');
                                  verifiedQueries[currentResult.query] = true;
                                  localStorage.setItem('verifiedQueries', JSON.stringify(verifiedQueries));
                                  console.log('Saved verification to localStorage:', currentResult.query);
                                  
                                  // Update trust components with humanVerified = true 
                                  setResults(prev => prev.map(r => { 
                                    if (r.id === result.id && r.trustComponents) { 
                                      const updatedComponents = { 
                                        ...r.trustComponents, 
                                        humanVerified: true
                                        // No need for boosts - verified = 100% trust
                                      }; 
                                      return { 
                                        ...r, 
                                        humanVerified: true, 
                                        trustComponents: updatedComponents 
                                      }; 
                                    } 
                                    return r; 
                                  })); 
                                } else { 
                                  toast.error(`Failed to verify response: ${response.status}`); 
                                } 
                              } catch (error) { 
                                console.error('Error verifying response:', error); 
                                toast.error('Error connecting to verification service.'); 
                              } 
                            }} 
                          />
                        </div>
                      )}
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="space-y-2"><div className="flex items-center gap-2 text-xs font-medium text-muted-foreground"><Cpu className="w-3 h-3" />Neural Confidence</div>{result.hrmConfidence !== undefined ? (<div className="space-y-1"><Progress value={result.hrmConfidence * 100} className="h-2" /><div className="flex items-center justify-between text-xs"><span>{(result.hrmConfidence * 100).toFixed(1)}%</span><Badge variant={result.hrmConfidence > 0.7 ? "default" : "secondary"}>{result.hrmConfidence > 0.7 ? "HIGH" : "LOW"}</Badge></div></div>) : (<Loader2 className="w-4 h-4 animate-spin" />)}</div>
                        <div className="space-y-2"><div className="flex items-center gap-2 text-xs font-medium text-muted-foreground"><Database className="w-3 h-3" />Knowledge Base</div>{result.contextFactsUsed || result.extractedFacts ? (<div className="text-xs"><span className="font-medium">{result.contextFactsUsed || result.extractedFacts?.length || 0}</span> facts used{(result.contextFactsUsed || result.extractedFacts?.length || 0) > 0 && (<><div className="text-muted-foreground mt-1">from {kbFactCount.toLocaleString()} total facts</div><div className="mt-2 max-h-32 overflow-y-auto border rounded p-2 bg-background/50"><div className="space-y-1">{(result.contextFacts || result.extractedFacts || []).map((fact, i) => (<div key={i} className="text-[11px] font-mono text-muted-foreground">• {fact}</div>))}</div></div></>)}</div>) : (<Loader2 className="w-4 h-4 animate-spin" />)}</div>
                        <div className="space-y-2"><div className="flex items-center gap-2 text-xs font-medium text-muted-foreground"><BookOpen className="w-3 h-3" />Deep Analysis</div>{result.llmExplanation ? (<Badge variant="outline" className="text-xs"><CheckCircle2 className="w-3 h-3 mr-1" />Complete</Badge>) : result.status === 'processing' ? (<div className="flex items-center gap-1 text-xs"><Loader2 className="w-3 h-3 animate-spin" />Generating...</div>) : (<span className="text-xs text-muted-foreground">Pending</span>)}</div>
                      </div>
                      {result.suggestedFacts && result.suggestedFacts.length > 0 && (<Alert className="mb-4 border-primary/50 bg-primary/5"><Sparkles className="w-4 h-4 text-primary" /><AlertDescription><div className="flex items-center justify-between mb-3"><span className="font-semibold text-sm">🎯 Suggested Facts to Add ({result.suggestedFacts.length})</span><Badge variant="default" className="text-xs">Click to Add</Badge></div><div className="space-y-2 max-h-[300px] overflow-y-auto">{result.suggestedFacts.map((suggestion, idx) => (<div key={idx} className="flex items-center justify-between p-3 bg-background/80 rounded-lg border hover:border-primary/50 transition-colors"><div className="flex-1 pr-2"><code className="text-sm font-mono text-primary">{suggestion.fact}</code><div className="flex items-center gap-2 mt-1"><Badge variant="secondary" className="text-xs">{(suggestion.confidence * 100).toFixed(0)}% confidence</Badge><span className="text-xs text-muted-foreground">from {suggestion.source}</span></div></div><Button size="sm" variant="default" className="ml-2 min-w-[100px]" disabled={confirmingFacts[`${result.id}-${suggestion.fact}`]} onClick={() => confirmFact(result.id, suggestion.fact)}>{confirmingFacts[`${result.id}-${suggestion.fact}`] ? (<Loader2 className="w-3 h-3 animate-spin" />) : (<><Plus className="w-3 h-3 mr-1" />Add Fact</>)}</Button></div>))}</div></AlertDescription></Alert>)}
                      {(result.llmExplanation && result.llmExplanation.trim() !== '') && (<><div className="mt-4 p-4 bg-gradient-to-br from-purple-950/10 to-background border border-purple-500/20 rounded-lg"><div className="flex items-center gap-2 mb-2"><BookOpen className="w-4 h-4 text-purple-500" /><span className="font-medium text-sm">Deep Analysis & Explanation</span><Badge variant="outline" className="text-xs ml-auto">LLM Analysis</Badge></div><div className="prose prose-sm dark:prose-invert max-w-none"><p className="text-sm whitespace-pre-wrap leading-relaxed">{result.llmExplanation}</p></div></div></>)}
                      {showDetails[result.id] && (<div className="mt-4 pt-4 border-t space-y-4">{result.hrmReasoning && result.hrmReasoning.length > 0 && (<div><span className="text-xs font-medium text-muted-foreground flex items-center gap-1"><Cpu className="w-3 h-3" />Neural Reasoning Terms</span><div className="flex flex-wrap gap-1 mt-1">{result.hrmReasoning.map((r, i) => (<Badge key={i} variant="outline" className="text-xs">{r}</Badge>))}</div></div>)}{result.extractedFacts && result.extractedFacts.length > 0 && (<div><span className="text-xs font-medium text-muted-foreground flex items-center gap-1"><Database className="w-3 h-3" />Facts from Knowledge Base</span><div className="space-y-1 mt-1">{result.extractedFacts.map((fact, i) => (<div key={i} className="flex items-center gap-2"><ArrowRight className="w-3 h-3 text-muted-foreground" /><code className="text-xs font-mono">{fact}</code></div>))}</div></div>)}</div>)}
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </ScrollArea>
      </div>
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {exampleQueries.map((example, idx) => (<Button key={idx} variant="outline" size="sm" className="text-xs" onClick={() => { setQuery(example); textareaRef.current?.focus(); }}>{example}</Button>))}
        </div>
        <div className="relative"><Textarea ref={textareaRef} value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask in English: 'What is AI?' or 'IsA(AI, Technology).' (symbolic queries end with period)" className="pr-20" disabled={isProcessing} /><Button onClick={handleSubmit} className="absolute right-2 bottom-2" size="sm" disabled={isProcessing || !query.trim()}>{isProcessing ? (<Loader2 className="w-4 h-4 animate-spin" />) : (<Send className="w-4 h-4" />)}</Button></div>
        <div className="flex items-center justify-between text-xs text-muted-foreground"><span>Press Ctrl+Enter to submit</span><div className="flex items-center gap-4"><span className="flex items-center gap-1"><Database className="w-3 h-3" />KB: {kbFactCount.toLocaleString()} facts</span><span className="flex items-center gap-1"><Cpu className="w-3 h-3" />HRM: &lt;10ms</span><span className="flex items-center gap-1"><Database className="w-3 h-3" />Search: ~30ms</span><span className="flex items-center gap-1"><BookOpen className="w-3 h-3" />LLM: ~5s</span></div></div>
      </div>
    </div>
  );
};

export default UnifiedQueryInterface;
