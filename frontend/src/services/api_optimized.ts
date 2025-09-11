import axios from 'axios';
import { appConfig } from '@/config/app.config';

// REALISTISCHE KONFIGURATION basierend auf gemessener Performance
const baseURL = appConfig.API_BASE_URL;
const apiKey = appConfig.API_KEY;

// Cache für API-Responses (wichtig bei 0.5 req/s Performance!)
const responseCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 30000; // 30 Sekunden Cache wegen langsamer API

console.log(`⚠️ API Performance: ~0.5 req/s (2000ms pro Request) - Cache aktiviert`);

export const httpClient = axios.create({
  baseURL,
  timeout: 5000, // 5 Sekunden Timeout (API braucht ~2s pro Request)
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

// Request Interceptor mit API Key
httpClient.interceptors.request.use((config) => {
  if (apiKey) {
    config.headers = config.headers || {};
    (config.headers as any)['X-API-Key'] = apiKey;
  }
  
  // Cache-Check für GET Requests
  if (config.method === 'get') {
    const cacheKey = `${config.url}?${JSON.stringify(config.params || {})}`;
    const cached = responseCache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      console.log(`📦 Cache Hit: ${config.url}`);
      // Return cached response direkt
      return Promise.reject({
        __cached: true,
        data: cached.data,
        config
      });
    }
  }
  
  return config;
});

// Response Interceptor mit Cache und Performance-Logging
httpClient.interceptors.response.use(
  (response) => {
    const duration = Date.now() - (response.config as any).__startTime;
    console.log(`✅ API Response: ${response.config?.url} (${duration}ms)`);
    
    // Cache GET responses
    if (response.config.method === 'get') {
      const cacheKey = `${response.config.url}?${JSON.stringify(response.config.params || {})}`;
      responseCache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now()
      });
    }
    
    // Warnung bei langsamen Requests
    if (duration > 1500) {
      console.warn(`⚠️ Slow API: ${response.config?.url} took ${duration}ms`);
    }
    
    return response;
  },
  (error) => {
    // Handle cached responses
    if (error.__cached) {
      return Promise.resolve({ 
        data: error.data, 
        status: 200, 
        cached: true,
        config: error.config 
      });
    }
    
    console.error(`❌ API Error: ${error.config?.url}`, {
      status: error.response?.status,
      message: error.message
    });
    
    // Bei Timeout: Hinweis auf Performance-Problem
    if (error.code === 'ECONNABORTED') {
      console.error('⏱️ API Timeout - Die API ist sehr langsam (0.5 req/s)');
    }
    
    return Promise.reject(error);
  }
);

// Performance-aware API functions
export const api = {
  // Batch multiple fact additions (wichtig bei langsamer API!)
  async addFactsBatch(facts: string[]): Promise<any> {
    const results = [];
    for (const fact of facts) {
      try {
        const result = await httpClient.post('/api/facts', { statement: fact });
        results.push({ fact, success: true, data: result.data });
      } catch (error) {
        results.push({ fact, success: false, error });
      }
    }
    return results;
  },
  
  // Get facts count mit Cache
  async getFactsCount(): Promise<number> {
    const response = await httpClient.get('/api/facts/count');
    return response.data.count;
  },
  
  // Search mit Cache
  async searchFacts(query: string, limit = 10): Promise<any> {
    return httpClient.post('/api/search', { query, limit });
  },
  
  // Reasoning mit Timeout-Warnung
  async reason(query: string): Promise<any> {
    console.warn('⏱️ Reasoning kann 2-3 Sekunden dauern...');
    return httpClient.post('/api/reason', { query });
  },
  
  // Clear Cache
  clearCache(): void {
    responseCache.clear();
    console.log('📦 Cache geleert');
  }
};

// Track request timing
httpClient.interceptors.request.use((config) => {
  (config as any).__startTime = Date.now();
  return config;
});

export const getApiBaseUrl = (): string => baseURL;

// Export cache stats for debugging
export const getCacheStats = () => ({
  size: responseCache.size,
  entries: Array.from(responseCache.keys())
});