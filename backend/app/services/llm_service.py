import os
import json
import base64
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings

class LLMService:
    """
    Ollama Local LLM and Vision-Language Model (VLM) Service.
    Integrates directly with local Ollama instance (e.g. Qwen2.5, Llama3.2, Gemma2, Mistral).

    ARCHITECTURAL MANDATE:
    AI/LLM outputs are strictly used for text parsing, semantic normalization,
    and explanations. The deterministic Rule Engine remains the sole compliance authority.
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = 3.0

    async def check_ollama_status(self) -> Dict[str, Any]:
        """
        Queries the local Ollama daemon to check connectivity and installed models.
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    return {
                        "connected": True,
                        "endpoint": self.base_url,
                        "active_model": self.model,
                        "installed_models": models,
                        "status": "ONLINE"
                    }
        except Exception as e:
            pass

        return {
            "connected": False,
            "endpoint": self.base_url,
            "active_model": self.model,
            "installed_models": [],
            "status": "OFFLINE_FALLBACK_ACTIVE"
        }

    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Sends a prompt to the local Ollama LLM.
        """
        try:
            payload: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            if system_prompt:
                payload["system"] = system_prompt

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
        except Exception:
            pass
        return None

    async def extract_declarations_from_image_or_text(
        self,
        ocr_text: str,
        image_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Uses local Ollama LLM / VLM with structured JSON output
        to extract statutory declarations from raw text.
        """
        prompt = (
            "You are a Legal Metrology Compliance Parser. Extract the following fields from the package text as JSON:\n"
            "- mrp (string with currency and tax note)\n"
            "- net_quantity (string with metric unit)\n"
            "- unit_sale_price (string)\n"
            "- manufacturing_date (MM/YYYY or string)\n"
            "- expiry_date (string or null)\n"
            "- manufacturer (name and address)\n"
            "- consumer_care (contacts)\n"
            "- country_of_origin (country)\n"
            "- generic_name (commodity name)\n\n"
            f"Package Text Content:\n{ocr_text}\n\n"
            "Return ONLY valid JSON matching this schema."
        )

        try:
            payload: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            if image_base64:
                payload["images"] = [image_base64]

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("response", "{}")
                    parsed = json.loads(response_text)
                    return parsed
        except Exception:
            pass

        return {}

    def set_model_config(self, base_url: Optional[str] = None, model: Optional[str] = None):
        if base_url:
            self.base_url = base_url.rstrip("/")
        if model:
            self.model = model

    async def analyze_full_inspection(
        self,
        inspection_number: str,
        category: str,
        declarations: List[Dict[str, Any]],
        compliance_results: List[Dict[str, Any]],
        images_meta: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive, end-to-end statutory Legal Metrology inspection report.
        Synthesizes findings from Rule Engine, OCR, and packaging declarations.
        """
        passes = [r for r in compliance_results if r.get("outcome") == "PASS"]
        reviews = [r for r in compliance_results if r.get("outcome") == "REVIEW"]
        fails = [r for r in compliance_results if r.get("outcome") in ["FAIL", "POSSIBLE_NON_COMPLIANCE"]]

        prompt = (
            f"You are a Senior Legal Metrology Compliance Expert for the Government of India.\n"
            f"Analyze inspection dossier '{inspection_number}' for commodity category '{category}'.\n\n"
            f"Declarations Extracted:\n"
            + "\n".join([f"- {d.get('field_name')}: {d.get('normalized_value')} (Confidence: {int(float(d.get('confidence', 0.9))*100)}%)" for d in declarations])
            + f"\n\nCompliance Matrix Summary:\n"
            + f"- Compliant Fields ({len(passes)}): {', '.join([p.get('field', '') for p in passes]) or 'None'}\n"
            + f"- Needs Review ({len(reviews)}): {', '.join([r.get('field', '') for r in reviews]) or 'None'}\n"
            + f"- Non-Compliant ({len(fails)}): {', '.join([f.get('field', '') for f in fails]) or 'None'}\n\n"
            f"Provide a structured JSON response with:\n"
            f"1. 'executive_summary': A clear 2-3 sentence overview.\n"
            f"2. 'statutory_breakdown': A dictionary mapping fields to observations.\n"
            f"3. 'risk_level': 'LOW', 'MEDIUM', or 'HIGH'.\n"
            f"4. 'legal_sections': List of applicable Legal Metrology Act 2009 / PCR 2011 sections.\n"
            f"5. 'recommendations': 2-3 actionable next steps for the enforcement officer."
        )

        system = "You are an official Legal Metrology Assistant. Return strictly valid JSON."

        try:
            payload: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "format": "json"
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    parsed = json.loads(data.get("response", "{}"))
                    parsed["model_used"] = f"Ollama ({self.model})"
                    parsed["generated_at"] = "LIVE_LLM"
                    return parsed
        except Exception:
            pass

        # Deterministic Expert Fallback Synthesis
        risk_level = "HIGH" if len(fails) > 0 else ("MEDIUM" if len(reviews) > 2 else "LOW")
        
        summary_text = (
            f"Inspection {inspection_number} for {category.replace('_', ' ').title()} commodity evaluated "
            f"with {len(passes)} compliant declarations, {len(reviews)} items requiring manual review, and "
            f"{len(fails)} statutory omissions. "
        )
        if len(fails) == 0 and len(reviews) <= 1:
            summary_text += "Package demonstrates high statutory alignment with Legal Metrology (Packaged Commodities) Rules, 2011."
        elif len(fails) > 0:
            summary_text += "Critical statutory declarations are missing or non-compliant, invoking Section 36 penalty provisions."
        else:
            summary_text += "Officer verification is advised to confirm low-contrast declarations and cross-surface consistency."

        recommendations = []
        if len(fails) > 0:
            recommendations.append(f"Issue statutory show-cause notice under Section 36(1) for omitted fields: {', '.join([f.get('field', '') for f in fails])}.")
        if len(reviews) > 0:
            recommendations.append(f"Perform manual visual verification on package surfaces for: {', '.join([r.get('field', '') for r in reviews])}.")
        if not recommendations:
            recommendations.append("Approve package compliance and archive statutory certificate.")

        return {
            "executive_summary": summary_text,
            "statutory_breakdown": {
                r.get("field", "general"): f"{r.get('outcome')}: {r.get('detected_value') or 'Omitted'} ({r.get('legal_reference') or 'PCR 2011'})"
                for r in compliance_results
            },
            "risk_level": risk_level,
            "legal_sections": [
                "Rule 6(1) of Legal Metrology (Packaged Commodities) Rules, 2011",
                "Section 18 of Legal Metrology Act, 2009",
                "Section 36 of Legal Metrology Act, 2009 (Penalties)"
            ],
            "recommendations": recommendations,
            "model_used": "Deterministic Statutory Synthesis (Rule Engine + RAG)",
            "generated_at": "DETERMINISTIC_SYNTHESIS"
        }

    async def explain_rule_finding(
        self,
        rule_id: str,
        field: str,
        detected_val: Optional[str],
        outcome: str,
        legal_reference: Optional[str] = None
    ) -> str:
        """
        Generates an easy-to-understand, neutral statutory explanation for an inspector via Ollama.
        """
        system = "You are a Legal Metrology Inspector Assistant in India. Provide brief, neutral, statutory explanations."
        prompt = (
            f"Explain in 1-2 neutral, objective sentences why the field '{field}' with detected value '{detected_val}' "
            f"yielded outcome '{outcome}' under rule '{rule_id}' ({legal_reference or 'PCR 2011'}). "
            f"Do not make criminal accusations; state statutory alignment clearly."
        )

        ollama_response = await self.generate_response(prompt, system_prompt=system)
        if ollama_response:
            return ollama_response

        # Robust deterministic fallback explanations
        if outcome == "PASS":
            return f"Declaration for '{field}' complies with standard {rule_id} requirements under {legal_reference or 'Legal Metrology Rules, 2011'}."
        elif outcome == "REVIEW":
            return f"Declaration '{field}' requires human verification due to low confidence OCR reading or layout ambiguity."
        else:
            return f"Mandatory declaration for '{field}' appears missing or does not conform to the prescribed statutory format under {legal_reference or 'Rule 6, PCR 2011'}."

llm_service = LLMService()
