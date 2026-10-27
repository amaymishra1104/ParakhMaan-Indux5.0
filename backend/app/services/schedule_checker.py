"""
Second Schedule Standard Pack Sizes & Statutory Schedules Checker.
Conforms strictly to Legal Metrology (Packaged Commodities) Rules, 2011 with Amendments.
"""
from typing import Dict, Any, List, Optional

class ScheduleChecker:
    """
    Validates commodities against Second Schedule permitted standard pack sizes (Rule 5).
    """

    # Second Schedule Permitted Pack Sizes: Commodity Name -> Permitted quantities (in standard grams or ml)
    SECOND_SCHEDULE_COMMODITIES: Dict[str, Dict[str, Any]] = {
        "BISCUITS": {
            "name": "Biscuits / Cookies",
            "permitted_mass_grams": [25, 50, 75, 100, 120, 150, 200, 250, 300, 400, 500, 1000],
            "units": ["g", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 1: Permitted standard sizes in grams."
        },
        "BREAD": {
            "name": "Bread including brown bread but excluding toasted bread",
            "permitted_mass_grams": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
            "units": ["g"],
            "legal_note": "Rule 5 & Second Schedule Item 2"
        },
        "TEA": {
            "name": "Tea",
            "permitted_mass_grams": [25, 50, 75, 100, 125, 150, 200, 250, 500, 1000, 2000, 5000],
            "units": ["g", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 3"
        },
        "COFFEE": {
            "name": "Coffee / Instant Coffee / Coffee-Chicory mixture",
            "permitted_mass_grams": [25, 50, 75, 100, 150, 200, 500, 1000],
            "units": ["g", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 4"
        },
        "EDIBLE_OIL": {
            "name": "Edible Oils, Vanaspati, Ghee, Mustard Oil",
            "permitted_mass_grams": [50, 100, 200, 500, 1000, 2000, 3000, 5000, 15000],
            "units": ["g", "kg", "ml", "L"],
            "legal_note": "Rule 5 & Second Schedule Item 6"
        },
        "MILK_POWDER": {
            "name": "Milk Powder / Baby Milk Food",
            "permitted_mass_grams": [50, 100, 200, 500, 1000],
            "units": ["g", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 7"
        },
        "BABY_FOOD": {
            "name": "Infant Milk / Weaning Food",
            "permitted_mass_grams": [200, 400, 500, 1000],
            "units": ["g", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 8"
        },
        "RICE_WHEAT_PULSES": {
            "name": "Rice, Wheat Flour (Atta), Maida, Suji, Pulses, Cereals",
            "permitted_mass_grams": [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 25000],
            "units": ["g", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 9"
        },
        "SUGAR": {
            "name": "Refined Sugar / Khandsari Sugar",
            "permitted_mass_grams": [100, 200, 500, 1000, 2000, 5000, 10000, 25000],
            "units": ["g", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 10"
        },
        "SALT": {
            "name": "Common Salt / Iodized Salt",
            "permitted_mass_grams": [200, 500, 1000, 2000, 5000],
            "units": ["g", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 11"
        },
        "DETERGENT": {
            "name": "Detergent Powders & Washing Cakes",
            "permitted_mass_grams": [50, 100, 125, 150, 200, 250, 500, 700, 1000, 1500, 2000, 3000, 4000, 5000],
            "units": ["g", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 13"
        },
        "TOILET_SOAP": {
            "name": "Toilet Soap / Bathing Soap Cakes",
            "permitted_mass_grams": [25, 50, 75, 100, 125, 150],
            "units": ["g"],
            "legal_note": "Rule 5 & Second Schedule Item 14"
        },
        "CEMENT": {
            "name": "Portland Cement in Bags",
            "permitted_mass_grams": [1000, 5000, 25000, 50000],
            "units": ["kg"],
            "legal_note": "Rule 5 & Second Schedule Item 15 (Max 50 kg for retail)"
        },
        "PAINTS": {
            "name": "Paints, Enamels, Varnishes",
            "permitted_mass_grams": [50, 100, 200, 500, 1000, 2000, 4000, 10000, 20000],
            "units": ["ml", "L", "kg"],
            "legal_note": "Rule 5 & Second Schedule Item 16"
        }
    }

    # Third Schedule: Commodities where quantity is qualified by "When Packed" due to environmental loss
    THIRD_SCHEDULE_WHEN_PACKED = [
        "SOAP_CAKES", "CAMPHOR", "AGARBATTIS", "TOBACCO", "MUSHROOMS", "FRESH_FRUITS_VEGETABLES"
    ]

    def find_matching_commodity(self, text_or_category: str) -> Optional[str]:
        t = text_or_category.upper()
        for key in self.SECOND_SCHEDULE_COMMODITIES:
            if key in t:
                return key
        # Specific keyword search
        if any(k in t for k in ["BISCUIT", "COOKIE", "OREO", "PARLE", "BRITANNIA"]):
            return "BISCUITS"
        if any(k in t for k in ["TEA", "CHAI", "TAJ MAHAL", "TATA TEA"]):
            return "TEA"
        if any(k in t for k in ["COFFEE", "NESCAFE", "BRU"]):
            return "COFFEE"
        if any(k in t for k in ["OIL", "GHEE", "VANASPATI", "FORTUNE", "SAFFOLA"]):
            return "EDIBLE_OIL"
        if any(k in t for k in ["RICE", "WHEAT", "ATTA", "AASHIRVAAD", "DAL", "PULSE"]):
            return "RICE_WHEAT_PULSES"
        if any(k in t for k in ["SUGAR", "CHINI"]):
            return "SUGAR"
        if any(k in t for k in ["SALT", "NAMAK", "TATA SALT"]):
            return "SALT"
        if any(k in t for k in ["DETERGENT", "SURF", "ARIEL", "TIDE", "RIN"]):
            return "DETERGENT"
        if any(k in t for k in ["SOAP", "DETTOL", "LUX", "DOVE", "LIFEBUOY"]):
            return "TOILET_SOAP"
        if any(k in t for k in ["CEMENT", "ULTRATECH", "AMBUJA"]):
            return "CEMENT"
        if any(k in t for k in ["PAINT", "ASIAN PAINTS", "BERGER"]):
            return "PAINTS"
        if any(k in t for k in ["BABY FOOD", "CERELAC", "NAN PRO"]):
            return "BABY_FOOD"
        return None

    def validate_pack_size(self, commodity_key: str, quantity: float, unit: str) -> Dict[str, Any]:
        """
        Validates if quantity is in the permitted Second Schedule standard pack list.
        """
        sched_entry = self.SECOND_SCHEDULE_COMMODITIES.get(commodity_key)
        if not sched_entry:
            return {
                "is_scheduled": False,
                "is_compliant": True,
                "message": "Commodity is not listed under Second Schedule standard packaging constraints."
            }

        unit_lower = unit.lower().strip()
        if unit_lower in ["kg", "l", "litre", "kilogram"]:
            qty_g = quantity * 1000.0
        else:
            qty_g = quantity

        permitted = sched_entry["permitted_mass_grams"]
        is_standard = any(abs(qty_g - p) < 0.01 for p in permitted)

        return {
            "is_scheduled": True,
            "commodity_key": commodity_key,
            "commodity_name": sched_entry["name"],
            "declared_quantity": quantity,
            "declared_unit": unit,
            "is_compliant": is_standard,
            "permitted_sizes": permitted,
            "legal_note": sched_entry["legal_note"],
            "message": f"Declared pack size ({quantity} {unit}) is a legally permitted standard size." if is_standard else f"Non-standard pack size ({quantity} {unit}). Second Schedule prescribes standard sizes: {', '.join(str(p)+'g' for p in permitted[:6])}..."
        }

schedule_checker = ScheduleChecker()
