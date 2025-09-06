// Central configuration for HAK_GAL Frontend
// All environment-specific values in one place

export interface AppConfig {
  // API Configuration
  API_BASE_URL: string;
  API_TIMEOUT: number;
  API_KEY: string;
  
  // WebSocket Configuration
  WS_URL: string;
  WS_PATH: string;
  WS_RECONNECTION_ATTEMPTS: number;
  WS_RECONNECTION_DELAY: number;
  WS_RECONNECTION_DELAY_MAX: number;
  
  // Ports
  PORTS: {
    BACKEND: number;
    GOVERNOR: number;
    PROXY: number;
    FRONTEND: number;
  };
  
  // Feature Flags
  FEATURES: {
    USE_PRO_UI: boolean;
    ENABLE_ANIMATIONS: boolean;
    ENABLE_PERFORMANCE_MONITORING: boolean;
    COMMAND_PALETTE_ENABLED: boolean;
    ENABLE_AI_FEATURES: boolean;
    ENABLE_MOCK_DATA: boolean;
    ENABLE_DEBUG_MODE: boolean;
  };
  
  // System Defaults (to be loaded dynamically)
  DEFAULTS: {
    INITIAL_FACT_COUNT: number;
    INITIAL_GROWTH_RATE: number;
    INITIAL_ENTITY_COUNT: number;
    INITIAL_PREDICATE_COUNT: number;
  };
  
  // Performance
  PERFORMANCE: {
    QUERY_HISTORY_LIMIT: number;
    SYSTEM_LOAD_HISTORY_LIMIT: number;
    REWARD_HISTORY_LIMIT: number;
  };
}

// Get value from environment or use default
const getEnvValue = <T>(key: string, defaultValue: T): T => {
  const value = import.meta.env[key];
  if (value === undefined || value === '') return defaultValue;
  
  // Handle boolean values
  if (typeof defaultValue === 'boolean') {
    return (value === 'true' || value === true) as T;
  }
  
  // Handle number values
  if (typeof defaultValue === 'number') {
    return (parseInt(value) || defaultValue) as T;
  }
  
  return value as T;
};

// Application configuration
export const appConfig: AppConfig = {
  // API Configuration
  API_BASE_URL: getEnvValue('VITE_API_BASE_URL', 'http://localhost:8088'),
  API_TIMEOUT: getEnvValue('VITE_API_TIMEOUT', 300000),
  API_KEY: getEnvValue('VITE_API_KEY', ''),
  
  // WebSocket Configuration
  WS_URL: getEnvValue('VITE_WS_URL', 'http://localhost:8088'),
  WS_PATH: getEnvValue('VITE_WS_PATH', '/socket.io'),
  WS_RECONNECTION_ATTEMPTS: getEnvValue('VITE_WS_RECONNECTION_ATTEMPTS', 3),
  WS_RECONNECTION_DELAY: getEnvValue('VITE_WS_RECONNECTION_DELAY', 2000),
  WS_RECONNECTION_DELAY_MAX: getEnvValue('VITE_WS_RECONNECTION_DELAY_MAX', 10000),
  
  // Ports
  PORTS: {
    BACKEND: getEnvValue('VITE_BACKEND_PORT', 5002),
    GOVERNOR: getEnvValue('VITE_GOVERNOR_PORT', 5001),
    PROXY: getEnvValue('VITE_PROXY_PORT', 8088),
    FRONTEND: getEnvValue('VITE_FRONTEND_PORT', 5173),
  },
  
  // Feature Flags
  FEATURES: {
    USE_PRO_UI: getEnvValue('VITE_USE_PRO_UI', true),
    ENABLE_ANIMATIONS: getEnvValue('VITE_ENABLE_ANIMATIONS', true),
    ENABLE_PERFORMANCE_MONITORING: getEnvValue('VITE_ENABLE_PERFORMANCE_MONITORING', true),
    COMMAND_PALETTE_ENABLED: getEnvValue('VITE_COMMAND_PALETTE_ENABLED', true),
    ENABLE_AI_FEATURES: getEnvValue('VITE_ENABLE_AI_FEATURES', true),
    ENABLE_MOCK_DATA: getEnvValue('VITE_ENABLE_MOCK_DATA', false),
    ENABLE_DEBUG_MODE: getEnvValue('VITE_ENABLE_DEBUG_MODE', false),
  },
  
  // System Defaults (will be overridden by dynamic loading)
  DEFAULTS: {
    INITIAL_FACT_COUNT: getEnvValue('VITE_INITIAL_FACT_COUNT', 0),
    INITIAL_GROWTH_RATE: getEnvValue('VITE_INITIAL_GROWTH_RATE', 0),
    INITIAL_ENTITY_COUNT: getEnvValue('VITE_INITIAL_ENTITY_COUNT', 0),
    INITIAL_PREDICATE_COUNT: getEnvValue('VITE_INITIAL_PREDICATE_COUNT', 0),
  },
  
  // Performance
  PERFORMANCE: {
    QUERY_HISTORY_LIMIT: getEnvValue('VITE_QUERY_HISTORY_LIMIT', 100),
    SYSTEM_LOAD_HISTORY_LIMIT: getEnvValue('VITE_SYSTEM_LOAD_HISTORY_LIMIT', 50),
    REWARD_HISTORY_LIMIT: getEnvValue('VITE_REWARD_HISTORY_LIMIT', 100),
  },
};

// Helper function to check if running in production
export const isProduction = () => import.meta.env.PROD;

// Helper function to check if running in development
export const isDevelopment = () => import.meta.env.DEV;

// Export individual config values for convenience
export const { API_BASE_URL, API_KEY, WS_URL, PORTS, FEATURES } = appConfig;

// Log configuration in development mode
if (isDevelopment() && appConfig.FEATURES.ENABLE_DEBUG_MODE) {
  console.log('🔧 App Configuration:', appConfig);
}
