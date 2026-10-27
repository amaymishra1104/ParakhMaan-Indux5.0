from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "INSPECTOR"
    badge_number: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    badge_number: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str

# --- Image Schemas ---
class ImageQualityMetadata(BaseModel):
    quality_score: float
    blur: bool
    glare: bool
    resolution_ok: bool
    perspective_ok: bool
    occlusion_detected: bool
    surface_visible: bool
    sharpness_score: float
    issues: List[str] = []

class ImageResponse(BaseModel):
    id: str
    inspection_id: str
    surface_type: str
    file_path: str
    original_filename: str
    quality_score: float
    quality_metadata: Optional[Dict[str, Any]] = None
    ocr_raw_data: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Declaration Schemas ---
class DeclarationResponse(BaseModel):
    id: str
    inspection_id: str
    image_id: Optional[str] = None
    field_name: str
    detected_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence: float
    bbox: Optional[List[float]] = None
    extraction_method: str
    is_verified: bool
    reviewer_value: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DeclarationCorrectionRequest(BaseModel):
    field_name: str
    corrected_value: str
    reason: Optional[str] = None

# --- Compliance Schemas ---
class ComplianceResultResponse(BaseModel):
    id: str
    inspection_id: str
    rule_id: str
    field: str
    detected_value: Optional[str] = None
    normalized_value: Optional[str] = None
    confidence: float
    outcome: str  # PASS, REVIEW, POSSIBLE_NON_COMPLIANCE
    severity: str
    evidence: Optional[Dict[str, Any]] = None
    legal_reference: Optional[str] = None
    explanation: Optional[str] = None
    reviewer_status: str
    created_at: datetime

    class Config:
        from_attributes = True

class RuleResponse(BaseModel):
    id: str
    rule_id: str
    layer: str
    category: str
    condition: Optional[str] = None
    requirement: str
    what_to_detect: str
    validation_logic: str
    severity: str
    source_ids: Optional[str] = None
    status: str
    version: str

    class Config:
        from_attributes = True

# --- Reviewer Action Schemas ---
class ReviewActionRequest(BaseModel):
    target_field: str
    action_type: str  # CONFIRM, CORRECT, REJECT, REQUEST_NEW_IMAGE
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: Optional[str] = None

class ReviewActionResponse(BaseModel):
    id: str
    inspection_id: str
    reviewer_id: Optional[str] = None
    action_type: str
    target_field: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Audit Event Schemas ---
class AuditEventResponse(BaseModel):
    id: str
    inspection_id: str
    user_id: Optional[str] = None
    event_type: str
    description: str
    state_before: Optional[Dict[str, Any]] = None
    state_after: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Inspection Schemas ---
class InspectionCreate(BaseModel):
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    category: str = "PACKAGED_COMMODITY"
    location: Optional[str] = None
    notes: Optional[str] = None

class InspectionUpdate(BaseModel):
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class InspectionFinalizeRequest(BaseModel):
    final_remarks: Optional[str] = None
    override_status: Optional[str] = None  # COMPLIANT, POSSIBLE_NON_COMPLIANCE, REVIEW

class InspectionResponse(BaseModel):
    id: str
    inspection_number: str
    inspection_mode: Optional[str] = "LEGAL_METROLOGY"
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    category: str
    status: str
    overall_outcome: str
    created_by_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    final_remarks: Optional[str] = None
    report_path: Optional[str] = None
    image_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InspectionDetailResponse(BaseModel):
    id: str
    inspection_number: str
    inspection_mode: Optional[str] = "LEGAL_METROLOGY"
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    category: str
    status: str
    overall_outcome: str
    created_by_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    final_remarks: Optional[str] = None
    report_path: Optional[str] = None
    images: List[ImageResponse] = []
    declarations: List[DeclarationResponse] = []
    compliance_results: List[ComplianceResultResponse] = []
    reviewer_actions: List[ReviewActionResponse] = []
    audit_events: List[AuditEventResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Dashboard Schemas ---
class DashboardSummaryResponse(BaseModel):
    total_inspections: int
    compliant_count: int
    needs_review_count: int
    non_compliance_count: int
    draft_count: int
    recent_inspections: List[InspectionResponse]
    common_violations: List[Dict[str, Any]]
    category_distribution: List[Dict[str, Any]]

# --- Defect Inspection Mode Schemas ---
class DefectInspectionCreate(BaseModel):
    product_name: Optional[str] = None
    brand_name: Optional[str] = None  # batch / lot identifier
    category: str = "GENERAL_MANUFACTURED"  # product line, e.g. METAL_SHEET, CASTING, CERAMIC_TILE
    location: Optional[str] = None  # production line / station
    notes: Optional[str] = None

class DefectDetectionResponse(BaseModel):
    id: str
    inspection_id: str
    image_id: Optional[str] = None
    defect_type: str
    severity: str
    confidence: float
    bbox: List[float] = []
    area_ratio: float = 0.0
    detector: str
    metrics: Optional[Dict[str, Any]] = None
    frame_index: Optional[int] = None
    frame_timestamp_ms: Optional[float] = None
    reviewer_status: str
    reviewer_note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DefectInspectionDetailResponse(BaseModel):
    id: str
    inspection_number: str
    inspection_mode: Optional[str] = "DEFECT"
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    category: str
    status: str
    overall_outcome: str
    location: Optional[str] = None
    notes: Optional[str] = None
    final_remarks: Optional[str] = None
    report_path: Optional[str] = None
    images: List[ImageResponse] = []
    defect_detections: List[DefectDetectionResponse] = []
    reviewer_actions: List[ReviewActionResponse] = []
    audit_events: List[AuditEventResponse] = []
    root_causes: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DefectInspectionSummary(InspectionResponse):
    defect_count: int = 0
    top_defect_type: Optional[str] = None

class DefectFeedbackRequest(BaseModel):
    action: str = Field(..., pattern="^(CONFIRM|REJECT|RELABEL)$")
    defect_type: Optional[str] = None  # required for RELABEL
    note: Optional[str] = None

class DefectFrameRequest(BaseModel):
    image_base64: str
    max_side: int = Field(640, ge=160, le=1920)
    inspection_id: Optional[str] = None  # uses that inspection's golden reference, if any

class DefectFinalizeRequest(BaseModel):
    final_remarks: Optional[str] = None
    override_outcome: Optional[str] = None  # PASS, REVIEW, DEFECTIVE
