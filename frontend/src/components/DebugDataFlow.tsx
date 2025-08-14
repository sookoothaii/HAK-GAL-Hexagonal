// Debug helper to verify WebSocket data flow
import { useEffect } from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';

export const DebugDataFlow: React.FC = () => {
  const isConnected = useGovernorStore(state => state.isConnected);
  const kbMetrics = useGovernorStore(state => state.kb.metrics);
  const governor = useGovernorStore(state => state.governor);
  const engines = useGovernorStore(state => state.engines);

  useEffect(() => {
    // Log state changes
    console.log('🔍 Debug - Connection Status:', isConnected);
    console.log('🔍 Debug - KB Metrics:', kbMetrics);
    console.log('🔍 Debug - Governor:', governor);
    console.log('🔍 Debug - Engines:', engines);
  }, [isConnected, kbMetrics, governor, engines]);

  return null;
};

// Add to Dashboard for debugging
export default DebugDataFlow;
