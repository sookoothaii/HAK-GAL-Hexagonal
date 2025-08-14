// Store Bridge - Connects unified WebSocket to existing stores
// Progressive migration approach - maintains backward compatibility
// This allows gradual migration from 3 stores to unified architecture

import { useEffect } from 'react';
import { getWebSocketManager } from '@/core/websocket/WebSocketManager';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { useHRMStore } from '@/stores/useHRMStore';
import { useIntelligenceStore } from '@/stores/useIntelligenceStore';

/**
 * Bridge Hook - Routes WebSocket events to existing stores
 * This maintains backward compatibility while we migrate to unified store
 * 
 * Migration Plan:
 * 1. Use this bridge initially (current)
 * 2. Gradually move components to unified store
 * 3. Remove bridge once all components migrated
 */
export const useStoreBridge = () => {
  const wsManager = getWebSocketManager();
  
  useEffect(() => {
    // Connect WebSocket
    wsManager.connect();
    
    // Get store actions
    const governorStore = useGovernorStore.getState();
    const hrmStore = useHRMStore.getState();
    const intelligenceStore = useIntelligenceStore.getState();
    
    // ============= Event Routing Map =============
    
    // Connection Events
    const handleConnectionStatus = (data: any) => {
      governorStore.handleConnectionStatus(data.connected);
      intelligenceStore.setConnectionStatus(data.connected);
    };
    
    // KB Events
    const handleKBUpdate = (data: any) => {
      // Route to Governor Store
      governorStore.handleKbUpdate(data);
      
      // Route to Intelligence Store
      if (data.factCount !== undefined) {
        intelligenceStore.updateKnowledgeBase({
          totalFacts: data.factCount,
          growthRate: data.growthRate
        });
      }
    };
    
    // Governor Events
    const handleGovernorUpdate = (data: any) => {
      governorStore.handleGovernorUpdate(data);
      
      // Also update Intelligence Store
      intelligenceStore.updateGovernor({
        status: data.status?.running ? 'running' : 'stopped',
        alpha: data.alpha,
        beta: data.beta,
        learningRate: data.learningRate
      });
    };
    
    // HRM Events
    const handleHRMUpdate = (data: any) => {
      // Route to HRM Store
      if (hrmStore.updateFromWebSocket) {
        hrmStore.updateFromWebSocket(data);
      }
      
      // Route to Intelligence Store
      intelligenceStore.handleHRMUpdate(data);
    };
    
    // System Events
    const handleSystemLoad = (data: any) => {
      governorStore.handleSystemLoadUpdate(data);
      intelligenceStore.updateMetrics({
        memoryUsage: data.memory,
        gpuUsage: data.gpu
      });
    };
    
    // LLM Events
    const handleLLMStatus = (data: any) => {
      governorStore.handleLlmUpdate(data);
      intelligenceStore.updateLLMStatus(data);
    };
    
    // Engine Events
    const handleEngineUpdate = (data: any) => {
      governorStore.handleEnginesUpdate(data);
    };
    
    // Reasoning Events
    const handleReasoningComplete = (data: any) => {
      // Update query in Governor Store
      if (data.queryId) {
        governorStore.updateQueryResponse(data.queryId, {
          status: 'success',
          ...data.response
        });
      }
      
      // Update Intelligence Store
      intelligenceStore.handleIntelligenceUpdate({
        neural: data.neural,
        knowledge: data.knowledge
      });
    };
    
    // ============= Register Event Handlers =============
    
    wsManager.on('connection_status', handleConnectionStatus);
    wsManager.on('kb_update', handleKBUpdate);
    wsManager.on('kb_metrics', handleKBUpdate);
    wsManager.on('governor_update', handleGovernorUpdate);
    wsManager.on('hrm_update', handleHRMUpdate);
    wsManager.on('hrm_status', handleHRMUpdate);
    wsManager.on('system_load', handleSystemLoad);
    wsManager.on('llm_status', handleLLMStatus);
    wsManager.on('engine_status', handleEngineUpdate);
    wsManager.on('engines_update', handleEngineUpdate);
    wsManager.on('reasoning_complete', handleReasoningComplete);
    
    // ============= Cleanup =============
    
    return () => {
      wsManager.off('connection_status', handleConnectionStatus);
      wsManager.off('kb_update', handleKBUpdate);
      wsManager.off('kb_metrics', handleKBUpdate);
      wsManager.off('governor_update', handleGovernorUpdate);
      wsManager.off('hrm_update', handleHRMUpdate);
      wsManager.off('hrm_status', handleHRMUpdate);
      wsManager.off('system_load', handleSystemLoad);
      wsManager.off('llm_status', handleLLMStatus);
      wsManager.off('engine_status', handleEngineUpdate);
      wsManager.off('engines_update', handleEngineUpdate);
      wsManager.off('reasoning_complete', handleReasoningComplete);
    };
  }, []);
  
  return wsManager;
};

/**
 * Migration Status Tracker
 * Tracks which components have been migrated to unified store
 */
export const MIGRATION_STATUS = {
  components: {
    ProDashboard: false,        // Still uses useGovernorStore
    ProUnifiedQuery: false,      // Still uses useIntelligenceStore
    ProGovernorControl: false,   // Still uses useGovernorStore
    ProSystemMonitoring: false,  // Still uses useGovernorStore
    ProKnowledgeStats: false,    // Still uses useGovernorStore
    HRMDashboard: false,         // Still uses useHRMStore
  },
  stores: {
    governor: 'active',         // Still needed
    hrm: 'active',             // Still needed
    intelligence: 'active',     // Still needed
    unified: 'created'          // Ready for migration
  },
  websockets: {
    previous: 3,               // Was using 3 separate connections
    current: 1,                // Now using 1 unified connection
    reduction: '66%'           // Performance improvement
  }
};

// Export for debugging
if (typeof window !== 'undefined') {
  (window as any).__STORE_BRIDGE__ = {
    migrationStatus: MIGRATION_STATUS,
    wsManager: getWebSocketManager()
  };
}

export default useStoreBridge;
