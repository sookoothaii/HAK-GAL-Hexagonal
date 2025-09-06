import { httpClient, getApiBaseUrl } from '@/services/api';

export default class ApiService {
  baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || getApiBaseUrl();
  }

  // Health (read-only)
  async health(): Promise<any> {
    const { data } = await httpClient.get(`/health`);
    return data;
  }

  // Limits & Flags (read-only)
  async limits(): Promise<any> {
    const { data } = await httpClient.get(`/api/limits`);
    return data;
  }

  // Mojo (read-only)
  async mojoStatus(): Promise<any> {
    const { data } = await httpClient.get(`/api/mojo/status`);
    return data;
  }

  async mojoBench(limit = 200, threshold = 0.95): Promise<any> {
    const { data } = await httpClient.get(`/api/mojo/bench`, { params: { limit, threshold } });
    return data;
  }

  // System status
  async status(light = false): Promise<any> {
    const { data } = await httpClient.get(`/api/status`, { params: { light: light ? 1 : undefined } });
    return data;
  }

  // Facts management
  async getFacts(limit = 100): Promise<any> {
    const { data } = await httpClient.get(`/api/facts`, { params: { limit } });
    return data;
  }

  async getFactsCount(): Promise<any> {
    const { data } = await httpClient.get(`/api/facts/count`);
    return data;
    }

  async addFact(statement: string, context = {}): Promise<any> {
    const { data } = await httpClient.post(`/api/facts`, { statement, context });
    return data;
  }

  async deleteFact(statement: string): Promise<any> {
    const { data } = await httpClient.post(`/api/facts/delete`, { statement });
    return data;
  }

  async updateFact(old_statement: string, new_statement: string): Promise<any> {
    const { data } = await httpClient.put(`/api/facts/update`, { old_statement, new_statement });
    return data;
  }

  // Reasoning
  async reason(query: string): Promise<any> {
    const { data } = await httpClient.post(`/api/reason`, { query });
    return data;
  }

  // Predicates (Top-N)
  async topPredicates(limit = 10, sampleLimit = 5000): Promise<any> {
    const { data } = await httpClient.get(`/api/predicates/top`, { params: { limit, sample_limit: sampleLimit } });
    return data;
  }

  // Enhanced API: Pagination
  async getFactsPaginated(page = 1, perPage = 50): Promise<{page:number;per_page:number;total:number;facts:any[]}> {
    const { data } = await httpClient.get(`/api/facts/paginated`, { params: { page, per_page: perPage } });
    return data;
  }

  // Enhanced API: Stats (aggregate)
  async getFactsStats(sampleLimit = 5000): Promise<any> {
    const { data } = await httpClient.get(`/api/facts/stats`, { params: { sample_limit: sampleLimit } });
    return data;
  }

  // Enhanced API: Export
  async exportFacts(limit = 1000, format: 'json' | 'jsonl' = 'json'): Promise<any> {
    const params: any = { limit, format };
    const { data } = await httpClient.get(`/api/facts/export`, { params, responseType: format === 'json' ? 'json' : 'text' as any });
    return data;
  }

  // Enhanced API: Bulk insert - WORKAROUND: Use parallel single inserts
  async bulkInsert(statements: string[]): Promise<any> {
    // Since /api/facts/bulk doesn't exist, we'll insert facts in parallel batches
    const results = {
      inserted: 0,
      errors: [] as string[],
      statements: statements.length
    };

    // Process in batches of 5 parallel requests to avoid overwhelming the server
    const batchSize = 5;
    
    for (let i = 0; i < statements.length; i += batchSize) {
      const batch = statements.slice(i, i + batchSize);
      const promises = batch.map(async (statement) => {
        try {
          await this.addFact(statement);
          return { success: true, statement };
        } catch (error: any) {
          return { 
            success: false, 
            statement, 
            error: error.response?.data?.error || error.message || 'Unknown error'
          };
        }
      });

      const batchResults = await Promise.all(promises);
      
      for (const result of batchResults) {
        if (result.success) {
          results.inserted++;
        } else {
          results.errors.push(`Failed: ${result.statement} - ${result.error}`);
        }
      }
    }

    return results;
  }

  // Analysis (read-only)
  async similarityTop(sampleLimit = 2000, threshold = 0.95, topK = 50): Promise<any> {
    const { data } = await httpClient.get(`/api/analysis/similarity-top`, { params: { sample_limit: sampleLimit, threshold, top_k: topK } });
    return data;
  }

  async dupesPPJoin(sampleLimit = 2000, threshold = 0.9, topK = 100): Promise<any> {
    const { data } = await httpClient.get(`/api/analysis/dupes-ppjoin`, { params: { sample_limit: sampleLimit, threshold, top_k: topK } });
    return data;
  }
}
