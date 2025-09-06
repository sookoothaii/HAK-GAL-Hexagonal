/**
 * Backend Configuration - Centralized via app.config.ts
 */

import { appConfig } from '@/config/app.config';

export interface BackendConfig {
  name: string;
  apiUrl: string;
  wsUrl: string;
  port: number;
  type: 'hexagonal';
  dataSource: 'sqlite';
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
    mojo: boolean;
    write: boolean; // Indicates write capability
  };
  stats: {
    facts: number | 'dynamic';
    responseTime: string;
    architecture: string;
    database: string;
  };
}

// Single Backend Configuration - Using centralized config
export const BACKEND: BackendConfig = {
  name: 'HAK-GAL Hexagonal (Write Mode)',
  apiUrl: '', // Using proxy
  wsUrl: appConfig.WS_PATH,
  port: appConfig.PORTS.BACKEND,
  type: 'hexagonal',
  dataSource: 'sqlite',
  features: {
    websocket: true,
    governor: true,
    autoLearning: true,
    neuralReasoning: true,
    hrm: true,
    llmIntegration: true,
    graphGeneration: true,
    emergencyTools: true,
    sentryMonitoring: true,
    cudaAcceleration: true,
    mojo: true,
    write: true
  },
  stats: {
    facts: 'dynamic', // Fetched from /api/facts/count
    responseTime: '<10ms',
    architecture: 'Hexagonal Clean Architecture',
    database: 'SQLite (hexagonal_kb.db)'
  }
};

// Legacy exports for backward compatibility (all point to same backend now)
export const BACKENDS = { 
  hexagonal: BACKEND,
  primary: BACKEND 
};

// Simplified getters (no switching needed)
export const getActiveBackend = (): BackendConfig => BACKEND;
export const setActiveBackend = (key: string): void => {
  // No-op: Backend switching is disabled
  console.debug('Backend switching disabled - using 5002 (WRITE) only');
};

// Check if feature is available
export const hasFeature = (feature: keyof BackendConfig['features']): boolean => {
  return BACKEND.features[feature] || false;
};

// Export current backend for backward compatibility
export const CURRENT_BACKEND = BACKEND;
export const API_BASE_URL = ''; // Using proxy
export const WS_URL = '/socket.io';
export const BACKEND_NAME = BACKEND.name;
export const BACKEND_TYPE = BACKEND.type;
export const DATA_SOURCE = BACKEND.dataSource;

// Helper to fetch dynamic facts count
export const fetchFactsCount = async (): Promise<number> => {
  try {
    const response = await fetch('/api/facts/count');
    if (response.ok) {
      const data = await response.json();
      return data.count || 0;
    }
  } catch (error) {
    console.error('Failed to fetch facts count:', error);
  }
  return 0;
};

// Admin fallback path (5001) - not exposed to UI
// Only used internally when primary endpoints fail
export const ADMIN_API_PATH = '/api-admin';
