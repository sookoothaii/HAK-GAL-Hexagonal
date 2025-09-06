// useConfidenceCache.ts - Frontend Confidence Learning Cache
// ============================================================
// Implements client-side confidence history for learning feedback

import { useState, useEffect, useCallback } from 'react';

interface ConfidenceEntry {
  query: string;
  baseConfidence: number;
  adjustedConfidence: number;
  feedbackCount: number;
  lastUpdated: string;
  verifications: Array<{
    timestamp: string;
    type: 'positive' | 'negative';
    confidence: number;
  }>;
}

interface ConfidenceCache {
  entries: Record<string, ConfidenceEntry>;
  version: string;
}

const CACHE_KEY = 'hrm_confidence_cache';
const CACHE_VERSION = '1.0.0';
const MAX_VERIFICATIONS_PER_QUERY = 50;
const LEARNING_RATE = 0.1;

export const useConfidenceCache = () => {
  const [cache, setCache] = useState<ConfidenceCache>(() => {
    // Load from localStorage on init
    try {
      const stored = localStorage.getItem(CACHE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.version === CACHE_VERSION) {
          return parsed;
        }
      }
    } catch (e) {
      console.error('Failed to load confidence cache:', e);
    }
    
    // Default empty cache
    return {
      entries: {},
      version: CACHE_VERSION
    };
  });

  // Save to localStorage whenever cache changes
  useEffect(() => {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
    } catch (e) {
      console.error('Failed to save confidence cache:', e);
    }
  }, [cache]);

  /**
   * Normalize query for consistent caching
   */
  const normalizeQuery = useCallback((query: string): string => {
    const normalized = query.trim().toLowerCase();
    return normalized.endsWith('.') ? normalized : normalized + '.';
  }, []);

  /**
   * Get adjusted confidence for a query
   */
  const getAdjustedConfidence = useCallback((query: string, baseConfidence: number): {
    confidence: number;
    hasHistory: boolean;
    feedbackCount: number;
    adjustment: number;
  } => {
    const key = normalizeQuery(query);
    const entry = cache.entries[key];
    
    if (!entry || entry.verifications.length === 0) {
      return {
        confidence: baseConfidence,
        hasHistory: false,
        feedbackCount: 0,
        adjustment: 0
      };
    }
    
    // Calculate adjustment based on verification history
    let totalWeight = 0;
    let weightedScore = 0;
    const now = new Date().getTime();
    
    entry.verifications.forEach((verification, index) => {
      const age = now - new Date(verification.timestamp).getTime();
      const ageHours = age / (1000 * 60 * 60);
      
      // Exponential decay - recent feedback matters more
      const weight = Math.pow(0.95, ageHours / 24); // Daily decay
      
      // Positive feedback increases confidence, negative decreases
      const score = verification.type === 'positive' ? 1.0 : -0.5;
      
      weightedScore += weight * score;
      totalWeight += weight;
    });
    
    if (totalWeight === 0) {
      return {
        confidence: baseConfidence,
        hasHistory: true,
        feedbackCount: entry.verifications.length,
        adjustment: 0
      };
    }
    
    // Calculate adjustment
    const averageScore = weightedScore / totalWeight;
    const confidenceFactor = Math.min(1.0, entry.verifications.length / 10); // More data = stronger adjustment
    const adjustment = LEARNING_RATE * averageScore * confidenceFactor;
    
    // Apply adjustment with bounds
    const adjustedConfidence = Math.max(0, Math.min(1, baseConfidence + adjustment));
    
    return {
      confidence: adjustedConfidence,
      hasHistory: true,
      feedbackCount: entry.verifications.length,
      adjustment: adjustment
    };
  }, [cache, normalizeQuery]);

  /**
   * Add verification feedback for a query
   */
  const addVerification = useCallback((
    query: string,
    type: 'positive' | 'negative',
    confidence: number
  ): void => {
    const key = normalizeQuery(query);
    
    setCache(prevCache => {
      const newCache = { ...prevCache };
      
      // Initialize entry if needed
      if (!newCache.entries[key]) {
        newCache.entries[key] = {
          query: query,
          baseConfidence: confidence,
          adjustedConfidence: confidence,
          feedbackCount: 0,
          lastUpdated: new Date().toISOString(),
          verifications: []
        };
      }
      
      // Add verification
      const entry = newCache.entries[key];
      entry.verifications.push({
        timestamp: new Date().toISOString(),
        type: type,
        confidence: confidence
      });
      
      // Limit verification history
      if (entry.verifications.length > MAX_VERIFICATIONS_PER_QUERY) {
        entry.verifications = entry.verifications.slice(-MAX_VERIFICATIONS_PER_QUERY);
      }
      
      // Update metadata
      entry.feedbackCount = entry.verifications.length;
      entry.lastUpdated = new Date().toISOString();
      
      // Calculate new adjusted confidence
      const adjustment = getAdjustedConfidence(query, confidence);
      entry.adjustedConfidence = adjustment.confidence;
      
      return newCache;
    });
  }, [normalizeQuery, getAdjustedConfidence]);

  /**
   * Get statistics about the cache
   */
  const getStatistics = useCallback(() => {
    const totalQueries = Object.keys(cache.entries).length;
    const totalFeedback = Object.values(cache.entries).reduce(
      (sum, entry) => sum + entry.verifications.length, 0
    );
    
    const positiveFeedback = Object.values(cache.entries).reduce(
      (sum, entry) => sum + entry.verifications.filter(v => v.type === 'positive').length, 0
    );
    
    const negativeFeedback = totalFeedback - positiveFeedback;
    
    const averageAdjustment = totalQueries > 0
      ? Object.values(cache.entries).reduce(
          (sum, entry) => sum + (entry.adjustedConfidence - entry.baseConfidence), 0
        ) / totalQueries
      : 0;
    
    return {
      totalQueries,
      totalFeedback,
      positiveFeedback,
      negativeFeedback,
      averageAdjustment,
      cacheSize: JSON.stringify(cache).length
    };
  }, [cache]);

  /**
   * Clear old entries from cache
   */
  const clearOldEntries = useCallback((daysOld: number = 30): void => {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - daysOld);
    const cutoffTime = cutoff.getTime();
    
    setCache(prevCache => {
      const newCache = { ...prevCache };
      
      Object.keys(newCache.entries).forEach(key => {
        const entry = newCache.entries[key];
        const lastUpdated = new Date(entry.lastUpdated).getTime();
        
        if (lastUpdated < cutoffTime) {
          delete newCache.entries[key];
        }
      });
      
      return newCache;
    });
  }, []);

  /**
   * Clear entire cache
   */
  const clearCache = useCallback((): void => {
    setCache({
      entries: {},
      version: CACHE_VERSION
    });
  }, []);

  /**
   * Export cache data
   */
  const exportCache = useCallback((): string => {
    return JSON.stringify(cache, null, 2);
  }, [cache]);

  /**
   * Import cache data
   */
  const importCache = useCallback((data: string): boolean => {
    try {
      const parsed = JSON.parse(data);
      if (parsed.version === CACHE_VERSION) {
        setCache(parsed);
        return true;
      }
    } catch (e) {
      console.error('Failed to import cache:', e);
    }
    return false;
  }, []);

  return {
    getAdjustedConfidence,
    addVerification,
    getStatistics,
    clearOldEntries,
    clearCache,
    exportCache,
    importCache,
    cache
  };
};

export default useConfidenceCache;
