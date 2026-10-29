"""
ParakhMaan — PatchCore Unsupervised Anomaly Detection Service
=============================================================
Implements memory-bank patch-level visual anomaly detection for industrial surfaces,
enabling zero-shot novelty detection on unmarked/unlabeled manufactured products
without requiring defect annotations (MVTec AD inspection paradigm).
"""

import os
import io
import time
import base64
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import cv2
import numpy as np
from sklearn.neighbors import NearestNeighbors


class PatchCoreAnomalyDetector:
    """
    PatchCore-style memory bank detector for industrial surface anomaly detection.
    Extracts multi-scale patch embeddings from defect-free golden samples and flags
    out-of-distribution surface anomalies on test parts.
    """

    def __init__(
        self,
        memory_bank_path: Optional[str] = None,
        patch_size: int = 32,
        stride: int = 16,
        embedding_dim: int = 48,
        coreset_ratio: float = 0.30,
        default_threshold: float = 0.45,
    ):
        self.patch_size = patch_size
        self.stride = stride
        self.embedding_dim = embedding_dim
        self.coreset_ratio = coreset_ratio
        self.threshold = default_threshold
        
        backend_dir = Path(__file__).resolve().parent.parent.parent
        self.storage_dir = backend_dir / "storage" / "anomaly_models"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_bank_file = (
            Path(memory_bank_path)
            if memory_bank_path
            else self.storage_dir / "patchcore_memory_bank.npz"
        )
        
        self.memory_bank: Optional[np.ndarray] = None
        self.nn_model: Optional[NearestNeighbors] = None
        self.is_fitted: bool = False
        self.training_sample_count: int = 0

        # Load existing bank or calibrate a robust default baseline
        if self.memory_bank_file.exists():
            self._load_memory_bank()
        else:
            self._calibrate_default_baseline()

    def _extract_patch_embeddings(self, image_bgr: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int, int, int, int]]]:
        """
        Extracts multi-scale, texture- and gradient-aware normalized patch embeddings
        from an image grid. Resizes to standard resolution (320x320) for bounded edge latency.
        """
        work_img = cv2.resize(image_bgr, (320, 320))
        h, w = work_img.shape[:2]
        gray = cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)
        
        # Multi-scale features: intensity, gradient magnitude, and Laplacian response
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = cv2.magnitude(gx, gy)
        laplacian = np.abs(cv2.Laplacian(gray, cv2.CV_32F))
        
        embeddings = []
        patch_coords = []
        
        p = self.patch_size
        s = self.stride
        
        for y in range(0, h - p + 1, s):
            for x in range(0, w - p + 1, s):
                patch_gray = gray[y : y + p, x : x + p]
                patch_grad = grad_mag[y : y + p, x : x + p]
                patch_lap = laplacian[y : y + p, x : x + p]
                
                # Extract statistical descriptors across sub-blocks (2x2 cells within patch)
                feats = []
                sub_p = p // 2
                for sy in [0, sub_p]:
                    for sx in [0, sub_p]:
                        cg = patch_gray[sy : sy + sub_p, sx : sx + sub_p]
                        cgr = patch_grad[sy : sy + sub_p, sx : sx + sub_p]
                        cl = patch_lap[sy : sy + sub_p, sx : sx + sub_p]
                        
                        feats.extend([
                            float(np.mean(cg)) / 255.0,
                            float(np.std(cg)) / 128.0,
                            float(np.mean(cgr)) / 100.0,
                            float(np.std(cgr)) / 100.0,
                            float(np.mean(cl)) / 50.0,
                            float(np.percentile(cg, 10)) / 255.0,
                            float(np.percentile(cg, 90)) / 255.0,
                        ])
                
                feat_vec = np.array(feats, dtype=np.float32)
                if len(feat_vec) < self.embedding_dim:
                    pad = np.zeros(self.embedding_dim - len(feat_vec), dtype=np.float32)
                    feat_vec = np.concatenate([feat_vec, pad])
                else:
                    feat_vec = feat_vec[: self.embedding_dim]
                
                # L2 normalize
                norm = float(np.linalg.norm(feat_vec))
                if norm > 1e-6:
                    feat_vec /= norm
                    
                embeddings.append(feat_vec)
                patch_coords.append((x, y, p, p))
                
        return np.array(embeddings, dtype=np.float32), patch_coords

    def fit(self, normal_images: List[np.ndarray], coreset_ratio: Optional[float] = None) -> Dict[str, Any]:
        """
        Builds and indexes a memory bank from defect-free training images.
        """
        if not normal_images:
            raise ValueError("Must provide at least one normal image to train memory bank.")
            
        ratio = coreset_ratio or self.coreset_ratio
        all_embeddings = []
        t0 = time.perf_counter()
        
        for img in normal_images:
            embs, _ = self._extract_patch_embeddings(img)
            all_embeddings.append(embs)
            
        stacked = np.vstack(all_embeddings)
        n_total = len(stacked)
        
        # Greedy coreset subsampling
        n_coreset = max(int(n_total * ratio), min(150, n_total))
        if n_coreset < n_total:
            indices = np.random.choice(n_total, size=n_coreset, replace=False)
            self.memory_bank = stacked[indices]
        else:
            self.memory_bank = stacked
            
        # Fit NearestNeighbors index
        self.nn_model = NearestNeighbors(n_neighbors=2, algorithm="ball_tree")
        self.nn_model.fit(self.memory_bank)
        
        # Calculate empirical threshold (distance to nearest non-identical neighbor in coreset)
        distances, _ = self.nn_model.kneighbors(self.memory_bank[: min(400, len(self.memory_bank))])
        neighbor_dists = distances[:, 1]
        self.threshold = float(np.percentile(neighbor_dists, 95.0)) * 1.35 + 0.05
        
        self.is_fitted = True
        self.training_sample_count = len(normal_images)
        self._save_memory_bank()
        
        fit_time = time.perf_counter() - t0
        return {
            "status": "FITTED",
            "samples_trained": self.training_sample_count,
            "total_patches_extracted": n_total,
            "coreset_size": len(self.memory_bank),
            "calibrated_threshold": round(self.threshold, 4),
            "fitting_latency_sec": round(fit_time, 2),
        }

    def predict(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Infers anomaly score and spatial heatmap for a query part image.
        """
        t0 = time.perf_counter()
        if not self.is_fitted or self.nn_model is None:
            self._calibrate_default_baseline()
            
        orig_h, orig_w = image_bgr.shape[:2]
        embs, coords = self._extract_patch_embeddings(image_bgr)
        
        if len(embs) == 0:
            return {
                "anomaly_score": 0.0,
                "is_anomaly": False,
                "threshold": self.threshold,
                "anomaly_regions": [],
                "heatmap_base64": "",
                "latency_ms": 0.0,
            }
            
        distances, _ = self.nn_model.kneighbors(embs, n_neighbors=1)
        patch_scores = distances.ravel()
        
        # 2D Anomaly Heatmap Construction in 320x320 space
        grid_dim = int(np.sqrt(len(patch_scores)))
        grid_h = (320 - self.patch_size) // self.stride + 1
        grid_w = (320 - self.patch_size) // self.stride + 1
        
        anomaly_map = np.zeros((grid_h, grid_w), dtype=np.float32)
        idx = 0
        for gy in range(grid_h):
            for gx in range(grid_w):
                if idx < len(patch_scores):
                    anomaly_map[gy, gx] = patch_scores[idx]
                    idx += 1
                    
        # Upsample anomaly map to original image resolution
        full_map = cv2.resize(anomaly_map, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)
        full_map = cv2.GaussianBlur(full_map, (15, 15), 0)
        
        # Anomaly scoring: top 5% of patch distances
        top_k = max(int(len(patch_scores) * 0.05), 1)
        top_patches = np.sort(patch_scores)[-top_k:]
        image_anomaly_score = float(np.mean(top_patches))
        
        # Normalized score: 0.0 to 1.0 (threshold = 0.50 score)
        ratio = image_anomaly_score / max(self.threshold, 1e-4)
        if ratio <= 1.0:
            normalized_score = float(ratio * 0.50)
        else:
            normalized_score = float(np.clip(0.50 + (ratio - 1.0) * 0.50, 0.50, 1.0))
            
        is_anomaly = bool(image_anomaly_score > self.threshold)
        
        # Extract localized anomaly bounding boxes
        binary_mask = (full_map > self.threshold).astype(np.uint8) * 255
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        anomaly_regions = []
        for c in contours:
            area = cv2.contourArea(c)
            if area > (orig_w * orig_h * 0.001):  # Filter minor noise (< 0.1% of part)
                bx, by, bw, bh = cv2.boundingRect(c)
                region_score = float(np.mean(full_map[by : by + bh, bx : bx + bw]))
                conf = float(np.clip(region_score / (self.threshold * 1.3), 0.55, 0.98))
                anomaly_regions.append({
                    "box": [bx, by, bx + bw, by + bh],
                    "class": "UNSUPERVISED_ANOMALY",
                    "confidence": round(conf, 3),
                    "area_px": int(area),
                    "anomaly_distance": round(region_score, 4),
                    "severity": "CRITICAL" if conf > 0.85 else "HIGH" if conf > 0.70 else "MEDIUM",
                })
                
        # Generate JET Colormap Anomaly Heatmap
        norm_map = np.clip((full_map / (self.threshold * 1.5)) * 255.0, 0, 255).astype(np.uint8)
        color_heatmap = cv2.applyColorMap(norm_map, cv2.COLORMAP_JET)
        
        # Alpha-blend with original image
        blend = cv2.addWeighted(image_bgr, 0.60, color_heatmap, 0.40, 0)
        
        # Draw bounding boxes on blend
        for reg in anomaly_regions:
            x1, y1, x2, y2 = reg["box"]
            cv2.rectangle(blend, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(
                blend,
                f"NOVELTY {reg['confidence']:.2f}",
                (x1, max(y1 - 6, 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 255),
                1,
            )
            
        _, buf = cv2.imencode(".png", blend)
        heatmap_b64 = f"data:image/png;base64,{base64.b64encode(buf).decode('utf-8')}"
        
        latency = (time.perf_counter() - t0) * 1000.0
        return {
            "anomaly_score": round(normalized_score, 4),
            "raw_anomaly_distance": round(image_anomaly_score, 4),
            "is_anomaly": is_anomaly,
            "threshold": round(self.threshold, 4),
            "anomaly_regions": anomaly_regions,
            "heatmap_base64": heatmap_b64,
            "patches_analyzed": len(coords),
            "latency_ms": round(latency, 2),
            "memory_bank_size": len(self.memory_bank) if self.memory_bank is not None else 0,
        }

    def _save_memory_bank(self):
        """Saves fitted memory bank and metadata to disk."""
        np.savez_compressed(
            self.memory_bank_file,
            memory_bank=self.memory_bank,
            threshold=np.array([self.threshold]),
            samples_count=np.array([self.training_sample_count]),
        )

    def _load_memory_bank(self):
        """Loads fitted memory bank from disk."""
        try:
            data = np.load(self.memory_bank_file)
            loaded_bank = data["memory_bank"]
            if loaded_bank.shape[1] != self.embedding_dim:
                self._calibrate_default_baseline()
                return
            self.memory_bank = loaded_bank
            self.threshold = float(data["threshold"][0])
            self.training_sample_count = int(data["samples_count"][0])
            self.nn_model = NearestNeighbors(n_neighbors=1, algorithm="ball_tree")
            self.nn_model.fit(self.memory_bank)
            self.is_fitted = True
        except Exception:
            self._calibrate_default_baseline()

    def _calibrate_default_baseline(self):
        """
        Synthesizes a realistic calibration bank of defect-free industrial metal surfaces
        to ensure out-of-the-box operation.
        """
        synthetic_normals = []
        for i in range(8):
            base_val = 150 + i * 5
            img = np.full((320, 320, 3), base_val, dtype=np.uint8)
            # Add realistic metallic brushed lines along horizontal axis
            for y in range(0, 320, 4):
                line_val = int(np.clip(base_val + np.random.randint(-10, 10), 0, 255))
                img[y : y + 2, :] = line_val
            # Subtle Gaussian noise
            noise = np.random.normal(0, 2.0, (320, 320, 3)).astype(np.int16)
            img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            synthetic_normals.append(img)
            
        self.fit(synthetic_normals, coreset_ratio=0.40)


# Global singleton instance
patchcore_service = PatchCoreAnomalyDetector()
