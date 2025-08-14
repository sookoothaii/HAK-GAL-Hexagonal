// useIntelligenceStore.ts - Unified Store for all Intelligence Layers
// Nach HAK/GAL Artikel 7 (Konjugierte Zustände)
// Integriert: HRM, Knowledge Base, Philosophical Intelligence, Trust Metrics

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

// === Core Types ===

export interface NeuralReasoning {
  confidence: number;              // 0-1 HRM confidence
  gap: number;                     // Separation between true/false
  reasoning: string[];             // Reasoning terms
  processingTime: number;          // Inference time in ms
  vocabulary: Map<string, number>; // 694 terms
  modelStatus: 'operational' | 'training' | 'offline';
}

export interface KnowledgeBase {
  totalFacts: number;              // 6,121+ facts
  categories: Map<string, number>; // Facts by category
  searchResults: FactResult[];    // Current search results
  verifiedFacts: Set<string>;     // Human-verified facts
  growthRate: number;              // Facts/minute
  lastUpdate: string;              // ISO timestamp
}

export interface FactResult {
  id: string;
  statement: string;
  confidence: number;
  source: 'kb' | 'inference' | 'human' | 'llm';
  verified: boolean;
  timestamp: string;
}

export interface PhilosophicalIntelligence {
  spikeCoherence: number;          // 0-1 coherence between H/L cycles
  deonticLevel: 'obligatory' | 'permitted' | 'neutral' | 'discouraged' | 'forbidden';
  agentConsensus: number;          // 0-1 dual agent agreement
  rewardHackDetected: boolean;     // Critical alert
  ethicalConfidence: number;       // 0-1 ethical alignment
  friendshipScore: number;         // Truth friendship metric
}

export interface TrustMetrics {
  overall: number;                 // 0-1 aggregate trust
  components: {
    neural: number;                // HRM confidence
    factual: number;               // Fabulometer score
    sources: number;               // Citation quality
    consensus: number;             // LLM agreement
    ethical: number;               // PI alignment
    human: boolean;                // Human verified
  };
  explanation: string;             // Why this trust level
  suggestions: string[];           // How to improve trust
}

export interface QueryIntelligence {
  id: string;
  query: string;
  timestamp: string;
  
  // Multi-layer responses
  neural: NeuralReasoning;
  knowledge: {
    facts: FactResult[];
    citations: string[];
  };
  philosophical: PhilosophicalIntelligence;
  trust: TrustMetrics;
  
  // LLM responses
  symbolicResponse?: string;
  naturalLanguageResponse?: string;
  explanation?: string;
  
  // Status
  status: 'pending' | 'processing' | 'complete' | 'error';
  errors?: string[];
}

export interface SystemMetrics {
  // Performance
  apiLatency: number;              // ms
  learningRate: number;            // facts/min
  memoryUsage: number;             // MB
  gpuUsage?: number;               // %
  
  // AI Metrics
  hrmInferences: number;           // total count
  philosophicalChecks: number;     // total count
  fabulometerScans: number;        // total count
  verifications: number;           // human verifications
  
  // Health
  systemStatus: 'operational' | 'degraded' | 'critical' | 'offline';
  activeEngines: string[];
  llmProviders: Map<string, 'online' | 'offline' | 'error'>;
}

export interface GovernorState {
  status: 'running' | 'stopped' | 'paused';
  alpha: number;
  beta: number;
  lastAction: string;
  learningRate: number;
}

export interface LLMStatus {
  providers: Record<string, any>;
  activeCount: number;
}

// === Main Store Interface ===

interface IntelligenceState {
  // Core Intelligence
  neural: NeuralReasoning;
  knowledge: KnowledgeBase;
  philosophical: PhilosophicalIntelligence;
  trust: TrustMetrics;
  
  // Query History
  queries: QueryIntelligence[];
  activeQuery: QueryIntelligence | null;
  
  // System State
  metrics: SystemMetrics;
  governor: GovernorState;
  llmProviders: LLMStatus;
  isConnected: boolean;
  
  // Configuration
  config: {
    autoVerification: boolean;
    trustThreshold: number;        // Min trust for auto-accept
    ethicsEnabled: boolean;
    batchMode: boolean;
    maxHistorySize: number;
  };
  
  // Actions - Neural
  updateNeuralReasoning: (update: Partial<NeuralReasoning>) => void;
  processHRMResponse: (query: string, response: any) => void;
  
  // Actions - Knowledge
  updateKnowledgeBase: (update: Partial<KnowledgeBase>) => void;
  addVerifiedFact: (fact: string) => void;
  searchKnowledge: (query: string) => Promise<FactResult[]>;
  
  // Actions - Philosophical
  updatePhilosophical: (update: Partial<PhilosophicalIntelligence>) => void;
  checkEthics: (action: string) => Promise<boolean>;
  
  // Actions - Trust
  calculateTrust: (components: Partial<TrustMetrics['components']>) => number;
  updateTrust: (trust: Partial<TrustMetrics>) => void;
  
  // Actions - Queries
  submitQuery: (query: string) => Promise<void>;
  updateQueryStatus: (id: string, status: QueryIntelligence['status']) => void;
  clearHistory: () => void;
  
  // Actions - System
  updateMetrics: (metrics: Partial<SystemMetrics>) => void;
  setConnectionStatus: (connected: boolean) => void;
  updateConfig: (config: Partial<IntelligenceState['config']>) => void;
  updateGovernor: (governor: Partial<GovernorState>) => void;
  updateLLMStatus: (status: Partial<LLMStatus>) => void;
  
  // WebSocket Handlers
  handleIntelligenceUpdate: (data: any) => void;
  handleHRMUpdate: (data: any) => void;
  handlePhilosophicalUpdate: (data: any) => void;
  handleTrustUpdate: (data: any) => void;
}

// === Store Implementation ===

export const useIntelligenceStore = create(immer<IntelligenceState>((set, get) => ({
  // Initial State
  neural: {
    confidence: 0,
    gap: 0.802,
    reasoning: [],
    processingTime: 0,
    vocabulary: new Map(),
    modelStatus: 'offline'
  },
  
  knowledge: {
    totalFacts: 3080,  // Real facts count from backend
    categories: new Map(),
    searchResults: [],
    verifiedFacts: new Set(),
    growthRate: 0,
    lastUpdate: new Date().toISOString()
  },
  
  philosophical: {
    spikeCoherence: 0.6,
    deonticLevel: 'neutral',
    agentConsensus: 0.8,
    rewardHackDetected: false,
    ethicalConfidence: 0.75,
    friendshipScore: 0.977
  },
  
  trust: {
    overall: 0,
    components: {
      neural: 0,
      factual: 0,
      sources: 0,
      consensus: 0,
      ethical: 0,
      human: false
    },
    explanation: '',
    suggestions: []
  },
  
  queries: [],
  activeQuery: null,
  
  metrics: {
    apiLatency: 7,
    learningRate: 30,
    memoryUsage: 450,
    hrmInferences: 0,
    philosophicalChecks: 0,
    fabulometerScans: 0,
    verifications: 0,
    systemStatus: 'operational',
    activeEngines: [],
    llmProviders: new Map()
  },
  
  governor: {
    status: 'stopped',
    alpha: 0,
    beta: 0,
    lastAction: '',
    learningRate: 0
  },
  
  llmProviders: {
    providers: {},
    activeCount: 0
  },
  
  isConnected: false,
  
  config: {
    autoVerification: true,
    trustThreshold: 0.7,
    ethicsEnabled: true,
    batchMode: false,
    maxHistorySize: 100
  },
  
  // === Actions Implementation ===
  
  updateNeuralReasoning: (update) => set((state) => {
    Object.assign(state.neural, update);
  }),
  
  processHRMResponse: (query, response) => set((state) => {
    state.neural.confidence = response.confidence || 0;
    state.neural.reasoning = response.reasoning_terms || [];
    state.neural.processingTime = response.processing_time || 0;
    state.neural.modelStatus = 'operational';
    
    // Update metrics
    state.metrics.hrmInferences++;
  }),
  
  updateKnowledgeBase: (update) => set((state) => {
    Object.assign(state.knowledge, update);
  }),
  
  addVerifiedFact: (fact) => set((state) => {
    state.knowledge.verifiedFacts.add(fact);
    state.metrics.verifications++;
  }),
  
  searchKnowledge: async (query) => {
    // API call to search knowledge base
    try {
      const { API_BASE_URL } = await import('@/config/backends');
      const response = await fetch(`${API_BASE_URL}/api/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'ask', query })
      });
      
      if (response.ok) {
        const data = await response.json();
        const facts = data.chatResponse?.relevant_facts || [];
        
        set((state) => {
          state.knowledge.searchResults = facts.map((f: string, i: number) => ({
            id: `fact-${Date.now()}-${i}`,
            statement: f,
            confidence: 0.8,
            source: 'kb' as const,
            verified: state.knowledge.verifiedFacts.has(f),
            timestamp: new Date().toISOString()
          }));
        });
        
        return get().knowledge.searchResults;
      }
    } catch (error) {
      console.error('Knowledge search error:', error);
    }
    return [];
  },
  
  updatePhilosophical: (update) => set((state) => {
    Object.assign(state.philosophical, update);
    
    // Check for reward hack
    if (update.ethicalConfidence !== undefined && update.ethicalConfidence < 0.3) {
      state.philosophical.rewardHackDetected = true;
    }
  }),
  
  checkEthics: async (action) => {
    // Placeholder for ethics check
    const state = get();
    return state.philosophical.ethicalConfidence > 0.5 && 
           !state.philosophical.rewardHackDetected;
  },
  
  calculateTrust: (components) => {
    const weights = {
      neural: 0.25,
      factual: 0.25,
      sources: 0.20,
      consensus: 0.20,
      ethical: 0.10
    };
    
    let score = 0;
    for (const [key, weight] of Object.entries(weights)) {
      const value = components[key as keyof typeof components];
      if (typeof value === 'number') {
        score += value * weight;
      }
    }
    
    // Boost for human verification
    if (components.human) {
      score = Math.min(1, score * 1.1);
    }
    
    return score;
  },
  
  updateTrust: (trust) => set((state) => {
    Object.assign(state.trust, trust);
  }),
  
  submitQuery: async (query) => {
    const queryId = `query-${Date.now()}`;
    
    // Create new query record
    const newQuery: QueryIntelligence = {
      id: queryId,
      query,
      timestamp: new Date().toISOString(),
      neural: { ...get().neural },
      knowledge: { facts: [], citations: [] },
      philosophical: { ...get().philosophical },
      trust: { ...get().trust },
      status: 'pending'
    };
    
    set((state) => {
      state.queries = [newQuery, ...state.queries].slice(0, state.config.maxHistorySize);
      state.activeQuery = newQuery;
    });
    
    try {
      // 1. HRM Neural Reasoning
      const { API_BASE_URL } = await import('@/config/backends');
      const hrmResponse = await fetch(`${API_BASE_URL}/api/hrm/reason`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      if (hrmResponse.ok) {
        const hrmData = await hrmResponse.json();
        get().processHRMResponse(query, hrmData);
      }
      
      // 2. Knowledge Search
      await get().searchKnowledge(query);
      
      // 3. Calculate Trust
      const trustScore = get().calculateTrust({
        neural: get().neural.confidence,
        factual: 0.8, // Placeholder
        sources: get().knowledge.searchResults.length > 0 ? 0.9 : 0.1,
        consensus: 0.7, // Placeholder
        ethical: get().philosophical.ethicalConfidence,
        human: false
      });
      
      get().updateTrust({
        overall: trustScore,
        components: {
          neural: get().neural.confidence,
          factual: 0.8,
          sources: get().knowledge.searchResults.length > 0 ? 0.9 : 0.1,
          consensus: 0.7,
          ethical: get().philosophical.ethicalConfidence,
          human: false
        }
      });
      
      // Update query status
      get().updateQueryStatus(queryId, 'complete');
      
    } catch (error) {
      console.error('Query processing error:', error);
      get().updateQueryStatus(queryId, 'error');
    }
  },
  
  updateQueryStatus: (id, status) => set((state) => {
    const query = state.queries.find(q => q.id === id);
    if (query) {
      query.status = status;
    }
  }),
  
  clearHistory: () => set((state) => {
    state.queries = [];
    state.activeQuery = null;
  }),
  
  updateMetrics: (metrics) => set((state) => {
    Object.assign(state.metrics, metrics);
  }),
  
  setConnectionStatus: (connected) => set((state) => {
    state.isConnected = connected;
    if (!connected) {
      state.metrics.systemStatus = 'offline';
    }
  }),
  
  updateConfig: (config) => set((state) => {
    Object.assign(state.config, config);
  }),
  
  updateGovernor: (governor) => set((state) => {
    Object.assign(state.governor, governor);
  }),
  
  updateLLMStatus: (status) => set((state) => {
    Object.assign(state.llmProviders, status);
  }),
  
  // WebSocket Handlers
  handleIntelligenceUpdate: (data) => set((state) => {
    // Unified update handler
    if (data.neural) state.updateNeuralReasoning(data.neural);
    if (data.knowledge) state.updateKnowledgeBase(data.knowledge);
    if (data.philosophical) state.updatePhilosophical(data.philosophical);
    if (data.trust) state.updateTrust(data.trust);
    if (data.metrics) state.updateMetrics(data.metrics);
  }),
  
  handleHRMUpdate: (data) => set((state) => {
    if (data.confidence !== undefined) state.neural.confidence = data.confidence;
    if (data.gap !== undefined) state.neural.gap = data.gap;
    if (data.reasoning) state.neural.reasoning = data.reasoning;
    if (data.status) state.neural.modelStatus = data.status;
  }),
  
  handlePhilosophicalUpdate: (data) => set((state) => {
    if (data.spikeCoherence !== undefined) state.philosophical.spikeCoherence = data.spikeCoherence;
    if (data.deonticLevel) state.philosophical.deonticLevel = data.deonticLevel;
    if (data.rewardHack !== undefined) state.philosophical.rewardHackDetected = data.rewardHack;
    
    // Alert on reward hack
    if (data.rewardHack) {
      console.warn('⚠️ REWARD HACK DETECTED!');
      // Could trigger UI alert here
    }
  }),
  
  handleTrustUpdate: (data) => set((state) => {
    if (data.overall !== undefined) state.trust.overall = data.overall;
    if (data.components) Object.assign(state.trust.components, data.components);
    if (data.explanation) state.trust.explanation = data.explanation;
  })
})));

// === Global Exposure for Debugging ===

if (typeof window !== 'undefined') {
  (window as any).__INTELLIGENCE_STORE__ = useIntelligenceStore;
  
  // Debug helpers
  (window as any).getIntelligence = () => {
    const state = useIntelligenceStore.getState();
    return {
      neural: {
        confidence: state.neural.confidence,
        gap: state.neural.gap,
        status: state.neural.modelStatus
      },
      knowledge: {
        facts: state.knowledge.totalFacts,
        verified: state.knowledge.verifiedFacts.size,
        growth: state.knowledge.growthRate
      },
      philosophical: {
        coherence: state.philosophical.spikeCoherence,
        ethics: state.philosophical.deonticLevel,
        consensus: state.philosophical.agentConsensus
      },
      trust: {
        overall: state.trust.overall,
        components: state.trust.components
      }
    };
  };
  
  (window as any).simulateQuery = (query: string) => {
    return useIntelligenceStore.getState().submitQuery(query);
  };
}