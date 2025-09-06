// HAK-GAL Socket Hook - NOW USES CENTRAL WEBSOCKET
import { useEffect } from 'react';
import wsManager from '@/utils/centralWebSocket';

export const useHakGalSocket = () => {
  useEffect(() => {
    const socket = wsManager.getSocket();
    if (!socket) {
      console.log('[HakGalSocket] Waiting for central socket...');
      return;
    }
    
    console.log('[HakGalSocket] Using central WebSocket connection');
    
    // Setup HAK-GAL specific event listeners if needed
    socket.on('hakgal_update', (data: any) => {
      console.log('[HakGalSocket] HAK-GAL Update:', data);
    });
    
    return () => {
      // Cleanup listeners
      socket.off('hakgal_update');
    };
  }, []);
};

export default useHakGalSocket;
