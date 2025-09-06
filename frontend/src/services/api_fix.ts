import axios from 'axios';
import { appConfig } from '@/config/app.config';

// QUICK FIX: Direct connection to Backend on 5002
// Bypass Caddy Proxy (8088) und connect directly to hexagonal_api_enhanced_clean.py
const baseURL = 'http://localhost:5002';
const apiKey = (import.meta as any)?.env?.VITE_API_KEY || '';

export const httpClient = axios.create({
  baseURL,
  timeout: appConfig.API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

httpClient.interceptors.request.use((config) => {
  if (apiKey) {
    config.headers = config.headers || {};
    (config.headers as any)['X-API-Key'] = apiKey;
  }
  return config;
});

// Add response interceptor for better error handling
httpClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data
    });
    return Promise.reject(error);
  }
);

export const getApiBaseUrl = (): string => baseURL;

// Health check function
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const response = await httpClient.get('/health');
    return response.status === 200;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};

// Test API endpoints
export const testApiEndpoints = async () => {
  const endpoints = [
    { name: 'Health', method: 'GET', url: '/health' },
    { name: 'Status', method: 'GET', url: '/api/status' },
    { name: 'Facts Count', method: 'GET', url: '/api/facts/count' },
    { name: 'Facts List', method: 'GET', url: '/api/facts?limit=10' }
  ];

  const results = [];
  
  for (const endpoint of endpoints) {
    try {
      const response = await httpClient.request({
        method: endpoint.method,
        url: endpoint.url
      });
      results.push({
        ...endpoint,
        status: response.status,
        success: true,
        data: response.data
      });
    } catch (error: any) {
      results.push({
        ...endpoint,
        status: error.response?.status || 0,
        success: false,
        error: error.message
      });
    }
  }
  
  return results;
};