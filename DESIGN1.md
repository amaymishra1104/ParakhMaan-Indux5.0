# Dual-Mode Design Notes
# SIH26034 + Surface Defect Inspection Mode

## Mode Indicator
Show a clear visual badge on every Inspection:
- **Legal Metrology** → Blue badge (`#0075de`)
- **Surface Defect** → Amber / Orange badge (`#dd5b00` or similar)

## Defect Visualization
- Draw bounding boxes on images using the existing Evidence Viewer / overlay system
- Colour coding by severity:
  - LOW → Green (`#1aae39`)
  - MEDIUM → Amber
  - HIGH → Orange
  - CRITICAL → Red
- Show defect type + confidence on the box or on hover
- Reuse existing heatmap_service logic where possible for attention overlays

## Dashboard
- Keep all existing Legal Metrology cards and charts
- Add a new section or tab: **Defect Analytics**
  - Total defects detected
  - Top defect types (Pareto style)
  - Severity distribution
  - Trend over time

## New Components (Recommended)
- `DefectOverlay.tsx` — Bounding boxes on image
- `DefectTable.tsx` — List of defects with severity and confidence
- `DefectCharts.tsx` — Analytics charts (Recharts)

## Consistency Rules
- Reuse existing design tokens from current DESIGN.md (colors, typography, rounded, spacing)
- Do not create a completely new visual language
- Defect mode should feel like a natural extension of the same product
- Navbar should have a clear way to switch or filter by mode

## Edge / Real-time Considerations
- Show latency (ms) or FPS when running defect detection
- Support continuous capture mode in CameraCaptureModal later
