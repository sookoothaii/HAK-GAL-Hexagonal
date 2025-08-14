// Enterprise-Grade WebSocket Service with Advanced Features
import { io, Socket } from 'socket.io-client';
import { API_BASE_URL } from '@/config';
import { useEffect, useState } from 'react';

export interface WebSocketConfig {
  reconnectionAttempts: number;
  reconnectionDelay: number;
  reconnectionDelayMax: number;
  timeout: number;
  autoConnect: boolean;
  auth?: Record<string, any>;
}

export interface MessageQueue {
  id: string;
  event: string;
  data: any;
  timestamp: number;
  retries: number;
  maxRetries: number;
}

export interface ConnectionMetrics {
  latency: number;
  messagesPerSecond: number;
  bytesReceived: number;
  bytesSent: number;
  reconnections: number;
  errors: number;
}

class EnterpriseWebSocketService {
  private socket: Socket | null = null;
  private config: WebSocketConfig;
  private messageQueue: MessageQueue[] = [];
  private isProcessingQueue = false;
  private connectionMetrics: ConnectionMetrics = {
    latency: 0,
    messagesPerSecond: 0,
    bytesReceived: 0,
    bytesSent: 0,
    reconnections: 0,
    errors: 0,
  };
  private messageTimestamps: number[] = [];
  private pingInterval: NodeJS.Timeout | null = null;
  private listeners: Map<string, Set<Function>> = new Map();
  private connectionPromise: Promise<void> | null = null;

  constructor(config: Partial<WebSocketConfig> = {}) {
    this.config = {
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 30000,
      timeout: 20000,
      autoConnect: true,
      ...config,
    };
  }

  // Advanced connection management with promise-based connection
  async connect(): Promise<void> {
    if (this.connectionPromise) {
      return this.connectionPromise;
    }

    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        this.socket = io(API_BASE_URL, {
          reconnection: true,
          reconnectionAttempts: this.config.reconnectionAttempts,
          reconnectionDelay: this.config.reconnectionDelay,
          reconnectionDelayMax: this.config.reconnectionDelayMax,
          timeout: this.config.timeout,
          autoConnect: this.config.autoConnect,
          auth: this.config.auth,
          transports: ['websocket', 'polling'], // Fallback support
          // Performance optimizations
          perMessageDeflate: true,
          forceBase64: false,
        });

        this.setupEventHandlers();
        this.startMetricsCollection();
        
        // Connection established
        this.socket.once('connect', () => {
          console.log('🚀 WebSocket connected with ID:', this.socket?.id);
          this.processMessageQueue();
          resolve();
        });

        // Connection failed
        this.socket.once('connect_error', (error) => {
          console.error('❌ WebSocket connection failed:', error);
          reject(error);
        });

      } catch (error) {
        reject(error);
      }
    });

    return this.connectionPromise;
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    // Connection lifecycle events
    this.socket.on('connect', () => {
      this.emit('connection:established', { id: this.socket?.id });
      this.startPingPong();
    });

    this.socket.on('disconnect', (reason) => {
      console.warn('🔌 WebSocket disconnected:', reason);
      this.emit('connection:lost', { reason });
      this.stopPingPong();
      
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, attempt reconnection
        this.socket?.connect();
      }
    });

    this.socket.on('reconnect', (attemptNumber) => {
      this.connectionMetrics.reconnections++;
      this.emit('connection:reconnected', { attempts: attemptNumber });
      this.processMessageQueue();
    });

    this.socket.on('error', (error) => {
      console.error('❌ WebSocket error:', error);
      this.connectionMetrics.errors++;
      this.emit('connection:error', error);
    });

    // Message tracking for metrics
    this.socket.onAny((event, ...args) => {
      this.trackMessage('received', event, args);
    });

    this.socket.onAnyOutgoing((event, ...args) => {
      this.trackMessage('sent', event, args);
    });
  }

  // High-performance message emission with queuing
  emit(event: string, data?: any, options: { retry?: boolean; maxRetries?: number } = {}): void {
    const message: MessageQueue = {
      id: `${Date.now()}-${Math.random()}`,
      event,
      data,
      timestamp: Date.now(),
      retries: 0,
      maxRetries: options.maxRetries || 3,
    };

    if (!this.socket?.connected && options.retry !== false) {
      // Queue message for later delivery
      this.messageQueue.push(message);
      console.log(`📦 Message queued: ${event}`);
      return;
    }

    this.sendMessage(message);
  }

  private sendMessage(message: MessageQueue): void {
    if (!this.socket?.connected) {
      if (message.retries < message.maxRetries) {
        message.retries++;
        this.messageQueue.push(message);
      } else {
        console.error(`❌ Message dropped after ${message.maxRetries} retries:`, message.event);
        this.emit('message:dropped', message);
      }
      return;
    }

    try {
      this.socket.emit(message.event, message.data);
    } catch (error) {
      console.error(`❌ Failed to send message:`, error);
      if (message.retries < message.maxRetries) {
        message.retries++;
        this.messageQueue.push(message);
      }
    }
  }

  // Process queued messages with rate limiting
  private async processMessageQueue(): Promise<void> {
    if (this.isProcessingQueue || this.messageQueue.length === 0) return;

    this.isProcessingQueue = true;
    const BATCH_SIZE = 10;
    const BATCH_DELAY = 100; // ms

    while (this.messageQueue.length > 0 && this.socket?.connected) {
      const batch = this.messageQueue.splice(0, BATCH_SIZE);
      
      for (const message of batch) {
        this.sendMessage(message);
      }
      
      if (this.messageQueue.length > 0) {
        await new Promise(resolve => setTimeout(resolve, BATCH_DELAY));
      }
    }

    this.isProcessingQueue = false;
  }

  // Advanced event subscription with automatic cleanup
  on(event: string, handler: Function): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
      
      // Set up the actual socket listener only once per event
      this.socket?.on(event, (...args) => {
        this.listeners.get(event)?.forEach(handler => {
          try {
            handler(...args);
          } catch (error) {
            console.error(`Error in event handler for ${event}:`, error);
          }
        });
      });
    }
    
    this.listeners.get(event)?.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(handler);
      if (this.listeners.get(event)?.size === 0) {
        this.listeners.delete(event);
        this.socket?.off(event);
      }
    };
  }

  // Internal event emitter for service events
  private emit(event: string, data?: any): void {
    this.listeners.get(event)?.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error(`Error in internal event handler for ${event}:`, error);
      }
    });
  }

  // Latency monitoring with ping-pong
  private startPingPong(): void {
    this.pingInterval = setInterval(() => {
      const start = Date.now();
      
      this.socket?.emit('ping', {}, (response: any) => {
        this.connectionMetrics.latency = Date.now() - start;
        this.emit('metrics:latency', this.connectionMetrics.latency);
      });
    }, 5000);
  }

  private stopPingPong(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  // Performance metrics collection
  private startMetricsCollection(): void {
    // Messages per second calculation
    setInterval(() => {
      const now = Date.now();
      const recentMessages = this.messageTimestamps.filter(ts => now - ts < 1000);
      this.connectionMetrics.messagesPerSecond = recentMessages.length;
      this.messageTimestamps = recentMessages;
      
      this.emit('metrics:update', { ...this.connectionMetrics });
    }, 1000);
  }

  private trackMessage(direction: 'sent' | 'received', event: string, args: any[]): void {
    this.messageTimestamps.push(Date.now());
    
    // Estimate message size
    const messageSize = new Blob([JSON.stringify({ event, args })]).size;
    
    if (direction === 'sent') {
      this.connectionMetrics.bytesSent += messageSize;
    } else {
      this.connectionMetrics.bytesReceived += messageSize;
    }
  }

  // Connection state management
  get isConnected(): boolean {
    return this.socket?.connected || false;
  }

  get metrics(): ConnectionMetrics {
    return { ...this.connectionMetrics };
  }

  get queueSize(): number {
    return this.messageQueue.length;
  }

  // Graceful disconnect with queue preservation
  disconnect(clearQueue = false): void {
    this.stopPingPong();
    
    if (clearQueue) {
      this.messageQueue = [];
    }
    
    this.socket?.disconnect();
    this.socket = null;
    this.connectionPromise = null;
  }

  // Force reconnection
  async reconnect(): Promise<void> {
    this.disconnect(false);
    return this.connect();
  }
}

// Export singleton instance
export const wsService = new EnterpriseWebSocketService();

// Export hook for React components
export const useWebSocket = (event: string, handler: Function, deps: any[] = []) => {
  useEffect(() => {
    const unsubscribe = wsService.on(event, handler);
    return unsubscribe;
  }, deps);
  
  return {
    emit: wsService.emit.bind(wsService),
    isConnected: wsService.isConnected,
    metrics: wsService.metrics,
  };
};
