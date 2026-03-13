import { API_CONFIG } from '../utils/env';

// API Configuration
export { API_CONFIG };

// Orchestrator Configuration
export const ORCHESTRATOR_CONFIG = {
  production: {
    title: 'Production',
    description: 'Schedule manufacturing orders',
    icon: '🏭',
    color: 'from-macos-blue to-macos-blue-dark',
    totalSteps: 9,
    steps: [
      'Reading orders from Google Sheets',
      'Validating and cleaning orders',
      'Checking machine capacity',
      'Checking materials availability',
      'Analyzing deadlines',
      'Calculating setup times',
      'Structuring data for optimizer',
      'Running optimizer',
      'Generating reports',
    ],
  },
  invoices: {
    title: 'Invoices',
    description: 'Generate tax-compliant invoices',
    icon: '📄',
    color: 'from-macos-green to-macos-green-dark',
    totalSteps: 3,
    steps: [
      'Reading invoice requests',
      'Processing invoices',
      'Writing results to sheets',
    ],
  },
  quality: {
    title: 'Quality',
    description: 'Inspect production batches',
    icon: '🔍',
    color: 'from-macos-orange to-macos-orange-dark',
    totalSteps: 3,
    steps: [
      'Reading inspection data',
      'Processing quality inspections',
      'Writing results to sheets',
    ],
  },
  quotations: {
    title: 'Quotations',
    description: 'Generate customer quotes',
    icon: '💰',
    color: 'from-macos-purple to-purple-700',
    totalSteps: 3,
    steps: [
      'Reading quotation requests',
      'Processing quotations',
      'Writing results to sheets',
    ],
  },
  rnd: {
    title: 'R&D',
    description: 'Design material formulations',
    icon: '🧪',
    color: 'from-macos-red to-macos-red-dark',
    totalSteps: 3,
    steps: [
      'Reading formulation requests',
      'Processing formulations',
      'Writing results to sheets',
    ],
  },
};

// Status Colors
export const STATUS_COLORS = {
  idle: {
    text: 'text-macos-gray-500',
    bg: 'bg-macos-gray-100',
    border: 'border-macos-gray-200',
  },
  running: {
    text: 'text-macos-orange',
    bg: 'bg-orange-100',
    border: 'border-orange-200',
  },
  completed: {
    text: 'text-macos-green',
    bg: 'bg-green-100',
    border: 'border-green-200',
  },
  error: {
    text: 'text-macos-red',
    bg: 'bg-red-100',
    border: 'border-red-200',
  },
  pending: {
    text: 'text-macos-yellow',
    bg: 'bg-yellow-100',
    border: 'border-yellow-200',
  },
};

// Decision Colors
export const DECISION_COLORS = {
  PROCEED: {
    text: 'text-macos-green',
    bg: 'bg-green-100',
    icon: 'CheckCircleIcon',
  },
  ACCEPT: {
    text: 'text-macos-green',
    bg: 'bg-green-100',
    icon: 'CheckCircleIcon',
  },
  DELAY: {
    text: 'text-macos-orange',
    bg: 'bg-orange-100',
    icon: 'ExclamationTriangleIcon',
  },
  CONDITIONAL_ACCEPT: {
    text: 'text-macos-orange',
    bg: 'bg-orange-100',
    icon: 'ExclamationTriangleIcon',
  },
  REJECT: {
    text: 'text-macos-red',
    bg: 'bg-red-100',
    icon: 'XCircleIcon',
  },
};

// Risk Score Colors
export const RISK_SCORE_COLORS = {
  low: 'bg-green-100 text-macos-green',
  medium: 'bg-orange-100 text-macos-orange',
  high: 'bg-red-100 text-macos-red',
};

// Priority Colors
export const PRIORITY_COLORS = {
  low: {
    text: 'text-macos-gray-600',
    bg: 'bg-macos-gray-100',
  },
  normal: {
    text: 'text-macos-blue',
    bg: 'bg-blue-100',
  },
  high: {
    text: 'text-macos-orange',
    bg: 'bg-orange-100',
  },
  critical: {
    text: 'text-macos-red',
    bg: 'bg-red-100',
  },
};

// Machine Status
export const MACHINE_STATUS = {
  active: {
    text: 'text-macos-green',
    bg: 'bg-green-100',
    dot: 'bg-macos-green',
  },
  maintenance: {
    text: 'text-macos-orange',
    bg: 'bg-orange-100',
    dot: 'bg-macos-orange',
  },
  offline: {
    text: 'text-macos-red',
    bg: 'bg-red-100',
    dot: 'bg-macos-red',
  },
};

// Material Status
export const MATERIAL_STATUS = {
  ok: {
    text: 'text-macos-green',
    bg: 'bg-green-100',
  },
  low: {
    text: 'text-macos-orange',
    bg: 'bg-orange-100',
  },
  critical: {
    text: 'text-macos-red',
    bg: 'bg-red-100',
  },
};

// Animation Durations
export const ANIMATION_DURATION = {
  fast: 0.15,
  normal: 0.3,
  slow: 0.5,
};

// Breakpoints
export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

// Z-Index Layers
export const Z_INDEX = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
};

// Default Values
export const DEFAULTS = {
  pageSize: 25,
  refreshInterval: 30000, // 30 seconds
  debounceDelay: 300,
  animationDelay: 0.1,
};