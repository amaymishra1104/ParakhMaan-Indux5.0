import {
  DashboardSummary,
  Inspection,
  PackageImage,
  ComplianceResult,
  DefectInspection,
  DefectAnalyzeResult,
  DefectVideoSummary,
  DefectDetection,
  DefectAnalytics,
  DefectLogItem,
  DefectDetectorStatus,
  LiveFrameResult
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';
const BACKEND_BASE = API_BASE.replace('/api/v1', '');

export function getStorageUrl(filePath?: string): string {
  if (!filePath) return '';
  if (filePath.startsWith('http') || filePath.startsWith('data:')) return filePath;
  const norm = filePath.replace(/\\/g, '/');
  const idx = norm.indexOf('storage');
  return idx !== -1 ? `${BACKEND_BASE}/${norm.substring(idx)}` : filePath;
}

async function postForm<T>(url: string, formData: FormData): Promise<T> {
  return fetchJson<T>(url, { method: 'POST', body: formData });
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...init?.headers,
    },
  });

  if (!res.ok) {
    let errorDetail = `HTTP Error ${res.status}: ${res.statusText}`;
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return res.json() as Promise<T>;
}

export const api = {
  // Demo Seeding
  async seedDemoData(): Promise<any> {
    return fetchJson(`${API_BASE}/demo/seed`, {
      method: 'POST',
    });
  },

  // RAG Question Answering
  async askRuleBook(query: string): Promise<{
    answer: string;
    citations: Array<{ source: string; page: number; text_snippet: string }>;
  }> {
    return fetchJson(`${API_BASE}/rag/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
  },

  // Dashboard
  async getDashboardSummary(): Promise<DashboardSummary> {
    return fetchJson<DashboardSummary>(`${API_BASE}/dashboard/summary`);
  },

  // Inspections CRUD & Lifecycle
  async listInspections(params?: { outcome?: string; search?: string }): Promise<Inspection[]> {
    const url = new URL(`${API_BASE}/inspections`);
    if (params?.outcome) url.searchParams.set('outcome', params.outcome);
    if (params?.search) url.searchParams.set('search', params.search);
    return fetchJson<Inspection[]>(url.toString());
  },

  async createInspection(data: {
    product_name?: string;
    brand_name?: string;
    category?: string;
    location?: string;
    notes?: string;
  }): Promise<Inspection> {
    return fetchJson<Inspection>(`${API_BASE}/inspections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  async getInspection(id: string): Promise<Inspection> {
    return fetchJson<Inspection>(`${API_BASE}/inspections/${id}`);
  },

  async uploadImage(inspectionId: string, file: File, surfaceType: string): Promise<PackageImage> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('surface_type', surfaceType);

    const res = await fetch(`${API_BASE}/inspections/${inspectionId}/images`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Upload failed: ${err}`);
    }

    return res.json();
  },

  async captureCameraImage(
    inspectionId: string,
    base64Data: string,
    surfaceType: string
  ): Promise<PackageImage> {
    return fetchJson<PackageImage>(`${API_BASE}/inspections/${inspectionId}/images/capture`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: base64Data,
        surface_type: surfaceType,
      }),
    });
  },

  async processInspection(id: string): Promise<Inspection> {
    return fetchJson<Inspection>(`${API_BASE}/inspections/${id}/process`, {
      method: 'POST',
    });
  },

  async reprocessInspection(id: string): Promise<Inspection> {
    return fetchJson<Inspection>(`${API_BASE}/inspections/${id}/reprocess`, {
      method: 'POST',
    });
  },

  async finalizeInspection(
    id: string,
    data: { final_remarks?: string; override_status?: string }
  ): Promise<Inspection> {
    return fetchJson<Inspection>(`${API_BASE}/inspections/${id}/finalize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  // Heatmap & Evidence
  async getImageHeatmap(
    inspectionId: string,
    imageId: string
  ): Promise<{ heatmap_data_url: string }> {
    return fetchJson<{ heatmap_data_url: string }>(
      `${API_BASE}/inspections/${inspectionId}/heatmap/${imageId}`
    );
  },

  // AI Deep Analysis & LLM Status
  async getDeepAiAnalysis(id: string): Promise<any> {
    return fetchJson(`${API_BASE}/inspections/${id}/ai-analysis`, {
      method: 'POST',
    });
  },

  async getLlmStatus(): Promise<any> {
    return fetchJson(`${API_BASE}/llm/status`);
  },

  // Review Actions
  async submitReviewAction(
    inspectionId: string,
    actionData: {
      target_field: string;
      action_type: string;
      previous_value?: string;
      new_value?: string;
      reason?: string;
    }
  ): Promise<any> {
    return fetchJson(`${API_BASE}/reviews/${inspectionId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(actionData),
    });
  },

  // PDF Report URL helper
  getReportUrl(id: string): string {
    return `${API_BASE}/reports/${id}/report`;
  },

  // Inspector Statutory Tools
  async getRulesDatabase(): Promise<any> {
    return fetchJson(`${API_BASE}/tools/rules-database`);
  },

  async getSchedules(): Promise<any> {
    return fetchJson(`${API_BASE}/tools/schedules`);
  },

  async calculateMPE(quantity: number, unit: string): Promise<any> {
    return fetchJson(`${API_BASE}/tools/mpe-calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity, unit }),
    });
  },

  async evaluateLotSampling(data: {
    lot_size: number;
    declared_quantity: number;
    unit: string;
    measured_weights: number[];
  }): Promise<any> {
    return fetchJson(`${API_BASE}/tools/lot-sample-evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  async calculatePDPFont(data: {
    package_shape: string;
    height_cm: number;
    width_cm: number;
    depth_or_diameter_cm: number;
  }): Promise<any> {
    return fetchJson(`${API_BASE}/tools/pdp-font-check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },
};

export const defectApi = {
  async getStatus(): Promise<DefectDetectorStatus> {
    return fetchJson<DefectDetectorStatus>(`${API_BASE}/defects/status`);
  },

  async seedDemoData(): Promise<any> {
    return fetchJson(`${API_BASE}/defects/demo/seed`, { method: 'POST' });
  },

  async createInspection(data: {
    product_name?: string;
    brand_name?: string;
    category?: string;
    location?: string;
    notes?: string;
  }): Promise<DefectInspection> {
    return fetchJson<DefectInspection>(`${API_BASE}/defects/inspections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  async listInspections(params?: { outcome?: string; search?: string }): Promise<DefectInspection[]> {
    const url = new URL(`${API_BASE}/defects/inspections`);
    if (params?.outcome) url.searchParams.set('outcome', params.outcome);
    if (params?.search) url.searchParams.set('search', params.search);
    return fetchJson<DefectInspection[]>(url.toString());
  },

  async getInspection(id: string): Promise<DefectInspection> {
    return fetchJson<DefectInspection>(`${API_BASE}/defects/inspections/${id}`);
  },

  async uploadReference(inspectionId: string, file: File): Promise<PackageImage> {
    const formData = new FormData();
    formData.append('file', file);
    return postForm<PackageImage>(`${API_BASE}/defects/inspections/${inspectionId}/reference`, formData);
  },

  async analyzeImage(inspectionId: string, file: File, surfaceType = 'SURFACE'): Promise<DefectAnalyzeResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('surface_type', surfaceType);
    return postForm<DefectAnalyzeResult>(`${API_BASE}/defects/inspections/${inspectionId}/analyze`, formData);
  },

  async analyzeCapture(inspectionId: string, base64Data: string, surfaceType = 'SURFACE'): Promise<DefectAnalyzeResult> {
    return fetchJson<DefectAnalyzeResult>(`${API_BASE}/defects/inspections/${inspectionId}/capture`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_base64: base64Data, surface_type: surfaceType }),
    });
  },

  async analyzeVideo(
    inspectionId: string,
    file: File,
    options?: { sampleFps?: number; maxFrames?: number }
  ): Promise<DefectVideoSummary> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sample_fps', String(options?.sampleFps ?? 2));
    formData.append('max_frames', String(options?.maxFrames ?? 40));
    return postForm<DefectVideoSummary>(`${API_BASE}/defects/inspections/${inspectionId}/video`, formData);
  },

  async analyzeLiveFrame(base64Data: string, options?: { maxSide?: number; inspectionId?: string }): Promise<LiveFrameResult> {
    return fetchJson<LiveFrameResult>(`${API_BASE}/defects/analyze-frame`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: base64Data,
        max_side: options?.maxSide ?? 640,
        inspection_id: options?.inspectionId,
      }),
    });
  },

  async deleteImage(inspectionId: string, imageId: string): Promise<any> {
    return fetchJson(`${API_BASE}/defects/inspections/${inspectionId}/images/${imageId}`, { method: 'DELETE' });
  },

  async submitFeedback(
    detectionId: string,
    data: { action: 'CONFIRM' | 'REJECT' | 'RELABEL'; defect_type?: string; note?: string }
  ): Promise<{ detection: DefectDetection; overall_outcome: string; training_sample_saved: boolean }> {
    return fetchJson(`${API_BASE}/defects/detections/${detectionId}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  async finalizeInspection(
    id: string,
    data: { final_remarks?: string; override_outcome?: string }
  ): Promise<DefectInspection> {
    return fetchJson<DefectInspection>(`${API_BASE}/defects/inspections/${id}/finalize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  async getOverlay(inspectionId: string, imageId: string): Promise<{ overlay_data_url: string }> {
    return fetchJson(`${API_BASE}/defects/inspections/${inspectionId}/overlay/${imageId}`);
  },

  getReportUrl(id: string): string {
    return `${API_BASE}/defects/inspections/${id}/report`;
  },

  async getAnalytics(params?: { days?: number; product?: string }): Promise<DefectAnalytics> {
    const url = new URL(`${API_BASE}/defects/analytics`);
    if (params?.days) url.searchParams.set('days', String(params.days));
    if (params?.product) url.searchParams.set('product', params.product);
    return fetchJson<DefectAnalytics>(url.toString());
  },

  async getLog(params?: {
    defect_type?: string;
    severity?: string;
    reviewer_status?: string;
    product?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ total: number; items: DefectLogItem[] }> {
    const url = new URL(`${API_BASE}/defects/log`);
    Object.entries(params || {}).forEach(([k, v]) => {
      if (v !== undefined && v !== '') url.searchParams.set(k, String(v));
    });
    return fetchJson(url.toString());
  },
};
