/**
 * Dynamic Default Loader
 * Loads initial values from backend instead of using hardcoded defaults
 */

import { httpClient } from '@/services/api';
import { appConfig } from '@/config/app.config';

export interface SystemDefaults {
  factCount: number;
  growthRate: number;
  entityCount: number;
  predicateCount: number;
  nodeCount: number;
  edgeCount: number;
}

class DefaultsService {
  private cache: SystemDefaults | null = null;
  private loadPromise: Promise<SystemDefaults> | null = null;

  /**
   * Load system defaults from backend
   */
  async loadDefaults(): Promise<SystemDefaults> {
    // Return cached values if available
    if (this.cache) {
      return this.cache;
    }

    // Return existing promise if already loading
    if (this.loadPromise) {
      return this.loadPromise;
    }

    // Start loading
    this.loadPromise = this._loadFromBackend();
    
    try {
      this.cache = await this.loadPromise;
      return this.cache;
    } catch (error) {
      console.error('Failed to load defaults from backend:', error);
      // Return app config defaults as fallback
      return this.getFallbackDefaults();
    } finally {
      this.loadPromise = null;
    }
  }

  /**
   * Get current defaults (cached or fallback)
   */
  getDefaults(): SystemDefaults {
    return this.cache || this.getFallbackDefaults();
  }

  /**
   * Force reload defaults from backend
   */
  async reloadDefaults(): Promise<SystemDefaults> {
    this.cache = null;
    return this.loadDefaults();
  }

  /**
   * Private method to load from backend
   */
  private async _loadFromBackend(): Promise<SystemDefaults> {
    try {
      // Try to get KB metrics first
      const kbResponse = await httpClient.get('/api/status');
      
      if (kbResponse.status === 200 && kbResponse.data) {
        const data = kbResponse.data;
        
        // Extract values with multiple fallback paths for different backend versions
        const factCount = 
          data.knowledge_base_facts || 
          data.fact_count || 
          data.factCount || 
          data.kb_metrics?.fact_count ||
          data.kb_metrics?.factCount ||
          0;

        const predicateCount = 
          data.unique_predicates || 
          data.predicate_count || 
          data.predicateCount ||
          data.kb_metrics?.unique_predicates ||
          data.kb_metrics?.predicateCount ||
          0;

        const entityCount = 
          data.unique_entities || 
          data.entity_count || 
          data.entityCount ||
          data.kb_metrics?.unique_entities ||
          data.kb_metrics?.entityCount ||
          0;

        const growthRate = 
          data.growth_rate || 
          data.growthRate ||
          data.kb_metrics?.growth_rate ||
          data.kb_metrics?.growthRate ||
          0;

        return {
          factCount,
          growthRate,
          entityCount,
          predicateCount,
          nodeCount: entityCount, // Nodes are entities in the graph
          edgeCount: predicateCount // Edges are predicates in the graph
        };
      }
    } catch (error) {
      console.warn('KB status endpoint failed, trying facts count endpoint...');
    }

    // Return fallback defaults
    return this.getFallbackDefaults();
  }

  /**
   * Get fallback defaults from config
   */
  private getFallbackDefaults(): SystemDefaults {
    return {
      factCount: appConfig.DEFAULTS.INITIAL_FACT_COUNT,
      growthRate: appConfig.DEFAULTS.INITIAL_GROWTH_RATE,
      entityCount: appConfig.DEFAULTS.INITIAL_ENTITY_COUNT,
      predicateCount: appConfig.DEFAULTS.INITIAL_PREDICATE_COUNT,
      nodeCount: appConfig.DEFAULTS.INITIAL_ENTITY_COUNT,
      edgeCount: appConfig.DEFAULTS.INITIAL_PREDICATE_COUNT
    };
  }
}

// Export singleton instance
export const defaultsService = new DefaultsService();

// Helper function to initialize defaults on app start
export const initializeDefaults = async (): Promise<void> => {
  try {
    const defaults = await defaultsService.loadDefaults();
    console.log('📊 Loaded system defaults:', defaults);
    
    // Update the store if available
    if (typeof window !== 'undefined' && (window as any).__GOVERNOR_STORE__) {
      const store = (window as any).__GOVERNOR_STORE__.getState();
      store.handleKbUpdate({
        metrics: {
          factCount: defaults.factCount,
          growthRate: defaults.growthRate,
          nodeCount: defaults.nodeCount,
          edgeCount: defaults.edgeCount,
          connectivity: 0,
          entropy: 0
        }
      });
    }
  } catch (error) {
    console.error('Failed to initialize defaults:', error);
  }
};