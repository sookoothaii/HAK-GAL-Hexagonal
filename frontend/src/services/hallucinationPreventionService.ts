/**
 * Hallucination Prevention API Service
 * Integration für HAK-GAL Frontend
 */

import axios, { AxiosInstance } from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5002';
const API_KEY = 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d';

// Types
export interface ValidationResult {
  valid: boolean;
  confidence: number;
  category: string;
  issues: string[];
  correction: string | null;
  reasoning: string;
  timestamp: string;
}

export interface BatchValidationRequest {
  fact_ids: number[];
  validation_level: 'basic' | 'comprehensive' | 'strict';
}

export interface BatchValidationResult {
  batch_id: string;
  total_facts: number;
  valid_facts: number;
  invalid_facts: number;
  success_rate: number;
  results: ValidationResult[];
  duration: number;
}

export interface QualityAnalysisResult {
  success: boolean;
  analysis: {
    total_facts: number;
    quality_assessment: string;
    predicates: Record<string, number>;
    hasproperty_percent: number;
  };
  timestamp: string;
}

export interface Statistics {
  total_validated: number;
  invalid_found: number;
  corrections_suggested: number;
  validation_time_avg: number;
  cache_hits: number;
  auto_validation_enabled: boolean;
  validation_threshold: number;
  validators_available: {
    scientific: boolean;
    maximal: boolean;
    quality_check: boolean;
    llm_reasoning: boolean;
  };
}

// API Client Class
class HallucinationPreventionService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/hallucination-prevention`,
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('Hallucination Prevention API Error:', error);
        if (error.response?.status === 403) {
          throw new Error('API Key invalid or missing');
        }
        if (error.response?.status === 500) {
          throw new Error('Server error - check request format');
        }
        throw error;
      }
    );
  }

  // Health Check
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.data.status === 'operational';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  // Get Statistics
  async getStatistics(): Promise<Statistics> {
    const response = await this.client.get('/statistics');
    return response.data.statistics;
  }

  // Single Fact Validation
  async validateFact(fact: string): Promise<ValidationResult> {
    const response = await this.client.post('/validate', { fact });
    return response.data.validation_result;
  }

  // Batch Validation
  async validateBatch(
    factIds: number[],
    level: 'basic' | 'comprehensive' | 'strict' = 'comprehensive'
  ): Promise<BatchValidationResult> {
    const response = await this.client.post('/validate-batch', {
      fact_ids: factIds,
      validation_level: level,
    });
    return response.data.batch_result;
  }

  // Quality Analysis
  async runQualityAnalysis(): Promise<QualityAnalysisResult> {
    const response = await this.client.post('/quality-analysis', {});
    return response.data;
  }

  // Suggest Correction
  async suggestCorrection(fact: string): Promise<{
    success: boolean;
    correction: string | null;
    confidence: number;
    original_issues: string[];
  }> {
    const response = await this.client.post('/suggest-correction', { fact });
    return response.data;
  }

  // Get Invalid Facts
  async getInvalidFacts(limit: number = 100): Promise<{
    count: number;
    invalid_facts: any[];
  }> {
    const response = await this.client.get(`/invalid-facts?limit=${limit}`);
    return response.data;
  }

  // Governance Compliance Check
  async checkGovernanceCompliance(fact: string): Promise<{
    compliant: boolean;
    confidence: number;
    governance_checks_passed: {
      structural: boolean;
      scientific: boolean;
      content_safety: boolean;
    };
    issues: string[];
  }> {
    const response = await this.client.post('/governance-compliance', { fact });
    return response.data.governance_compliance;
  }
}

// Export singleton instance
export const hallucinationAPI = new HallucinationPreventionService();

// Export types and class
export default HallucinationPreventionService;
