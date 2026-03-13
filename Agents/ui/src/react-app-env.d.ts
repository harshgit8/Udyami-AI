/// <reference types="react-scripts" />

// Extend Window interface for runtime environment
declare global {
  interface Window {
    ENV?: Record<string, string>;
  }
}

// Process environment types
declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: 'development' | 'production' | 'test';
    REACT_APP_API_URL?: string;
    REACT_APP_WS_URL?: string;
  }
}

export {};