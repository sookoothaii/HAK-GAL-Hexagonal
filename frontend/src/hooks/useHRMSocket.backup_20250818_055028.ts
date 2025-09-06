// HRM WebSocket Hook
// Integrates HRM events with the frontend

import { useEffect } from 'react';
import { wsService } from './useGovernorSocket';
import { useHRMStore } from '@/stores/useHRMStore';

export const useHRMSocket = () => {
  useEffect(() => {
    const socket = (wsService as any).socket;
    if (!socket) return;

    // HRM Status Update
    const handleHRMStatus = (data: any) => {
      console.log('🧠 HRM Status Update:', data);
      useHRMStore.getState().handleHRMMetricsUpdate({
        modelStatus: data.status || 'operational',
        parameters: data.parameters || 572673,
        vocabulary: data.vocabulary || 694,
        device: data.device || 'cuda'
      });
    };

    // HRM Query Result
    const handleHRMResult = (data: any) => {
      console.log('🔮 HRM Query Result:', data);
      
      // Determine if statement is likely true based on confidence
      const isTrue = data.confidence > 0.5;
      
      useHRMStore.getState().addHRMQuery({
        query: data.query || '',
        confidence: data.confidence || 0,
        reasoning: data.reasoning_terms || [],
        isTrue: isTrue,
        processingTime: data.processing_time || 0
      });
      
      // Stop processing
      useHRMStore.getState().setHRMProcessing(false);
    };

    // HRM Batch Result
    const handleHRMBatchResult = (data: any) => {
      console.log('📦 HRM Batch Result:', data);
      
      if (data.results && data.statistics) {
        useHRMStore.getState().addHRMBatch({
          queries: data.results.map((r: any) => r.query),
          results: data.results.map((r: any) => ({
            query: r.query,
            confidence: r.confidence,
            reasoning: r.reasoning_terms || [],
            isTrue: r.confidence > 0.5,
            processingTime: 0
          })),
          statistics: data.statistics
        });
      }
    };

    // HRM Metrics Update (Prometheus)
    const handleHRMMetrics = (data: any) => {
      console.log('📊 HRM Prometheus Metrics:', data);
      
      if (data.summary) {
        useHRMStore.getState().updatePrometheusMetrics({
          hrm_model_parameters: data.summary.model_parameters,
          hrm_confidence_gap: data.summary.confidence_gap,
          hrm_requests_total: data.summary.total_requests
        });
      }
    };

    // HRM Training Status
    const handleHRMTrainingStatus = (data: any) => {
      console.log('🎓 HRM Training Status:', data);
      
      useHRMStore.getState().updateTrainingStatus({
        totalEpochsTrained: data.total_epochs_trained || 0,
        bestGapAchieved: data.best_gap_achieved || 0,
        trainingSessions: data.training_sessions || 0,
        currentGap: data.current_gap || 0,
        readyForTraining: data.ready_for_training || false,
        lastTraining: data.last_training
      });
    };

    // HRM Error
    const handleHRMError = (data: any) => {
      console.error('❌ HRM Error:', data);
      useHRMStore.getState().setHRMProcessing(false);
    };

    // Register event listeners
    socket.on('hrm_status', handleHRMStatus);
    socket.on('hrm_result', handleHRMResult);
    socket.on('hrm_batch_result', handleHRMBatchResult);
    socket.on('hrm_metrics', handleHRMMetrics);
    socket.on('hrm_training_status', handleHRMTrainingStatus);
    socket.on('hrm_error', handleHRMError);

    // Request initial HRM status
    socket.emit('hrm_status_request');

    // Cleanup
    return () => {
      socket.off('hrm_status', handleHRMStatus);
      socket.off('hrm_result', handleHRMResult);
      socket.off('hrm_batch_result', handleHRMBatchResult);
      socket.off('hrm_metrics', handleHRMMetrics);
      socket.off('hrm_training_status', handleHRMTrainingStatus);
      socket.off('hrm_error', handleHRMError);
    };
  }, []);

  // Send HRM Query
  const sendHRMQuery = (query: string) => {
    console.log('📤 Sending HRM Query:', query);
    useHRMStore.getState().setHRMProcessing(true);
    wsService.emit('hrm_reason', { query });
  };

  // Send HRM Batch
  const sendHRMBatch = (queries: string[]) => {
    console.log('📤 Sending HRM Batch:', queries.length, 'queries');
    wsService.emit('hrm_batch_reason', { queries });
  };

  // Request Metrics
  const requestMetrics = () => {
    wsService.emit('hrm_metrics_request');
  };

  // Request Training Status
  const requestTrainingStatus = () => {
  import('@/config/backends').then(({ API_BASE_URL }) => fetch(`${API_BASE_URL}/api/hrm/training/status`))
      .then(res => res.json())
      .then(data => {
        useHRMStore.getState().updateTrainingStatus(data);
      })
      .catch(err => console.error('Failed to fetch training status:', err));
  };

  return {
    sendHRMQuery,
    sendHRMBatch,
    requestMetrics,
    requestTrainingStatus
  };
};
