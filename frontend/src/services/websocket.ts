// WebSocket Service with Dynamic Backend Support
import io, { Socket } from 'socket.io-client';
import { getApiBaseUrl } from '@/services/api';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { convertToCamelCase } from '@/lib/utils';

class WebSocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Function[]> = new Map();

  connect() {
    if (this.socket?.connected) return;

    // Use dynamic backend URL instead of hardcoded
    const baseUrl = getApiBaseUrl();
    const path = '/socket.io';
    const apiKey = (import.meta as any)?.env?.VITE_API_KEY || '';

    console.log(`🔌 Connecting to WebSocket at origin ${baseUrl} (path=${path})`);

    // Prefer same-origin connection; attach auth via query
    this.socket = io(baseUrl, {
      path,
      reconnectionAttempts: 5,
      reconnectionDelay: 3000,
      transports: ['websocket'],
      extraHeaders: apiKey ? { 'X-API-Key': apiKey } : undefined,
      auth: apiKey ? { apiKey } : undefined,
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log(`✅ WebSocket connected to ${WS_URL}`);
      this.emit('connected', true);
      this.socket?.emit('request_initial_data');
    });

    this.socket.on('disconnect', () => {
      console.log('❌ WebSocket disconnected');
      this.emit('connected', false);
    });
    
    // All event handlers for both backends
    const events = [
      // Original Backend Events
      'governor_update',
      'system_update',
      'kb_update',
      'llm_status',
      'engine_status',
      'auto_learning_update',
      'query_result',
      'initial_data',
      'system_load_update',
      'engine_status_update',
      'visualization_update',
      'command_response',
      'thesis_update',
      'dual_response',
      
      // Hexagonal Backend Events
      'emergency_fix_status',
      'reasoning_complete',
      'fact_added',
      'governor_decision',
      'monitoring_metrics'
    ];

    events.forEach(event => {
      this.socket?.on(event, (data: any) => {
        this.emit(event, data);
      });
    });

    this.socket.on('error', (error: any) => {
      console.error('WebSocket error:', error);
      this.emit('error', error);
    });
  }

  disconnect() {
    this.socket?.disconnect();
    this.socket = null;
    this.listeners.clear();
  }

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)?.push(callback);
  }

  off(event: string, callback: Function) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const processedData = event !== 'connected' ? convertToCamelCase(data) : data;
      callbacks.forEach(callback => callback(processedData));
    }
  }

  sendCommand(command: string, params?: any) {
    if (this.socket?.connected) {
      this.socket.emit('command', { command, params });
    } else {
      console.error('WebSocket not connected');
    }
  }

  sendQuery(query: string) {
    if (this.socket?.connected) {
      this.socket.emit('query', { query });
    } else {
      console.error('WebSocket not connected');
    }
  }

  toggleGovernor(enabled: boolean) {
    if (this.socket?.connected) {
      this.socket.emit('governor_control', { action: enabled ? 'start' : 'stop' });
    }
  }

  toggleAutoLearning(enabled: boolean) {
    if (this.socket?.connected) {
      this.socket.emit('auto_learning_control', { enabled });
    }
  }

  setLearningParameters(params: any) {
    if (this.socket?.connected) {
      this.socket.emit('set_learning_parameters', params);
    }
  }

  sendThesisFeedback(thesisId: string, action: 'approve' | 'reject') {
    if (this.socket?.connected) {
      this.socket.emit('thesis_feedback', { thesis_id: thesisId, action });
    }
  }
}

const wsService = new WebSocketService();
export default wsService;
