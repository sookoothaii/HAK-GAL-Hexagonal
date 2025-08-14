// src/store/systemStore.ts
import { create } from 'zustand';

// Define the structure of our state
interface SystemState {
  llmStatus: Record<string, { online: boolean; tokensUsed?: number; cost?: number }>;
  engineStatus: {
    aethelred: string; // e.g., 'IDLE', 'GENESIS', 'INFERENCE'
    thesis: string;    // e.g., 'IDLE', 'VERIFYING'
  };
  governorLog: string[];
  isConnected: boolean;
  lastResponse: Record<string, any> | null;
  actions: {
    setConnectionStatus: (status: boolean) => void;
    addGovernorLog: (log: string) => void;
    updateLlmStatus: (status: Record<string, any>) => void;
    updateEngineStatus: (status: { aethelred: string, thesis: string }) => void;
    setLastResponse: (response: Record<string, any>) => void;
    sendCommand: (command: string) => void; // Placeholder, will be managed by the socket hook
  };
}

export const useSystemStore = create<SystemState>((set) => ({
  // Initial default state
  llmStatus: {
    'FOL': { online: false },
    'GEMINI': { online: false },
    'DEEPSEEK': { online: false },
    'MISTRAL': { online: false },
  },
  engineStatus: {
    aethelred: 'UNKNOWN',
    thesis: 'UNKNOWN',
  },
  governorLog: [],
  isConnected: false,
  lastResponse: null,

  // Actions to update the state
  actions: {
    setConnectionStatus: (status) => set({ isConnected: status }),
    addGovernorLog: (log) => set((state) => ({ governorLog: [log, ...state.governorLog.slice(0, 9)] })), // Keep last 10 logs
    updateLlmStatus: (status) => set({ llmStatus: status }),
    updateEngineStatus: (status) => set({ engineStatus: status }),
    setLastResponse: (response) => set({ lastResponse: response }),
  }
}));
