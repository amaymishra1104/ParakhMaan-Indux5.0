import base64
import os
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.industrial_quality_gate import industrial_quality_gate
from app.services.golden_reference_service import golden_reference_service
from app.services.inspection_decision_engine import inspection_decision_engine
from app.services.defect_detection_service import defect_detector, synthesize_surface_sample

client = TestClient(app)


def test_quality_gate_clean_image():
    img = synthesize_surface_sample([])
    res = industrial_quality_gate.analyze(img)
    assert res["status"] in ("SUITABLE", "SUITABLE_WITH_WARNINGS")
    assert "sharpness" in res["measurements"]
    assert "exposure" in res["measurements"]
    assert "glare_ratio" in res["measurements"]


def test_quality_gate_blurred_image():
    img = synthesize_surface_sample([])
    # Blur heavily
    blurred = cv2.GaussianBlur(img, (45, 45), 0)
    res = industrial_quality_gate.analyze(blurred)
    assert res["status"] in ("UNSUITABLE", "SUITABLE_WITH_WARNINGS")
    assert any("blur" in w.lower() or "sharpness" in w.lower() for w in res["warnings"])
    assert len(res["recommendations"]) > 0


def test_golden_reference_comparison():
    ref = synthesize_surface_sample([])
    # Inspected image has a synthetic scratch added
    insp = synthesize_surface_sample(["SCRATCH"], seed=10)
    res = golden_reference_service.align_and_compare(insp, ref, profile_name="METAL_SHEET")
    assert "aligned" in res
    assert "similarity_score" in res
    assert "difference_heatmap_base64" in res
    assert res["similarity_score"] >= 0.0


def test_decision_engine_rules():
    # 1. Clean + suitable -> PASS
    q_good = {"status": "SUITABLE", "quality_score": 95, "warnings": []}
    res_pass = inspection_decision_engine.evaluate([], q_good, "METAL_SHEET")
    assert res_pass["outcome"] == "PASS"
    assert res_pass["decision_code"] == "ALL_CLEAR"

    # 2. Critical defect -> DEFECTIVE
    dets_bad = [{
        "defect_type": "CRACK",
        "severity": "CRITICAL",
        "confidence": 0.95,
        "is_critical": True
    }]
    res_fail = inspection_decision_engine.evaluate(dets_bad, q_good, "METAL_SHEET")
    assert res_fail["outcome"] == "DEFECTIVE"
    assert "CRITICAL_SEVERITY_DETECTED" in res_fail["rule_violations"]

    # 3. Unsuitable image -> REVIEW
    q_bad = {"status": "UNSUITABLE", "quality_score": 30, "warnings": ["Excessive blur"]}
    res_review = inspection_decision_engine.evaluate([], q_bad, "METAL_SHEET")
    assert res_review["outcome"] == "REVIEW"
    assert "IMAGE_UNSUITABLE_FOR_INSPECTION" in res_review["rule_violations"]


def test_defect_detector_onnx_status():
    status = defect_detector.status()
    assert status["model_loaded"] is True
    assert status["inference_engine"] == "ONNXRuntime"
    assert status["backend"] == "hybrid"


def test_api_benchmarks_endpoint():
    res = client.get("/api/v1/defects/benchmarks")
    assert res.status_code == 200
    data = res.json()
    assert "system_status" in data
    assert data["system_status"]["model_loaded"] is True


def test_api_models_status_endpoint():
    res = client.get("/api/v1/defects/models/status")
    assert res.status_code == 200
    data = res.json()
    assert "detector_status" in data
    assert "classes" in data
    assert "SCRATCH" in data["classes"]
    assert "supported_profiles" in data


def test_api_analyze_frame_with_decision():
    img = synthesize_surface_sample(["SCRATCH"])
    _, buf = cv2.imencode(".jpg", img)
    b64 = base64.b64encode(buf).decode("utf-8")
    res = client.post("/api/v1/defects/analyze-frame", json={"image_base64": b64, "max_side": 480})
    assert res.status_code == 200
    data = res.json()
    assert "quality_gate" in data
    assert "decision" in data
    assert "decision_code" in data
    assert "detections" in data


def test_api_pareto_analytics_endpoint():
    res = client.get("/api/v1/defects/analytics/pareto")
    assert res.status_code == 200
    data = res.json()
    assert "pareto_distribution" in data
    assert "vital_few" in data


def test_api_dataset_export_endpoint():
    res = client.post("/api/v1/defects/dataset/export")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "manifest_path" in data


def test_int8_quantization_and_precision_switching():
    # Test precision switching between FP32 and INT8
    status_fp32 = defect_detector.switch_precision("FP32")
    assert status_fp32["precision"] == "FP32"
    assert status_fp32["model_loaded"] is True

    status_int8 = defect_detector.switch_precision("INT8")
    assert status_int8["precision"] == "INT8"
    assert status_int8["model_loaded"] is True
    assert status_int8["int8_available"] is True

    # Revert to FP32 for default test consistency
    defect_detector.switch_precision("FP32")


def test_jetson_profile_endpoint():
    res = client.get("/api/v1/defects/models/jetson-profile")
    assert res.status_code == 200
    data = res.json()
    assert "target_device" in data or "jetson_orin_nano_specifications" in data


def test_patchcore_anomaly_detection_and_training():
    from app.services.patchcore_anomaly_service import patchcore_service
    # Test clean surface
    clean = np.full((320, 320, 3), 160, dtype=np.uint8)
    for y in range(0, 320, 4):
        clean[y : y + 2, :] = 165
    res_clean = patchcore_service.predict(clean)
    assert "anomaly_score" in res_clean
    assert "is_anomaly" in res_clean
    assert res_clean["is_anomaly"] is False

    # Test anomalous surface (foreign burn / tear)
    defective = clean.copy()
    cv2.circle(defective, (160, 160), 30, (20, 20, 20), -1)
    res_def = patchcore_service.predict(defective)
    assert res_def["anomaly_score"] > res_clean["anomaly_score"]
    assert res_def["is_anomaly"] is True
    assert len(res_def["anomaly_regions"]) >= 1


def test_industrial_plc_service_and_pneumatic_trigger():
    from app.services.industrial_plc_service import plc_service
    status = plc_service.get_status()
    assert status["online"] is True
    assert "PNEUMATIC_REJECT_ACTUATOR" in status["coils"]
    assert "LAST_INSPECTION_DECISION" in status["holding_registers"]

    # Trigger pneumatic reject
    act = plc_service.trigger_pneumatic_reject(duration_ms=100, defect_class="CRACK", confidence=0.96)
    assert act["status"] == "ACTUATED"
    assert act["valve_state"] == "OPEN_PULSE"
    assert act["stack_light"] == "RED"

    # Verify registers updated
    status_updated = plc_service.get_status()
    assert status_updated["holding_registers"]["LAST_INSPECTION_DECISION"] == 2  # 2: DEFECTIVE


def test_api_plc_endpoints():
    # GET status
    res = client.get("/api/v1/defects/plc/status")
    assert res.status_code == 200
    data = res.json()
    assert data["online"] is True
    assert "coils" in data
    assert "opc_ua_nodes" in data

    # POST trigger
    res_trig = client.post("/api/v1/defects/plc/trigger?duration_ms=120&defect_class=SCRATCH")
    assert res_trig.status_code == 200
    trig_data = res_trig.json()
    assert trig_data["status"] == "ACTUATED"
    assert trig_data["pulse_duration_ms"] == 120
