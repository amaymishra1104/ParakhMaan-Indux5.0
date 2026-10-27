# Dual-Mode Inspection Platform
# SIH26034 (Legal Metrology) + PS 12 (Surface Defect Inspection)

## Core Principle
Add **Surface Defect Inspection** as a completely separate mode.
Do NOT break or heavily modify the existing Legal Metrology flow.

## Modes
- `LEGAL_METROLOGY` → Existing full flow (OCR + Rule Engine + Compliance)
- `SURFACE_DEFECT` → New defect detection flow

## Architecture
```
Image / Camera / Video Frame
        ↓
Image Quality Gate (OpenCV) — Shared
        ↓
┌─────────────────────┬─────────────────────┐
│ LEGAL_METROLOGY     │ SURFACE_DEFECT      │
│ OCR + LLM           │ Defect Detector     │
│ Declaration Extract │ (OpenCV baseline)   │
│ Rule Engine         │ Defect Scoring      │
│ Compliance Result   │ Defect Instances    │
└─────────────────────┴─────────────────────┘
        ↓
Evidence + Overlay / Heatmap (Shared, mode-aware)
        ↓
Dashboard + PDF Report + Audit (Shared)
```

## New Model: DefectDetection
Fields:
- id
- inspection_id
- image_id
- defect_type (SCRATCH, CRACK, DENT, DISCOLOURATION, DIMENSIONAL, FOREIGN, OTHER)
- severity (LOW, MEDIUM, HIGH, CRITICAL)
- confidence (0.0–1.0)
- bbox (JSON: [x1, y1, x2, y2])
- area_pixels
- notes
- created_at

Also add to Inspection model:
- inspection_mode: "LEGAL_METROLOGY" | "SURFACE_DEFECT" (default: LEGAL_METROLOGY)

## New Service: defect_detection_service.py
Phase 1 (Hackathon Demo – No Training Required):
- Classical OpenCV methods:
  - Scratches → Canny + Hough line detection
  - Cracks → Morphological blackhat
  - Discolouration → LAB colour deviation from reference region
  - Dents → Gradient / shading anomaly
  - Dimensional anomaly → Contour area / aspect ratio checks
- Return list of DefectDetection objects

Structure the service so a YOLO model can be plugged in later (hybrid approach).

## New Analytics Service
- Defect frequency by type
- Severity distribution
- Time trend
- Simple root-cause hints based on rules

## Frontend Changes
1. Mode selector when creating a new inspection
2. Conditional rendering in inspection detail:
   - LEGAL_METROLOGY → existing Compliance Matrix
   - SURFACE_DEFECT → Defect Table + Bounding Box Overlay
3. Dashboard: Add Defect Analytics cards / section
4. New pages under `/defects/` (optional but recommended)
5. Extend CameraCaptureModal for continuous / video mode later

## Constraints
- Keep Legal Metrology fully working
- Reuse: CameraCaptureModal, ImageQualityCard, EvidenceViewer, heatmap_service, auth, storage, PDF report framework, audit
- Maintain dual-engine philosophy (AI detects, deterministic logic decides)
- Clean separation of modes
- Fix `.gitignore` so `frontend/src/lib/api.ts` is not ignored

## Estimated Scope
~10 new files + ~10 modified files
1500–2500 lines of new code
