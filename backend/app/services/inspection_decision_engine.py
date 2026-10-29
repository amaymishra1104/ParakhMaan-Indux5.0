"""
Defensible Inspection Decision Engine for ParakhMaan Industrial QC.
------------------------------------------------------------------
Implements traceable, deterministic, auditable decision rules that synthesize:
  1. Optical Image Quality Gate status
  2. Deep learning and morphological defect findings
  3. Golden-reference tolerance checks
  4. Human reviewer sign-offs and corrections
  5. Policy-based risk tolerances

Outcomes:
  - PASS: All acceptance criteria met within certified tolerances.
  - REJECT (DEFECTIVE): Validated disqualifying defect or critical tolerance violation.
  - MANUAL REVIEW: Low optical confidence, borderline detection score, or conflicting sensor data.
"""

from typing import Any, Dict, List, Optional


class DefectDecisionEngine:
    POLICY_VERSION = "2026.1-industrial-qc"

    def __init__(
        self,
        critical_conf_threshold: float = 0.45,
        high_conf_threshold: float = 0.60,
        medium_defect_limit: int = 2,
        allow_unsuitable_auto_pass: bool = False,
    ):
        self.critical_conf_threshold = critical_conf_threshold
        self.high_conf_threshold = high_conf_threshold
        self.medium_defect_limit = medium_defect_limit
        self.allow_unsuitable_auto_pass = allow_unsuitable_auto_pass

    def evaluate(
        self,
        detections: List[Dict[str, Any]],
        quality_gate: Optional[Dict[str, Any]] = None,
        reference_comparison: Optional[Any] = None,
        reviewer_actions: Optional[List[Dict[str, Any]]] = None,
        profile_name: Optional[str] = "METAL_SHEET",
    ) -> Dict[str, Any]:
        if isinstance(reference_comparison, str):
            profile_name = reference_comparison
            reference_comparison = None

        reasons: List[str] = []
        rule_violations: List[str] = []

        # 1. Human Inspector Overrides take precedence if present
        if reviewer_actions:
            for act in reviewer_actions:
                action_type = act.get("action_type")
                if action_type == "CONFIRM" and act.get("severity") in ("CRITICAL", "HIGH"):
                    return {
                        "outcome": "DEFECTIVE",
                        "decision_code": "HUMAN_CONFIRMED_DEFECT",
                        "policy_version": self.POLICY_VERSION,
                        "primary_reason": f"Quality inspector confirmed {act.get('defect_type')} defect as {act.get('severity')}.",
                        "reasons": [f"Reviewer override by {act.get('reviewer_id') or 'inspector'}"],
                        "rule_violations": ["CRITICAL_SEVERITY_CONFIRMED"],
                        "confidence_band": "HIGH",
                        "human_review_required": False,
                    }

        # 2. Optical Quality Gate Evaluation
        quality_status = (quality_gate or {}).get("quality_status") or (quality_gate or {}).get("status", "SUITABLE")
        if quality_status == "UNSUITABLE":
            reasons.append("Image optical quality is UNSUITABLE (blur, glare, or poor framing). Automatic PASS prohibited.")
            return {
                "outcome": "REVIEW",
                "decision_code": "IMAGE_UNSUITABLE_FOR_INSPECTION",
                "policy_version": self.POLICY_VERSION,
                "primary_reason": "Inspection frame optical quality does not meet minimum industrial standards. Recapture or manual review required.",
                "reasons": reasons + (quality_gate.get("issues", []) if quality_gate else []),
                "rule_violations": ["OPTICAL_STANDARDS_VIOLATED", "IMAGE_UNSUITABLE_FOR_INSPECTION"],
                "confidence_band": "LOW",
                "human_review_required": True,
            }

        # Filter out detections rejected by a reviewer
        active_dets = [d for d in detections if d.get("reviewer_status") != "REJECTED"]

        # 3. Reference Tolerance Check
        if reference_comparison and isinstance(reference_comparison, dict):
            tol = reference_comparison.get("tolerance_evaluation", {})
            if tol.get("overall_status") == "REJECT":
                rule_violations.append("GOLDEN_REFERENCE_TOLERANCE_EXCEEDED")
                reasons.append(
                    f"Golden reference comparison exceeded tolerance: anomaly area {reference_comparison.get('anomaly_area_ratio', 0) * 100:.2f}% "
                    f"(max: {reference_comparison.get('anomaly_area_tolerance', 0) * 100:.2f}%), "
                    f"mean Delta-E {reference_comparison.get('mean_delta_e', 0):.1f} (max: {reference_comparison.get('max_color_delta_e_tolerance', 0):.1f})."
                )

        # 4. Critical & High Severity Automated Defects
        critical_defects = [
            d for d in active_dets
            if (d.get("severity") == "CRITICAL" or d.get("is_critical"))
            and (d.get("confidence", 0) >= 0.40 or d.get("reviewer_status") in ("CONFIRMED", "RELABELED"))
        ]
        high_defects = [
            d for d in active_dets
            if d.get("severity") == "HIGH"
            and (d.get("confidence", 0) >= 0.45 or d.get("reviewer_status") in ("CONFIRMED", "RELABELED"))
        ]
        medium_defects = [
            d for d in active_dets
            if d.get("severity") == "MEDIUM" and d.get("confidence", 0) >= 0.40
        ]

        if critical_defects:
            for cd in critical_defects:
                rule_violations.append(f"CRITICAL_{cd.get('defect_type', 'DEFECT')}_DETECTED")
                reasons.append(f"Critical defect detected: {cd.get('defect_type')} (confidence: {cd.get('confidence', 0) * 100:.0f}%, area: {cd.get('area_ratio', 0) * 100:.2f}%).")

            return {
                "outcome": "DEFECTIVE",
                "decision_code": "CRITICAL_DEFECT_DETECTED",
                "policy_version": self.POLICY_VERSION,
                "primary_reason": f"Disqualifying {critical_defects[0].get('defect_type')} detected violating structural integrity.",
                "reasons": reasons,
                "rule_violations": ["CRITICAL_SEVERITY_DETECTED"] + rule_violations,
                "confidence_band": "VERY_HIGH",
                "human_review_required": False,
            }

        if high_defects or len(rule_violations) > 0:
            for hd in high_defects:
                rule_violations.append(f"HIGH_{hd.get('defect_type', 'DEFECT')}_DETECTED")
                reasons.append(f"High-severity defect detected: {hd.get('defect_type')} (confidence: {hd.get('confidence', 0) * 100:.0f}%).")

            return {
                "outcome": "DEFECTIVE",
                "decision_code": "HIGH_SEVERITY_DEFECT_DETECTED",
                "policy_version": self.POLICY_VERSION,
                "primary_reason": "High severity quality defect detected violating acceptance threshold.",
                "reasons": reasons,
                "rule_violations": rule_violations,
                "confidence_band": "HIGH",
                "human_review_required": False,
            }

        # 5. Multiple Medium Defects or Borderline Cases
        if len(medium_defects) > self.medium_defect_limit:
            rule_violations.append("EXCESSIVE_MEDIUM_DEFECTS")
            reasons.append(f"Product exhibits {len(medium_defects)} medium defects, exceeding batch allowance of {self.medium_defect_limit}.")
            return {
                "outcome": "DEFECTIVE",
                "decision_code": "MULTIPLE_MEDIUM_DEFECTS",
                "policy_version": self.POLICY_VERSION,
                "primary_reason": f"Cumulative defect density exceeded threshold ({len(medium_defects)} defects observed).",
                "reasons": reasons,
                "rule_violations": rule_violations,
                "confidence_band": "MEDIUM",
                "human_review_required": False,
            }

        if len(medium_defects) > 0:
            reasons.append(f"{len(medium_defects)} minor/medium defects observed requiring inspector sign-off.")
            return {
                "outcome": "REVIEW",
                "decision_code": "BORDERLINE_DEFECTS_OR_QUALITY_WARNING",
                "policy_version": self.POLICY_VERSION,
                "primary_reason": "Low-severity or borderline defects observed; human verification recommended before release.",
                "reasons": reasons,
                "rule_violations": rule_violations,
                "confidence_band": "MEDIUM",
                "human_review_required": True,
            }

        # 6. Clean PASS (even with subtle lighting/framing warnings)
        pass_reasons = ["Zero disqualifying defects detected"]
        if quality_status == "SUITABLE_WITH_WARNINGS":
            pass_reasons.append("Optical quality accepted with minor warnings")
        else:
            pass_reasons.append("Optical quality verified as SUITABLE")

        return {
            "outcome": "PASS",
            "decision_code": "ALL_CLEAR",
            "policy_version": self.POLICY_VERSION,
            "primary_reason": "Surface free of disqualifying defects; meets all optical and reference criteria.",
            "reasons": pass_reasons,
            "rule_violations": [],
            "confidence_band": "HIGH",
            "human_review_required": False,
        }


inspection_decision_engine = DefectDecisionEngine()
