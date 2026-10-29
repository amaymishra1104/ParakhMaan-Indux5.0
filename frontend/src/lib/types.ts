export interface DashboardSummary {
  total_inspections: number;
  compliant_count: number;
  needs_review_count: number;
  non_compliance_count: number;
  draft_count: number;
  recent_inspections: Inspection[];
  common_violations: Array<{
    rule_id: string;
    field: string;
    description?: string;
    count: number;
  }>;
  category_distribution: Array<{
    category: string;
    count: number;
  }>;
}

export interface PackageImage {
  id: string;
  inspection_id?: string;
  surface_type: string;
  file_path: string;
  original_filename: string;
  quality_score: number;
  quality_metadata?: {
    quality_score: number;
    blur: boolean;
    glare: boolean;
    resolution_ok: boolean;
    perspective_ok: boolean;
    occlusion_detected: boolean;
    surface_visible: boolean;
    sharpness_score?: number;
    is_empty?: boolean;
    issues: string[];
    defect_scan?: DefectScanMeta & { frame_index?: number; timestamp_ms?: number };
  };
  ocr_raw_data?: Array<{
    text: string;
    confidence: number;
    bbox?: [number, number, number, number];
    surface_type?: string;
  }>;
  created_at?: string;
}

export interface Declaration {
  id: string;
  inspection_id: string;
  image_id?: string;
  field_name?: string;
  field?: string;
  raw_text?: string;
  detected_value?: string;
  normalized_value?: string;
  confidence: number;
  bbox?: number[];
  unit?: string;
  surface_type?: string;
  extraction_method?: string;
  is_verified?: boolean;
  reviewer_value?: string;
  created_at?: string;
}

export interface ComplianceResult {
  id: string;
  inspection_id: string;
  rule_id: string;
  field: string;
  detected_value?: string;
  normalized_value?: string;
  confidence: number;
  outcome: 'PASS' | 'REVIEW' | 'POSSIBLE_NON_COMPLIANCE' | string;
  severity?: string;
  evidence?: {
    image_id?: string;
    surface_type?: string;
    bbox?: [number, number, number, number];
    detected_text?: string;
    [key: string]: any;
  };
  legal_reference?: string;
  statutory_reference?: string;
  requirement?: string;
  statutory_requirement?: string;
  explanation?: string;
  reasoning?: string;
  surface_type?: string;
  bbox?: number[];
  manual_override?: boolean;
  override_action?: string;
  override_reason?: string;
  override_by?: string;
  override_at?: string;
  reviewer_status?: string;
  created_at?: string;
}

export interface ReviewAction {
  id: string;
  inspection_id: string;
  reviewer_id?: string;
  action_type: 'CONFIRM' | 'CORRECT' | 'REJECT' | 'REQUEST_NEW_IMAGE' | string;
  target_field: string;
  previous_value?: string;
  new_value?: string;
  reason?: string;
  created_at: string;
}

export interface AuditEvent {
  id: string;
  inspection_id: string;
  user_id?: string;
  event_type: string;
  description?: string;
  details?: any;
  performed_by?: string;
  state_before?: any;
  state_after?: any;
  created_at: string;
}

export interface Inspection {
  id: string;
  inspection_number: string;
  inspection_mode?: 'LEGAL_METROLOGY' | 'DEFECT' | string;
  product_name?: string;
  brand_name?: string;
  category: string;
  status: string;
  overall_outcome: 'COMPLIANT' | 'NEEDS_MANUAL_REVIEW' | 'POSSIBLE_NON_COMPLIANCE' | 'REVIEW' | 'PASS' | string;
  created_by_id?: string;
  location?: string;
  notes?: string;
  final_remarks?: string;
  report_path?: string;
  image_count?: number;
  images?: PackageImage[];
  declarations?: Declaration[];
  compliance_results?: ComplianceResult[];
  reviewer_actions?: ReviewAction[];
  audit_events?: AuditEvent[];
  created_at: string;
  updated_at?: string;
}

// --- Defect Inspection mode ---
export type DefectSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type DefectOutcome = 'PASS' | 'REVIEW' | 'DEFECTIVE' | 'PENDING';

export interface DefectDetection {
  id?: string;
  inspection_id?: string;
  image_id?: string | null;
  defect_type: string;
  severity: DefectSeverity | string;
  confidence: number;
  bbox: number[];
  area_ratio?: number;
  detector: string;
  metrics?: Record<string, any>;
  frame_index?: number | null;
  frame_timestamp_ms?: number | null;
  reviewer_status?: 'PENDING' | 'CONFIRMED' | 'REJECTED' | 'RELABELED' | string;
  reviewer_note?: string | null;
  created_at?: string;
}

export interface DefectScanMeta {
  latency_ms: number;
  fps: number | null;
  backend: string;
  image_size: [number, number];
  product_mask_used: boolean;
  reference_used: boolean;
  mean_brightness?: number;
  exposure_ok?: boolean;
  detection_count: number;
  outcome: DefectOutcome | string;
}

export interface LiveFrameResult extends DefectScanMeta {
  detections: DefectDetection[];
  quality_gate?: QualityGateResult;
  decision?: string;
  decision_code?: string;
  decision_reasons?: string[];
}

export interface DefectAnalyzeResult {
  image: PackageImage;
  detections: DefectDetection[];
  scan: DefectScanMeta;
  overall_outcome: DefectOutcome | string;
}

export interface DefectVideoSummary {
  video: string;
  source_fps: number;
  total_frames: number;
  frames_sampled: number;
  frames_with_defects: number;
  keyframes_saved: number;
  avg_latency_ms: number | null;
  processing_fps: number | null;
  detections_by_type: Record<string, number>;
  overall_outcome: DefectOutcome | string;
}

export interface RootCauseHint {
  defect_type: string;
  count: number;
  high_severity_count: number;
  priority: 'HIGH' | 'MEDIUM' | string;
  likely_causes: string[];
  recommended_actions: string[];
  evidence: string[];
}

export interface DefectInspection {
  id: string;
  inspection_number: string;
  inspection_mode?: string;
  product_name?: string;
  brand_name?: string;
  category: string;
  status: string;
  overall_outcome: DefectOutcome | string;
  location?: string;
  notes?: string;
  final_remarks?: string;
  report_path?: string;
  image_count?: number;
  defect_count?: number;
  top_defect_type?: string | null;
  images?: PackageImage[];
  defect_detections?: DefectDetection[];
  reviewer_actions?: ReviewAction[];
  audit_events?: AuditEvent[];
  root_causes?: RootCauseHint[];
  decision_analysis?: DecisionAnalysis;
  quality_gate?: QualityGateResult;
  reference_analysis?: ReferenceComparisonResult;
  created_at: string;
  updated_at?: string;
}

export interface QualityGateResult {
  status: 'SUITABLE' | 'SUITABLE_WITH_WARNINGS' | 'UNSUITABLE' | string;
  quality_status?: string;
  quality_score: number;
  recapture_recommended: boolean;
  measurements: {
    sharpness?: number;
    sharpness_index?: number;
    sharpness_threshold?: number;
    exposure?: number;
    mean_luminance?: number;
    contrast_std?: number;
    glare_ratio?: number;
    glare_ratio_max?: number;
    dimensions?: [number, number];
    product_coverage_ratio?: number;
  };
  issues: string[];
  warnings: string[];
  recommended_actions: string[];
  recommendations?: string[];
}

export interface DecisionAnalysis {
  outcome: 'PASS' | 'DEFECTIVE' | 'REVIEW' | string;
  decision_code: string;
  policy_version: string;
  primary_reason: string;
  reasons: string[];
  rule_violations: string[];
  confidence_band: string;
  human_review_required: boolean;
}

export interface ReferenceComparisonResult {
  reference_version: string;
  profile_category: string;
  alignment: {
    method: string;
    inlier_count: number;
    total_matches: number;
    alignment_confidence: number;
    status: string;
  };
  within_tolerance: boolean;
  mean_delta_e: number;
  max_color_delta_e_tolerance: number;
  anomaly_area_ratio: number;
  anomaly_area_tolerance: number;
  anomaly_regions_count: number;
  difference_heatmap_base64: string;
  aligned_inspected_base64: string;
  similarity_score?: number;
  aligned?: boolean;
}

export interface EdgeBenchmarkReport {
  test_configuration: {
    timestamp: string;
    hardware: string;
    model: string;
    model_size_mb: number;
    parameters_total: number;
    input_resolution: number[];
    warmup_runs: number;
    benchmark_runs: number;
  };
  pipeline_latency_ms: {
    image_acquisition_or_synthetic_load: { mean: number; p50: number; p95: number };
    image_quality_gate: { mean: number; p50: number; p95: number };
    neural_input_preprocessing: { mean: number; p50: number; p95: number };
    onnx_neural_inference_defectnet: { mean: number; p50: number; p95: number };
    opencv_morphological_linear_shading: { mean: number; p50: number; p95: number };
    nms_and_fusion_postprocessing: { mean: number; p50: number; p95: number };
    end_to_end_full_pipeline: { mean: number; p50: number; p95: number };
  };
  system_resources: {
    cpu_usage_pct: number;
    memory_process_rss_mb: number;
    system_memory_used_pct: number;
  };
  throughput_fps: {
    neural_only_fps: number;
    end_to_end_fps: number;
  };
  deployment_readiness: {
    edge_device_profile: string;
    neural_latency_acceptable_for_30fps: boolean;
    pipeline_status: string;
    recommendation: string;
  };
}

export interface ParetoAnalysis {
  total_detections: number;
  total_confirmed: number;
  vital_few: string[];
  pareto_distribution: Array<{
    category: string;
    count: number;
    confirmed_count: number;
    percentage: number;
    cumulative_percentage: number;
    in_vital_few: boolean;
  }>;
}

export interface DefectAnalytics {
  window_days: number;
  totals: {
    inspections: number;
    defective: number;
    review: number;
    pass: number;
    pending: number;
    defect_rate: number;
    detections: number;
  };
  most_frequent_type: string | null;
  by_type: Array<{
    defect_type: string;
    count: number;
    share: number;
    avg_confidence: number;
    severities: Record<string, number>;
  }>;
  by_severity: Record<string, number>;
  trend: Array<{ date: string; total: number; by_type: Record<string, number> }>;
  by_product: Array<{
    product_name: string;
    inspections: number;
    defective: number;
    defect_rate: number;
    detections: number;
    top_defect_type: string | null;
  }>;
  hotspots: Record<string, { grid: number[][]; dominant_region: string | null; dominant_share: number }>;
  feedback: {
    confirmed: number;
    relabeled: number;
    rejected: number;
    pending: number;
    precision_estimate: number | null;
  };
  performance: {
    frames_analyzed: number;
    avg_latency_ms: number | null;
    throughput_fps: number | null;
  };
  root_causes: RootCauseHint[];
  known_defect_types: string[];
}

export interface DefectLogItem extends DefectDetection {
  inspection_number: string;
  product_name?: string;
  batch?: string;
}

export interface DefectDetectorStatus {
  backend: string;
  precision?: string;
  opencv_version: string;
  model_loaded: boolean;
  model_path: string | null;
  int8_available?: boolean;
  jetson_profile_available?: boolean;
  model_classes: string[];
  model_error: string | null;
  defect_types: string[];
}

export interface JetsonProfile {
  model_name: string;
  fp32_size_kb: number;
  int8_size_kb: number;
  compression_ratio: number;
  size_reduction_pct: number;
  quantization_type: string;
  cpu_benchmarks: {
    fp32_mean_latency_ms: number;
    fp32_throughput_fps: number;
    int8_mean_latency_ms: number;
    int8_throughput_fps: number;
  };
  jetson_orin_nano_specifications: {
    target_device: string;
    gpu_architecture: string;
    ai_performance_tops: number;
    tensorrt_precision: string;
    estimated_jetson_tensorrt_latency_ms: number;
    estimated_jetson_throughput_fps: number;
    power_profiles: string[];
  };
}

export interface AnomalyPrediction {
  anomaly_score: number;
  raw_anomaly_distance: number;
  is_anomaly: boolean;
  threshold: number;
  anomaly_regions: Array<{
    box: [number, number, number, number];
    class: string;
    confidence: number;
    area_px: number;
    anomaly_distance: number;
    severity: string;
  }>;
  heatmap_base64: string;
  patches_analyzed: number;
  latency_ms: number;
  memory_bank_size: number;
}

export interface PLCStatus {
  online: boolean;
  protocol: string;
  host: string;
  port: number;
  simulation_mode: boolean;
  coils: Record<string, boolean>;
  holding_registers: Record<string, number>;
  opc_ua_nodes: Record<string, any>;
  last_actuation?: {
    timestamp: string;
    event_type: string;
    actuator: string;
    duration_ms: number;
    defect_class: string;
  };
  rejection_rate_pct: number;
}
