import os
import cv2
import numpy as np
import pytest
from app.services.image_quality import ImageQualityAnalyzer

def test_image_quality_blur_and_glare(tmp_path):
    analyzer = ImageQualityAnalyzer()

    # 1. Create a sharp package test image
    sharp_img = np.full((600, 600, 3), 220, dtype=np.uint8)
    cv2.rectangle(sharp_img, (50, 50), (550, 550), (0, 0, 0), 2)
    cv2.putText(sharp_img, "LEGAL METROLOGY DECLARATION", (70, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(sharp_img, "NET QTY: 500g  MRP: Rs. 100", (70, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    sharp_path = str(tmp_path / "sharp.jpg")
    cv2.imwrite(sharp_path, sharp_img)

    res_sharp = analyzer.analyze(sharp_path)
    assert res_sharp["quality_score"] >= 0.80
    assert res_sharp["blur"] is False

    # 2. Create a blurry test image
    blurry_img = cv2.GaussianBlur(sharp_img, (25, 25), 0)
    blurry_path = str(tmp_path / "blurry.jpg")
    cv2.imwrite(blurry_path, blurry_img)

    res_blurry = analyzer.analyze(blurry_path)
    assert res_blurry["blur"] is True
    assert res_blurry["quality_score"] < 0.80

    # 3. Create a glare test image
    glare_img = sharp_img.copy()
    cv2.circle(glare_img, (300, 300), 180, (255, 255, 255), -1)
    glare_path = str(tmp_path / "glare.jpg")
    cv2.imwrite(glare_path, glare_img)

    res_glare = analyzer.analyze(glare_path)
    assert res_glare["glare"] is True

def test_image_quality_blank_or_empty_photo(tmp_path):
    analyzer = ImageQualityAnalyzer()

    # Create solid white / blank image (no text, no package)
    blank_img = np.full((600, 600, 3), 255, dtype=np.uint8)
    blank_path = str(tmp_path / "blank.jpg")
    cv2.imwrite(blank_path, blank_img)

    res_blank = analyzer.analyze(blank_path)
    assert res_blank["is_empty"] is True
    assert res_blank["quality_score"] == 0.0
    assert res_blank["surface_visible"] is False
    assert any("BLANK_OR_EMPTY_IMAGE" in issue for issue in res_blank["issues"])

