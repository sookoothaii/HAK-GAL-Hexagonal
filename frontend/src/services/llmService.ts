// LLM Service with extended timeout for long-running requests
import { httpClient } from './api';

// Special client for LLM requests with longer timeout
export const llmClient = {
  async getExplanation(data: any) {
    // Override timeout for this specific request
    return httpClient.post('/api/llm/get-explanation', data, {
      timeout: 120000, // 2 minutes specifically for LLM
      // Add custom headers if needed
      headers: {
        'Content-Type': 'application/json',
        'X-Long-Request': 'true'
      }
    });
  },
  
  async generateFacts(data: any) {
    return httpClient.post('/api/llm/generate', data, {
      timeout: 90000 // 90 seconds for fact generation
    });
  }
};

export default llmClient;
