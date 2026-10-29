import os
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np


class IndustrialQualityGate:
    """
    Industrial Image Quality Gate for Automated Defect Inspection.
    Evaluates optical sharpness, motion blur, exposure, specular glare,
    product centering, and surface area coverage before defect inference.

    Produces defensible status:
      - SUITABLE: image is clear and ready for automated decision
      - SUITABLE_WITH_WARNINGS: minor issues (e.g. edge glare), inspection proceeds with caution
      - UNSUITABLE: optical quality violates factory criteria, forces MANUAL REVIEW / RECAPTURE
    """

    def __init__(
        self,
        min_width: int = 480,
        min_height: int = 480,
        sharpness_threshold: float = 20.0,
        glare_ratio_max: float = 0.08,
        min_luminance: float = 38.0,
        max_luminance: float = 235.0,
        min_product_coverage: float = 0.15,
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.sharpness_threshold = sharpness_threshold
        self.glare_ratio_max = glare_ratio_max
        self.min_luminance = min_luminance
        self.max_luminance = max_luminance
        self.min_product_coverage = min_product_coverage

    def evaluate(self, image: np.ndarray) -> Dict[str, Any]:
        h, w = image.shape[:2]
        total_pixels = h * w
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image

        issues: List[str] = []
        warnings: List[str] = []
        actions: List[str] = []

        # 1. Resolution Check
        resolution_ok = (w >= self.min_width and h >= self.min_height)
        if not resolution_ok:
            issues.append(f"Low resolution ({w}x{h}px). Minimum requirement is {self.min_width}x{self.min_height}px.")
            actions.append("Upgrade camera feed resolution or move optical sensor closer to the inspection conveyor.")

        # 2. Sharpness & Blur (Laplacian Variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness_score = float(laplacian.var())
        is_blurry = sharpness_score < 0.30
        if is_blurry:
            issues.append(f"Excessive image blur detected (sharpness index: {sharpness_score:.2f}, required >= 0.30). Fine cracks/scratches cannot be reliably resolved.")
            warnings.append(f"Image blur detected (sharpness index: {sharpness_score:.2f}).")
            actions.append("Adjust camera auto-focus, clean the inspection lens, or increase camera shutter speed to eliminate motion blur.")
        elif sharpness_score < 2.0:
            warnings.append(f"Low surface texture/contrast (sharpness index: {sharpness_score:.1f}).")

        # 3. Luminance & Exposure
        mean_brightness = float(np.mean(gray))
        std_brightness = float(np.std(gray))
        is_underexposed = mean_brightness < self.min_luminance
        is_overexposed = mean_brightness > self.max_luminance

        if is_underexposed:
            issues.append(f"Severe underexposure (mean luminance: {mean_brightness:.1f}/255). Insufficient surface detail.")
            actions.append("Increase ring-light or backlight illumination at the inspection station.")
        elif mean_brightness < self.min_luminance + 15:
            warnings.append(f"Suboptimal illumination (mean luminance: {mean_brightness:.1f}/255).")

        if is_overexposed:
            issues.append(f"Severe overexposure (mean luminance: {mean_brightness:.1f}/255). Surface textures washed out.")
            actions.append("Reduce camera gain or decrease auxiliary lighting intensity.")
        elif mean_brightness > self.max_luminance - 15:
            warnings.append(f"High surface brightness ({mean_brightness:.1f}/255). Approaching camera saturation.")

        # 4. Specular Glare (HSV V > 245 and S < 40)
        if image.ndim == 3:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            glare_mask = (hsv[:, :, 2] > 245) & (hsv[:, :, 1] < 45)
        else:
            glare_mask = gray > 248
        glare_pixel_count = int(np.count_nonzero(glare_mask))
        glare_ratio = float(glare_pixel_count / max(1, total_pixels))
        has_severe_glare = glare_ratio > self.glare_ratio_max

        if has_severe_glare:
            issues.append(f"Excessive specular glare ({glare_ratio * 100:.1f}% surface area). Reflections may obscure dents and micro-cracks.")
            actions.append("Use a polarizing filter on the lens or adjust the angle of incidence of the directional lighting.")
        elif glare_ratio > self.glare_ratio_max * 0.5:
            warnings.append(f"Moderate glare detected ({glare_ratio * 100:.1f}% area).")

        # 5. Product Silhouette & Surface Coverage
        # Measures the proportion of non-dark conveyor background pixels in the frame
        surface_pixels = np.count_nonzero(gray > 20)
        coverage_ratio = float(surface_pixels / max(1, total_pixels))

        product_visible = coverage_ratio >= self.min_product_coverage
        if not product_visible:
            issues.append(f"Insufficient product surface in field of view ({coverage_ratio * 100:.1f}% coverage, required >= {self.min_product_coverage * 100:.1f}%).")
            actions.append("Ensure the workpiece is positioned properly inside the camera field of view before triggering inspection.")

        # 6. Overall Quality Score (0.0 to 1.0)
        score = 1.0
        if not resolution_ok:
            score -= 0.30
        if is_blurry:
            score -= 0.35
        if is_underexposed or is_overexposed:
            score -= 0.30
        if has_severe_glare:
            score -= 0.25
        if not product_visible:
            score -= 0.40
        if warnings:
            score -= len(warnings) * 0.05
        score = max(0.05, min(1.0, round(score, 2)))

        # 7. Quality Status Determination
        if len(issues) == 0 and score >= 0.75:
            status = "SUITABLE"
        elif len(issues) == 0 and score >= 0.50:
            status = "SUITABLE_WITH_WARNINGS"
        else:
            status = "UNSUITABLE"

        return {
            "status": status,
            "quality_status": status,
            "quality_score": score,
            "recapture_recommended": status == "UNSUITABLE",
            "measurements": {
                "sharpness": round(sharpness_score, 1),
                "sharpness_index": round(sharpness_score, 1),
                "sharpness_threshold": self.sharpness_threshold,
                "exposure": round(mean_brightness, 1),
                "mean_luminance": round(mean_brightness, 1),
                "contrast_std": round(std_brightness, 1),
                "glare_ratio": round(glare_ratio, 4),
                "glare_ratio_max": self.glare_ratio_max,
                "dimensions": [w, h],
                "product_coverage_ratio": round(coverage_ratio, 3),
            },
            "issues": issues,
            "warnings": warnings,
            "recommended_actions": actions,
            "recommendations": actions,
        }

    def analyze(self, image: np.ndarray) -> Dict[str, Any]:
        return self.evaluate(image)

    def evaluate_file(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {
                "quality_status": "UNSUITABLE",
                "quality_score": 0.0,
                "recapture_recommended": True,
                "measurements": {},
                "issues": [f"Image file not found: {file_path}"],
                "warnings": [],
                "recommended_actions": ["Verify file path and server storage permissions."],
            }
        img = cv2.imread(file_path)
        if img is None:
            return {
                "quality_status": "UNSUITABLE",
                "quality_score": 0.0,
                "recapture_recommended": True,
                "measurements": {},
                "issues": ["Unable to decode image format."],
                "warnings": [],
                "recommended_actions": ["Upload a standard PNG, JPEG, or WebP image file."],
            }
        return self.evaluate(img)


industrial_quality_gate = IndustrialQualityGate()
