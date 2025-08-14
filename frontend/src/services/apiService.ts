/**
 * Unified API Service for HAK-GAL
 * Handles all HTTP requests to both backend systems
 */

import { API_BASE_URL, CURRENT_BACKEND } from '@/config/backends';

class ApiService {
  private baseUrl: string;
  private headers: HeadersInit;
  
  constructor() {
    this.baseUrl = API_BASE_URL;
    this.headers = {
      'Content-Type': 'application/json',
    };
  }
  
  // Helper for fetch with timeout
  private async fetchWithTimeout(url: string, options: RequestInit = {}, timeout = 10000): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(id);
      return response;
    } catch (error) {
      clearTimeout(id);
      throw error;
    }
  }
  
  // Health check
  async health(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/health`);
    return response.json();
  }
  
  // System status
  async status(light = false): Promise<any> {
    const url = light ? `${this.baseUrl}/api/status?light=1` : `${this.baseUrl}/api/status`;
    const response = await this.fetchWithTimeout(url);
    return response.json();
  }
  
  // Facts management
  async getFacts(limit = 100): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/facts?limit=${limit}`);
    return response.json();
  }
  
  async getFactsCount(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/facts/count`);
    return response.json();
  }
  
  async addFact(statement: string, context = {}): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/facts`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ statement, context })
    });
    return response.json();
  }
  
  // Search
  async search(query: string, limit = 10, minConfidence = 0.5): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/search`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ query, limit, min_confidence: minConfidence })
    });
    return response.json();
  }
  
  // Reasoning
  async reason(query: string): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/reason`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ query })
    });
    return response.json();
  }
  
  // Predicates (Top-N)
  async topPredicates(limit = 10, sampleLimit = 5000): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/predicates/top?limit=${limit}&sample_limit=${sampleLimit}`);
    return response.json();
  }

  // Quality metrics
  async qualityMetrics(sampleLimit = 5000): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/quality/metrics?sample_limit=${sampleLimit}`);
    return response.json();
  }
  
  // Governor control
  async governorStatus(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/governor/status`);
    return response.json();
  }
  
  async governorStart(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/governor/start`, {
      method: 'POST',
      headers: this.headers
    });
    return response.json();
  }
  
  async governorStop(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/governor/stop`, {
      method: 'POST',
      headers: this.headers
    });
    return response.json();
  }
  
  async governorDecision(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/governor/decision`);
    return response.json();
  }
  
  async governorMetrics(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/governor/metrics`);
    return response.json();
  }
  
  // Emergency Graph Functions (Hexagonal)
  async graphStatus(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/graph/emergency-status`);
    return response.json();
  }
  
  async generateGraph(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/graph/emergency-generate`, {
      method: 'POST',
      headers: this.headers
    }, 300000); // 5 minute timeout for graph generation
    return response.json();
  }
  
  async cleanDatabase(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/graph/emergency-clean`, {
      method: 'POST',
      headers: this.headers
    }, 600000); // 10 minute timeout
    return response.json();
  }
  
  async detectCorruption(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/graph/emergency-detect`, {
      method: 'POST',
      headers: this.headers
    }, 600000);
    return response.json();
  }
  
  async fixEngines(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/graph/emergency-fix-engines`, {
      method: 'POST',
      headers: this.headers
    }, 600000);
    return response.json();
  }
  
  // Architecture info
  async architecture(): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/architecture`);
    return response.json();
  }
}

// Singleton instance
const apiService = new ApiService();
export default apiService;

// Export for direct use
export { apiService, ApiService };
