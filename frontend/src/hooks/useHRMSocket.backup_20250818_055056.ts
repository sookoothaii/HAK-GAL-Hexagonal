// HRM WebSocket Hook - FIXED VERSION
// Uses REST API for HRM reasoning instead of WebSocket

import { useEffect } from 'react';
import { wsService } from './useGovernorSocket';
import { useHRMStore } from '@/stores/useHRMStore';
import { toast } from 'sonner';

export const useHRMSocket = () => {
  useEffect(() => {
    const socket = (wsService as any).socket;
    if (!socket) return;

    // HRM Status Update
    const handleHRMStatus = (data: any) => {
      console.log('🧠 HRM Status Update:', data);
      useHRMStore.getState().handleHRMMetricsUpdate({
        modelStatus: data.status || 'operational',
        parameters: data.parameters || 3549825,  // GPT-5's model
        vocabulary: data.vocab_size || data.vocabulary || 694,
        device: data.device || 'cuda'
      });
    };

    // Register minimal WebSocket listeners
    socket.on('hrm_status', handleHRMStatus);
    
    // Request initial HRM status via REST API
    fetch('http://localhost:5002/api/reason', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'IsA(Test, Test)' })
    })
    .then(res => res.json())
    .then(data => {
      if (data.device) {
        useHRMStore.getState().handleHRMMetricsUpdate({
          modelStatus: 'operational',
          device: data.device
        });
      }
    })
    .catch(err => console.error('HRM status check failed:', err));

    // Cleanup
    return () => {
      socket.off('hrm_status', handleHRMStatus);
    };
  }, []);

  // Send HRM Query via REST API
  const sendHRMQuery = async (query: string) => {
    console.log('📤 Sending HRM Query via REST:', query);
    useHRMStore.getState().setHRMProcessing(true);
    
    try {
      const startTime = Date.now();
      
      // Use REST API directly
      const response = await fetch('http://localhost:5002/api/reason', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      const processingTime = Date.now() - startTime;
      
      console.log('🔮 HRM REST Result:', data);
      
      // Update store with actual neural confidence
      const confidence = data.confidence || 0;
      const isTrue = confidence > 0.5;
      
      useHRMStore.getState().addHRMQuery({
        query: data.query || query,
        confidence: confidence,  // This is the real neural confidence!
        reasoning: data.reasoning_terms || [],
        isTrue: isTrue,
        processingTime: processingTime
      });
      
      // Update neural confidence in main store if available
      if (window.useGovernorStore) {
        const store = window.useGovernorStore.getState();
        if (store.setNeuralConfidence) {
          store.setNeuralConfidence(confidence);
        }
      }
      
      // Stop processing
      useHRMStore.getState().setHRMProcessing(false);
      
      // Show confidence in toast
      const confidencePercent = (confidence * 100).toFixed(1);
      if (confidence > 0.7) {
        toast.success(`High confidence: ${confidencePercent}%`);
      } else if (confidence < 0.3) {
        toast.warning(`Low confidence: ${confidencePercent}%`);
      }
      
    } catch (error) {
      console.error('❌ HRM REST Error:', error);
      useHRMStore.getState().setHRMProcessing(false);
      toast.error('Failed to process query');
    }
  };

  // Send HRM Batch via REST API
  const sendHRMBatch = async (queries: string[]) => {
    console.log('📤 Sending HRM Batch:', queries.length, 'queries');
    
    const results = [];
    const startTime = Date.now();
    
    for (const query of queries) {
      try {
        const response = await fetch('http://localhost:5002/api/reason', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query })
        });
        
        if (response.ok) {
          const data = await response.json();
          results.push({
            query: query,
            confidence: data.confidence || 0,
            reasoning: data.reasoning_terms || [],
            isTrue: (data.confidence || 0) > 0.5,
            processingTime: 0
          });
        }
      } catch (err) {
        console.error(`Failed to process ${query}:`, err);
      }
    }
    
    const totalTime = Date.now() - startTime;
    
    // Calculate statistics
    const confidences = results.map(r => r.confidence);
    const avgConfidence = confidences.reduce((a, b) => a + b, 0) / confidences.length;
    const highCount = confidences.filter(c => c > 0.7).length;
    const lowCount = confidences.filter(c => c < 0.3).length;
    
    useHRMStore.getState().addHRMBatch({
      queries: queries,
      results: results,
      statistics: {
        totalQueries: queries.length,
        avgConfidence: avgConfidence,
        stdConfidence: 0,
        highConfidenceCount: highCount,
        lowConfidenceCount: lowCount,
        processingTime: totalTime
      }
    });
  };

  // Request Metrics via REST
  const requestMetrics = async () => {
    try {
      const response = await fetch('http://localhost:5002/api/status');
      const data = await response.json();
      console.log('📊 System Status:', data);
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    }
  };

  // Request Training Status
  const requestTrainingStatus = async () => {
    // Training status not implemented in current backend
    console.log('Training status check not available');
  };

  return {
    sendHRMQuery,
    sendHRMBatch,
    requestMetrics,
    requestTrainingStatus
  };
};