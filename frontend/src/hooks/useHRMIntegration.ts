// useHRMIntegration.ts - Fixed integration with backend HRM (Proxy-aware)
import { useState, useEffect } from 'react';
import axios from 'axios';

export interface HRMResult {
  confidence: number;
  reasoning_terms: string[];
  device: string;
  success: boolean;
}

export const useHRMIntegration = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Detect the correct API base URL
  const getAPIBaseURL = () => {
    // Check if we're running through proxy (port 8088)
    if (window.location.port === '8088') {
      return `${window.location.protocol}//${window.location.hostname}:8088`;
    }
    // Check if we have a specific API URL in environment
    if (import.meta.env.VITE_API_BASE_URL) {
      return import.meta.env.VITE_API_BASE_URL;
    }
    // Default to proxy
    return 'http://127.0.0.1:8088';
  };
  
  const queryHRM = async (query: string): Promise<HRMResult> => {
    setIsProcessing(true);
    
    try {
      const baseURL = getAPIBaseURL();
      console.log(`[HRM] Using API base URL: ${baseURL}`);
      
      // Direct REST API call to backend HRM through proxy
      const response = await axios.post(
        `${baseURL}/api/reason`,
        { query },
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 5000
        }
      );
      
      if (response.data) {
        const confidence = response.data.confidence || 0;
        console.log(`[HRM] Query: ${query} -> Confidence: ${confidence}`);
        
        return {
          confidence: confidence,
          reasoning_terms: response.data.reasoning_terms || [],
          device: response.data.device || 'cpu',
          success: true
        };
      }
    } catch (error) {
      console.error('[HRM] Query failed:', error);
      // Log more details for debugging
      if (axios.isAxiosError(error)) {
        console.error('[HRM] Response:', error.response?.data);
        console.error('[HRM] Status:', error.response?.status);
      }
    } finally {
      setIsProcessing(false);
    }
    
    return {
      confidence: 0,
      reasoning_terms: [],
      device: 'unknown',
      success: false
    };
  };
  
  return {
    queryHRM,
    isProcessing
  };
};

// Export a global function for easy debugging
if (typeof window !== 'undefined') {
  (window as any).testHRM = async (query: string) => {
    const baseURL = window.location.port === '8088' 
      ? `${window.location.protocol}//${window.location.hostname}:8088`
      : 'http://127.0.0.1:8088';
    
    console.log(`[HRM Test] Using URL: ${baseURL}/api/reason`);
    
    const response = await fetch(`${baseURL}/api/reason`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const data = await response.json();
    console.log('[HRM Test] Result:', data);
    return data;
  };
  
  // Also add a test for the current page's query
  (window as any).testCurrentQuery = async () => {
    // Try to extract query from the page
    const queryElement = document.querySelector('[data-query]') || 
                        document.querySelector('.query-text') ||
                        document.querySelector('code');
    
    if (queryElement) {
      const query = queryElement.textContent || 'IsA(Socrates, Philosopher).';
      return (window as any).testHRM(query);
    }
    
    // Default test
    return (window as any).testHRM('IsA(Socrates, Philosopher).');
  };
}
