"""
ParakhMaan Industrial Defect Detector - Empirical Comparative Evaluation Pipeline
---------------------------------------------------------------------------------
Evaluates and benchmarks three computer vision approaches on a held-out test dataset:
  1. Deep Learning ONNX Model (parakhmaan_defect_v1.onnx)
  2. Classical Computer Vision (OpenCV morphological & colorimetric baselines)
  3. Fused Hybrid Engine (ONNX + OpenCV Complementary Deduplication)

Computes real Precision, Recall, F1 score, False Positive Rate, Miss Rate,
and Latency profiles (Mean, P50, P95 ms, and FPS).
Saves benchmark report to backend/storage/benchmarks/benchmark_results.json.
"""

import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple
import cv2
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.services.defect_detection_service import DefectDetector, DEFECT_TYPES
from scripts.train_defect_detector import generate_sample, CLASSES


def iou(b1: List[float], b2: List[float]) -> float:
    ix1, iy1 = max(b1[0], b2[0]), max(b1[1], b2[1])
    ix2, iy2 = min(b1[2], b2[2]), min(b1[3], b2[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter <= 0:
        return 0.0
    a1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
    a2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
    return inter / max(1e-6, a1 + a2 - inter)


def evaluate_mode(mode: str, test_samples: List[Tuple[np.ndarray, List[Dict]]]) -> Dict[str, Any]:
    # Temporarily set backend
    detector = DefectDetector()
    detector.backend = mode

    latencies: List[float] = []
    tp = 0
    fp = 0
    fn = 0
    per_class = {c: {"tp": 0, "fp": 0, "fn": 0} for c in CLASSES}

    for img, ground_truths in test_samples:
        t0 = time.perf_counter()
        res = detector.detect(img)
        lat = (time.perf_counter() - t0) * 1000.0
        latencies.append(lat)

        pred_dets = res["detections"]
        matched_gt = set()

        for d in pred_dets:
            dtype = d["defect_type"]
            bbox = d["bbox"]

            match = False
            for g_idx, gt in enumerate(ground_truths):
                if g_idx in matched_gt:
                    continue
                if gt["name"] == dtype and iou(bbox, gt["bbox"]) >= 0.20:
                    match = True
                    matched_gt.add(g_idx)
                    break

            if match:
                tp += 1
                if dtype in per_class:
                    per_class[dtype]["tp"] += 1
            else:
                fp += 1
                if dtype in per_class:
                    per_class[dtype]["fp"] += 1

        unmatched = len(ground_truths) - len(matched_gt)
        fn += unmatched
        for g_idx, gt in enumerate(ground_truths):
            if g_idx not in matched_gt:
                gname = gt["name"]
                if gname in per_class:
                    per_class[gname]["fn"] += 1

    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * (precision * recall) / max(1e-6, precision + recall)
    fpr = fp / max(1, tp + fp)
    miss_rate = fn / max(1, tp + fn)

    mean_lat = float(np.mean(latencies))
    p50_lat = float(np.percentile(latencies, 50))
    p95_lat = float(np.percentile(latencies, 95))
    fps = 1000.0 / max(0.1, mean_lat)

    return {
        "mode": mode.upper(),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "miss_rate": round(miss_rate, 4),
        "mean_latency_ms": round(mean_lat, 2),
        "p50_latency_ms": round(p50_lat, 2),
        "p95_latency_ms": round(p95_lat, 2),
        "throughput_fps": round(fps, 1),
        "class_performance": per_class,
    }


def run_benchmark(num_test_samples: int = 60):
    print(f"\n==========================================================================")
    print(f"  ParakhMaan Empirical Evaluation Pipeline (Indux 5.0 Hackathon Baseline)")
    print(f"==========================================================================")
    print(f"  Generating {num_test_samples} held-out industrial test samples (seed: 9000+)...")

    test_samples = [generate_sample(seed=9000 + i, size=(640, 640)) for i in range(num_test_samples)]

    results = {}
    for mode in ["onnx", "opencv", "hybrid"]:
        print(f"  Evaluating mode: {mode.upper()}...")
        results[mode] = evaluate_mode(mode, test_samples)

    print("\n--------------------------------------------------------------------------")
    print(f"{'Method':<12} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Mean Latency':<12} | {'Throughput':<10}")
    print("--------------------------------------------------------------------------")
    for mode, r in results.items():
        print(f"{r['mode']:<12} | {r['precision']*100:>8.1f}%  | {r['recall']*100:>8.1f}%  | {r['f1_score']*100:>8.1f}%  | {r['mean_latency_ms']:>10.1f}ms | {r['throughput_fps']:>8.1f} FPS")
    print("--------------------------------------------------------------------------\n")

    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "benchmarks", "benchmark_results.json"))
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "test_sample_count": num_test_samples,
        "input_resolution": "640x640",
        "methods_evaluated": results,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Benchmark results successfully saved to: {report_path}")
    return report


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    run_benchmark(count)
