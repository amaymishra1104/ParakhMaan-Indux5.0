import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
import os

class ImageQualityAnalyzer:
    """
    OpenCV-based Image Quality Engine for Legal Metrology inspections.
    Analyzes sharpness, blur, specular glare, resolution, perspective, and visibility.
    Strictly flags empty, blank, solid-color, or featureless images.
    """

    def __init__(
        self,
        min_width: int = 400,
        min_height: int = 400,
        blur_threshold: float = 65.0,
        glare_ratio_threshold: float = 0.08
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.blur_threshold = blur_threshold
        self.glare_ratio_threshold = glare_ratio_threshold

    def analyze(self, image_path: str) -> Dict[str, Any]:
        if not os.path.exists(image_path):
            return {
                "quality_score": 0.0,
                "blur": True,
                "glare": False,
                "resolution_ok": False,
                "perspective_ok": False,
                "occlusion_detected": True,
                "surface_visible": False,
                "is_empty": True,
                "sharpness_score": 0.0,
                "issues": ["Image file not found on server"]
            }

        # Load image via OpenCV
        img = cv2.imread(image_path)
        if img is None:
            return {
                "quality_score": 0.0,
                "blur": True,
                "glare": False,
                "resolution_ok": False,
                "perspective_ok": False,
                "occlusion_detected": True,
                "surface_visible": False,
                "is_empty": True,
                "sharpness_score": 0.0,
                "issues": ["Unable to decode image format"]
            }

        height, width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        issues: List[str] = []

        total_pixels = width * height

        # 1. Blank / Empty / Solid Color Detection
        std_dev = float(np.std(gray))
        edges = cv2.Canny(gray, 50, 150)
        edge_pixel_count = int(np.count_nonzero(edges))
        edge_density = float(edge_pixel_count / total_pixels)

        # Truly blank or uniform color image has near-zero variance and 0 edges
        is_empty = (std_dev < 6.0) or (std_dev < 12.0 and edge_pixel_count < 15)
        if is_empty:
            issues.append("BLANK_OR_EMPTY_IMAGE: No package structure, text, or identifiable surface features detected.")

        # 2. Resolution Check
        resolution_ok = (width >= self.min_width and height >= self.min_height)
        if not resolution_ok:
            issues.append(f"Low resolution ({width}x{height}px). Minimum recommended is {self.min_width}x{self.min_height}px.")

        # 3. Blur / Sharpness Detection (Laplacian Variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness_score = float(laplacian.var())
        is_blurry = sharpness_score < self.blur_threshold and not is_empty
        if is_blurry:
            issues.append(f"Image is blurry (sharpness index: {sharpness_score:.1f}, required >= {self.blur_threshold:.1f}). Text may be illegible.")

        # 4. Glare / Overexposure Detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]
        glare_mask = v_channel > 245
        glare_pixels = np.sum(glare_mask)
        glare_ratio = float(glare_pixels / total_pixels)
        has_glare = (glare_ratio > self.glare_ratio_threshold) and not is_empty
        if has_glare:
            issues.append(f"Specular reflection/glare detected ({glare_ratio * 100:.1f}% area). May obscure mandatory declarations.")

        # 5. Contrast & Exposure Check
        mean_brightness = float(np.mean(gray))
        if mean_brightness < 35 and not is_empty:
            issues.append("Image is severely underexposed / too dark.")
        elif mean_brightness > 245 and not is_empty:
            issues.append("Image is severely overexposed / washed out.")

        # 6. Perspective / Aspect Ratio
        aspect_ratio = width / height
        perspective_ok = 0.25 <= aspect_ratio <= 4.0

        # Calculate composite quality score (0.0 to 1.0)
        if is_empty:
            quality_score = 0.0
            surface_visible = False
        else:
            surface_visible = True
            quality_score = 1.0
            if is_blurry:
                quality_score -= 0.35
            if has_glare:
                quality_score -= 0.25
            if not resolution_ok:
                quality_score -= 0.25
            if not perspective_ok:
                quality_score -= 0.15
            if mean_brightness < 40 or mean_brightness > 230:
                quality_score -= 0.15

            quality_score = max(0.1, min(1.0, round(quality_score, 2)))

        return {
            "quality_score": quality_score,
            "blur": is_blurry,
            "glare": has_glare,
            "resolution_ok": resolution_ok,
            "perspective_ok": perspective_ok,
            "occlusion_detected": False,
            "surface_visible": surface_visible,
            "is_empty": is_empty,
            "sharpness_score": round(sharpness_score, 2),
            "glare_ratio": round(glare_ratio, 4),
            "edge_density": round(edge_density, 5),
            "dimensions": {"width": width, "height": height},
            "issues": issues
        }

image_quality_analyzer = ImageQualityAnalyzer()
