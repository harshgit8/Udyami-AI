import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { OrchestratorState, OrchestratorType, SystemStatus, WebSocketMessage } from '../types';
import { orchestratorService } from '../services/orchestratorService';
import { API_CONFIG } from '../utils/env';

interface OrchestratorContextType {
  orchestrators: Record<OrchestratorType, OrchestratorState>;
  systemStatus: SystemStatus;
  runOrchestrator: (type: OrchestratorType) => Promise<void>;
  stopOrchestrator: (type: OrchestratorType) => void;
  refreshStatus: () => Promise<void>;
  syncSheets: () => Promise<void>;
}

const OrchestratorContext = createContext<OrchestratorContextType | undefined>(undefined);

type Action =
  | { type: 'SET_ORCHESTRATOR_STATUS'; payload: { orchestratorType: OrchestratorType; state: Partial<OrchestratorState> } }
  | { type: 'SET_SYSTEM_STATUS'; payload: SystemStatus }
  | { type: 'RESET_ORCHESTRATOR'; payload: OrchestratorType };

const initialOrchestratorState: OrchestratorState = {
  type: 'production',
  status: 'idle',
  progress: 0,
  currentStep: '',
  totalSteps: 0,
  completedSteps: 0,
};

const initialState = {
  orchestrators: {
    production: { ...initialOrchestratorState, type: 'production' as OrchestratorType, totalSteps: 9 },
    invoices: { ...initialOrchestratorState, type: 'invoices' as OrchestratorType, totalSteps: 3 },
    quality: { ...initialOrchestratorState, type: 'quality' as OrchestratorType, totalSteps: 3 },
    quotations: { ...initialOrchestratorState, type: 'quotations' as OrchestratorType, totalSteps: 3 },
    rnd: { ...initialOrchestratorState, type: 'rnd' as OrchestratorType, totalSteps: 3 },
  },
  systemStatus: {
    sheetsConnected: false,
    lastSync: new Date(),
    geminiApiStatus: 'disconnected' as 'connected' | 'disconnected' | 'error',
    totalOrders: 0,
    activeOrchestrators: 0,
  },
};

function orchestratorReducer(state: typeof initialState, action: Action): typeof initialState {
  switch (action.type) {
    case 'SET_ORCHESTRATOR_STATUS':
      return {
        ...state,
        orchestrators: {
          ...state.orchestrators,
          [action.payload.orchestratorType]: {
            ...state.orchestrators[action.payload.orchestratorType],
            ...action.payload.state,
          },
        },
      };
    case 'SET_SYSTEM_STATUS':
      return {
        ...state,
        systemStatus: action.payload,
      };
    case 'RESET_ORCHESTRATOR':
      return {
        ...state,
        orchestrators: {
          ...state.orchestrators,
          [action.payload]: {
            ...initialOrchestratorState,
            type: action.payload,
            totalSteps: state.orchestrators[action.payload].totalSteps,
          },
        },
      };
    default:
      return state;
  }
}

export function OrchestratorProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(orchestratorReducer, initialState);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket(API_CONFIG.WS_URL);

    ws.onopen = () => {
      // WebSocket connected successfully
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        if (message.type === 'progress') {
          dispatch({
            type: 'SET_ORCHESTRATOR_STATUS',
            payload: {
              orchestratorType: message.orchestrator,
              state: {
                status: 'running',
                progress: message.data.progress,
                currentStep: message.data.currentStep,
                completedSteps: message.data.completedSteps,
              },
            },
          });
        } else if (message.type === 'result') {
          dispatch({
            type: 'SET_ORCHESTRATOR_STATUS',
            payload: {
              orchestratorType: message.orchestrator,
              state: {
                status: 'completed',
                progress: 100,
                endTime: new Date(),
                results: message.data,
              },
            },
          });
        } else if (message.type === 'error') {
          dispatch({
            type: 'SET_ORCHESTRATOR_STATUS',
            payload: {
              orchestratorType: message.orchestrator,
              state: {
                status: 'error',
                error: message.data.error,
                endTime: new Date(),
              },
            },
          });
        }
      } catch (error) {
        // Error parsing WebSocket message
      }
    };

    ws.onclose = () => {
      // WebSocket disconnected
    };

    ws.onerror = (error) => {
      // WebSocket error occurred
    };

    return () => {
      ws.close();
    };
  }, []);

  // Load initial system status
  useEffect(() => {
    refreshStatus();
  }, []);

  const runOrchestrator = async (type: OrchestratorType) => {
    try {
      dispatch({
        type: 'SET_ORCHESTRATOR_STATUS',
        payload: {
          orchestratorType: type,
          state: {
            status: 'running',
            progress: 0,
            currentStep: 'Starting...',
            completedSteps: 0,
            startTime: new Date(),
            error: undefined,
          },
        },
      });

      await orchestratorService.run(type);
    } catch (error) {
      dispatch({
        type: 'SET_ORCHESTRATOR_STATUS',
        payload: {
          orchestratorType: type,
          state: {
            status: 'error',
            error: error instanceof Error ? error.message : 'Unknown error',
            endTime: new Date(),
          },
        },
      });
    }
  };

  const stopOrchestrator = (type: OrchestratorType) => {
    orchestratorService.stop(type);
    dispatch({
      type: 'RESET_ORCHESTRATOR',
      payload: type,
    });
  };

  const refreshStatus = async () => {
    try {
      const status = await orchestratorService.getSystemStatus();
      dispatch({
        type: 'SET_SYSTEM_STATUS',
        payload: status,
      });
    } catch (error) {
      // Error refreshing status
    }
  };

  const syncSheets = async () => {
    try {
      await orchestratorService.syncSheets();
      await refreshStatus();
    } catch (error) {
      // Error syncing sheets
    }
  };

  const value: OrchestratorContextType = {
    orchestrators: state.orchestrators,
    systemStatus: state.systemStatus,
    runOrchestrator,
    stopOrchestrator,
    refreshStatus,
    syncSheets,
  };

  return (
    <OrchestratorContext.Provider value={value}>
      {children}
    </OrchestratorContext.Provider>
  );
}

export function useOrchestrator() {
  const context = useContext(OrchestratorContext);
  if (context === undefined) {
    throw new Error('useOrchestrator must be used within an OrchestratorProvider');
  }
  return context;
}