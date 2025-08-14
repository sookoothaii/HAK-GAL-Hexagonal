// useIntelligenceSocket.ts - Unified WebSocket handling for all intelligence layers
// Nach HAK/GAL Artikel 5 (System-Metareflexion)

import { useEffect } from 'react';
import { useIntelligenceStore } from '@/stores/useIntelligenceStore';
import wsService from '@/services/websocket';

export const useIntelligenceSocket = () => {
  const store = useIntelligenceStore();
  
  useEffect(() => {
    // Connection handlers
    const handleConnect = () => {
      console.log('[Intelligence Socket] Connected');
      store.setConnectionStatus(true);
    };
    
    const handleDisconnect = () => {
      console.log('[Intelligence Socket] Disconnected');
      store.setConnectionStatus(false);
    };
    
    // Intelligence layer updates
    const handleIntelligenceUpdate = (data: any) => {
      console.log('[Intelligence Socket] Intelligence update:', data);
      store.handleIntelligenceUpdate(data);
    };
    
    const handleHRMUpdate = (data: any) => {
      console.log('[Intelligence Socket] HRM update:', data);
      store.handleHRMUpdate(data);
    };
    
    const handlePhilosophicalUpdate = (data: any) => {
      console.log('[Intelligence Socket] Philosophical update:', data);
      store.handlePhilosophicalUpdate(data);
    };
    
    const handleTrustUpdate = (data: any) => {
      console.log('[Intelligence Socket] Trust update:', data);
      store.handleTrustUpdate(data);
    };
    
    // Knowledge base updates
    const handleKBUpdate = (data: any) => {
      console.log('[Intelligence Socket] KB update:', data);
      if (data.total_facts !== undefined) {
        store.updateKnowledgeBase({
          factCount: data.total_facts,
          growthRate: data.growth_rate || 0,
          categories: data.categories || {}
        });
      }
    };
    
    // System metrics
    const handleMetricsUpdate = (data: any) => {
      console.log('[Intelligence Socket] Metrics update:', data);
      store.updateMetrics(data);
    };
    
    // Governor updates
    const handleGovernorUpdate = (data: any) => {
      console.log('[Intelligence Socket] Governor update:', data);
      if (data.status) {
        store.updateGovernor({
          status: data.status,
          alpha: data.alpha || 0,
          beta: data.beta || 0,
          lastAction: data.last_action || '',
          learningRate: data.learning_rate || 0
        });
      }
    };
    
    // LLM status updates
    const handleLLMStatus = (data: any) => {
      console.log('[Intelligence Socket] LLM status:', data);
      if (data.providers) {
        store.updateLLMStatus({
          providers: data.providers,
          activeCount: Object.values(data.providers).filter((p: any) => p.status === 'online').length
        });
      }
    };
    
    // Register all event handlers
    wsService.on('connect', handleConnect);
    wsService.on('disconnect', handleDisconnect);
    wsService.on('intelligence_update', handleIntelligenceUpdate);
    wsService.on('hrm_update', handleHRMUpdate);
    wsService.on('philosophical_update', handlePhilosophicalUpdate);
    wsService.on('trust_update', handleTrustUpdate);
    wsService.on('kb_update', handleKBUpdate);
    wsService.on('metrics_update', handleMetricsUpdate);
    wsService.on('governor_update', handleGovernorUpdate);
    wsService.on('llm_status', handleLLMStatus);
    
    // Legacy events for compatibility
    wsService.on('knowledge_base_update', handleKBUpdate);
    wsService.on('system_metrics', handleMetricsUpdate);
    
    // Cleanup on unmount
    return () => {
      wsService.off('connect', handleConnect);
      wsService.off('disconnect', handleDisconnect);
      wsService.off('intelligence_update', handleIntelligenceUpdate);
      wsService.off('hrm_update', handleHRMUpdate);
      wsService.off('philosophical_update', handlePhilosophicalUpdate);
      wsService.off('trust_update', handleTrustUpdate);
      wsService.off('kb_update', handleKBUpdate);
      wsService.off('metrics_update', handleMetricsUpdate);
      wsService.off('governor_update', handleGovernorUpdate);
      wsService.off('llm_status', handleLLMStatus);
      wsService.off('knowledge_base_update', handleKBUpdate);
      wsService.off('system_metrics', handleMetricsUpdate);
    };
  }, [store]);
};

// Export für debugging
export const getIntelligenceState = () => {
  const store = useIntelligenceStore.getState();
  return {
    connected: store.isConnected,
    neural: store.neuralReasoning,
    knowledge: store.knowledgeBase,
    philosophical: store.philosophicalIntelligence,
    trust: store.trustMetrics,
    governor: store.governor,
    llm: store.llmProviders
  };
};

// Helper function to simulate a query for testing
export const simulateQuery = async (query: string) => {
  const store = useIntelligenceStore.getState();
  
  // Simulate processing
  store.processQuery({
    id: `sim-${Date.now()}`,
    query,
    status: 'processing'
  });
  
  // Simulate results after delay
  setTimeout(() => {
    store.processQuery({
      id: `sim-${Date.now()}`,
      query,
      status: 'complete',
      hrmConfidence: Math.random(),
      factCount: Math.floor(Math.random() * 10),
      llmResponse: `Simulated response for: ${query}`,
      trustScore: Math.random()
    });
  }, 2000);
};

// Add to window for debugging
if (typeof window !== 'undefined') {
  (window as any).__INTELLIGENCE_SOCKET__ = {
    getState: getIntelligenceState,
    simulateQuery
  };
}