// src/hooks/useHakGalSocket.ts
import { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { useSystemStore } from '@/store/systemStore';
import { WS_URL } from '@/config/backends';

export const useHakGalSocket = () => {
  const socket = useRef<Socket | null>(null);
  const { setConnectionStatus, updateLlmStatus, addGovernorLog, updateEngineStatus } = useSystemStore(state => state.actions);
  const actions = useSystemStore(state => state.actions);

  useEffect(() => {
    // Prevent multiple connections
    if (socket.current) return;

    console.log(`[Socket] Waiting 2 seconds before connecting...`);
    const timer = setTimeout(() => {
      console.log(`[Socket] Attempting to connect to ${WS_URL}`);
      socket.current = io(WS_URL, {
        transports: ['websocket'],
        reconnectionAttempts: 5,
        reconnectionDelay: 3000,
      });

      // --- Centralized action mapping ---
      actions.sendCommand = (command: string) => {
        if (socket.current?.connected) {
          console.log(`[Socket] Sending command: ${command}`);
          socket.current.emit('command', { command });
        } else {
          console.error('[Socket] Cannot send command: not connected.');
        }
      };

      socket.current.on('connect', () => {
        console.log('[Socket] Connection established!');
        setConnectionStatus(true);
      });

      socket.current.on('disconnect', () => {
        console.log('[Socket] Connection lost.');
        setConnectionStatus(false);
      });

      // --- Register listeners for backend events ---
      
      // Example listener for LLM status updates
      socket.current.on('llm_status_update', (data) => {
        console.log('[Socket] Received llm_status_update:', data);
        updateLlmStatus(data);
      });

      // Example listener for Governor logs
      socket.current.on('governor_log', (data) => {
        console.log('[Socket] Received governor_log:', data);
        addGovernorLog(data.log);
      });

      // Listener for Engine status updates
      socket.current.on('engine_status_update', (data) => {
        console.log('[Socket] Received engine_status_update:', data);
        updateEngineStatus(data);
      });

      // Listener for command responses
      socket.current.on('command_response', (data) => {
        console.log('[Socket] Received command_response:', data);
        actions.setLastResponse(data);
      });
      
      // Add more listeners for 'veritas_update', etc. here
    }, 2000);


    // Cleanup on component unmount
    return () => {
      clearTimeout(timer);
      if (socket.current) {
        console.log('[Socket] Disconnecting...');
        socket.current.disconnect();
        socket.current = null;
      }
    };
  }, [setConnectionStatus, updateLlmStatus, addGovernorLog]);
};
