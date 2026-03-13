import { OrchestratorType, SystemStatus, ApiResponse } from '../types';
import { API_CONFIG } from '../utils/env';

class OrchestratorService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_CONFIG.BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: ApiResponse<T> = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Request failed');
    }

    return data.data as T;
  }

  async run(type: OrchestratorType): Promise<void> {
    await this.request(`/orchestrators/${type}`, {
      method: 'POST',
    });
  }

  async stop(type: OrchestratorType): Promise<void> {
    await this.request(`/orchestrators/${type}/stop`, {
      method: 'POST',
    });
  }

  async getSystemStatus(): Promise<SystemStatus> {
    return this.request<SystemStatus>('/status');
  }

  async getResults(type: OrchestratorType): Promise<any> {
    return this.request(`/results/${type}`);
  }

  async syncSheets(): Promise<void> {
    await this.request('/sheets/sync', {
      method: 'POST',
    });
  }

  async getOrders(): Promise<any[]> {
    return this.request('/orders');
  }

  async getInvoices(): Promise<any[]> {
    return this.request('/invoices');
  }

  async getQualityInspections(): Promise<any[]> {
    return this.request('/quality');
  }

  async getQuotations(): Promise<any[]> {
    return this.request('/quotations');
  }

  async getRnDRequests(): Promise<any[]> {
    return this.request('/rnd');
  }

  async getMachines(): Promise<any[]> {
    return this.request('/machines');
  }

  async getMaterials(): Promise<any[]> {
    return this.request('/materials');
  }

  async updateMachine(machineId: string, data: any): Promise<void> {
    await this.request(`/machines/${machineId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async updateMaterial(materialName: string, data: any): Promise<void> {
    await this.request(`/materials/${materialName}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }
}

export const orchestratorService = new OrchestratorService();