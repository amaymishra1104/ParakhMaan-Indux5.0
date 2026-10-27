from typing import List, Dict, Any

class ProductClassifier:
    """
    Product and Category Classification Service.
    Determines statutory category for rule applicability.
    """

    FOOD_KEYWORDS = ["food", "snack", "chips", "biscuit", "oil", "flour", "atta", "sugar", "tea", "coffee", "juice", "milk", "spice", "masala", "grain", "rice", "wheat", "pulse", "chocolate", "wafer", "noodle"]
    COSMETICS_KEYWORDS = ["soap", "shampoo", "cream", "lotion", "perfume", "deodorant", "lipstick", "skin", "hair", "cosmetic", "face wash", "oil"]
    MEDICAL_KEYWORDS = ["bandage", "syringe", "gauge", "diagnostic", "medical", "sterile", "tablet", "capsule", "pharma"]
    ELECTRONICS_KEYWORDS = ["cable", "charger", "adapter", "battery", "usb", "light", "bulb", "led", "electronic", "device"]

    def classify(self, text_corpus: str, user_selected_category: str = "PACKAGED_COMMODITY") -> Dict[str, Any]:
        text_lower = text_corpus.lower()
        
        # Check explicit selection first
        if user_selected_category and user_selected_category not in ["PACKAGED_COMMODITY", "OTHER"]:
            return {
                "category": user_selected_category,
                "confidence": 0.95,
                "classification_method": "USER_SPECIFIED"
            }

        food_score = sum(1 for kw in self.FOOD_KEYWORDS if kw in text_lower)
        cosmetic_score = sum(1 for kw in self.COSMETICS_KEYWORDS if kw in text_lower)
        medical_score = sum(1 for kw in self.MEDICAL_KEYWORDS if kw in text_lower)
        electronic_score = sum(1 for kw in self.ELECTRONICS_KEYWORDS if kw in text_lower)

        scores = [
            ("PACKAGED_FOOD", food_score),
            ("COSMETICS", cosmetic_score),
            ("MEDICAL_DEVICE", medical_score),
            ("ELECTRONICS", electronic_score),
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        top_cat, top_score = scores[0]

        if top_score >= 1:
            confidence = min(0.95, 0.70 + (top_score * 0.08))
            return {
                "category": top_cat,
                "confidence": round(confidence, 2),
                "classification_method": "KEYWORD_HEURISTIC"
            }

        return {
            "category": "PACKAGED_COMMODITY",
            "confidence": 0.60,
            "classification_method": "DEFAULT_FALLBACK"
        }

product_classifier = ProductClassifier()
