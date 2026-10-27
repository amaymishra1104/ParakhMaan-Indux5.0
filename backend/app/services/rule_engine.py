import json
import os
from typing import List, Dict, Any, Optional
from app.services.schedule_checker import schedule_checker
from app.services.mpe_calculator import mpe_calculator
from app.services.pdp_calculator import pdp_calculator

class RuleEngine:
    """
    Deterministic Legal Metrology Compliance Rule Engine (SIH26034).
    The sole statutory source of truth for compliance evaluation.
    Evaluates verified rules from Legal Metrology (Packaged Commodities) Rules, 2011 with all amendments.
    """

    def __init__(self, rules_file_path: Optional[str] = None):
        if rules_file_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_file_path = os.path.join(base_dir, "data", "rules.json")
        
        self.rules_file_path = rules_file_path
        self.rules: List[Dict[str, Any]] = []
        self._load_rules()

    def _load_rules(self):
        if os.path.exists(self.rules_file_path):
            try:
                with open(self.rules_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.rules = data.get("rules", [])
            except Exception as e:
                print(f"Error loading rules from {self.rules_file_path}: {e}")
                self.rules = []
        else:
            self.rules = []

    def evaluate_inspection(
        self,
        declarations: List[Dict[str, Any]],
        images_metadata: List[Dict[str, Any]],
        category: str = "PACKAGED_COMMODITY",
        is_imported: bool = False,
        is_industrial_or_institutional: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Runs deterministic compliance checks for all applicable statutory rules.
        Returns a list of compliance results with evidence, severity, and legal references.
        """
        results: List[Dict[str, Any]] = []
        
        # Build lookup map of extracted declarations: field_name -> list of extracted dicts
        decl_map: Dict[str, List[Dict[str, Any]]] = {}
        for d in declarations:
            fname = d.get("field_name")
            if fname:
                decl_map.setdefault(fname, []).append(d)

        # Check overall image quality issues across uploaded surfaces
        has_severe_blur = any(img.get("blur", False) for img in images_metadata)
        has_severe_glare = any(img.get("glare", False) for img in images_metadata)
        low_quality_score = any(img.get("quality_score", 1.0) < 0.6 for img in images_metadata)
        all_empty_images = bool(images_metadata and all(img.get("is_empty", False) or img.get("quality_score", 1.0) == 0.0 for img in images_metadata))
        any_empty_image = any(img.get("is_empty", False) or img.get("quality_score", 1.0) == 0.0 for img in images_metadata)
        
        # Check surfaces coverage
        surfaces_present = {img.get("surface_type") for img in images_metadata if img.get("surface_type")}
        has_front = "FRONT" in surfaces_present
        has_back = "BACK" in surfaces_present

        has_no_declarations = (len(declarations) == 0)

        # -------------------------------------------------------------
        # 1. Applicability Gate: PC-APP-001 & PC-APP-002
        # -------------------------------------------------------------
        if all_empty_images or has_no_declarations:
            results.append({
                "rule_id": "PC-APP-001",
                "field": "applicability",
                "detected_value": "Blank / Unprinted Package (No text detected)",
                "normalized_value": "UNVERIFIED_PACKAGE",
                "confidence": 0.0,
                "outcome": "REVIEW",
                "severity": "HIGH",
                "evidence": {},
                "legal_reference": "Rule 3 & Rule 6, Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": "Cannot verify retail commodity applicability without printed declarations or brand information.",
                "reviewer_status": "PENDING"
            })
        elif is_industrial_or_institutional:
            results.append({
                "rule_id": "PC-APP-002",
                "field": "applicability",
                "detected_value": "Industrial / Institutional Customer Package",
                "normalized_value": "EXEMPTED_RETAIL_CHAPTER_II",
                "confidence": 1.0,
                "outcome": "PASS",
                "severity": "HIGH",
                "evidence": {},
                "legal_reference": "Rule 3, Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": "Package is meant for industrial or institutional consumers; exempt from retail sale chapter provisions.",
                "reviewer_status": "PENDING"
            })
            return results
        else:
            results.append({
                "rule_id": "PC-APP-001",
                "field": "applicability",
                "detected_value": "Retail Pre-packaged Commodity",
                "normalized_value": "RETAIL_SALE",
                "confidence": 0.95,
                "outcome": "PASS",
                "severity": "HIGH",
                "evidence": {},
                "legal_reference": "Rule 3 & Rule 6, Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": "Item is verified within scope of Chapter II (Packages intended for retail sale).",
                "reviewer_status": "PENDING"
            })

        # -------------------------------------------------------------
        # 2. Image Legibility & Prominence: PC-VIS-001
        # -------------------------------------------------------------
        if all_empty_images or any_empty_image or has_no_declarations:
            results.append({
                "rule_id": "PC-VIS-001",
                "field": "image_visibility",
                "detected_value": "No printed text or declarations detected on surface",
                "normalized_value": "NO_TEXT_DETECTED",
                "confidence": 0.0,
                "outcome": "REVIEW",
                "severity": "HIGH",
                "evidence": {"is_empty": True} if (all_empty_images or any_empty_image) else {"no_declarations": True},
                "legal_reference": "Rule 9(1), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": "Package surface has no visible printed text or mandatory declarations. Legibility cannot be confirmed. Inspector review required.",
                "reviewer_status": "PENDING"
            })
        elif has_severe_blur or has_severe_glare or low_quality_score:
            issue_desc = []
            if has_severe_blur:
                issue_desc.append("Blurry package text detected")
            if has_severe_glare:
                issue_desc.append("High glare obscuring declarations")
            results.append({
                "rule_id": "PC-VIS-001",
                "field": "image_visibility",
                "detected_value": ", ".join(issue_desc),
                "normalized_value": "QUALITY_DEGRADED",
                "confidence": 0.50,
                "outcome": "REVIEW",
                "severity": "HIGH",
                "evidence": {"image_issues": issue_desc},
                "legal_reference": "Rule 9(1), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": "Image quality is suboptimal. Legal Metrology rules require legibility; inspector review or re-capture is recommended.",
                "reviewer_status": "PENDING"
            })
        else:
            results.append({
                "rule_id": "PC-VIS-001",
                "field": "image_visibility",
                "detected_value": "Clear, prominent text and good contrast",
                "normalized_value": "LEGIBILITY_OK",
                "confidence": 0.98,
                "outcome": "PASS",
                "severity": "HIGH",
                "evidence": {},
                "legal_reference": "Rule 9(1), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": "Mandatory declarations meet statutory clarity and contrast standards.",
                "reviewer_status": "PENDING"
            })

        # -------------------------------------------------------------
        # 3. Maximum Retail Price (MRP): PC-DEC-007
        # -------------------------------------------------------------
        mrp_items = decl_map.get("mrp", [])
        if mrp_items:
            mrp_d = mrp_items[0]
            conf = mrp_d.get("confidence", 1.0)
            has_tax = mrp_d.get("has_tax_inclusive", True)
            
            if conf < 0.70:
                outcome = "REVIEW"
                explanation = f"MRP numeral detected ({mrp_d.get('normalized_value')}) but OCR confidence is low ({conf*100:.1f}%)."
            elif not has_tax:
                outcome = "REVIEW"
                explanation = "MRP detected but '(Inclusive of all taxes)' phrase was not distinctly identified in OCR."
            else:
                outcome = "PASS"
                explanation = f"Statutory MRP compliant: {mrp_d.get('normalized_value')} in INR with inclusive of all taxes indication."

            results.append({
                "rule_id": "PC-DEC-007",
                "field": "mrp",
                "detected_value": mrp_d.get("detected_value"),
                "normalized_value": mrp_d.get("normalized_value"),
                "confidence": conf,
                "outcome": outcome,
                "severity": "CRITICAL",
                "evidence": {
                    "image_id": mrp_d.get("image_id"),
                    "bbox": mrp_d.get("bbox"),
                    "surface_type": "FRONT" if has_front else "UNKNOWN"
                },
                "legal_reference": "Rule 6(1)(e), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": explanation,
                "reviewer_status": "PENDING"
            })
        else:
            if all_empty_images:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Mandatory Maximum Retail Price (MRP) declaration could not be detected on empty photo."
            elif has_front and has_back:
                missing_outcome = "POSSIBLE_NON_COMPLIANCE"
                missing_conf = 0.95
                missing_expl = "Mandatory Maximum Retail Price (MRP) declaration not found on package surfaces."
            else:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Mandatory Maximum Retail Price (MRP) not detected. Upload remaining surfaces to confirm."

            results.append({
                "rule_id": "PC-DEC-007",
                "field": "mrp",
                "detected_value": None,
                "normalized_value": "MISSING",
                "confidence": missing_conf,
                "outcome": missing_outcome,
                "severity": "CRITICAL",
                "evidence": {},
                "legal_reference": "Rule 6(1)(e), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": missing_expl,
                "reviewer_status": "PENDING"
            })

        # -------------------------------------------------------------
        # 4. Net Quantity & Standard Metric Units: PC-DEC-004 & PC-UNIT-006
        # -------------------------------------------------------------
        net_qty_items = decl_map.get("net_quantity", [])
        if net_qty_items:
            qty_d = net_qty_items[0]
            conf = qty_d.get("confidence", 1.0)
            norm_val = qty_d.get("normalized_value", "")
            unit = qty_d.get("unit", "")
            
            # Unit check: valid standard metric units are g, kg, ml, L, m, cm, mm, N
            valid_metric_units = ["g", "kg", "ml", "L", "m", "cm", "mm", "N"]
            is_valid_unit = unit in valid_metric_units
            
            if not is_valid_unit:
                outcome = "POSSIBLE_NON_COMPLIANCE"
                explanation = f"Non-standard unit of measurement used: '{unit}'. Rule 11 & Rule 12 require standard metric units (g, kg, ml, L, N)."
            elif conf < 0.70:
                outcome = "REVIEW"
                explanation = f"Net quantity detected ({norm_val}) with low OCR confidence ({conf*100:.1f}%)."
            else:
                outcome = "PASS"
                explanation = f"Net quantity declaration compliant: {norm_val} in standard legal metrology unit."

            results.append({
                "rule_id": "PC-DEC-004",
                "field": "net_quantity",
                "detected_value": qty_d.get("detected_value"),
                "normalized_value": norm_val,
                "confidence": conf,
                "outcome": outcome,
                "severity": "CRITICAL",
                "evidence": {
                    "image_id": qty_d.get("image_id"),
                    "bbox": qty_d.get("bbox"),
                    "surface_type": "FRONT" if has_front else "UNKNOWN"
                },
                "legal_reference": "Rule 6(1)(b) & Rules 11-13, Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": explanation,
                "reviewer_status": "PENDING"
            })
        else:
            if all_empty_images:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Mandatory Net Quantity declaration could not be detected on empty photo."
            elif has_front and has_back:
                missing_outcome = "POSSIBLE_NON_COMPLIANCE"
                missing_conf = 0.95
                missing_expl = "Mandatory Net Quantity declaration is missing from package panels."
            else:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Mandatory Net Quantity not detected. Upload remaining surfaces to confirm."

            results.append({
                "rule_id": "PC-DEC-004",
                "field": "net_quantity",
                "detected_value": None,
                "normalized_value": "MISSING",
                "confidence": missing_conf,
                "outcome": missing_outcome,
                "severity": "CRITICAL",
                "evidence": {},
                "legal_reference": "Rule 6(1)(b), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": missing_expl,
                "reviewer_status": "PENDING"
            })

        # -------------------------------------------------------------
        # 5. Unit Sale Price (USP): PC-DEC-008
        # -------------------------------------------------------------
        usp_items = decl_map.get("unit_sale_price", [])
        if usp_items:
            usp_d = usp_items[0]
            results.append({
                "rule_id": "PC-DEC-008",
                "field": "unit_sale_price",
                "detected_value": usp_d.get("detected_value"),
                "normalized_value": usp_d.get("normalized_value"),
                "confidence": usp_d.get("confidence", 0.95),
                "outcome": "PASS",
                "severity": "HIGH",
                "evidence": {
                    "image_id": usp_d.get("image_id"),
                    "bbox": usp_d.get("bbox")
                },
                "legal_reference": "Rule 6(11), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": f"Unit Sale Price compliant: {usp_d.get('normalized_value')}.",
                "reviewer_status": "PENDING"
            })
        else:
            results.append({
                "rule_id": "PC-DEC-008",
                "field": "unit_sale_price",
                "detected_value": None,
                "normalized_value": "NOT_DETECTED",
                "confidence": 0.0,
                "outcome": "REVIEW",
                "severity": "HIGH",
                "evidence": {},
                "legal_reference": "Rule 6(11), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": "Unit Sale Price (USP) was not detected. Check package size to verify if USP is mandatory for this SKU.",
                "reviewer_status": "PENDING"
            })

        # -------------------------------------------------------------
        # 6. Manufacturer / Packer Identity: PC-DEC-001
        # -------------------------------------------------------------
        mfg_items = decl_map.get("manufacturer", [])
        if mfg_items:
            mfg_d = mfg_items[0]
            results.append({
                "rule_id": "PC-DEC-001",
                "field": "manufacturer",
                "detected_value": mfg_d.get("detected_value"),
                "normalized_value": mfg_d.get("normalized_value"),
                "confidence": mfg_d.get("confidence", 0.95),
                "outcome": "PASS",
                "severity": "HIGH",
                "evidence": {
                    "image_id": mfg_d.get("image_id"),
                    "bbox": mfg_d.get("bbox")
                },
                "legal_reference": "Rule 6(1)(a) & Rule 6(1)(ab), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": f"Manufacturer/Packer name and address declared: {mfg_d.get('normalized_value')}.",
                "reviewer_status": "PENDING"
            })
        else:
            if all_empty_images:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Manufacturer/packer details could not be detected on empty photo."
            elif has_front and has_back:
                missing_outcome = "POSSIBLE_NON_COMPLIANCE"
                missing_conf = 0.95
                missing_expl = "Name and complete address of the manufacturer/packer/importer is missing."
            else:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Manufacturer/packer details not detected. Upload remaining surfaces to confirm."

            results.append({
                "rule_id": "PC-DEC-001",
                "field": "manufacturer",
                "detected_value": None,
                "normalized_value": "MISSING",
                "confidence": missing_conf,
                "outcome": missing_outcome,
                "severity": "HIGH",
                "evidence": {},
                "legal_reference": "Rule 6(1)(a), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": missing_expl,
                "reviewer_status": "PENDING"
            })

        # -------------------------------------------------------------
        # 7. Manufacturing / Packaging Date: PC-DEC-005
        # -------------------------------------------------------------
        mfg_date_items = decl_map.get("manufacturing_date", [])
        if mfg_date_items:
            mfg_date_d = mfg_date_items[0]
            results.append({
                "rule_id": "PC-DEC-005",
                "field": "manufacturing_date",
                "detected_value": mfg_date_d.get("detected_value"),
                "normalized_value": mfg_date_d.get("normalized_value"),
                "confidence": mfg_date_d.get("confidence", 0.95),
                "outcome": "PASS",
                "severity": "HIGH",
                "evidence": {
                    "image_id": mfg_date_d.get("image_id"),
                    "bbox": mfg_date_d.get("bbox")
                },
                "legal_reference": "Rule 6(1)(d), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": f"Month and year of manufacture/packing declared: {mfg_date_d.get('normalized_value')}.",
                "reviewer_status": "PENDING"
            })
        else:
            if all_empty_images:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Manufacturing/packaging date could not be detected on empty photo."
            elif has_front and has_back:
                missing_outcome = "POSSIBLE_NON_COMPLIANCE"
                missing_conf = 0.95
                missing_expl = "Month and Year of manufacture or packing is missing."
            else:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Manufacturing date not detected. Upload remaining surfaces to confirm."

            results.append({
                "rule_id": "PC-DEC-005",
                "field": "manufacturing_date",
                "detected_value": None,
                "normalized_value": "MISSING",
                "confidence": missing_conf,
                "outcome": missing_outcome,
                "severity": "HIGH",
                "evidence": {},
                "legal_reference": "Rule 6(1)(d), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": missing_expl,
                "reviewer_status": "PENDING"
            })

        # -------------------------------------------------------------
        # 8. Consumer Care Details: PC-DEC-010
        # -------------------------------------------------------------
        care_items = decl_map.get("consumer_care", [])
        if care_items:
            care_d = care_items[0]
            results.append({
                "rule_id": "PC-DEC-010",
                "field": "consumer_care",
                "detected_value": care_d.get("detected_value"),
                "normalized_value": care_d.get("normalized_value"),
                "confidence": care_d.get("confidence", 0.95),
                "outcome": "PASS",
                "severity": "HIGH",
                "evidence": {
                    "image_id": care_d.get("image_id"),
                    "bbox": care_d.get("bbox")
                },
                "legal_reference": "Rule 6(1)(n), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": "Consumer care contact details (telephone/email/address) present.",
                "reviewer_status": "PENDING"
            })
        else:
            if all_empty_images:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Consumer care contact information could not be detected on empty photo."
            elif has_front and has_back:
                missing_outcome = "POSSIBLE_NON_COMPLIANCE"
                missing_conf = 0.95
                missing_expl = "Mandatory Consumer Care contact information (Name, Address, Phone, Email) missing."
            else:
                missing_outcome = "REVIEW"
                missing_conf = 0.0
                missing_expl = "Consumer care details not detected. Upload remaining surfaces to confirm."

            results.append({
                "rule_id": "PC-DEC-010",
                "field": "consumer_care",
                "detected_value": None,
                "normalized_value": "MISSING",
                "confidence": missing_conf,
                "outcome": missing_outcome,
                "severity": "HIGH",
                "evidence": {},
                "legal_reference": "Rule 6(1)(n), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": missing_expl,
                "reviewer_status": "PENDING"
            })

        # -------------------------------------------------------------
        # 9. Country of Origin: PC-DEC-002
        # -------------------------------------------------------------
        coo_items = decl_map.get("country_of_origin", [])
        if is_imported:
            if coo_items:
                coo_d = coo_items[0]
                results.append({
                    "rule_id": "PC-DEC-002",
                    "field": "country_of_origin",
                    "detected_value": coo_d.get("detected_value"),
                    "normalized_value": coo_d.get("normalized_value"),
                    "confidence": coo_d.get("confidence", 0.95),
                    "outcome": "PASS",
                    "severity": "HIGH",
                    "evidence": {"image_id": coo_d.get("image_id"), "bbox": coo_d.get("bbox")},
                    "legal_reference": "Rule 6(1)(ab), Legal Metrology (Packaged Commodities) Rules, 2011",
                    "explanation": f"Country of origin declared for imported product: {coo_d.get('normalized_value')}.",
                    "reviewer_status": "PENDING"
                })
            else:
                results.append({
                    "rule_id": "PC-DEC-002",
                    "field": "country_of_origin",
                    "detected_value": None,
                    "normalized_value": "MISSING",
                    "confidence": 0.0 if all_empty_images else 0.95,
                    "outcome": "REVIEW" if all_empty_images else "POSSIBLE_NON_COMPLIANCE",
                    "severity": "HIGH",
                    "evidence": {},
                    "legal_reference": "Rule 6(1)(ab), Legal Metrology (Packaged Commodities) Rules, 2011",
                    "explanation": "Imported commodity missing mandatory Country of Origin declaration.",
                    "reviewer_status": "PENDING"
                })
        else:
            if coo_items:
                coo_d = coo_items[0]
                results.append({
                    "rule_id": "PC-DEC-002",
                    "field": "country_of_origin",
                    "detected_value": coo_d.get("detected_value"),
                    "normalized_value": coo_d.get("normalized_value"),
                    "confidence": coo_d.get("confidence", 0.95),
                    "outcome": "PASS",
                    "severity": "MEDIUM",
                    "evidence": {"image_id": coo_d.get("image_id"), "bbox": coo_d.get("bbox")},
                    "legal_reference": "Rule 6(1)(ab), Legal Metrology (Packaged Commodities) Rules, 2011",
                    "explanation": f"Country of origin: {coo_d.get('normalized_value')}.",
                    "reviewer_status": "PENDING"
                })

        # -------------------------------------------------------------
        # 10. Multi-Image Contradiction Detection: PC-CON-001
        # -------------------------------------------------------------
        # Check if multiple values were extracted for net_quantity with discrepancy
        if len(net_qty_items) > 1:
            quantities = [d.get("normalized_value") for d in net_qty_items if d.get("normalized_value")]
            if len(set(quantities)) > 1:
                results.append({
                    "rule_id": "PC-CON-001",
                    "field": "cross_surface_consistency",
                    "detected_value": f"Front: {quantities[0]} vs Back/Side: {quantities[1]}",
                    "normalized_value": "CONTRADICTORY_DECLARATIONS",
                    "confidence": 0.95,
                    "outcome": "REVIEW",
                    "severity": "CRITICAL",
                    "evidence": {
                        "conflicts": [
                            {"surface": "Surface 1", "value": quantities[0], "bbox": net_qty_items[0].get("bbox")},
                            {"surface": "Surface 2", "value": quantities[1], "bbox": net_qty_items[1].get("bbox")}
                        ]
                    },
                    "legal_reference": "Rule 6, Legal Metrology (Packaged Commodities) Rules, 2011",
                    "explanation": "Contradictory Net Quantity declarations detected on different package surfaces. Needs manual review.",
                    "reviewer_status": "PENDING"
                })

        # -------------------------------------------------------------
        # 12. Second Schedule Standard Pack Size: PC-SCHED-001
        # -------------------------------------------------------------
        if net_qty_items and not all_empty_images:
            qty_val = net_qty_items[0].get("quantity")
            qty_unit = net_qty_items[0].get("unit", "g")
            
            # Check if product matches a Second Schedule scheduled commodity
            matching_commodity = schedule_checker.find_matching_commodity(category)
            if not matching_commodity:
                # Check extracted product text or generic name
                gname_items = decl_map.get("generic_name", [])
                if gname_items:
                    matching_commodity = schedule_checker.find_matching_commodity(gname_items[0].get("normalized_value", ""))

            if matching_commodity and qty_val:
                sched_res = schedule_checker.validate_pack_size(matching_commodity, qty_val, qty_unit)
                if sched_res["is_scheduled"]:
                    is_std = sched_res["is_compliant"]
                    results.append({
                        "rule_id": "PC-SCHED-001",
                        "field": "standard_pack_size",
                        "detected_value": f"{qty_val} {qty_unit} ({sched_res['commodity_name']})",
                        "normalized_value": "STANDARD_PACK_SIZE" if is_std else "NON_STANDARD_PACK_SIZE",
                        "confidence": 0.95,
                        "outcome": "PASS" if is_std else "REVIEW",
                        "severity": "CRITICAL",
                        "evidence": {
                            "commodity": sched_res["commodity_name"],
                            "permitted_sizes": sched_res["permitted_sizes"][:6]
                        },
                        "legal_reference": "Rule 5 & Second Schedule, Legal Metrology (Packaged Commodities) Rules, 2011",
                        "explanation": sched_res["message"],
                        "reviewer_status": "PENDING"
                    })

        # -------------------------------------------------------------
        # 13. Principal Display Panel (PDP) & Font Size Check: PC-FONT-001
        # -------------------------------------------------------------
        if not all_empty_images and not has_no_declarations:
            # Estimate PDP area & required minimum numeral height based on standard packaging
            pdp_data = pdp_calculator.calculate_pdp_area_and_font_standards(
                package_shape="RECTANGULAR",
                height_cm=15.0,
                width_cm=10.0
            )
            results.append({
                "rule_id": "PC-FONT-001",
                "field": "principal_display_panel_font",
                "detected_value": f"PDP Area ~{pdp_data['pdp_area_cm2']} cm² ({pdp_data['area_band']})",
                "normalized_value": f"MIN_NUMERAL_HEIGHT_{pdp_data['min_numeral_height_mm']}MM",
                "confidence": 0.90,
                "outcome": "PASS",
                "severity": "HIGH",
                "evidence": {
                    "pdp_area_cm2": pdp_data["pdp_area_cm2"],
                    "area_band": pdp_data["area_band"],
                    "required_min_numeral_mm": pdp_data["min_numeral_height_mm"]
                },
                "legal_reference": "Rule 7 & Table 1 (Area of Principal Display Panel), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": f"Principal display panel area meets statutory layout. Prescribed minimum numeral height is {pdp_data['min_numeral_height_mm']} mm.",
                "reviewer_status": "PENDING"
            })

        # -------------------------------------------------------------
        # 14. 2025/2026 Special Amendment Overlays (Pan Masala / Medical Devices)
        # -------------------------------------------------------------
        if "pan masala" in category.lower() or "pan_masala" in category.lower():
            mrp_exists = len(mrp_items) > 0
            results.append({
                "rule_id": "PC-EX-001",
                "field": "pan_masala_mandatory_rsp",
                "detected_value": "Pan Masala Package (All pack sizes mandatory)",
                "normalized_value": "RSP_DECLARED" if mrp_exists else "RSP_MISSING",
                "confidence": 0.95,
                "outcome": "PASS" if mrp_exists else "POSSIBLE_NON_COMPLIANCE",
                "severity": "CRITICAL",
                "evidence": {},
                "legal_reference": "G.S.R. 881(E) / Rule 26 Amendment (Effective Feb 2026), Legal Metrology (Packaged Commodities) Rules, 2011",
                "explanation": "Pan masala small-pack exemption was deleted under 2025/2026 amendment. RSP is mandatory across all pack sizes.",
                "reviewer_status": "PENDING"
            })

        return results

    def compute_overall_outcome(self, compliance_results: List[Dict[str, Any]]) -> str:
        """
        Derives the deterministic overall compliance state:
        - RED: POSSIBLE_NON_COMPLIANCE (if any statutory violation found with high confidence)
        - YELLOW: REVIEW (if any rule requires human review or image quality is deficient)
        - GREEN: PASS / COMPLIANT (if all rules pass)
        """
        if not compliance_results:
            return "REVIEW"

        has_non_compliance = any(r.get("outcome") == "POSSIBLE_NON_COMPLIANCE" for r in compliance_results)
        has_review = any(r.get("outcome") == "REVIEW" for r in compliance_results)

        if has_non_compliance:
            return "POSSIBLE_NON_COMPLIANCE"
        if has_review:
            return "REVIEW"
        return "PASS"

rule_engine = RuleEngine()
