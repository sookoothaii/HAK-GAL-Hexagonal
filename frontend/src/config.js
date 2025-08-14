// Frontend Configuration for Hexagonal Backend
// =============================================

export const config = {
  // API Configuration - ONLY PORT 5001
  api: {
    baseUrl: 'http://127.0.0.1:5001',
    timeout: 30000,
    endpoints: {
      // Core endpoints
      health: '/health',
      status: '/api/status',
      facts: '/api/facts',
      search: '/api/search',
      reason: '/api/reason',
      architecture: '/api/architecture',
      
      // CRUD operations
      addFact: '/api/facts',
      deleteFact: '/api/facts/delete',
      updateFact: '/api/facts/update',
      
      // Governor
      governor: {
        status: '/api/governor/status',
        start: '/api/governor/start',
        stop: '/api/governor/stop',
        config: '/api/governor/config'
      },
      
      // LLM (optional)
      llm: {
        explanation: '/api/llm/get-explanation'
      }
    }
  },
  
  // WebSocket Configuration
  websocket: {
    url: 'ws://127.0.0.1:5001',
    reconnectInterval: 5000,
    events: {
      kbUpdate: 'kb_update',
      systemStatus: 'system_status',
      governorUpdate: 'governor_update',
      factAdded: 'fact_added',
      reasoningResult: 'reasoning_result'
    }
  },
  
  // Application Settings
  app: {
    name: 'HAK-GAL Hexagonal',
    version: '2.0.0',
    architecture: 'Hexagonal',
    database: 'SQLite',
    factCount: 3079,
    port: 5001,
    legacy: false  // Legacy removed!
  }
};

// Helper function to build API URLs
export const buildUrl = (endpoint) => {
  return `${config.api.baseUrl}${endpoint}`;
};

// Helper function for API calls
export const apiCall = async (endpoint, options = {}) => {
  const url = buildUrl(endpoint);
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: config.api.timeout,
  };
  
  const response = await fetch(url, { ...defaultOptions, ...options });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
};

export default config;
