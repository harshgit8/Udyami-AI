// Environment variable utilities for React apps
// Handles both build-time and runtime environment variables

declare global {
  interface Window {
    ENV?: Record<string, string>;
  }
}

/**
 * Get environment variable with fallback
 * Works in both development and production builds
 */
export const getEnvVar = (name: string, defaultValue: string = ''): string => {
  // Try runtime environment first (for production)
  if (typeof window !== 'undefined' && window.ENV && window.ENV[name]) {
    return window.ENV[name];
  }
  
  // Fallback to build-time environment (for development)
  if (typeof process !== 'undefined' && process.env && process.env[name]) {
    const value = process.env[name];
    return value !== undefined ? value : defaultValue;
  }
  
  return defaultValue;
};

/**
 * API Configuration
 */
export const API_CONFIG = {
  BASE_URL: getEnvVar('REACT_APP_API_URL', 'http://localhost:8000/api'),
  WS_URL: getEnvVar('REACT_APP_WS_URL', 'ws://localhost:8000/ws'),
  TIMEOUT: 30000, // 30 seconds
};

/**
 * Check if we're in development mode
 */
export const isDevelopment = (): boolean => {
  return getEnvVar('NODE_ENV', 'development') === 'development';
};

/**
 * Check if we're in production mode
 */
export const isProduction = (): boolean => {
  return getEnvVar('NODE_ENV', 'development') === 'production';
};