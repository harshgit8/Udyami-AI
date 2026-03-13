// Orchestrator Types
export type OrchestratorType = 'production' | 'invoices' | 'quality' | 'quotations' | 'rnd';

export type OrchestratorStatus = 'idle' | 'running' | 'completed' | 'error' | 'pending';

export interface OrchestratorState {
  type: OrchestratorType;
  status: OrchestratorStatus;
  progress: number;
  currentStep: string;
  totalSteps: number;
  completedSteps: number;
  startTime?: Date;
  endTime?: Date;
  error?: string;
  results?: any;
}

// System Status Types
export interface SystemStatus {
  sheetsConnected: boolean;
  lastSync: Date;
  geminiApiStatus: 'connected' | 'disconnected' | 'error';
  totalOrders: number;
  activeOrchestrators: number;
}

// Production Types
export interface Order {
  orderId: string;
  productType: string;
  quantity: number;
  dueDate: string;
  priority: 'low' | 'normal' | 'high' | 'critical';
  customer: string;
  notes?: string;
}

export interface ProductionDecision {
  orderId: string;
  decision: 'PROCEED' | 'DELAY' | 'REJECT';
  riskScore: number;
  reason: string;
  machine?: string;
  startTime?: string;
  endTime?: string;
  aiExplanation?: string;
  recommendation?: string;
}

// Invoice Types
export interface InvoiceRequest {
  invoiceRequestId: string;
  customerName: string;
  customerAddress: string;
  customerGstin: string;
  orderId: string;
  productType: string;
  quantity: number;
  subtotal: number;
  grandTotal: number;
  status: 'pending' | 'generated' | 'error';
}

// Quality Types
export interface QualityInspection {
  batchId: string;
  productType: string;
  quantity: number;
  inspectionStandard: string;
  decision: 'ACCEPT' | 'REJECT' | 'CONDITIONAL_ACCEPT';
  defectRate: number;
  confidence: number;
}

// Quotation Types
export interface QuotationRequest {
  quoteRequestId: string;
  customer: string;
  productType: string;
  quantity: number;
  application: string;
  grandTotal: number;
  status: 'pending' | 'generated' | 'error';
}

// R&D Types
export interface RnDRequest {
  requestId: string;
  application: string;
  standards: string[];
  costTarget: number;
  formulation?: string;
  status: 'pending' | 'completed' | 'error';
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'status' | 'progress' | 'result' | 'error';
  orchestrator: OrchestratorType;
  data: any;
  timestamp: string;
}

// Chart Data Types
export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

// Machine Configuration
export interface Machine {
  machineId: string;
  capableProducts: string[];
  productionRate: number;
  status: 'active' | 'maintenance' | 'offline';
}

// Material Inventory
export interface Material {
  name: string;
  current: number;
  minimum: number;
  unit: string;
  status: 'ok' | 'low' | 'critical';
}