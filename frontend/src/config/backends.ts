/**
 * Enhanced Backend Configuration for SQLite-based System
 * Updated for SQLite as primary data source
 */

export interface BackendConfig {
  name: string;
  apiUrl: string;
  wsUrl: string;
  port: number;
  type: 'hexagonal';
  dataSource: 'sqlite' | 'jsonl';
  features: {
    websocket: boolean;
    governor: boolean;
    autoLearning: boolean;
    neuralReasoning: boolean;
    hrm: boolean;
    llmIntegration: boolean;
    graphGeneration: boolean;
    emergencyTools: boolean;
    sentryMonitoring: boolean;
    cudaAcceleration: boolean;
  };
  stats: {
    facts: number | 'dynamic';  // Dynamic means fetched from API
    responseTime: string;
    architecture: string;
    database: string;
  };
}

// Backend Configuration (Hexagonal with SQLite)
export const BACKENDS: Record<string, BackendConfig> = {
  hexagonal: {
    name: 'HAK-GAL Hexagonal (SQLite Mode)',
    apiUrl: 'http://localhost:5001',
    wsUrl: 'http://localhost:5001',
    port: 5001,
    type: 'hexagonal',
    dataSource: 'sqlite',
    features: {
      websocket: true,
      governor: true,
      autoLearning: true,
      neuralReasoning: true,
      hrm: false,  // Uses legacy bridge
      llmIntegration: true,
      graphGeneration: true,
      emergencyTools: true,
      sentryMonitoring: true,
      cudaAcceleration: true
    },
    stats: {
      facts: 'dynamic',  // Will be fetched from /api/facts/count
      responseTime: '<20ms',
      architecture: 'Clean Hexagonal (Ports & Adapters)',
      database: 'SQLite (k_assistant.db)'
    }
  }
};

// Active backend (fixed to hexagonal)
export const getActiveBackend = (): BackendConfig => BACKENDS.hexagonal;

// No-op (single backend)
export const setActiveBackend = (): void => {};

// Check if feature is available
export const hasFeature = (feature: keyof BackendConfig['features']): boolean => {
  return getActiveBackend().features[feature] || false;
};

// Export current backend for backward compatibility
export const CURRENT_BACKEND = getActiveBackend();
export const API_BASE_URL = CURRENT_BACKEND.apiUrl;
export const WS_URL = CURRENT_BACKEND.wsUrl;
export const BACKEND_NAME = CURRENT_BACKEND.name;
export const BACKEND_TYPE = CURRENT_BACKEND.type;
export const DATA_SOURCE = CURRENT_BACKEND.dataSource;

// Helper to fetch dynamic facts count
export const fetchFactsCount = async (): Promise<number> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/facts/count`);
    if (response.ok) {
      const data = await response.json();
      return data.count || 0;
    }
  } catch (error) {
    console.error('Failed to fetch facts count:', error);
  }
  return 0;
};
