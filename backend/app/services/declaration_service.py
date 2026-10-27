import re
from typing import List, Dict, Any, Optional

class DeclarationExtractor:
    """
    Expert Legal Metrology Statutory Declaration Extraction Engine.
    Converts raw OCR text blocks into structured statutory declarations with confidence,
    bounding box linkages, and normalized metric/currency values.
    Features:
    - Adaptive noise & ligature cleaning for dot-matrix packaging prints.
    - Standalone and multi-line MRP detection (Rs 20, ₹20, 20/-, Rs. 20.00).
    - Month/Year manufacturing date extraction from standard and inkjet markings.
    - Strict barrier protections ensuring high precision.
    """

    EXPLICIT_MRP_PATTERN = re.compile(
        r"(?:m\.?r\.?p\.?|max(?:imum)?\s+retail\s+price|rsp)\s*[:.-]?\s*(?:rs\.?|inr|₹)?\s*([0-9]+(?:\.[0-9]{1,2})?)",
        re.IGNORECASE
    )
    CURRENCY_MRP_PATTERNS = [
        re.compile(r"(?:rs|inr|₹)[\.\:\s\-\_]*([0-9]+(?:\.[0-9]{1,2})?)", re.IGNORECASE),
        re.compile(r"([0-9]+(?:\.[0-9]{1,2})?)\s*(?:rs\.?|inr|₹)", re.IGNORECASE),
        re.compile(r"(?:^|\s)([0-9]+(?:\.[0-9]{1,2})?)\s*/-(?:\s|$)", re.IGNORECASE),
    ]
    TAXES_INCL_PATTERN = re.compile(r"incl(?:usive)?\.?\s*(?:of)?\s*(?:all)?\s*(?:taxes)?", re.IGNORECASE)

    UNIT_SALE_PRICE_PATTERN = re.compile(
        r"(?:unit\s*sale\s*price|u\.?s\.?p\.?)\s*[:.-]?\s*(?:rs\.?|inr|₹)?\s*([0-9]+(?:\.[0-9]{1,4})?)\s*(?:per|/)\s*([a-zA-Z]+|kg|g|gm|l|ml|litre|piece|item|unit|u|n)",
        re.IGNORECASE
    )

    NET_QTY_PATTERNS = [
        re.compile(r"(?:net\s*(?:quantity|qty|weight|wt|we|vol(?:ume)?|contents?)|amox|approx)\s*[:.-]?\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+|kg|g|gm|gms|ml|l|litre|litres|mtr|m|cm|mm|n|units?|pieces?|pcs?|nos?|gg)", re.IGNORECASE),
        re.compile(r"=\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+|kg|g|gm|gms|ml|l|litre|litres|mtr|m|cm|mm|units?|pieces?|pcs?|nos?|gg)\b", re.IGNORECASE),
        re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(kg|g|gm|gms|ml|l|litre|litres|mtr|m|cm|mm|units?|pieces?|pcs?|nos?|gg)\b", re.IGNORECASE),
    ]

    MONTH_REGEX = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"

    DATE_LABELLED_PATTERNS = [
        re.compile(rf"(?:mfd|mfg|manufactur(?:ed|ing)|pkd|packed|pkg|imported|date\s*of\s*mfg|mfg\s*date)\s*[:.-]?\s*([0-9]{{1,2}}[./-][0-9]{{1,2}}[./-][0-9]{{2,4}}|[0-9]{{1,2}}[./-][0-9]{{2,4}}|{MONTH_REGEX}\s*[0-9]{{2,4}}|[0-9]{{1,2}}\s+{MONTH_REGEX}\s+[0-9]{{2,4}})", re.IGNORECASE),
        re.compile(rf"(?:best\s*before|use\s*by|exp(?:iry)?\.?\s*date|expires?)\s*[:.-]?\s*([0-9]{{1,2}}[./-][0-9]{{1,2}}[./-][0-9]{{2,4}}|[0-9]{{1,2}}[./-][0-9]{{2,4}}|[0-9]{{1,2}}\s*(?:months?|days?|years?)\s*(?:from\s*(?:mfg|pkd|packaging|date))?|{MONTH_REGEX}\s*[0-9]{{2,4}})", re.IGNORECASE),
    ]

    STANDALONE_DATE_PATTERNS = [
        re.compile(r"\b([0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})\b"),                  # 24/05/2026, 24-05-26, 01.08.2025
        re.compile(r"\b([0-9]{4}[./-][0-9]{1,2}[./-][0-9]{1,2})\b"),                  # 2026-05-24, 2026/05/24
        re.compile(rf"\b([0-9]{{1,2}}\s+{MONTH_REGEX}\s+[0-9]{{2,4}})\b", re.IGNORECASE), # 24 May 2026
        re.compile(rf"\b({MONTH_REGEX}[\s\.\,\'\-]*[0-9]{{2,4}})\b", re.IGNORECASE),    # JAN 2026, AUG'26, May 2025
        re.compile(r"\b([0-9]{1,2}[./-][0-9]{4})\b"),                                   # 08/2026, 08-2026, 08.2026
        re.compile(r"\b([0-9]{4}[./-][0-9]{1,2})\b"),                                   # 2026/08, 2026-08
        re.compile(r"([0-9]{1,2}[./-](?:2[0-9]|19|20[2-3][0-9]))"),                    # 06/24, 6/24, 08/26, 05/25
    ]

    MFG_PATTERNS = [
        re.compile(r"(?:manufactured|mfd|packed|pkd|marketed|imported|bumjfactured|brand\s*owned)\s*(?:&|and|a)?\s*(?:packed|marketed|brand\s*owned)?\s*(?:by)?\s*[:.-]?\s*([^\n\r]+)", re.IGNORECASE),
        re.compile(r"(?:mfg\s*by|marketed\s*by|packed\s*by)\s*[:.-]?\s*([^\n\r]+)", re.IGNORECASE),
    ]

    COUNTRY_PATTERNS = [
        re.compile(r"(?:country\s*of\s*origin|made\s*in|origin)\s*[:.-]?\s*([a-zA-Z\s]+)", re.IGNORECASE),
    ]

    CONSUMER_CARE_PATTERNS = [
        re.compile(r"(?:consumer\s*care|customer\s*care|care\s*cell|feedback|queries|complaints?)\s*[:.-]?\s*([^\n\r]+)", re.IGNORECASE),
        re.compile(r"(?:toll[\s-]*free|helpline|phone|tel|call)\s*[:.-]?\s*([0-9\s-]{8,15})", re.IGNORECASE),
        re.compile(r"(?:email|e-mail)\s*[:.-]?\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", re.IGNORECASE),
    ]

    GENERIC_NAME_PATTERNS = [
        re.compile(r"(?:generic\s*name|common\s*name|product\s*name|commodity|ingredients?)\s*[:.-]?\s*([^\n\r]+)", re.IGNORECASE),
    ]

    HEADER_BARRIERS = [
        "batch", "b.no", "b. no", "lot", "mfd", "mfg", "pkd", "packed", "net", 
        "content", "quantity", "weight", "manufactured", "marketed", "consumer", 
        "care", "email", "website", "pwd", "pwm", "use by", "best before", "exp"
    ]

    def _clean_inkjet_text(self, text: str) -> str:
        """
        Cleans common OCR dot-matrix artifacts and ligatures.
        """
        t = text.replace('fi', '/').replace('fl', '/').replace('ß', 'B').replace('`', '')
        t = re.sub(r'([0-9])S(\.|$)', r'\g<1>5\2', t)
        return t

    def extract_from_spans(self, ocr_spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes OCR spans and extracts typed Legal Metrology declarations.
        """
        extracted_declarations: List[Dict[str, Any]] = []
        found_fields: Dict[str, float] = {}
        has_explicit_mrp = False

        # Pre-scan: Check if any span in the entire document explicitly mentions taxes inclusive
        doc_has_taxes_inclusive = any(bool(self.TAXES_INCL_PATTERN.search(s.get("text", ""))) for s in ocr_spans)

        # Track indices where MRP or Rupee/Batch markers were detected
        mrp_span_indices: List[int] = []
        batch_span_indices: List[int] = []

        for idx, span in enumerate(ocr_spans):
            raw_text = span.get("text", "").strip()
            bbox = span.get("bbox", [])
            confidence = float(span.get("confidence", 0.9))
            image_id = span.get("image_id")

            if not raw_text:
                continue

            text = self._clean_inkjet_text(raw_text)

            # Check if this span is a Unit Sale Price (USP) line (e.g. Unit Sale Price: Rs. 0.15 / g)
            is_usp_line = bool(
                self.UNIT_SALE_PRICE_PATTERN.search(text) or 
                re.search(r"(?:unit\s*sale\s*price|u\.?s\.?p\.?|/\s*(?:g|gm|kg|ml|l|litre|piece|item|unit|u|n))\b", text, re.IGNORECASE)
            )

            # Check if this span is a pure batch/lot line or pure quantity line
            is_pure_batch_or_qty = bool(
                any(text.lower().startswith(b) for b in ["batch no", "b.no", "b. no", "lot no", "pwm reg"]) or
                re.search(r"^([0-9]+(?:\.[0-9]+)?\s*(?:g|gm|kg|ml|l|litre|cm|mm|n|units?|pcs?)|3nx[0-9]+g=)$", text.replace(" ", ""), re.IGNORECASE)
            )

            # -----------------------------------------------------------------
            # 1. Check Unit Sale Price (USP) first to prevent USP numbers from being confused with MRP
            # -----------------------------------------------------------------
            if is_usp_line and "unit_sale_price" not in found_fields:
                usp_match = self.UNIT_SALE_PRICE_PATTERN.search(text)
                if usp_match:
                    price = usp_match.group(1)
                    unit = usp_match.group(2).lower()
                    extracted_declarations.append({
                        "field_name": "unit_sale_price",
                        "detected_value": raw_text,
                        "normalized_value": f"₹ {price} / {unit}",
                        "confidence": confidence,
                        "bbox": bbox,
                        "image_id": image_id,
                        "extraction_method": "REGEX",
                        "price": float(price),
                        "unit": unit
                    })
                    found_fields["unit_sale_price"] = confidence

            # -----------------------------------------------------------------
            # 2. Check MRP (Explicit pattern, Standalone Rs/₹/20/-, Multi-line lookahead)
            # -----------------------------------------------------------------
            if not is_usp_line and not is_pure_batch_or_qty:
                # 2a. Explicit MRP keyword match (e.g. MRP Rs. 149.00 or MRP ₹ 20)
                explicit_match = self.EXPLICIT_MRP_PATTERN.search(text)
                if explicit_match:
                    raw_amount = explicit_match.group(1)
                    has_taxes = bool(self.TAXES_INCL_PATTERN.search(text)) or doc_has_taxes_inclusive
                    normalized = f"₹ {float(raw_amount):.2f}" + (" (Incl. of all taxes)" if has_taxes else " (Taxes note missing)")
                    
                    if "mrp" in found_fields and not has_explicit_mrp:
                        extracted_declarations = [d for d in extracted_declarations if d["field_name"] != "mrp"]
                    
                    if "mrp" not in found_fields or not has_explicit_mrp:
                        extracted_declarations.append({
                            "field_name": "mrp",
                            "detected_value": raw_text,
                            "normalized_value": normalized,
                            "confidence": confidence,
                            "bbox": bbox,
                            "image_id": image_id,
                            "extraction_method": "REGEX",
                            "has_tax_inclusive": has_taxes,
                            "numeric_value": float(raw_amount)
                        })
                        found_fields["mrp"] = confidence
                        has_explicit_mrp = True
                        mrp_span_indices.append(idx)

                # 2b. Standalone Currency/Rupee match (e.g. Rs 20, ₹20, 20/-, Rs.. 175.00)
                elif "mrp" not in found_fields:
                    for pat in self.CURRENCY_MRP_PATTERNS:
                        curr_match = pat.search(text)
                        if curr_match:
                            raw_amount = curr_match.group(1)
                            # Guard: if amount is 0, skip
                            if float(raw_amount) > 0:
                                has_taxes = bool(self.TAXES_INCL_PATTERN.search(text)) or doc_has_taxes_inclusive
                                normalized = f"₹ {float(raw_amount):.2f}" + (" (Incl. of all taxes)" if has_taxes else " (Taxes note missing)")
                                extracted_declarations.append({
                                    "field_name": "mrp",
                                    "detected_value": raw_text,
                                    "normalized_value": normalized,
                                    "confidence": confidence,
                                    "bbox": bbox,
                                    "image_id": image_id,
                                    "extraction_method": "REGEX_CURRENCY",
                                    "has_tax_inclusive": has_taxes,
                                    "numeric_value": float(raw_amount)
                                })
                                found_fields["mrp"] = confidence
                                mrp_span_indices.append(idx)
                                break

                # 2c. Guarded Multi-line MRP lookahead: Line has MRP/Rs header without number
                if "mrp" not in found_fields:
                    if any(k in text.lower() for k in ["mrp", "m.r.p", "retail price", "rsp"]):
                        mrp_span_indices.append(idx)
                        if idx + 1 < len(ocr_spans):
                            next_span = ocr_spans[idx + 1]
                            next_t = self._clean_inkjet_text(next_span.get("text", "").strip())
                            is_barrier = any(next_t.lower().startswith(b) for b in self.HEADER_BARRIERS)
                            if not is_barrier:
                                num_match = re.search(r"^(?:rs\.?|inr|₹)?\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:/-)?$", next_t, re.IGNORECASE)
                                if num_match and num_match.group(1):
                                    raw_amount = num_match.group(1)
                                    combined_text = f"{raw_text} {next_span.get('text', '')}".strip()
                                    has_taxes = bool(self.TAXES_INCL_PATTERN.search(combined_text)) or doc_has_taxes_inclusive
                                    normalized = f"₹ {float(raw_amount):.2f}" + (" (Incl. of all taxes)" if has_taxes else " (Taxes note missing)")
                                    extracted_declarations.append({
                                        "field_name": "mrp",
                                        "detected_value": combined_text,
                                        "normalized_value": normalized,
                                        "confidence": confidence,
                                        "bbox": bbox or next_span.get("bbox", []),
                                        "image_id": image_id,
                                        "extraction_method": "REGEX_LOOKAHEAD",
                                        "has_tax_inclusive": has_taxes,
                                        "numeric_value": float(raw_amount)
                                    })
                                    found_fields["mrp"] = confidence
                                    has_explicit_mrp = True

            # -----------------------------------------------------------------
            # 3. Check Net Quantity (with multi-line aggregation)
            # -----------------------------------------------------------------
            if "net_quantity" not in found_fields or found_fields.get("net_quantity", 0.0) < confidence:
                combined_q_text = text
                if any(text.lower().startswith(p) for p in ["net", "amox", "approx", "content", "quantity", "weight", "qty"]) and idx + 1 < len(ocr_spans):
                    for ahead_idx in range(idx + 1, min(idx + 4, len(ocr_spans))):
                        ahead_t = ocr_spans[ahead_idx].get("text", "").strip()
                        combined_q_text += f" {ahead_t}"

                for pat in self.NET_QTY_PATTERNS:
                    match = pat.search(combined_q_text)
                    if match:
                        qty_num = match.group(1)
                        unit_str = match.group(2).lower()
                        norm_unit = self._normalize_unit(unit_str)
                        normalized = f"{qty_num} {norm_unit}"
                        extracted_declarations.append({
                            "field_name": "net_quantity",
                            "detected_value": combined_q_text.strip(),
                            "normalized_value": normalized,
                            "confidence": confidence,
                            "bbox": bbox,
                            "image_id": image_id,
                            "extraction_method": "REGEX",
                            "quantity": float(qty_num),
                            "unit": norm_unit
                        })
                        found_fields["net_quantity"] = confidence
                        break

            # -----------------------------------------------------------------
            # 4. Check Dates (Mfg / Expiry with label on current span)
            # -----------------------------------------------------------------
            for pat in self.DATE_LABELLED_PATTERNS:
                match = pat.search(text)
                if match:
                    date_val = match.group(1)
                    is_expiry = any(k in text.lower() for k in ["best before", "use by", "exp"])
                    field_name = "expiry_date" if is_expiry else "manufacturing_date"
                    if field_name not in found_fields:
                        extracted_declarations.append({
                            "field_name": field_name,
                            "detected_value": raw_text,
                            "normalized_value": date_val.strip(),
                            "confidence": confidence,
                            "bbox": bbox,
                            "image_id": image_id,
                            "extraction_method": "REGEX"
                        })
                        found_fields[field_name] = confidence

            # Track Batch / Mfd markers for multi-line lookahead
            if any(k in text.lower() for k in ["batch", "mfd", "mfg", "use by", "pkd", "b.no", "b. no"]):
                batch_span_indices.append(idx)

            # -----------------------------------------------------------------
            # 5. Check Manufacturer / Packer (with multiline aggregation)
            # -----------------------------------------------------------------
            if "manufacturer" not in found_fields:
                for pat in self.MFG_PATTERNS:
                    match = pat.search(text)
                    if match:
                        mfg_val = re.sub(r"^[,:\s\-\&]+", "", match.group(1)).strip()
                        combined_mfg = [mfg_val] if mfg_val else [raw_text.strip()]
                        for next_idx in range(idx + 1, min(idx + 4, len(ocr_spans))):
                            next_t = ocr_spans[next_idx].get("text", "").strip()
                            if any(k in next_t.lower() for k in ["ltd", "pvt", "road", "industrial", "kota", "nagar", "delhi", "mumbai", "india", "pvt.", "floor", "highway", "hw"]):
                                combined_mfg.append(next_t)
                            elif next_idx == idx + 1 and len(next_t) > 3 and not any(k in next_t.lower() for k in ["net", "mrp", "ingredients"]):
                                combined_mfg.append(next_t)

                        final_mfg = ", ".join(combined_mfg).strip(", ")
                        extracted_declarations.append({
                            "field_name": "manufacturer",
                            "detected_value": final_mfg,
                            "normalized_value": final_mfg,
                            "confidence": confidence,
                            "bbox": bbox,
                            "image_id": image_id,
                            "extraction_method": "REGEX"
                        })
                        found_fields["manufacturer"] = confidence
                        break

            # -----------------------------------------------------------------
            # 6. Check Country of Origin
            # -----------------------------------------------------------------
            if "country_of_origin" not in found_fields:
                match = self.COUNTRY_PATTERNS[0].search(text)
                if match:
                    coo = match.group(1).strip()
                    extracted_declarations.append({
                        "field_name": "country_of_origin",
                        "detected_value": raw_text,
                        "normalized_value": coo,
                        "confidence": confidence,
                        "bbox": bbox,
                        "image_id": image_id,
                        "extraction_method": "REGEX"
                    })
                    found_fields["country_of_origin"] = confidence

            # -----------------------------------------------------------------
            # 7. Check Consumer Care
            # -----------------------------------------------------------------
            if "consumer_care" not in found_fields:
                for pat in self.CONSUMER_CARE_PATTERNS:
                    match = pat.search(text)
                    if match:
                        care_info = raw_text
                        extracted_declarations.append({
                            "field_name": "consumer_care",
                            "detected_value": raw_text,
                            "normalized_value": care_info.strip(),
                            "confidence": confidence,
                            "bbox": bbox,
                            "image_id": image_id,
                            "extraction_method": "REGEX"
                        })
                        found_fields["consumer_care"] = confidence
                        break

            # -----------------------------------------------------------------
            # 8. Check Generic Name / Ingredients (with lookahead)
            # -----------------------------------------------------------------
            if "generic_name" not in found_fields:
                match = self.GENERIC_NAME_PATTERNS[0].search(text)
                if match:
                    raw_gname = match.group(1).strip().lstrip(":").strip()
                    if not raw_gname and idx + 1 < len(ocr_spans):
                        raw_gname = ocr_spans[idx + 1].get("text", "").strip()

                    if raw_gname:
                        clean_name = re.split(r"[\(;,%]", raw_gname)[0].strip()
                        gname = clean_name if len(clean_name) > 2 else raw_gname
                        extracted_declarations.append({
                            "field_name": "generic_name",
                            "detected_value": raw_text if raw_text != "INGREDIENTS:" else f"INGREDIENTS: {gname}",
                            "normalized_value": gname,
                            "confidence": confidence,
                            "bbox": bbox,
                            "image_id": image_id,
                            "extraction_method": "REGEX"
                        })
                        found_fields["generic_name"] = confidence

        # ---------------------------------------------------------------------
        # Post-Pass 1: Date Search Across All Spans (with Ligature & Dot-Matrix Normalization)
        # ---------------------------------------------------------------------
        if "manufacturing_date" not in found_fields:
            for s in ocr_spans:
                raw_t = s.get("text", "").strip()
                t = self._clean_inkjet_text(raw_t)
                for d_pat in self.STANDALONE_DATE_PATTERNS:
                    d_match = d_pat.search(t)
                    if d_match:
                        date_val = d_match.group(1).strip()
                        extracted_declarations.append({
                            "field_name": "manufacturing_date",
                            "detected_value": raw_t,
                            "normalized_value": date_val,
                            "confidence": float(s.get("confidence", 0.90)),
                            "bbox": s.get("bbox", []),
                            "image_id": s.get("image_id"),
                            "extraction_method": "STANDALONE_DATE_HEURISTIC"
                        })
                        found_fields["manufacturing_date"] = 0.90
                        break
                if "manufacturing_date" in found_fields:
                    break

        # ---------------------------------------------------------------------
        # Post-Pass 2: Batch Header Lookahead & Fallback Inkjet Code Classification
        # ---------------------------------------------------------------------
        for b_idx in batch_span_indices:
            for next_idx in range(b_idx + 1, min(b_idx + 4, len(ocr_spans))):
                span = ocr_spans[next_idx]
                raw_t = span.get("text", "").strip()
                t = self._clean_inkjet_text(raw_t)
                if any(t.lower().startswith(p) for p in ["net", "mrp", "mfg", "manufactured", "marketed"]):
                    continue
                
                # Check for date in lookahead
                if "manufacturing_date" not in found_fields:
                    for d_pat in self.STANDALONE_DATE_PATTERNS:
                        d_match = d_pat.search(t)
                        if d_match:
                            date_val = d_match.group(1).strip()
                            extracted_declarations.append({
                                "field_name": "manufacturing_date",
                                "detected_value": f"{ocr_spans[b_idx].get('text', '')} -> {raw_t}".strip(),
                                "normalized_value": date_val,
                                "confidence": float(span.get("confidence", 0.9)),
                                "bbox": span.get("bbox", []),
                                "image_id": span.get("image_id"),
                                "extraction_method": "BATCH_HEADER_LOOKAHEAD"
                            })
                            found_fields["manufacturing_date"] = 0.9
                            break
                
                # Check for batch_number in lookahead
                if "batch_number" not in found_fields and len(raw_t) >= 2:
                    extracted_declarations.append({
                        "field_name": "batch_number",
                        "detected_value": f"{ocr_spans[b_idx].get('text', '')} -> {raw_t}".strip(),
                        "normalized_value": raw_t,
                        "confidence": float(span.get("confidence", 0.92)),
                        "bbox": span.get("bbox", []),
                        "image_id": span.get("image_id"),
                        "extraction_method": "BATCH_INKJET_CODE"
                    })
                    found_fields["batch_number"] = 0.92
                    break

        return extracted_declarations

    def _normalize_unit(self, unit_raw: str) -> str:
        u = unit_raw.lower().strip()
        if u in ["g", "gm", "gms", "gram", "grams", "gg"]:
            return "g"
        if u in ["kg", "kgs", "kilogram", "kilograms"]:
            return "kg"
        if u in ["ml", "millilitre", "millilitres"]:
            return "ml"
        if u in ["l", "lt", "ltr", "litre", "litres"]:
            return "L"
        if u in ["m", "meter", "metre", "mtr"]:
            return "m"
        if u in ["cm", "centimetre", "centimeter"]:
            return "cm"
        if u in ["mm", "millimetre", "millimeter"]:
            return "mm"
        if u in ["n", "u", "unit", "units", "pc", "pcs", "piece", "pieces", "nos", "no"]:
            return "N"
        return u

declaration_extractor = DeclarationExtractor()
