// WebSocket Manager - ORIGINAL VERSION
// Phase 2: State Architecture Unification  
// Single connection replacing 3 separate hooks

import { io, Socket } from 'socket.io-client';
import { WS_URL } from '@/config/backends';

export interface WebSocketManager {
  socket: Socket | null;
  connect: () => void;
  disconnect: () => void;
  on: (event: string, handler: (data: any) => void) => void;
  off: (event: string, handler?: (data: any) => void) => void;
  emit: (event: string, data?: any) => void;
  isConnected: () => boolean;
}

class WebSocketManagerImpl implements WebSocketManager {
  socket: Socket | null = null;
  private eventHandlers: Map<string, Set<(data: any) => void>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  connect(): void {
    // Use the existing socket from useGovernorSocket to prevent double connections
    const governorSocket = (window as any).__GOVERNOR_SOCKET__;
    if (governorSocket) {
      console.log('[WebSocketManager] Using existing Governor socket');
      this.socket = governorSocket;
      this.setupCoreHandlers();
      return;
    }
    
    /* Original code - only used if no Governor socket exists
    if (this.socket?.connected) {
      console.log('[WebSocketManager] Already connected');
      return;
    }
    
    console.log('[WebSocketManager] Connecting to', WS_URL);
    
    this.socket = io(WS_URL, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts,
      transports: ['websocket', 'polling'],
    });
    
    this.setupCoreHandlers();
    */
  }
  
  private setupCoreHandlers(): void {
    if (!this.socket) return;
    
    this.socket.on('connect', () => {
      console.log('[WebSocketManager] Connected');
      this.reconnectAttempts = 0;
      this.notifyHandlers('connection_status', { connected: true });
    });
    
    this.socket.on('disconnect', (reason) => {
      console.log('[WebSocketManager] Disconnected:', reason);
      this.notifyHandlers('connection_status', { connected: false, reason });
    });
    
    this.socket.on('error', (error) => {
      console.error('[WebSocketManager] Error:', error);
      this.notifyHandlers('error', error);
    });
    
    // Forward all other events to registered handlers
    this.socket.onAny((event, data) => {
      this.notifyHandlers(event, data);
    });
  }
  
  private notifyHandlers(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`[WebSocketManager] Handler error for ${event}:`, error);
        }
      });
    }
  }
  
  disconnect(): void {
    if (this.socket) {
      console.log('[WebSocketManager] Disconnecting');
      this.socket.disconnect();
      this.socket = null;
    }
  }
  
  on(event: string, handler: (data: any) => void): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event)!.add(handler);
  }
  
  off(event: string, handler?: (data: any) => void): void {
    if (!handler) {
      this.eventHandlers.delete(event);
    } else {
      const handlers = this.eventHandlers.get(event);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.eventHandlers.delete(event);
        }
      }
    }
  }
  
  emit(event: string, data?: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn(`[WebSocketManager] Cannot emit ${event} - not connected`);
    }
  }
  
  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

// Singleton instance
let instance: WebSocketManager | null = null;

export const getWebSocketManager = (): WebSocketManager => {
  if (!instance) {
    instance = new WebSocketManagerImpl();
  }
  return instance;
};

// React Hook for WebSocket
import { useEffect } from 'react';

export const useWebSocket = (
  events?: { [event: string]: (data: any) => void }
) => {
  const manager = getWebSocketManager();
  
  useEffect(() => {
    // Connect on mount
    manager.connect();
    
    // Register event handlers
    if (events) {
      Object.entries(events).forEach(([event, handler]) => {
        manager.on(event, handler);
      });
    }
    
    // Cleanup
    return () => {
      if (events) {
        Object.entries(events).forEach(([event, handler]) => {
          manager.off(event, handler);
        });
      }
    };
  }, []); // Only run once on mount
  
  return manager;
};

export default getWebSocketManager;
