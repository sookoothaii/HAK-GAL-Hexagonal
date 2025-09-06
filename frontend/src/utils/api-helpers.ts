/**
 * Utility functions for robust API calls with graceful error handling
 * Handles 405/404/501 errors silently and returns fallback values
 */

import { httpClient } from '@/services/api';

export interface ApiCallOptions<T> {
  fallback?: T | null;
  onError?: (error: any) => void;
  silent?: boolean;
  retryMethods?: ('GET' | 'POST')[];
}

/**
 * Make a robust API call with automatic fallback handling
 * @param apiCall Function that returns a promise with the API call
 * @param options Configuration options for error handling
 * @returns The API response or fallback value
 */
export async function safeApiCall<T>(
  apiCall: () => Promise<T>,
  options: ApiCallOptions<T> = {}
): Promise<T | null> {
  const { fallback = null, onError, silent = true } = options;
  
  try {
    return await apiCall();
  } catch (error: any) {
    const status = error?.response?.status;
    const isExpectedError = status === 405 || status === 404 || status === 501;
    
    if (isExpectedError && silent) {
      // Silently handle expected missing endpoints
      console.debug(`Endpoint not available: ${error?.config?.url} (${status})`);
    } else if (onError) {
      onError(error);
    } else if (!silent) {
      console.error('API call failed:', error);
    }
    
    return fallback;
  }
}

/**
 * Try multiple HTTP methods if one fails with 405
 * @param endpoint The API endpoint
 * @param methods Array of methods to try in order
 * @param data Optional data for POST requests
 * @returns The first successful response or null
 */
export async function tryMultipleMethods<T>(
  endpoint: string,
  methods: ('GET' | 'POST')[] = ['GET', 'POST'],
  data?: any
): Promise<T | null> {
  for (const method of methods) {
    try {
      const response = await httpClient.request({
        method,
        url: endpoint,
        ...(method === 'POST' && data ? { data } : {})
      });
      return response.data;
    } catch (error: any) {
      const status = error?.response?.status;
      if (status === 405) {
        // Method not allowed, try next method
        console.debug(`Method ${method} not allowed for ${endpoint}, trying next...`);
        continue;
      }
      // Other errors, return null
      break;
    }
  }
  return null;
}

/**
 * Try multiple endpoints until one succeeds
 * @param endpoints Array of endpoints to try
 * @param method HTTP method to use
 * @returns The first successful response or null
 */
export async function tryMultipleEndpoints<T>(
  endpoints: string[],
  method: 'GET' | 'POST' = 'GET'
): Promise<T | null> {
  for (const endpoint of endpoints) {
    const result = await safeApiCall<T>(
      async () => (await httpClient.request({ method, url: endpoint })).data,
      { silent: true }
    );
    
    if (result !== null) {
      return result;
    }
  }
  return null;
}

/**
 * Batch multiple API calls with individual error handling
 * @param calls Array of API call configurations
 * @returns Array of results (successful responses or null for failures)
 */
export async function batchApiCalls<T>(
  calls: Array<{
    call: () => Promise<T>;
    fallback?: T | null;
  }>
): Promise<(T | null)[]> {
  return Promise.all(
    calls.map(({ call, fallback }) => 
      safeApiCall(call, { fallback, silent: true })
    )
  );
}

/**
 * Helper to check if an endpoint exists before calling it
 * @param endpoint The endpoint to check
 * @returns True if endpoint responds with 2xx or 3xx
 */
export async function endpointExists(endpoint: string): Promise<boolean> {
  try {
    const response = await httpClient.head(endpoint);
    return response.status >= 200 && response.status < 400;
  } catch (error: any) {
    // Try OPTIONS as fallback
    try {
      const response = await httpClient.options(endpoint);
      return response.status >= 200 && response.status < 400;
    } catch {
      return false;
    }
  }
}

/**
 * Cache for endpoint availability to avoid repeated checks
 */
const endpointCache = new Map<string, boolean>();

/**
 * Check if endpoint exists with caching
 * @param endpoint The endpoint to check
 * @param ttl Cache time-to-live in milliseconds (default: 5 minutes)
 * @returns True if endpoint is available
 */
export async function checkEndpointCached(
  endpoint: string,
  ttl: number = 5 * 60 * 1000
): Promise<boolean> {
  const cacheKey = endpoint;
  const cached = endpointCache.get(cacheKey);
  
  if (cached !== undefined) {
    // Cache hit
    return cached;
  }
  
  const exists = await endpointExists(endpoint);
  endpointCache.set(cacheKey, exists);
  
  // Clear cache after TTL
  setTimeout(() => {
    endpointCache.delete(cacheKey);
  }, ttl);
  
  return exists;
}

/**
 * Create a fallback chain for API calls
 * @param primary Primary API call
 * @param fallbacks Array of fallback functions to try in order
 * @returns The first successful result
 */
export async function withFallbacks<T>(
  primary: () => Promise<T>,
  ...fallbacks: Array<() => Promise<T> | T>
): Promise<T | null> {
  // Try primary
  const primaryResult = await safeApiCall(primary, { silent: true });
  if (primaryResult !== null) {
    return primaryResult;
  }
  
  // Try fallbacks in order
  for (const fallback of fallbacks) {
    try {
      const result = await fallback();
      if (result !== null && result !== undefined) {
        return result;
      }
    } catch {
      continue;
    }
  }
  
  return null;
}
