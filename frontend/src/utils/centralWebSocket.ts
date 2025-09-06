/**
 * Centralized WebSocket Manager
 * Ensures only ONE WebSocket connection exists
 */

import { io, Socket } from 'socket.io-client';

class CentralWebSocketManager {
  private static instance: CentralWebSocketManager;
  private socket: Socket | null = null;
  private isConnecting = false;
  private connectionAttempts = 0;
  
  private constructor() {
    // Private constructor for singleton
  }
  
  static getInstance(): CentralWebSocketManager {
    if (!CentralWebSocketManager.instance) {
      CentralWebSocketManager.instance = new CentralWebSocketManager();
    }
    return CentralWebSocketManager.instance;
  }
  
  connect(): Socket | null {
    // Return existing socket if already connected
    if (this.socket?.connected) {
      console.log('[CentralWebSocket] Using existing connection');
      return this.socket;
    }
    
    // Prevent multiple connection attempts
    if (this.isConnecting) {
      console.log('[CentralWebSocket] Connection already in progress');
      return this.socket;
    }
    
    // Limit connection attempts
    this.connectionAttempts++;
    if (this.connectionAttempts > 1) {
      console.warn(`[CentralWebSocket] Blocked connection attempt #${this.connectionAttempts}`);
      return this.socket;
    }
    
    this.isConnecting = true;
    console.log('[CentralWebSocket] Creating single WebSocket connection');
    
    // Create ONE socket connection
    this.socket = io('http://localhost:8088', {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 20000,
    });
    
    this.socket.on('connect', () => {
      console.log('[CentralWebSocket] ✅ Connected');
      this.isConnecting = false;
    });
    
    this.socket.on('disconnect', () => {
      console.log('[CentralWebSocket] ❌ Disconnected');
    });
    
    this.socket.on('connect_error', (error) => {
      console.log('[CentralWebSocket] Connection error:', error.message);
      this.isConnecting = false;
    });
    
    return this.socket;
  }
  
  getSocket(): Socket | null {
    return this.socket;
  }
  
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connectionAttempts = 0;
      console.log('[CentralWebSocket] Disconnected and reset');
    }
  }
}

// Export singleton instance
export const wsManager = CentralWebSocketManager.getInstance();

// Helper hook for components
export function useCentralWebSocket() {
  const socket = wsManager.connect();
  
  return {
    socket,
    connected: socket?.connected || false,
    disconnect: () => wsManager.disconnect(),
  };
}

// Prevent other connections
if (typeof window !== 'undefined') {
  (window as any).__CENTRAL_WS__ = wsManager;
  
  // Block duplicate socket.io connections
  const originalIo = (window as any).io;
  if (originalIo) {
    (window as any).io = function(...args: any[]) {
      console.warn('[CentralWebSocket] Blocked duplicate io() call');
      return wsManager.getSocket() || originalIo(...args);
    };
  }
}

export default wsManager;
