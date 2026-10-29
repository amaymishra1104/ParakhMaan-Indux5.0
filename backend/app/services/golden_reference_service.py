import base64
import os
import time
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np


class GoldenReferenceService:
    """
    Industrial Golden-Reference Comparison Engine.
    Handles reference profile registration, versioning, feature-based image alignment
    (homography warping), illumination-invariant structural difference analysis,
    thermal deviation heatmap generation, and tolerance evaluations.
    """

    def __init__(self):
        # Product inspection profiles with strict, configurable manufacturing tolerances
        self.profiles: Dict[str, Dict[str, Any]] = {
            "METAL_SHEET": {
                "category": "METAL_SHEET",
                "reference_version": "v2.1-master",
                "description": "Cold-rolled & brushed steel sheet specification",
                "max_dimensional_tolerance_pct": 2.5,
                "max_color_delta_e": 14.0,
                "anomaly_area_max_pct": 0.015,
                "intensity_deviation_threshold": 32,
            },
            "DIE_CASTING": {
                "category": "DIE_CASTING",
                "reference_version": "v1.4-master",
                "description": "Aluminum / Zinc die-cast automotive housing",
                "max_dimensional_tolerance_pct": 3.0,
                "max_color_delta_e": 18.0,
                "anomaly_area_max_pct": 0.025,
                "intensity_deviation_threshold": 38,
            },
            "MACHINED_PART": {
                "category": "MACHINED_PART",
                "reference_version": "v3.0-precision",
                "description": "CNC precision milled component",
                "max_dimensional_tolerance_pct": 1.2,
                "max_color_delta_e": 12.0,
                "anomaly_area_max_pct": 0.01,
                "intensity_deviation_threshold": 26,
            },
            "GENERAL_MANUFACTURED": {
                "category": "GENERAL_MANUFACTURED",
                "reference_version": "v1.0-standard",
                "description": "Standard manufactured consumer / industrial good",
                "max_dimensional_tolerance_pct": 4.0,
                "max_color_delta_e": 20.0,
                "anomaly_area_max_pct": 0.035,
                "intensity_deviation_threshold": 40,
            },
        }

    def get_profile(self, category: Optional[str]) -> Dict[str, Any]:
        cat = (category or "GENERAL_MANUFACTURED").upper()
        return self.profiles.get(cat, self.profiles["GENERAL_MANUFACTURED"])

    def align_images(
        self, inspected_img: np.ndarray, reference_img: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Aligns inspected_img to reference_img using ORB feature detection,
        FLANN / BFMatcher, and RANSAC homography estimation.
        If feature matching fails due to low texture, falls back to affine/direct scaling.
        """
        h_ref, w_ref = reference_img.shape[:2]
        h_ins, w_ins = inspected_img.shape[:2]

        gray_ref = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY) if reference_img.ndim == 3 else reference_img
        gray_ins = cv2.cvtColor(inspected_img, cv2.COLOR_BGR2GRAY) if inspected_img.ndim == 3 else inspected_img

        orb = cv2.ORB_create(nfeatures=1500, fastThreshold=12)
        kp_ref, des_ref = orb.detectAndCompute(gray_ref, None)
        kp_ins, des_ins = orb.detectAndCompute(gray_ins, None)

        alignment_info = {
            "method": "DIRECT_RESIZE",
            "inlier_count": 0,
            "total_matches": 0,
            "alignment_confidence": 0.40,
            "status": "FALLBACK",
        }

        if des_ref is not None and des_ins is not None and len(kp_ref) >= 10 and len(kp_ins) >= 10:
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            knn_matches = matcher.knnMatch(des_ins, des_ref, k=2)

            # Apply Lowe's ratio test
            good_matches = []
            for m, n in knn_matches:
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)

            alignment_info["total_matches"] = len(good_matches)

            if len(good_matches) >= 12:
                src_pts = np.float32([kp_ins[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_ref[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 4.0)
                if H is not None and mask is not None:
                    inliers = int(mask.sum())
                    alignment_info["inlier_count"] = inliers
                    if inliers >= 10:
                        aligned = cv2.warpPerspective(inspected_img, H, (w_ref, h_ref), flags=cv2.INTER_LINEAR)
                        alignment_info["method"] = "RANSAC_HOMOGRAPHY"
                        alignment_info["alignment_confidence"] = min(0.98, round(inliers / float(len(good_matches) + 5), 2))
                        alignment_info["status"] = "ALIGNED"
                        return aligned, alignment_info

        # Fallback: direct proportional resize
        aligned = cv2.resize(inspected_img, (w_ref, h_ref), interpolation=cv2.INTER_AREA)
        return aligned, alignment_info

    def compare(
        self,
        inspected_img: np.ndarray,
        reference_img: np.ndarray,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes full golden-reference comparative inspection:
          1. Feature-based alignment
          2. Normalization against illumination variation
          3. Multi-spectral absolute difference + structural deviation
          4. Difference heatmap generation (thermal colormap)
          5. Defective deviation regions extraction & bounding boxes
          6. Tolerance compliance verification
        """
        t0 = time.perf_counter()
        profile = self.get_profile(category)
        h_ref, w_ref = reference_img.shape[:2]

        # 1. Align Inspected to Reference
        aligned_inspected, align_meta = self.align_images(inspected_img, reference_img)

        # 2. Lighting Normalization
        # Convert both to LAB to isolate luminance (L) from color (A, B)
        lab_ref = cv2.cvtColor(reference_img, cv2.COLOR_BGR2LAB).astype(np.float32)
        lab_ins = cv2.cvtColor(aligned_inspected, cv2.COLOR_BGR2LAB).astype(np.float32)

        # Subtract local illumination bias (large-kernel blur) to prevent normal shading from tripping false positives
        blur_k = max(25, int(min(h_ref, w_ref) * 0.08) | 1)
        l_ref_local = cv2.GaussianBlur(lab_ref[:, :, 0], (blur_k, blur_k), 0)
        l_ins_local = cv2.GaussianBlur(lab_ins[:, :, 0], (blur_k, blur_k), 0)

        norm_l_ref = lab_ref[:, :, 0] - l_ref_local
        norm_l_ins = lab_ins[:, :, 0] - l_ins_local

        # 3. Structural & Color Deviation
        diff_l = np.abs(norm_l_ins - norm_l_ref)
        diff_a = np.abs(lab_ins[:, :, 1] - lab_ref[:, :, 1])
        diff_b = np.abs(lab_ins[:, :, 2] - lab_ref[:, :, 2])
        delta_e = np.sqrt(diff_l ** 2 + diff_a ** 2 + diff_b ** 2)

        # 4. Filter sub-pixel alignment jitter with morphological opening
        thr_val = float(profile["intensity_deviation_threshold"])
        raw_anomaly_mask = (delta_e > thr_val).astype(np.uint8) * 255
        clean_mask = cv2.morphologyEx(raw_anomaly_mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))

        total_pixels = h_ref * w_ref
        anomaly_pixels = int(np.count_nonzero(clean_mask))
        anomaly_area_ratio = float(anomaly_pixels / max(1, total_pixels))
        mean_delta_e = float(np.mean(delta_e))

        # 5. Extract Distinct Anomaly Regions (Bounding Boxes)
        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        anomaly_regions = []
        for c in contours:
            area = cv2.contourArea(c)
            if area >= max(40.0, 0.0003 * total_pixels):
                x, y, bw, bh = cv2.boundingRect(c)
                region_delta_e = float(delta_e[y : y + bh, x : x + bw].mean())
                anomaly_regions.append({
                    "bbox": [int(x), int(y), int(x + bw), int(y + bh)],
                    "area_pixels": int(area),
                    "area_ratio": round(float(area / total_pixels), 5),
                    "mean_delta_e": round(region_delta_e, 2),
                    "severity": "HIGH" if region_delta_e >= 35 or area >= 0.02 * total_pixels else "MEDIUM",
                })

        anomaly_regions.sort(key=lambda r: r["area_pixels"], reverse=True)

        # 6. Generate Difference Heatmap (Base64 JPEG)
        # Normalize delta_e to 0..255 for JET colormap
        norm_map = np.clip((delta_e / 50.0) * 255.0, 0, 255).astype(np.uint8)
        heatmap_color = cv2.applyColorMap(norm_map, cv2.COLORMAP_JET)
        blended_heatmap = cv2.addWeighted(aligned_inspected, 0.50, heatmap_color, 0.50, 0)

        _, buf = cv2.imencode(".jpg", blended_heatmap, [cv2.IMWRITE_JPEG_QUALITY, 85])
        heatmap_base64 = f"data:image/jpeg;base64,{base64.b64encode(buf).decode('utf-8')}" if buf is not None else ""

        _, buf_aligned = cv2.imencode(".jpg", aligned_inspected, [cv2.IMWRITE_JPEG_QUALITY, 85])
        aligned_base64 = f"data:image/jpeg;base64,{base64.b64encode(buf_aligned).decode('utf-8')}" if buf_aligned is not None else ""

        # 7. Evaluate against Tolerance Criteria
        tol_area = profile["anomaly_area_max_pct"]
        tol_delta_e = profile["max_color_delta_e"]

        within_tolerance = (anomaly_area_ratio <= tol_area) and (mean_delta_e <= tol_delta_e)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        res = {
            "reference_version": profile["reference_version"],
            "profile_category": profile["category"],
            "alignment": align_meta,
            "within_tolerance": within_tolerance,
            "mean_delta_e": round(mean_delta_e, 2),
            "max_color_delta_e_tolerance": tol_delta_e,
            "anomaly_area_ratio": round(anomaly_area_ratio, 4),
            "anomaly_area_tolerance": tol_area,
            "anomaly_regions_count": len(anomaly_regions),
            "anomaly_regions": anomaly_regions[:12],
            "difference_heatmap_base64": heatmap_base64,
            "aligned_inspected_base64": aligned_base64,
            "latency_ms": round(latency_ms, 1),
            "tolerance_evaluation": {
                "color_deviation_ok": mean_delta_e <= tol_delta_e,
                "surface_anomaly_ok": anomaly_area_ratio <= tol_area,
                "overall_status": "PASS" if within_tolerance else "REJECT",
            },
        }
        res["aligned"] = res["alignment"]["status"] in ("ALIGNED", "FALLBACK")
        res["similarity_score"] = max(0.0, round(1.0 - min(1.0, mean_delta_e / 50.0), 3))
        return res

    def align_and_compare(
        self,
        inspected: np.ndarray,
        reference: np.ndarray,
        profile_name: Optional[str] = "METAL_SHEET",
    ) -> Dict[str, Any]:
        return self.compare(inspected, reference, category=profile_name)

    @property
    def PROFILES(self) -> Dict[str, Dict[str, Any]]:
        return self.profiles


golden_reference_service = GoldenReferenceService()
