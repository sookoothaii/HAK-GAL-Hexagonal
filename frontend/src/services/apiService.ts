/**
 * Unified API Service for HAK-GAL
 * Handles all HTTP requests to both backend systems
 */

import { API_BASE_URL, CURRENT_BACKEND } from '@/config/backends';

export default class ApiService {
  baseUrl: string;
  headers: Record<string, string>;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.headers = { 'Content-Type': 'application/json' };
  }

  async fetchWithTimeout(url: string, options: RequestInit = {}, timeout = 15000): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    try {
      return await fetch(url, { ...options, signal: controller.signal });
    } finally {
      clearTimeout(id);
    }
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

  async deleteFact(statement: string): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/facts/delete`, {
      method: 'POST', headers: this.headers, body: JSON.stringify({ statement })
    });
    return response.json();
  }

  async updateFact(old_statement: string, new_statement: string): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/facts/update`, {
      method: 'PUT', headers: this.headers, body: JSON.stringify({ old_statement, new_statement })
    });
    return response.json();
  }

  // Reasoning
  async reason(query: string): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/reason`, {
      method: 'POST', headers: this.headers, body: JSON.stringify({ query })
    });
    return response.json();
  }

  // Predicates (Top-N)
  async topPredicates(limit = 10, sampleLimit = 5000): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/predicates/top?limit=${limit}&sample_limit=${sampleLimit}`);
    return response.json();
  }

  // Enhanced API: Pagination
  async getFactsPaginated(page = 1, perPage = 50): Promise<{page:number;per_page:number;total:number;facts:any[]}> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/facts/paginated?page=${page}&per_page=${perPage}`);
    return response.json();
  }

  // Enhanced API: Stats (aggregate)
  async getFactsStats(sampleLimit = 5000): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/facts/stats?sample_limit=${sampleLimit}`);
    return response.json();
  }

  // Enhanced API: Export
  async exportFacts(limit = 1000, format: 'json' | 'jsonl' = 'json'): Promise<any> {
    const url = `${this.baseUrl}/api/facts/export?limit=${limit}&format=${format}`;
    const response = await this.fetchWithTimeout(url);
    if (format === 'json') return response.json();
    return response.text();
  }

  // Enhanced API: Bulk insert
  async bulkInsert(statements: string[]): Promise<any> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}/api/facts/bulk`, {
      method: 'POST', headers: this.headers, body: JSON.stringify({ statements })
    });
    return response.json();
  }
}
