import pytest
from app.services.declaration_service import DeclarationExtractor

def test_declaration_mrp_extraction():
    extractor = DeclarationExtractor()
    spans = [
        {"text": "MRP Rs. 149.00 (Incl. of all taxes)", "confidence": 0.98, "bbox": [10, 10, 50, 20], "image_id": "img_1"},
        {"text": "Net Qty: 1 kg", "confidence": 0.97, "bbox": [10, 30, 50, 40], "image_id": "img_1"},
        {"text": "Unit Sale Price: Rs. 0.15 / g", "confidence": 0.94, "bbox": [10, 50, 50, 60], "image_id": "img_1"},
        {"text": "Mfg Date: 08/2026", "confidence": 0.95, "bbox": [10, 70, 50, 80], "image_id": "img_1"},
        {"text": "Manufactured by: Pure Foods India Ltd", "confidence": 0.93, "bbox": [10, 90, 50, 100], "image_id": "img_1"}
    ]

    decls = extractor.extract_from_spans(spans)
    decl_map = {d["field_name"]: d for d in decls}

    assert "mrp" in decl_map
    assert decl_map["mrp"]["numeric_value"] == 149.0
    assert decl_map["mrp"]["has_tax_inclusive"] is True

    assert "net_quantity" in decl_map
    assert decl_map["net_quantity"]["quantity"] == 1.0
    assert decl_map["net_quantity"]["unit"] == "kg"

    assert "unit_sale_price" in decl_map
    assert "manufacturing_date" in decl_map
    assert "manufacturer" in decl_map


def test_declaration_standalone_rupee_and_mrp():
    """
    Tests standalone Rs 20, ₹ 20, 20/-, and multi-line MRP lookahead.
    """
    extractor = DeclarationExtractor()
    
    # Case 1: Standalone Rs 20
    spans_rs = [{"text": "Rs 20", "confidence": 0.95, "bbox": [10, 10, 50, 20], "image_id": "img_1"}]
    decls_rs = extractor.extract_from_spans(spans_rs)
    decl_map_rs = {d["field_name"]: d for d in decls_rs}
    assert "mrp" in decl_map_rs
    assert decl_map_rs["mrp"]["numeric_value"] == 20.0
    assert "20.00" in decl_map_rs["mrp"]["normalized_value"]

    # Case 2: Standalone ₹ 20
    spans_rupee = [{"text": "₹ 20", "confidence": 0.95, "bbox": [10, 10, 50, 20], "image_id": "img_1"}]
    decls_rupee = extractor.extract_from_spans(spans_rupee)
    decl_map_rupee = {d["field_name"]: d for d in decls_rupee}
    assert "mrp" in decl_map_rupee
    assert decl_map_rupee["mrp"]["numeric_value"] == 20.0

    # Case 3: Standalone 20/-
    spans_slash = [{"text": "20/-", "confidence": 0.95, "bbox": [10, 10, 50, 20], "image_id": "img_1"}]
    decls_slash = extractor.extract_from_spans(spans_slash)
    decl_map_slash = {d["field_name"]: d for d in decls_slash}
    assert "mrp" in decl_map_slash
    assert decl_map_slash["mrp"]["numeric_value"] == 20.0

    # Case 4: Multiline MRP lookahead
    spans_multi = [
        {"text": "MRP Rs. (incl. of all taxes)", "confidence": 0.92, "bbox": [10, 10, 50, 20], "image_id": "img_1"},
        {"text": "20", "confidence": 0.95, "bbox": [10, 25, 50, 35], "image_id": "img_1"}
    ]
    decls_multi = extractor.extract_from_spans(spans_multi)
    decl_map_multi = {d["field_name"]: d for d in decls_multi}
    assert "mrp" in decl_map_multi
    assert decl_map_multi["mrp"]["numeric_value"] == 20.0
    assert decl_map_multi["mrp"]["has_tax_inclusive"] is True


def test_declaration_barrier_lookahead_no_wrong_mrp():
    """
    Tests that MRP lookahead does not jump over a Batch header to grab a batch code as MRP,
    and that non-date batch codes (like N Ei 245) are saved as batch_number, NOT manufacturing_date.
    """
    extractor = DeclarationExtractor()
    spans = [
        {"text": "MRP Rs. (incl. of all", "confidence": 0.92, "bbox": [10, 10, 50, 20], "image_id": "img_1"},
        {"text": "Batch No., Mfd. & use by date:", "confidence": 0.94, "bbox": [10, 25, 50, 35], "image_id": "img_1"},
        {"text": "N Ei 245", "confidence": 0.90, "bbox": [10, 40, 50, 50], "image_id": "img_1"},
        {"text": "Net Quantity: 30 g", "confidence": 0.96, "bbox": [10, 60, 50, 70], "image_id": "img_1"}
    ]
    decls = extractor.extract_from_spans(spans)
    decl_map = {d["field_name"]: d for d in decls}

    # 245 is a batch code, must NOT be extracted as MRP!
    assert "mrp" not in decl_map or decl_map.get("mrp", {}).get("numeric_value") != 245.0
    # N Ei 245 is a batch number, NOT a manufacturing date
    assert "batch_number" in decl_map
    assert "N Ei 245" in decl_map["batch_number"]["normalized_value"]
    assert "manufacturing_date" not in decl_map


def test_declaration_manufacturing_date_proximity_and_lookahead():
    """
    Tests manufacturing date extraction when printed near MRP/Rupee or multi-line batch headers.
    """
    extractor = DeclarationExtractor()

    # Case 1: Date printed near Rs 20
    spans_near_mrp = [
        {"text": "Rs 20 (incl. of all taxes)", "confidence": 0.95, "bbox": [10, 10, 50, 20], "image_id": "img_1"},
        {"text": "08/2026", "confidence": 0.92, "bbox": [10, 30, 50, 40], "image_id": "img_1"}
    ]
    decls_near = extractor.extract_from_spans(spans_near_mrp)
    decl_map_near = {d["field_name"]: d for d in decls_near}
    assert "mrp" in decl_map_near
    assert "manufacturing_date" in decl_map_near
    assert decl_map_near["manufacturing_date"]["normalized_value"] == "08/2026"

    # Case 2: Multi-line Batch & Mfd header lookahead with valid date
    spans_batch = [
        {"text": "Batch No., Mfd. & use by date:", "confidence": 0.94, "bbox": [10, 10, 50, 20], "image_id": "img_1"},
        {"text": "24/05/2026", "confidence": 0.93, "bbox": [10, 25, 50, 35], "image_id": "img_1"}
    ]
    decls_batch = extractor.extract_from_spans(spans_batch)
    decl_map_batch = {d["field_name"]: d for d in decls_batch}
    assert "manufacturing_date" in decl_map_batch
    assert decl_map_batch["manufacturing_date"]["normalized_value"] == "24/05/2026"

    # Case 3: Standalone Month Year e.g. JAN 2026
    spans_month = [
        {"text": "Net Qty: 50 g", "confidence": 0.95, "bbox": [10, 10, 50, 20], "image_id": "img_1"},
        {"text": "JAN 2026", "confidence": 0.91, "bbox": [10, 30, 50, 40], "image_id": "img_1"}
    ]
    decls_month = extractor.extract_from_spans(spans_month)
    decl_map_month = {d["field_name"]: d for d in decls_month}
    assert "manufacturing_date" in decl_map_month
    assert decl_map_month["manufacturing_date"]["normalized_value"] == "JAN 2026"
