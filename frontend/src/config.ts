// src/config.ts
// Legacy config file - now imports from backends.ts for dual-backend support

import { API_BASE_URL as API_URL, WS_URL, CURRENT_BACKEND } from './config/backends';

// Export for backward compatibility
export const API_BASE_URL = API_URL;
export const WEBSOCKET_URL = WS_URL;

// Additional exports for components that need backend info
export const ACTIVE_BACKEND = CURRENT_BACKEND;

// Helper to check if current backend supports a feature
export const hasFeature = (feature: keyof typeof CURRENT_BACKEND.features): boolean => {
  return CURRENT_BACKEND.features[feature] === true;
};
