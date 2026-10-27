"""
First Schedule Maximum Permissible Error (MPE) and Fifth Schedule Sampling Engine.
Conforms strictly to Legal Metrology (Packaged Commodities) Rules, 2011.
"""
from typing import Dict, Any, List, Optional
import math

class MPECalculator:
    """
    Computes statutory Maximum Permissible Error (MPE) under First Schedule of PCR 2011.
    """

    @staticmethod
    def get_mpe_for_mass_or_volume(quantity: float, unit: str) -> Dict[str, Any]:
        """
        Calculates First Schedule MPE in grams or ml.
        """
        unit_lower = unit.lower().strip()
        
        # Convert to base grams or ml
        if unit_lower in ["kg", "l", "litre", "litres", "kilogram", "kilograms"]:
            qty_base = quantity * 1000.0
            base_unit = "g" if "g" in unit_lower else "ml"
        elif unit_lower in ["g", "gm", "gms", "ml", "gram", "grams", "millilitre"]:
            qty_base = quantity
            base_unit = "g" if "g" in unit_lower else "ml"
        else:
            # Fallback for count/meters
            return {
                "declared_quantity": quantity,
                "unit": unit,
                "mpe_percent": 0.0,
                "mpe_absolute": 0.0,
                "min_permitted_quantity": quantity,
                "tier_description": "Units/Count or Linear (Standard count tolerance: 0% unless multi-piece)"
            }

        # First Schedule Table for Mass / Volume
        if qty_base <= 50.0:
            mpe_pct = 9.0
            mpe_abs = (qty_base * 0.09)
            tier = "Up to 50 g/ml (9.0%)"
        elif 50.0 < qty_base <= 100.0:
            mpe_pct = (4.5 / qty_base) * 100.0
            mpe_abs = 4.5
            tier = "50 g/ml to 100 g/ml (4.5 g/ml fixed)"
        elif 100.0 < qty_base <= 200.0:
            mpe_pct = 4.5
            mpe_abs = (qty_base * 0.045)
            tier = "100 g/ml to 200 g/ml (4.5%)"
        elif 200.0 < qty_base <= 300.0:
            mpe_pct = (9.0 / qty_base) * 100.0
            mpe_abs = 9.0
            tier = "200 g/ml to 300 g/ml (9.0 g/ml fixed)"
        elif 300.0 < qty_base <= 500.0:
            mpe_pct = 3.0
            mpe_abs = (qty_base * 0.03)
            tier = "300 g/ml to 500 g/ml (3.0%)"
        elif 500.0 < qty_base <= 1000.0:
            mpe_pct = (15.0 / qty_base) * 100.0
            mpe_abs = 15.0
            tier = "500 g/ml to 1000 g/ml (15.0 g/ml fixed)"
        elif 1000.0 < qty_base <= 10000.0:
            mpe_pct = 1.5
            mpe_abs = (qty_base * 0.015)
            tier = "1 kg/L to 10 kg/L (1.5%)"
        elif 10000.0 < qty_base <= 15000.0:
            mpe_pct = (150.0 / qty_base) * 100.0
            mpe_abs = 150.0
            tier = "10 kg/L to 15 kg/L (150.0 g/ml fixed)"
        else:
            mpe_pct = 1.0
            mpe_abs = (qty_base * 0.01)
            tier = "More than 15 kg/L (1.0%)"

        mpe_abs = round(mpe_abs, 2)
        min_permitted = round(qty_base - mpe_abs, 2)
        t2_error_abs = round(mpe_abs * 2.0, 2)
        min_t2_permitted = round(qty_base - t2_error_abs, 2)

        return {
            "declared_quantity": quantity,
            "declared_quantity_base": qty_base,
            "unit": unit,
            "base_unit": base_unit,
            "mpe_percent": round(mpe_pct, 2),
            "mpe_absolute": mpe_abs,
            "t1_limit": min_permitted,
            "t2_error_absolute": t2_error_abs,
            "t2_limit": min_t2_permitted,
            "tier_description": tier,
            "legal_reference": "First Schedule (Rule 22), Legal Metrology (Packaged Commodities) Rules, 2011"
        }

    @staticmethod
    def evaluate_sample_lot(
        lot_size: int,
        declared_quantity: float,
        unit: str,
        measured_weights: List[float]
    ) -> Dict[str, Any]:
        """
        Evaluates physical net quantity inspection under Fifth Schedule sampling protocol.
        """
        mpe_data = MPECalculator.get_mpe_for_mass_or_volume(declared_quantity, unit)
        qty_base = mpe_data.get("declared_quantity_base", declared_quantity)
        mpe_abs = mpe_data["mpe_absolute"]
        t1_thresh = mpe_data["t1_limit"]
        t2_thresh = mpe_data["t2_limit"]

        sample_size = len(measured_weights)
        if sample_size == 0:
            return {
                "lot_status": "NO_SAMPLES",
                "message": "No sample weights provided."
            }

        # Fifth Schedule sample size requirements:
        if lot_size <= 500:
            recommended_sample = 32
            max_allowable_defective = 1
        elif lot_size <= 3200:
            recommended_sample = 80
            max_allowable_defective = 3
        else:
            recommended_sample = 125
            max_allowable_defective = 5

        # Calculate Sample Statistics
        mean_weight = float(sum(measured_weights) / sample_size)
        variance = float(sum((x - mean_weight) ** 2 for x in measured_weights) / max(1, sample_size - 1))
        std_dev = math.sqrt(variance)

        # Correction factor (Student's t-correction for sample mean)
        correction_factor = 2.0 / math.sqrt(sample_size)
        corrected_mean = round(mean_weight + (correction_factor * std_dev / math.sqrt(sample_size)), 2)

        # Count T1 and T2 defectives
        t1_defectives = [w for w in measured_weights if w < t1_thresh]
        t2_defectives = [w for w in measured_weights if w < t2_thresh]

        t1_count = len(t1_defectives)
        t2_count = len(t2_defectives)

        # Statutory Fifth Schedule Criteria:
        # 1. Corrected average net quantity >= declared net quantity
        # 2. Number of units with deficiency > MPE (T1 error) <= max_allowable_defective
        # 3. No unit with deficiency > 2x MPE (T2 error)
        is_mean_pass = corrected_mean >= qty_base
        is_t1_pass = t1_count <= max_allowable_defective
        is_t2_pass = (t2_count == 0)

        lot_pass = is_mean_pass and is_t1_pass and is_t2_pass
        outcome = "PASS" if lot_pass else "POSSIBLE_NON_COMPLIANCE"

        reasons: List[str] = []
        if not is_t2_pass:
            reasons.append(f"{t2_count} unit(s) exceeded twice the Maximum Permissible Error (below {t2_thresh} {mpe_data['base_unit']}). Fatal lot failure under Rule 19(2).")
        if not is_t1_pass:
            reasons.append(f"Number of deficient packages ({t1_count}) exceeded the statutory limit ({max_allowable_defective}) for sample size {sample_size}.")
        if not is_mean_pass:
            reasons.append(f"Corrected average net quantity ({corrected_mean} {mpe_data['base_unit']}) is less than declared net quantity ({qty_base} {mpe_data['base_unit']}).")

        if not reasons:
            reasons.append(f"Lot inspection compliant: Sample average {mean_weight:.2f} {mpe_data['base_unit']} satisfies legal tolerance. Deficient units within permissible limits.")

        return {
            "lot_size": lot_size,
            "sample_size": sample_size,
            "recommended_sample_size": recommended_sample,
            "declared_quantity": declared_quantity,
            "unit": unit,
            "mpe_data": mpe_data,
            "mean_weight": round(mean_weight, 2),
            "std_dev": round(std_dev, 2),
            "corrected_mean": corrected_mean,
            "t1_defectives_count": t1_count,
            "t2_defectives_count": t2_count,
            "max_allowable_t1": max_allowable_defective,
            "outcome": outcome,
            "is_mean_compliant": is_mean_pass,
            "is_t1_compliant": is_t1_pass,
            "is_t2_compliant": is_t2_pass,
            "reasons": reasons,
            "legal_reference": "Fifth & Sixth Schedule (Rules 19-22), Legal Metrology (Packaged Commodities) Rules, 2011"
        }

mpe_calculator = MPECalculator()
