// V4 - Cleaned and synchronized with the new store actions - WITH PERMANENT FIX
import { io, Socket } from 'socket.io-client';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { getActiveBackend } from '@/config/backends';

class WebSocketService {
  private socket: Socket | null = null;
  
  constructor() {
    this.connect();
  }
  
  private connect() {
    const activeBackend = getActiveBackend();
    const BACKEND_URL = activeBackend.wsUrl;
    console.log(`[WebSocket] Connecting to ${activeBackend.name} at:`, BACKEND_URL);
    
    this.socket = io(BACKEND_URL, {
      transports: ['websocket'],
      reconnection: true,
    });
    
    this.setupEventListeners();
  }
  
  private fixLLMProviders(providers: any[]): any[] {
    // PERMANENT FIX: If provider has tokens, it MUST be online
    return providers.map((provider: any) => {
      const tokensUsed = provider.tokens_used || provider.tokensUsed || 0;
      const fixed = {
        ...provider,
        // Normalize to camelCase
        tokensUsed: tokensUsed,
        responseTime: provider.response_time || provider.responseTime || 0,
        // Force online if tokens used
        status: tokensUsed > 0 ? 'online' : (provider.status || 'offline')
      };
      // Remove snake_case duplicates
      delete fixed.tokens_used;
      delete fixed.response_time;
      return fixed;
    });
  }
  
  private setupEventListeners() {
    if (!this.socket) return;
    
    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected to HAK-GAL Backend');
      useGovernorStore.getState().handleConnectionStatus(true);
      this.socket?.emit('request_initial_data');
    });
    
    this.socket.on('disconnect', () => {
      console.log('❌ WebSocket disconnected');
      useGovernorStore.getState().handleConnectionStatus(false);
    });
    
    this.socket.on('system_load_update', (data) => {
      useGovernorStore.getState().handleSystemLoadUpdate(data);
    });
    
    this.socket.on('governor_update', (data) => {
      useGovernorStore.getState().handleGovernorUpdate(data);
    });
    
    this.socket.on('kb_update', (data) => {
      console.log('📊 KB Update received:', data);
      useGovernorStore.getState().handleKbUpdate(data);
    });
    
    this.socket.on('engine_status', (data) => {
      useGovernorStore.getState().handleEnginesUpdate(data);
    });
    
    this.socket.on('llm_status', (data) => {
      console.log('🤖 LLM Status Update received:', data);
      if (data.providers && data.providers.length > 0) {
        // Apply the fix to all LLM status updates
        const fixedProviders = this.fixLLMProviders(data.providers);
        useGovernorStore.getState().handleLlmUpdate({ providers: fixedProviders });
        console.log('✅ Fixed LLM providers:', fixedProviders.map(p => ({name: p.name, status: p.status})));
      } else {
        useGovernorStore.getState().handleLlmUpdate(data);
      }
    });
    
    this.socket.on('system_gpu_update', (data) => {
      console.log('🎮 GPU Update received:', data);
      useGovernorStore.getState().handleGpuUpdate(data);
    });
    
    this.socket.on('gpu_update', (data) => {
      console.log('🎮 GPU Broadcast received:', data);
      useGovernorStore.getState().handleGpuUpdate(data);
    });
    
    // Enhanced: Auto-learning events
    this.socket.on('auto_learning_update', (data) => {
      console.log('🧠 Auto-Learning Update received:', data);
      if (data.config) {
        useGovernorStore.getState().updateAutoLearningConfig(data.config);
      }
    });
    
    // Enhanced: Emergency fixes events
    this.socket.on('emergency_fix_status', (data) => {
      console.log('🛡️ Emergency Fix Status received:', data);
      // Store emergency fix status in store
      useGovernorStore.getState().handleEmergencyFixUpdate(data);
    });
    
    // Enhanced: Monitoring events
    this.socket.on('monitoring_update', (data) => {
      console.log('📊 Monitoring Update received:', data);
      // Store monitoring data in store
      useGovernorStore.getState().handleMonitoringUpdate(data);
    });
    
    // Enhanced: System status events
    this.socket.on('system_status_update', (data) => {
      console.log('🖥️ System Status Update received:', data);
      // Update system status with detailed information
      useGovernorStore.getState().handleSystemStatusUpdate(data);
    });
    
    // Enhanced: Engine detailed events
    this.socket.on('engine_detailed_update', (data) => {
      console.log('⚙️ Engine Detailed Update received:', data);
      // Update engines with detailed metrics
      useGovernorStore.getState().handleEngineDetailedUpdate(data);
    });
    
    // Enhanced: LLM detailed events
    this.socket.on('llm_detailed_update', (data) => {
      console.log('🤖 LLM Detailed Update received:', data);
      if (data.providers && data.providers.length > 0) {
        const fixedProviders = this.fixLLMProviders(data.providers);
        useGovernorStore.getState().handleLlmDetailedUpdate({ providers: fixedProviders });
      }
    });
    
    // Enhanced: Knowledge base detailed events
    this.socket.on('kb_detailed_update', (data) => {
      console.log('📚 KB Detailed Update received:', data);
      useGovernorStore.getState().handleKbDetailedUpdate(data);
    });
    
    // Enhanced: Governor detailed events
    this.socket.on('governor_detailed_update', (data) => {
      console.log('🎯 Governor Detailed Update received:', data);
      useGovernorStore.getState().handleGovernorDetailedUpdate(data);
    });

    // --- HEXAGONAL BACKEND EVENT HANDLERS ---
    this.socket.on('graph_update', (data) => {
      console.log('🕸️ [Hexagonal] Graph Update received:', data);
      // The data from the backend is { factCount, nodeCount, edgeCount }
      // We pass this to the store action that now supports these new fields.
      useGovernorStore.getState().handleKbUpdate({ metrics: data });
    });

    this.socket.on('hexagonal_status_update', (data) => {
      console.log('💠 [Hexagonal] Status Update received:', data);
      // This is a placeholder for a potential new, unified status event.
      // TODO: Map data to the appropriate store actions.
    });
    
    this.socket.on('initial_data', (data) => {
      console.log('📦 Initial data received:', data);
      
      // Fix LLM providers in initial data
      if (data.llm_providers && data.llm_providers.length > 0) {
        console.log('🤖 Initial LLM Providers (before fix):', data.llm_providers);
        data.llm_providers = this.fixLLMProviders(data.llm_providers);
        console.log('✅ Initial LLM Providers (after fix):', data.llm_providers);
      }
      
      // Check for different possible formats
      if (data.kb_metrics) {
        console.log('Found kb_metrics (snake_case):', data.kb_metrics);
        useGovernorStore.getState().handleKbUpdate({ 
          metrics: {
            factCount: data.kb_metrics.fact_count || 0,
            growthRate: data.kb_metrics.growth_rate || 0,
            connectivity: data.kb_metrics.connectivity || 0,
            entropy: data.kb_metrics.entropy || 0,
            uniquePredicates: data.kb_metrics.unique_predicates || 0,
            uniqueEntities: data.kb_metrics.unique_entities || 0
          }
        });
      }
      
      useGovernorStore.getState().handleInitialData(data);
    });

    this.socket.on('command_response', (data) => {
      const store = useGovernorStore.getState();
      const pendingQuery = store.queryHistory.find(q => q.status === 'pending');
      if (pendingQuery) {
        store.updateQueryResponse(pendingQuery.id, {
          status: data.status === 'success' ? 'success' : 'error',
          symbolicResponse: data.result?.symbolic_response || data.message || 'No symbolic response.',
          naturalLanguageExplanation: data.result?.natural_language_explanation || ''
        });
      }
    });
    
    // Handle dual response events
    this.socket.on('dual_response', (data) => {
      console.log('🔄 Dual Response received:', data);
      console.log('  - Query ID:', data.queryId);
      console.log('  - Status:', data.status);
      console.log('  - Symbolic length:', data.symbolicResponse?.length || 0);
      console.log('  - Neurologic length:', data.neurologicResponse?.length || 0);
      console.log('  - Neurologic preview:', data.neurologicResponse?.substring(0, 100) + '...');
      
      const store = useGovernorStore.getState();
      
      if (data.queryId) {
        store.updateQueryResponse(data.queryId, {
          status: data.status || 'success',
          symbolicResponse: data.symbolicResponse || 'No logical facts found.',
          neurologicResponse: data.neurologicResponse || 'No LLM response available.',
          kbFactsUsed: data.kbFactsUsed || 0,
          processingTime: data.processingTime || 0
        });
      }
    });
  }
  
  public emit(event: string, data?: any) {
    this.socket?.emit(event, data);
  }
  
  public toggleGovernor(enabled: boolean) {
    this.emit('governor_control', { action: enabled ? 'start' : 'stop' });
  }
  
  public sendCommand(command: string, query?: string | object) {
    if (command === 'ask_dual' && typeof query === 'object') {
      // Handle dual response command
      this.emit('ask_dual', query);
    } else {
      // Legacy command handling
      const fullQuery = `${command} ${query || ''}`.trim();
      const newId = crypto.randomUUID();
      
      useGovernorStore.getState().addQueryResponse({
        id: newId,
        timestamp: new Date().toISOString(),
        query: fullQuery,
        symbolicResponse: 'Processing...',
        status: 'pending'
      });
      
      this.emit('command', { command, query: query || '' });
    }
  }

  public startEngine(engineName: string) {
    this.emit('engine_control', { action: 'start', engine_id: engineName });
  }

  public stopEngine(engineName: string) {
    this.emit('engine_control', { action: 'stop', engine_id: engineName });
  }

  public toggleAutoLearning(enabled: boolean) {
    this.emit('auto_learning_control', { action: enabled ? 'start' : 'stop' });
  }

  public sendMessage(event: string, data?: any) {
    this.emit(event, data);
  }

  // Enhanced: Auto-learning configuration
  public updateAutoLearningConfig(config: any) {
    this.emit('auto_learning_config', config);
  }

  // Enhanced: Engine configuration
  public updateEngineConfig(engineName: string, config: any) {
    this.emit('engine_config', { engine: engineName, config });
  }

  // Enhanced: Emergency fixes control
  public toggleEmergencyFix(fixName: string, enabled: boolean) {
    this.emit('emergency_fix_control', { fix: fixName, enabled });
  }

  // Enhanced: Monitoring control
  public toggleMonitoring(monitoringType: string, enabled: boolean) {
    this.emit('monitoring_control', { type: monitoringType, enabled });
  }

  // Enhanced: Request detailed system status
  public requestSystemStatus() {
    this.emit('request_system_status');
  }

  // Enhanced: Request emergency status
  public requestEmergencyStatus() {
    this.emit('request_emergency_status');
  }
}

export const wsService = new WebSocketService();

export const useGovernorSocket = () => {
  return wsService;
};