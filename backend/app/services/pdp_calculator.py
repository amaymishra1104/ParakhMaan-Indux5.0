"""
Rule 7 Principal Display Panel (PDP) & Font-Size Area Band Calculator.
Conforms strictly to Legal Metrology (Packaged Commodities) Rules, 2011.
"""
from typing import Dict, Any

class PDPCalculator:
    """
    Computes minimum numeral and letter height based on PDP area under Rule 7, Table 1.
    """

    @staticmethod
    def calculate_pdp_area_and_font_standards(
        package_shape: str = "RECTANGULAR",
        height_cm: float = 15.0,
        width_cm: float = 10.0,
        depth_or_diameter_cm: float = 5.0
    ) -> Dict[str, Any]:
        """
        Determines PDP Area in cm^2 and corresponding statutory minimum numeral/letter height.
        Rule 7(1):
        - Rectangular: Height x Width of the front panel
        - Cylindrical: 40% of Height x Circumference (0.4 * H * pi * D)
        - Other: 40% of total surface area
        """
        shape_upper = package_shape.upper().strip()

        if shape_upper == "CYLINDRICAL":
            # PDP area = 40% of height * circumference
            circumference = 3.14159 * depth_or_diameter_cm
            pdp_area_cm2 = 0.40 * height_cm * circumference
        elif shape_upper in ["RECTANGULAR", "FLAT_POUCH", "BOX"]:
            # PDP area = height * width
            pdp_area_cm2 = height_cm * width_cm
        else:
            # General 3D package: 40% of total surface area
            surface_area = 2 * (height_cm * width_cm + height_cm * depth_or_diameter_cm + width_cm * depth_or_diameter_cm)
            pdp_area_cm2 = 0.40 * surface_area

        pdp_area_cm2 = round(pdp_area_cm2, 2)

        # Rule 7 Table: Area Band -> Min Numeral Height (Printed vs Molded/Blown)
        if pdp_area_cm2 <= 50.0:
            area_band = "Area <= 50 cm²"
            min_numeral_mm = 1.0
            min_blown_mm = 1.5
            min_other_char_mm = 1.0
        elif 50.0 < pdp_area_cm2 <= 100.0:
            area_band = "50 cm² < Area <= 100 cm²"
            min_numeral_mm = 1.5
            min_blown_mm = 2.0
            min_other_char_mm = 1.0
        elif 100.0 < pdp_area_cm2 <= 500.0:
            area_band = "100 cm² < Area <= 500 cm²"
            min_numeral_mm = 2.5
            min_blown_mm = 4.0
            min_other_char_mm = 1.5
        elif 500.0 < pdp_area_cm2 <= 2500.0:
            area_band = "500 cm² < Area <= 2500 cm²"
            min_numeral_mm = 4.0
            min_blown_mm = 6.0
            min_other_char_mm = 2.0
        else:
            area_band = "Area > 2500 cm²"
            min_numeral_mm = 6.0
            min_blown_mm = 6.0
            min_other_char_mm = 3.0

        return {
            "package_shape": shape_upper,
            "dimensions_cm": {
                "height": height_cm,
                "width": width_cm,
                "depth_or_diameter": depth_or_diameter_cm
            },
            "pdp_area_cm2": pdp_area_cm2,
            "area_band": area_band,
            "min_numeral_height_mm": min_numeral_mm,
            "min_blown_or_molded_height_mm": min_blown_mm,
            "min_other_declarations_height_mm": min_other_char_mm,
            "legal_reference": "Rule 7(1) & Table (Principal Display Panel), Legal Metrology (Packaged Commodities) Rules, 2011"
        }

pdp_calculator = PDPCalculator()
