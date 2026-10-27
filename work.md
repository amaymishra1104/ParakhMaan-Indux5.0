You are a Senior Full-Stack + AI/ML Engineer responsible for building a production-quality working prototype for Smart India Hackathon 2026 problem statement SIH26034:

"AI-Powered Legal Metrology Compliance & Inspection Platform"

PROJECT OBJECTIVE
-----------------
Build a working web-based prototype that allows a Legal Metrology inspector to upload 1–4 images of a packaged commodity and automatically:

1. Analyze image quality.
2. Detect/read package text using OCR.
3. Extract structured legal declarations.
4. Identify product/category context.
5. Determine applicable compliance rules.
6. Validate extracted declarations against a deterministic rule engine.
7. Produce PASS / REVIEW / POSSIBLE NON-COMPLIANCE results.
8. Show visual evidence with bounding boxes and confidence scores.
9. Allow human review of uncertain cases.
10. Generate an inspection report.
11. Store inspection history.

IMPORTANT LEGAL/ARCHITECTURAL PRINCIPLE
-----------------------------------------
AI/LLM must NEVER be the final legal decision maker.

Use this architecture:

Image
  ↓
Image Quality
  ↓
OCR / Computer Vision
  ↓
Declaration Extraction
  ↓
LLM/NLP for semantic normalization if needed
  ↓
Structured Data
  ↓
DETERMINISTIC VERSIONED RULE ENGINE
  ↓
Compliance Result
  ↓
Evidence
  ↓
Human Review when uncertain

The LLM may interpret, normalize or explain information, but the deterministic rule engine is the sole source of truth for compliance decisions.

Never automatically accuse a company of fraud or illegality.

Use these states:

GREEN  = COMPLIANT
YELLOW = NEEDS MANUAL REVIEW
RED    = POSSIBLE NON-COMPLIANCE

If OCR is uncertain, image quality is poor, required package surfaces are missing, or rule applicability is uncertain, return REVIEW instead of guessing.


==================================================
1. TECHNOLOGY STACK
==================================================

FRONTEND
---------
Next.js
React
TypeScript
Tailwind CSS
shadcn/ui if useful
Recharts or ECharts for dashboard

BACKEND
-------
Python
FastAPI
Pydantic
SQLAlchemy

AI / COMPUTER VISION
--------------------
OpenCV
PaddleOCR / PP-OCR
YOLO-family model where useful for package/category detection

LLM
---
Use an open-source local LLM.

Preferred options:
- Qwen
- Llama
- Mistral
- Gemma

Make the LLM provider abstraction configurable so the model can later be changed without modifying business logic.

Use LLM only for:
- semantic declaration extraction
- normalization
- ambiguous text interpretation
- human-readable explanations

Do NOT allow LLM output to directly determine compliance.

RAG
---
For the optional "Ask the Rule Book" feature, use:
- FAISS or Qdrant
- embeddings
- retrieval
- open-source LLM

DATABASE
--------
PostgreSQL

OBJECT STORAGE
--------------
MinIO for local development
S3-compatible abstraction for production

REPORTS
-------
ReportLab

AUTHENTICATION
--------------
JWT
Role-based access control

DEPLOYMENT
----------
Docker
docker-compose for local development


==================================================
2. PROJECT STRUCTURE
==================================================

Create a clean monorepo:

legal-metrology-ai/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── types/
│   └── public/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── core/
│   │   └── utils/
│   │
│   └── tests/
│
├── ai/
│   ├── image_quality/
│   ├── ocr/
│   ├── extraction/
│   ├── classification/
│   └── llm/
│
├── rule-engine/
│   ├── rules/
│   ├── validators/
│   ├── applicability/
│   └── tests/
│
├── reports/
│
├── database/
│   └── migrations/
│
├── data/
│
├── docs/
│
├── docker-compose.yml
├── .env.example
├── README.md
└── .gitignore


==================================================
3. MVP USER FLOW
==================================================

Build this exact flow first:

LOGIN
  ↓
DASHBOARD
  ↓
CREATE NEW INSPECTION
  ↓
UPLOAD 1–4 PACKAGE IMAGES
  ↓
IMAGE QUALITY ANALYSIS
  ↓
OCR
  ↓
DECLARATION EXTRACTION
  ↓
PRODUCT/CATEGORY CLASSIFICATION
  ↓
RULE ENGINE
  ↓
COMPLIANCE MATRIX
  ↓
EVIDENCE VIEWER
  ↓
MANUAL REVIEW IF REQUIRED
  ↓
FINALIZE INSPECTION
  ↓
GENERATE PDF REPORT
  ↓
SAVE INSPECTION HISTORY


==================================================
4. FRONTEND REQUIREMENTS
==================================================

Create the following pages:

/login
/dashboard
/inspections
/inspections/new
/inspections/[id]
/inspections/[id]/review
/reports

Dashboard should show:

- Total inspections
- Compliant
- Needs review
- Possible non-compliance
- Recent inspections
- Common issues

Create a clean government/enterprise inspection UI.

Do NOT create an over-designed flashy UI.

Prioritize:
- clarity
- usability
- evidence visibility
- inspector workflow
- responsive design


==================================================
5. IMAGE UPLOAD
==================================================

Allow upload of 1–4 images.

Each image should have:

- image ID
- inspection ID
- surface type
- original filename
- quality score
- storage path
- upload timestamp

Surface types:

FRONT
BACK
SIDE
TOP
BOTTOM
UNKNOWN

Display uploaded images as thumbnails.

Allow inspector to remove/replace images.


==================================================
6. IMAGE QUALITY ENGINE
==================================================

Implement OpenCV-based checks:

- blur detection
- sharpness
- glare/reflection detection
- resolution
- perspective/rotation
- occlusion
- image coverage

Return:

{
  "quality_score": 0.94,
  "blur": false,
  "glare": false,
  "resolution_ok": true,
  "perspective_ok": true,
  "occlusion_detected": false,
  "surface_visible": true
}

If image quality is too poor:

status = REVIEW

Do not continue blindly.

Show the inspector why the image needs review.


==================================================
7. OCR ENGINE
==================================================

Integrate PaddleOCR.

OCR output must preserve:

- text
- confidence
- bounding box
- image ID

Example:

{
  "text": "MRP ₹499",
  "confidence": 0.97,
  "bbox": [100, 200, 300, 250],
  "image_id": "img_123"
}

Display OCR text and bounding boxes on the image.

Create an OCR service abstraction so OCR provider can be replaced later.


==================================================
8. DECLARATION EXTRACTION
==================================================

Convert raw OCR text into structured declarations.

Support core fields:

- product_name
- manufacturer
- manufacturer_address
- packer
- importer
- net_quantity
- mrp
- manufacturing_or_packing_date
- consumer_care
- country_of_origin
- other_applicable_declarations

Example:

OCR:

"ABC Foods
Net Qty 500 g
MRP ₹60
Mfd 06/2026
Made in India"

Convert to:

{
  "product_name": null,
  "manufacturer": "ABC Foods",
  "net_quantity": "500 g",
  "mrp": "₹60",
  "manufacturing_or_packing_date": "06/2026",
  "country_of_origin": "India"
}

Use deterministic parsing/regex where possible.

Use LLM only where semantic interpretation is required.

Every extracted field must retain:

- value
- normalized_value
- confidence
- source_image
- bounding_box
- extraction_method


==================================================
9. LLM SERVICE
==================================================

Create an abstraction:

LLMService

with functions such as:

extract_declarations()
normalize_declaration()
explain_result()

Do not hard-code the application to one LLM.

Support a configurable local model endpoint.

For example:

OLLAMA_BASE_URL
LLM_MODEL

Never expose LLM secrets to frontend.

Validate all LLM output against Pydantic schemas.

If LLM returns malformed JSON:
- retry once
- fallback to deterministic extraction
- otherwise mark field REVIEW

The LLM must never directly output:

"LEGAL"
"ILLEGAL"
"FRAUD"
as a final compliance decision.

It may explain a deterministic result generated by the rule engine.


==================================================
10. PRODUCT CLASSIFICATION
==================================================

Create a product/category service.

Initial MVP may use:

- simple classifier
- YOLO
- OCR-based category hints
- manually selected category fallback

Supported example categories can include:

- packaged food
- cosmetics
- household goods
- toy
- imported packaged commodity
- other

Do not pretend the classifier is highly accurate without evaluation.

Store:

category
confidence
classification_method

If confidence is low:

status = REVIEW


==================================================
11. RULE ENGINE
==================================================

THIS IS THE MOST IMPORTANT BACKEND COMPONENT.

Create a deterministic rule engine independent from the LLM.

Rules should be versioned.

Each rule should contain:

- rule_id
- version
- effective_from
- effective_to
- product_category
- applicability_conditions
- required_declaration
- validation_type
- severity
- evidence_requirement
- description

Example conceptual rule:

{
  "rule_id": "LM-MRP-001",
  "version": "1.0",
  "category": "packaged_commodity",
  "required_field": "mrp",
  "validation": "presence",
  "severity": "high"
}

Rules should be stored in JSON/YAML initially and persisted/managed through PostgreSQL as the system matures.

The rule engine must support:

1. rule applicability
2. required fields
3. presence validation
4. value validation
5. format validation
6. consistency validation
7. confidence threshold
8. severity
9. evidence requirement
10. rule version

IMPORTANT:

Do not invent legal rules.

Only encode rules that are explicitly verified from authoritative Legal Metrology source material.

If a rule is not verified, mark it as:

"RULE_PENDING_VERIFICATION"

Do not present unverified rules as legal truth.


==================================================
12. COMPLIANCE ENGINE
==================================================

For every applicable rule:

INPUT:

- extracted declarations
- confidence
- image quality
- product category
- context
- rule

OUTPUT:

{
  "rule_id": "LM-MRP-001",
  "field": "mrp",
  "detected_value": "₹60",
  "normalized_value": "60 INR",
  "confidence": 0.97,
  "outcome": "PASS",
  "evidence": {
      "image_id": "img_123",
      "bbox": [100,200,300,250]
  }
}

Possible outcomes:

PASS
REVIEW
POSSIBLE_NON_COMPLIANCE

Never use binary AI-only classification.


==================================================
13. MULTI-IMAGE LOGIC
==================================================

Treat the package as a 3D object.

The system must track which surfaces have been inspected.

Example:

Front = scanned
Back = missing

Final result:

INSPECTION INCOMPLETE / REVIEW

NOT:

COMPLIANT

Also detect contradictions.

Example:

Front:
Net Qty = 500g

Back:
Net Qty = 450g

Result:

REVIEW
Reason:
CONTRADICTORY_DECLARATIONS

Highlight both pieces of evidence.


==================================================
14. EVIDENCE SYSTEM
==================================================

Every compliance result must be traceable.

Store:

- detected value
- normalized value
- OCR confidence
- image quality
- bounding box
- image ID
- rule ID
- rule version
- validation result
- reviewer action
- timestamp
- inspection ID

Build an Evidence Viewer.

When user clicks a result:

MRP → PASS

show:

- image
- highlighted bounding box
- detected value
- confidence
- rule ID
- rule version
- validation explanation

Example:

MRP
Value: ₹499
Confidence: 97%
Rule: LM-MRP-001
Result: PASS

Evidence:
Image #2
[Highlighted region]


==================================================
15. MANUAL REVIEW
==================================================

Create a review queue.

Cases requiring review:

- poor image
- low OCR confidence
- conflicting OCR outputs
- missing required surface
- uncertain category
- contradictory package declarations
- ambiguous rule applicability

Inspector actions:

CONFIRM
CORRECT
REJECT
REQUEST NEW IMAGE

Store reviewer identity and timestamp.

The system must preserve AI output and reviewer correction.


==================================================
16. COMPLIANCE MATRIX UI
==================================================

Create a table:

Field
Detected Value
Confidence
Rule
Evidence
Result

Example:

MRP              ₹60       97%    LM-001    View     PASS
Net Quantity     500 g     98%    LM-002    View     PASS
Manufacturer     ABC       94%    LM-003    View     PASS
Date             ?6/2026   61%    LM-004    View     REVIEW
Required Field   Missing   96%    LM-005    View     POSSIBLE NC

Use clear status badges.


==================================================
17. INSPECTION FINALIZATION
==================================================

The inspector should not be forced to accept an uncertain result automatically.

Final inspection status should be based on:

- rule engine outcomes
- reviewer decisions
- inspection completeness

Store:

DRAFT
PROCESSING
REVIEW
FINALIZED

Do not allow arbitrary frontend manipulation of compliance state.

The backend must recalculate/validate final status.


==================================================
18. PDF REPORT
==================================================

Generate a professional PDF.

Report should contain:

- inspection ID
- inspector
- timestamp
- product
- category
- uploaded images
- extracted declarations
- compliance matrix
- evidence
- rule references
- reviewer decisions
- final status

Use ReportLab.

Every result should reference the corresponding evidence.


==================================================
19. DATABASE
==================================================

Create PostgreSQL models for:

User
Product
Inspection
Image
Declaration
Rule
RuleVersion
ComplianceResult
Violation
ReviewerAction
AuditEvent

Suggested relationships:

Inspection
 ├── Images
 ├── Declarations
 ├── Results
 ├── ReviewerActions
 └── AuditEvents

Result
 ├── Rule
 └── Evidence/Image


==================================================
20. AUDIT LOG
==================================================

Create audit events:

- inspection_created
- image_uploaded
- OCR_completed
- declaration_extracted
- rule_evaluated
- review_started
- reviewer_corrected
- inspection_finalized
- report_generated

Store:

who
what
when
previous_state
new_state


==================================================
21. API DESIGN
==================================================

Create REST APIs.

Examples:

POST   /api/v1/inspections
GET    /api/v1/inspections
GET    /api/v1/inspections/{id}

POST   /api/v1/inspections/{id}/images
DELETE /api/v1/images/{id}

POST   /api/v1/inspections/{id}/process

GET    /api/v1/inspections/{id}/ocr
GET    /api/v1/inspections/{id}/declarations
GET    /api/v1/inspections/{id}/results

POST   /api/v1/inspections/{id}/review
POST   /api/v1/inspections/{id}/finalize

GET    /api/v1/inspections/{id}/report

GET    /api/v1/dashboard/summary


==================================================
22. SECURITY
==================================================

Implement:

- JWT authentication
- RBAC
- input validation
- file type validation
- file size limits
- secure image storage
- no secrets in Git
- environment variables
- backend authorization for every protected operation

Roles:

INSPECTOR
SUPERVISOR
ADMIN


==================================================
23. ERROR HANDLING
==================================================

Never crash the entire inspection pipeline because one AI component fails.

Example:

OCR failure
→ retry
→ fallback
→ REVIEW

LLM failure
→ deterministic extraction
→ REVIEW if necessary

Image quality failure
→ ask for another image

Classifier failure
→ manual category selection

Rule engine failure
→ DO NOT produce a compliance decision

Instead:

SYSTEM_ERROR / REVIEW


==================================================
24. TESTING
==================================================

Create unit tests for:

- image quality
- OCR parsing
- declaration extraction
- normalization
- rule applicability
- rule validation
- compliance status
- multi-image contradictions
- reviewer corrections
- report generation
- API endpoints

Most importantly test rule engine deterministically.

Given the same input + same rule version:

output must always be the same.


==================================================
25. DEMO DATA
==================================================

Create a small synthetic/demo dataset.

Include:

1. Clearly compliant package
2. Missing declaration
3. Blurry package
4. Glare package
5. Low OCR confidence
6. Contradictory front/back declarations
7. Different product categories

Do NOT claim these are official SIH datasets.

Do NOT claim model accuracy without evaluation.


==================================================
26. DASHBOARD
==================================================

Dashboard cards:

Total Inspections
Compliant
Needs Review
Possible Non-Compliance

Charts:

Inspection status
Common issues
Inspection trend

Recent inspections table:

ID
Product
Category
Status
Date
Reviewer


==================================================
27. OPTIONAL PHASE 2
==================================================

ONLY after MVP works, implement:

1. OCR consensus
2. difficult-text recovery
3. better multi-image reconstruction
4. contradiction detection
5. rule-admin UI
6. Ask the Rule Book RAG assistant
7. e-commerce listing inspection
8. improved dashboard


==================================================
28. OPTIONAL PHASE 3
==================================================

Only after Phase 2:

1. Lot registration
2. Sampling
3. Package clustering
4. Lot fingerprint
5. Anomaly detection
6. Adaptive sampling
7. Lot reports


==================================================
29. OPTIONAL PHASE 4
==================================================

Future roadmap:

1. Company inspection history
2. Repeat violation detection
3. Warehouse intelligence
4. Risk scoring
5. Inspection prioritisation
6. Multilingual OCR
7. Offline mobile app
8. Tamper-evident evidence ledger
9. Citizen reporting


==================================================
30. DEVELOPMENT STRATEGY
==================================================

DO NOT attempt to build all features at once.

Follow this exact order:

STEP 1
------
Project setup
Docker
PostgreSQL
MinIO
FastAPI
Next.js

STEP 2
------
Authentication
Dashboard shell
Inspection CRUD

STEP 3
------
Image upload
Image storage
Image quality

STEP 4
------
PaddleOCR integration
OCR result viewer
Bounding boxes

STEP 5
------
Declaration extraction
Structured JSON
Confidence handling

STEP 6
------
Product classification
Category selection fallback

STEP 7
------
Rule engine
Rule schema
Rule applicability
Validation
Compliance result

STEP 8
------
Evidence viewer
Compliance matrix
Review queue

STEP 9
------
Inspection finalization
Audit logs
PDF report

STEP 10
-------
End-to-end testing
Demo dataset
UI polish
Docker deployment


==================================================
31. IMPORTANT IMPLEMENTATION RULES
==================================================

1. Build working code, not pseudo-code.

2. Keep services modular.

3. Do not put everything into one file.

4. Use TypeScript on frontend.

5. Use Pydantic schemas for API contracts.

6. Use SQLAlchemy for database access.

7. Use environment variables for configuration.

8. Add README instructions.

9. Add Docker setup.

10. Add seed/demo data.

11. Add API documentation through FastAPI Swagger.

12. Write tests alongside modules.

13. Keep AI services replaceable.

14. Keep rule engine completely independent from LLM.

15. Never invent legal rules.

16. Never allow an LLM response to directly determine compliance.

17. Never treat OCR failure as legal non-compliance.

18. Never assume unseen package surfaces are compliant.

19. Always preserve evidence.

20. Prefer REVIEW over a false accusation.


==================================================
32. FIRST DEVELOPMENT TASK
==================================================

DO NOT start by implementing every feature.

First:

1. Create the complete repository structure.
2. Initialize Next.js frontend.
3. Initialize FastAPI backend.
4. Configure PostgreSQL.
5. Configure MinIO.
6. Configure Docker Compose.
7. Create database models.
8. Create basic authentication.
9. Create inspection CRUD.
10. Create image upload API.
11. Build the initial frontend flow.

After completing this, run the project and verify:

Frontend works
Backend works
Database connects
MinIO works
Image upload works
Inspection can be created

Then proceed to OCR.

At every stage:

- run the application
- test the feature
- fix errors
- only then move to the next stage.

Do not generate a huge amount of unfinished code.

Build incrementally and keep the project runnable after every major step.


==================================================
33. FINAL SUCCESS CRITERIA
==================================================

The MVP is considered successful only if this complete scenario works:

Inspector logs in
       ↓
Creates inspection
       ↓
Uploads front/back/side package images
       ↓
System evaluates image quality
       ↓
OCR extracts text
       ↓
System extracts declarations
       ↓
Product category identified
       ↓
Applicable rules selected
       ↓
Deterministic rule engine validates them
       ↓
Results shown as:
PASS / REVIEW / POSSIBLE NON-COMPLIANCE
       ↓
Inspector can click a result
       ↓
Evidence region is highlighted
       ↓
Uncertain case goes to manual review
       ↓
Inspector confirms/corrects
       ↓
Inspection finalized
       ↓
PDF report generated
       ↓
Inspection stored in history


START NOW
---------

Begin with STEP 1 only.

First inspect the environment and create the project structure.

Then implement:

- repository structure
- Next.js frontend
- FastAPI backend
- PostgreSQL
- MinIO
- Docker Compose
- basic health checks
- initial README

Do not jump to OCR or advanced AI until the base application is running.

After implementation, show:

1. Files created
2. Commands to run
3. Environment variables required
4. What is currently working
5. Next recommended task

Then wait for the next instruction.