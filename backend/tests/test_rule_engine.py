import pytest
from app.services.rule_engine import RuleEngine

def test_rule_engine_determinism():
    """
    Test that the deterministic rule engine produces identical outputs
    for identical inputs across multiple runs (No stochastic hallucinations).
    """
    engine = RuleEngine()

    mock_declarations = [
        {"field_name": "mrp", "detected_value": "MRP Rs. 50.00 (Incl. of all taxes)", "normalized_value": "₹ 50.00 (Incl. of all taxes)", "confidence": 0.98, "has_tax_inclusive": True},
        {"field_name": "net_quantity", "detected_value": "Net Qty: 250 g", "normalized_value": "250 g", "confidence": 0.96, "unit": "g"},
        {"field_name": "manufacturer", "detected_value": "ABC Industries Pvt Ltd", "normalized_value": "ABC Industries Pvt Ltd", "confidence": 0.95},
        {"field_name": "manufacturing_date", "detected_value": "05/2026", "normalized_value": "05/2026", "confidence": 0.97},
        {"field_name": "consumer_care", "detected_value": "Care: 1800-000-111", "normalized_value": "1800-000-111", "confidence": 0.95},
    ]

    mock_images = [
        {"surface_type": "FRONT", "quality_score": 0.95, "blur": False, "glare": False},
        {"surface_type": "BACK", "quality_score": 0.95, "blur": False, "glare": False}
    ]

    run1 = engine.evaluate_inspection(mock_declarations, mock_images, category="PACKAGED_FOOD")
    run2 = engine.evaluate_inspection(mock_declarations, mock_images, category="PACKAGED_FOOD")

    assert len(run1) == len(run2)
    for r1, r2 in zip(run1, run2):
        assert r1["rule_id"] == r2["rule_id"]
        assert r1["outcome"] == r2["outcome"]
        assert r1["normalized_value"] == r2["normalized_value"]

def test_rule_engine_missing_mrp_detection():
    """
    Test that a package missing mandatory MRP flags POSSIBLE_NON_COMPLIANCE.
    """
    engine = RuleEngine()

    mock_declarations = [
        {"field_name": "net_quantity", "detected_value": "Net Qty: 250 g", "normalized_value": "250 g", "confidence": 0.96, "unit": "g"},
    ]

    mock_images = [
        {"surface_type": "FRONT", "quality_score": 0.95, "blur": False, "glare": False},
        {"surface_type": "BACK", "quality_score": 0.95, "blur": False, "glare": False}
    ]

    results = engine.evaluate_inspection(mock_declarations, mock_images)
    mrp_res = next((r for r in results if r["field"] == "mrp"), None)

    assert mrp_res is not None
    assert mrp_res["outcome"] == "POSSIBLE_NON_COMPLIANCE"
    assert engine.compute_overall_outcome(results) == "POSSIBLE_NON_COMPLIANCE"

def test_rule_engine_contradiction_detection():
    """
    Test that conflicting Net Quantity declarations trigger a REVIEW state.
    """
    engine = RuleEngine()

    mock_declarations = [
        {"field_name": "net_quantity", "detected_value": "Net Qty: 500 g", "normalized_value": "500 g", "confidence": 0.98, "unit": "g", "bbox": [10, 10, 50, 50]},
        {"field_name": "net_quantity", "detected_value": "Net Weight: 450 g", "normalized_value": "450 g", "confidence": 0.97, "unit": "g", "bbox": [10, 10, 50, 50]},
        {"field_name": "mrp", "detected_value": "MRP Rs. 50 (Incl. taxes)", "normalized_value": "₹ 50.00 (Incl. of all taxes)", "confidence": 0.98, "has_tax_inclusive": True},
        {"field_name": "manufacturer", "detected_value": "XYZ Ltd", "normalized_value": "XYZ Ltd", "confidence": 0.95},
        {"field_name": "manufacturing_date", "detected_value": "05/2026", "normalized_value": "05/2026", "confidence": 0.95},
        {"field_name": "consumer_care", "detected_value": "support@xyz.com", "normalized_value": "support@xyz.com", "confidence": 0.95}
    ]

    mock_images = [
        {"surface_type": "FRONT", "quality_score": 0.95, "blur": False, "glare": False},
        {"surface_type": "BACK", "quality_score": 0.95, "blur": False, "glare": False}
    ]

    results = engine.evaluate_inspection(mock_declarations, mock_images)
    con_res = next((r for r in results if r["rule_id"] == "PC-CON-001"), None)

    assert con_res is not None
    assert con_res["outcome"] == "REVIEW"
    assert engine.compute_overall_outcome(results) == "REVIEW"

def test_rule_engine_empty_photo_zero_confidence():
    """
    Test that uploading an empty or blank photo results in 0.0 confidence (0%)
    and flags REVIEW for visibility and applicability instead of claiming false high confidence.
    """
    engine = RuleEngine()

    empty_declarations = []
    empty_images = [
        {"surface_type": "FRONT", "quality_score": 0.0, "blur": False, "glare": False, "is_empty": True}
    ]

    results = engine.evaluate_inspection(empty_declarations, empty_images)
    
    # 1. Image Visibility must be flagged with 0.0 confidence
    vis_res = next((r for r in results if r["rule_id"] == "PC-VIS-001"), None)
    assert vis_res is not None
    assert vis_res["outcome"] == "REVIEW"
    assert vis_res["confidence"] == 0.0

    # 2. Missing MRP on empty image must have confidence 0.0, not legacy 85%
    mrp_res = next((r for r in results if r["field"] == "mrp"), None)
    assert mrp_res is not None
    assert mrp_res["confidence"] == 0.0
    assert mrp_res["outcome"] == "REVIEW"

    # 3. Overall outcome must be REVIEW
    assert engine.compute_overall_outcome(results) == "REVIEW"

