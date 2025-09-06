// HRM Socket Hook - ORIGINAL VERSION
import { useEffect } from 'react';
import { io, Socket } from 'socket.io-client';
import { useHRMStore } from '@/stores/useHRMStore';
import { getApiBaseUrl } from '@/services/api';

let socket: Socket | null = null;

export const useHRMSocket = () => {
  useEffect(() => {
    if (!socket) {
      const baseUrl = getApiBaseUrl();
      socket = io(baseUrl, {
        path: '/socket.io',
        transports: ['websocket', 'polling'],
        reconnection: true,
      });
      
      console.log('[HRMSocket] Connecting to', baseUrl);
    }
    
    const hrmStore = useHRMStore.getState();
    
    // Setup HRM-specific event listeners
    socket.on('hrm_update', (data: any) => {
      console.log('[HRMSocket] HRM Update:', data);
      if (hrmStore.updateFromWebSocket) {
        hrmStore.updateFromWebSocket(data);
      }
    });
    
    socket.on('hrm_status', (data: any) => {
      console.log('[HRMSocket] HRM Status:', data);
      if (hrmStore.updateFromWebSocket) {
        hrmStore.updateFromWebSocket(data);
      }
    });
    
    return () => {
      // Don't disconnect on unmount - keep connection alive
    };
  }, []);
};

export default useHRMSocket;
