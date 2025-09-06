import axios from 'axios';
import { appConfig } from '@/config/app.config';

// Use configuration from central config file
const baseURL = appConfig.API_BASE_URL;
const apiKey = appConfig.API_KEY;

console.log(`🎯 Using Caddy Proxy on port ${appConfig.PORTS.PROXY} -> Backend ${appConfig.PORTS.BACKEND}`);

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

// Enhanced error logging for proxy debugging
httpClient.interceptors.response.use(
  (response) => {
    console.log(`✅ PROXY Success: ${response.config?.method?.toUpperCase()} ${response.config?.url} -> ${response.status}`);
    return response;
  },
  (error) => {
    console.error(`❌ PROXY Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} -> ${error.response?.status || 'Network Error'}`, {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });
    return Promise.reject(error);
  }
);

export const getApiBaseUrl = (): string => baseURL;