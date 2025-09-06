import axios from 'axios';

// Bevorzuge Proxy-BaseURL; niemals auf window.origin (5173) zurückfallen
const envBase = (import.meta as any)?.env?.VITE_API_BASE_URL;
const baseURL = envBase && String(envBase).length > 0 ? String(envBase) : 'http://localhost:8088';

// TEMPORARILY DISABLED: API key causing CORS issues with Caddy
// const apiKey = (import.meta as any)?.env?.VITE_API_KEY || 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d';

import { appConfig } from '@/config/app.config';

export const httpClient = axios.create({
  baseURL,
  timeout: appConfig.API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

// TEMPORARILY DISABLED: Don't send API key to avoid CORS issues
/*
httpClient.interceptors.request.use((config) => {
  // Add API key for write operations
  const needsApiKey = config.url && (
    config.url.includes('/api/facts') ||
    config.url.includes('/api/command') ||
    config.url.includes('/api/governor/start') ||
    config.url.includes('/api/governor/stop')
  ) && config.method && ['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase());
  
  if (needsApiKey || apiKey) {
    config.headers = config.headers || {};
    (config.headers as any)['X-API-Key'] = apiKey || 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d';
  }
  
  return config;
});
*/

export const getApiBaseUrl = (): string => baseURL;