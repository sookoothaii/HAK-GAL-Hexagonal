// HRM Extension for Governor Store
// Implements HAK/GAL Verfassung compliant HRM integration

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

// --- HRM Data Structures ---

export interface HRMMetrics {
  modelStatus: 'operational' | 'training' | 'offline';
  parameters: number;
  vocabulary: number;
  factsLoaded: number;
  confidenceGap: number;
  device: string;
  lastTrainingEpoch?: number;
  trainingLoss?: number;
}

export interface HRMQueryResult {
  query: string;
  confidence: number;
  reasoning: string[];
  isTrue: boolean;
  processingTime: number;
}

export interface HRMBatchResult {
  queries: string[];
  results: HRMQueryResult[];
  statistics: {
    totalQueries: number;
    avgConfidence: number;
    stdConfidence: number;
    highConfidenceCount: number;
    lowConfidenceCount: number;
    processingTime: number;
  };
}

export interface PrometheusMetrics {
  hrm_requests_total?: number;
  hrm_confidence_gap?: number;
  hrm_model_parameters?: number;
  hrm_vocabulary_size?: number;
  hrm_batch_size_avg?: number;
  hrm_request_duration_avg?: number;
}

export interface HRMTrainingStatus {
  totalEpochsTrained: number;
  bestGapAchieved: number;
  trainingSessions: number;
  currentGap: number;
  readyForTraining: boolean;
  lastTraining?: {
    epochsTrained: number;
    factsUsed: number;
    finalLoss: number;
    finalGap: number;
  };
}

// --- Extended State Interface ---

export interface HRMState {
  // Core HRM State
  hrm: {
    metrics: HRMMetrics;
    queryHistory: HRMQueryResult[];
    batchHistory: HRMBatchResult[];
    prometheus: PrometheusMetrics;
    training: HRMTrainingStatus;
    isProcessing: boolean;
  };
  
  // Actions
  handleHRMMetricsUpdate: (metrics: Partial<HRMMetrics>) => void;
  addHRMQuery: (result: HRMQueryResult) => void;
  addHRMBatch: (result: HRMBatchResult) => void;
  updatePrometheusMetrics: (metrics: PrometheusMetrics) => void;
  updateTrainingStatus: (status: Partial<HRMTrainingStatus>) => void;
  setHRMProcessing: (processing: boolean) => void;
  clearHRMHistory: () => void;
}

// --- HRM Store Implementation ---

export const useHRMStore = create(immer<HRMState>((set) => ({
  // Initial HRM State
  hrm: {
    metrics: {
      modelStatus: 'offline',
      parameters: 572673, // Known from documentation
      vocabulary: 694,
      factsLoaded: 2576,
      confidenceGap: 0.802,
      device: 'cuda'
    },
    queryHistory: [],
    batchHistory: [],
    prometheus: {},
    training: {
      totalEpochsTrained: 80,
      bestGapAchieved: 0.802,
      trainingSessions: 1,
      currentGap: 0.802,
      readyForTraining: true
    },
    isProcessing: false
  },

  // HRM Actions
  handleHRMMetricsUpdate: (metrics) => set((state) => {
    state.hrm.metrics = { ...state.hrm.metrics, ...metrics };
  }),

  addHRMQuery: (result) => set((state) => {
    // Add to history (keep last 100)
    state.hrm.queryHistory = [result, ...state.hrm.queryHistory].slice(0, 100);
    
    // Update confidence gap if we have true/false samples
    const recentQueries = state.hrm.queryHistory.slice(0, 10);
    const trueQueries = recentQueries.filter(q => q.isTrue);
    const falseQueries = recentQueries.filter(q => !q.isTrue);
    
    if (trueQueries.length > 0 && falseQueries.length > 0) {
      const avgTrue = trueQueries.reduce((sum, q) => sum + q.confidence, 0) / trueQueries.length;
      const avgFalse = falseQueries.reduce((sum, q) => sum + q.confidence, 0) / falseQueries.length;
      state.hrm.metrics.confidenceGap = avgTrue - avgFalse;
    }
  }),

  addHRMBatch: (result) => set((state) => {
    state.hrm.batchHistory = [result, ...state.hrm.batchHistory].slice(0, 50);
  }),

  updatePrometheusMetrics: (metrics) => set((state) => {
    state.hrm.prometheus = { ...state.hrm.prometheus, ...metrics };
  }),

  updateTrainingStatus: (status) => set((state) => {
    state.hrm.training = { ...state.hrm.training, ...status };
  }),

  setHRMProcessing: (processing) => set((state) => {
    state.hrm.isProcessing = processing;
  }),

  clearHRMHistory: () => set((state) => {
    state.hrm.queryHistory = [];
    state.hrm.batchHistory = [];
  })
})));

// --- Merge with existing Governor Store ---

export const mergeHRMWithGovernorStore = () => {
  // This function would be called to merge HRM state with existing Governor store
  // For now, we export the HRM store separately
  
  if (typeof window !== 'undefined') {
    (window as any).__HRM_STORE__ = useHRMStore;
    
    // Debug function
    (window as any).getHRMStatus = () => {
      const state = useHRMStore.getState();
      console.log('🧠 HRM Status:', {
        model: state.hrm.metrics.modelStatus,
        gap: state.hrm.metrics.confidenceGap,
        queries: state.hrm.queryHistory.length,
        device: state.hrm.metrics.device
      });
      return state.hrm.metrics;
    };
  }
};

// Initialize on import
mergeHRMWithGovernorStore();
