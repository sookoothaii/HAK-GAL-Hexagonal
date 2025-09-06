// Intelligence Socket Hook - ORIGINAL VERSION
import { useEffect } from 'react';
import { io, Socket } from 'socket.io-client';
import { useIntelligenceStore } from '@/stores/useIntelligenceStore';
import { getApiBaseUrl } from '@/services/api';

let socket: Socket | null = null;

export const useIntelligenceSocket = () => {
  useEffect(() => {
    if (!socket) {
      const baseUrl = getApiBaseUrl();
      socket = io(baseUrl, {
        path: '/socket.io',
        transports: ['websocket', 'polling'],
        reconnection: true,
      });
      
      console.log('[IntelligenceSocket] Connecting to', baseUrl);
    }
    
    const intelligenceStore = useIntelligenceStore.getState();
    
    // Setup Intelligence-specific event listeners
    socket.on('intelligence_update', (data: any) => {
      console.log('[IntelligenceSocket] Intelligence Update:', data);
      intelligenceStore.handleIntelligenceUpdate(data);
    });
    
    socket.on('neural_update', (data: any) => {
      console.log('[IntelligenceSocket] Neural Update:', data);
      intelligenceStore.updateNeuralStatus(data);
    });
    
    socket.on('knowledge_update', (data: any) => {
      console.log('[IntelligenceSocket] Knowledge Update:', data);
      intelligenceStore.updateKnowledgeBase(data);
    });
    
    return () => {
      // Don't disconnect on unmount - keep connection alive
    };
  }, []);
};

export default useIntelligenceSocket;
