// V4 - Cleaned, consistent, and fully synchronized with the backend data structures.
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

// --- Data Structures (Single Source of Truth) ---

export interface QueryResponse {
  id: string;
  timestamp: string;
  query: string;
  symbolicResponse: string;
  neurologicResponse?: string; // NEW: Raw LLM response
  naturalLanguageExplanation?: string;
  processingTime?: number; // NEW: Time taken to process
  kbFactsUsed?: number; // NEW: Number of KB facts used
  status: 'pending' | 'success' | 'error';
}

export interface RewardDataPoint {
  timestamp: number;
  reward: number;
  action: string;
}

export interface KbMetrics {
  factCount: number;
  growthRate: number;
  connectivity: number;
  entropy: number;
  nodeCount: number; // Added for graph visualization
  edgeCount: number; // Added for graph visualization
}

export interface LLMProvider {
  name: string;
  model: string;
  status: 'online' | 'offline' | 'error';
  tokensUsed: number;
  cost: number;
  responseTime: number;
  // Also accept snake_case from backend
  tokens_used?: number;
  response_time?: number;
  [key: string]: any; // Allow any additional fields
}

export interface EngineStatus {
  name: string;
  status: 'running' | 'stopped' | 'error';
  mode?: string;
  progress?: number;
  lastActivity?: string;
}

export interface GovernorDecision {
  timestamp: string;
  type: string;
  action: string;
  target: string;
  reason: string;
  priority: string;
  executed: boolean;
}

export interface KnowledgeCategory {
  name: string;
  factCount: number;
  pfabScore: number;
  lastUpdated: string;
}

// --- Main State Interface ---

interface TopicPreference {
  name: string;
  weight: number;
  icon?: string;
  description?: string;
  category?: string;
}

interface TopicPreferences {
  topics: TopicPreference[];
  autoMode: boolean;
}

interface AutoLearningConfig {
  enabled: boolean;
  loopIntervalSeconds: number;
  bootstrapThreshold: number;
  explorationRate: number;
  minCategoryCoverage: number;
  minPfabScore: number;
  minKnowledgeGrowthRate: number;
  minLlmHealth: number;
}

interface GovernorState {
  // System-level state
  isConnected: boolean;
  systemStatus: 'operational' | 'degraded' | 'offline';
  systemLoad: { cpu: number; memory: number; gpu?: number; gpu_memory?: number };
  systemLoadHistory: { time: string; cpu: number; memory: number; gpu?: number }[];
  
  // GPU Information
  gpuInfo: {
    metrics?: any[];
    summary?: any;
    name?: string;
    temperature?: number;
    utilization?: number;
    memory_used?: number;
    memory_total?: number;
    memory_percent?: number;
    power_draw?: number | null;
    power_limit?: number | null;
    clock_speed?: number | null;
    fan_speed?: number | null;
  } | null;

  // Module-specific states
  governor: {
    status: string;
    running: boolean;
    decisions: GovernorDecision[];
    rewardHistory: number[]; // Simplified for now
    metrics?: any; // Enhanced: Add metrics property
  };
  
  kb: {
    metrics: KbMetrics;
    categories: KnowledgeCategory[];
  };

  engines: EngineStatus[];
  llmProviders: LLMProvider[];
  queryHistory: QueryResponse[];
  
  // Auto-learning configuration
  autoLearningConfig: AutoLearningConfig;
  
  // Topic preferences
  topicPreferences: TopicPreferences;
  
  // Enhanced: Additional state properties for backend integration
  emergencyFixes: any[];
  monitoringMetrics: any;
  systemDetails: any;

  // Actions
  handleConnectionStatus: (status: boolean) => void;
  handleInitialData: (payload: any) => void;
  handleSystemLoadUpdate: (payload: { cpu: number; memory: number; gpu?: number; gpu_memory?: number }) => void;
  handleGovernorUpdate: (payload: any) => void;
  handleKbUpdate: (payload: any) => void;
  handleEnginesUpdate: (payload: { engines: EngineStatus[] }) => void;
  handleLlmUpdate: (payload: { providers: LLMProvider[] }) => void;
  handleGpuUpdate: (payload: { gpu: any }) => void;
  addQueryResponse: (response: QueryResponse) => void;
  updateQueryResponse: (id: string, updates: Partial<QueryResponse>) => void;
  updateAutoLearningConfig: (config: Partial<AutoLearningConfig>) => void;
  updateAutoLearningField: (field: keyof AutoLearningConfig, value: any) => void;
  updateTopicPreferences: (preferences: TopicPreferences) => void;
  // Enhanced: New handlers for detailed backend events
  handleEmergencyFixUpdate: (payload: any) => void;
  handleMonitoringUpdate: (payload: any) => void;
  handleSystemStatusUpdate: (payload: any) => void;
  handleEngineDetailedUpdate: (payload: any) => void;
  handleLlmDetailedUpdate: (payload: any) => void;
  handleKbDetailedUpdate: (payload: any) => void;
  handleGovernorDetailedUpdate: (payload: any) => void;
}

// --- Store Implementation ---

export const useGovernorStore = create(immer<GovernorState>((set) => ({
  // Initial State
  isConnected: false,
  systemStatus: 'offline',
  systemLoad: { cpu: 0, memory: 0 },
  systemLoadHistory: [],
  gpuInfo: null,

  governor: {
    status: "INITIALIZING",
    running: false,
    decisions: [],
    rewardHistory: [],
  },

  kb: {
    metrics: { factCount: 0, growthRate: 0, connectivity: 0, entropy: 0, nodeCount: 0, edgeCount: 0 }, // Initial value 0, will be updated from backend
    categories: [],
  },

  engines: [],
  llmProviders: [],
  queryHistory: [],
  
  autoLearningConfig: {
    enabled: true,
    loopIntervalSeconds: 15,
    bootstrapThreshold: 100,
    explorationRate: 0.3,
    minCategoryCoverage: 50,
    minPfabScore: 70,
    minKnowledgeGrowthRate: 3.0,
    minLlmHealth: 75
  },
  
  topicPreferences: {
    topics: [],
    autoMode: true
  },
  
  // Enhanced: Initialize additional state properties
  emergencyFixes: [] as any[],
  monitoringMetrics: null,
  systemDetails: null,

  // --- Actions ---

  handleConnectionStatus: (status) => set((state) => {
    state.isConnected = status;
    state.systemStatus = status ? 'operational' : 'offline';
  }),

  handleSystemLoadUpdate: (payload) => set((state) => {
    state.systemLoad = payload;
    state.systemLoadHistory.push({ time: new Date().toLocaleTimeString(), ...payload });
    if (state.systemLoadHistory.length > 50) state.systemLoadHistory.shift();
  }),

  handleGovernorUpdate: (payload) => set((state) => {
    if (payload.governorStatus) state.governor.status = payload.governorStatus;
    if (payload.status) {
      state.governor.running = payload.status.running;
      if (payload.status.recentDecisions) state.governor.decisions = payload.status.recentDecisions;
    }
    if (payload.reward !== null && payload.reward !== undefined) {
      state.governor.rewardHistory.push(payload.reward);
      if (state.governor.rewardHistory.length > 100) state.governor.rewardHistory.shift();
    }
  }),

  handleKbUpdate: (payload) => set((state) => {
    if (payload.metrics) {
      // Handle both camelCase and snake_case from different backend versions
      state.kb.metrics = {
        factCount: payload.metrics.factCount || payload.metrics.fact_count || state.kb.metrics.factCount,
        growthRate: payload.metrics.growthRate || payload.metrics.growth_rate || 0,
        connectivity: payload.metrics.connectivity || 0,
        entropy: payload.metrics.entropy || 0,
        nodeCount: payload.metrics.nodeCount || state.kb.metrics.nodeCount,
        edgeCount: payload.metrics.edgeCount || state.kb.metrics.edgeCount,
      };
    } else if (payload.factCount !== undefined || payload.fact_count !== undefined) {
      // Fallback: accept flat payloads like { fact_count, factCount, ... }
      state.kb.metrics = {
        factCount: payload.factCount || payload.fact_count || state.kb.metrics.factCount,
        growthRate: payload.growthRate || payload.growth_rate || state.kb.metrics.growthRate || 0,
        connectivity: payload.connectivity || state.kb.metrics.connectivity || 0,
        entropy: payload.entropy || state.kb.metrics.entropy || 0,
        nodeCount: payload.nodeCount || state.kb.metrics.nodeCount || 0,
        edgeCount: payload.edgeCount || state.kb.metrics.edgeCount || 0,
      };
    }
    if (payload.categories) {
      state.kb.categories = payload.categories;
    }
  }),

  handleEnginesUpdate: (payload) => set((state) => {
    if (payload.engines) state.engines = payload.engines;
  }),

  handleLlmUpdate: (payload) => set((state) => {
    if (payload.providers) state.llmProviders = payload.providers;
  }),
  
  handleGpuUpdate: (payload) => set((state) => {
    if (payload.gpu) {
      state.gpuInfo = payload.gpu;
    }
  }),

  handleInitialData: (payload) => set((state) => {
    // This is the critical fix. We now ensure all parts of the initial payload are processed.
    if (payload.governorStatus) state.governor.status = payload.governorStatus;
    if (payload.governorRunning !== undefined) state.governor.running = payload.governorRunning;
    if (payload.engines) state.engines = payload.engines;
    if (payload.llmProviders) state.llmProviders = payload.llmProviders;
    if (payload.kbMetrics) {
      state.kb.metrics.factCount = payload.kbMetrics.factCount || payload.kbMetrics.fact_count || state.kb.metrics.factCount;
      state.kb.metrics.growthRate = payload.kbMetrics.growthRate || payload.kbMetrics.growth_rate || 0;
      state.kb.metrics.connectivity = payload.kbMetrics.connectivity || 0;
      state.kb.metrics.entropy = payload.kbMetrics.entropy || 0;
      state.kb.metrics.nodeCount = payload.kbMetrics.nodeCount || 0;
      state.kb.metrics.edgeCount = payload.kbMetrics.edgeCount || 0;
    }
    if (payload.knowledgeCategories) state.kb.categories = payload.knowledgeCategories;
    if (payload.governorDecisions) state.governor.decisions = payload.governorDecisions;
    if (payload.autoLearning) state.autoLearningConfig = payload.autoLearning;
  }),

  addQueryResponse: (response) => set((state) => {
    state.queryHistory = [response, ...state.queryHistory].slice(0, 100);
  }),

  updateQueryResponse: (id, updates) => set((state) => {
    const index = state.queryHistory.findIndex(q => q.id === id);
    if (index !== -1) {
      state.queryHistory[index] = { ...state.queryHistory[index], ...updates };
    }
  }),
  
  updateAutoLearningConfig: (config) => set((state) => {
    state.autoLearningConfig = { ...state.autoLearningConfig, ...config };
  }),
  
  updateAutoLearningField: (field, value) => set((state) => {
    state.autoLearningConfig[field] = value;
  }),
  
  updateTopicPreferences: (preferences) => set((state) => {
    state.topicPreferences = preferences;
  }),
  
  // Enhanced: New handlers for detailed backend events
  handleEmergencyFixUpdate: (payload) => set((state) => {
    // Store emergency fix status
    if (payload.fixes) {
      state.emergencyFixes = payload.fixes;
    }
  }),
  
  handleMonitoringUpdate: (payload) => set((state) => {
    // Store monitoring data
    if (payload.metrics) {
      state.monitoringMetrics = payload.metrics;
    }
  }),
  
  handleSystemStatusUpdate: (payload) => set((state) => {
    // Update system status with detailed information
    if (payload.status) {
      state.systemStatus = payload.status;
    }
    if (payload.details) {
      state.systemDetails = payload.details;
    }
  }),
  
  handleEngineDetailedUpdate: (payload) => set((state) => {
    // Update engines with detailed metrics
    if (payload.engines) {
      state.engines = payload.engines;
    }
  }),
  
  handleLlmDetailedUpdate: (payload) => set((state) => {
    // Update LLM providers with detailed information
    if (payload.providers) {
      state.llmProviders = payload.providers;
    }
  }),
  
  handleKbDetailedUpdate: (payload) => set((state) => {
    // Update knowledge base with detailed information
    if (payload.metrics) {
      state.kb.metrics = {
        ...state.kb.metrics,
        ...payload.metrics
      };
    }
    if (payload.categories) {
      state.kb.categories = payload.categories;
    }
  }),
  
  handleGovernorDetailedUpdate: (payload) => set((state) => {
    // Update governor with detailed information
    if (payload.status) {
      state.governor.status = payload.status;
    }
    if (payload.decisions) {
      state.governor.decisions = payload.decisions;
    }
    if (payload.metrics) {
      state.governor.metrics = payload.metrics;
    }
  }),
})));

// EXPOSE STORE GLOBALLY FOR DEBUGGING
if (typeof window !== 'undefined') {
  (window as any).__GOVERNOR_STORE__ = useGovernorStore;
}