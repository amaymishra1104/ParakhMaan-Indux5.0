"""
ParakhMaan — INT8 ONNX Model Quantization & NVIDIA Jetson Orin Nano Profile Generator
=====================================================================================
Quantizes the FP32 ParakhMaanDefectNet ONNX model into an optimized INT8 representation
targeting embedded edge gateways such as NVIDIA Jetson Orin Nano, AGX Orin, and industrial IPCs.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import numpy as np
import onnx
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType


def quantize_fp32_to_int8(
    input_model_path: str,
    output_model_path: str,
    weight_type: QuantType = QuantType.QInt8,
) -> dict:
    """
    Quantizes an ONNX model dynamically to INT8 precision.
    """
    input_p = Path(input_model_path)
    output_p = Path(output_model_path)
    output_p.parent.mkdir(parents=True, exist_ok=True)

    if not input_p.exists():
        raise FileNotFoundError(f"Input model not found at {input_p}")

    fp32_size_bytes = os.path.getsize(input_p)
    t0 = time.perf_counter()

    print(f"[*] Quantizing FP32 model: {input_p} ({fp32_size_bytes / 1024:.1f} KB)")
    quantize_dynamic(
        model_input=str(input_p),
        model_output=str(output_p),
        weight_type=weight_type,
    )
    quant_duration = time.perf_counter() - t0
    int8_size_bytes = os.path.getsize(output_p)

    compression_ratio = fp32_size_bytes / max(int8_size_bytes, 1)
    reduction_pct = (1.0 - (int8_size_bytes / fp32_size_bytes)) * 100.0

    print(f"[+] Quantization completed in {quant_duration:.2f}s")
    print(f"[+] INT8 model saved: {output_p} ({int8_size_bytes / 1024:.1f} KB)")
    print(f"[+] Footprint reduction: {reduction_pct:.1f}% (Compression ratio: {compression_ratio:.2f}x)")

    # Verify that the INT8 model is valid and runnable
    sess_int8 = ort.InferenceSession(str(output_p), providers=["CPUExecutionProvider"])
    dummy_input = np.random.randn(1, 3, 640, 640).astype(np.float32)
    input_name = sess_int8.get_inputs()[0].name
    out = sess_int8.run(None, {input_name: dummy_input})

    # Benchmark FP32 vs INT8 latency
    sess_fp32 = ort.InferenceSession(str(input_p), providers=["CPUExecutionProvider"])
    
    # Warmup
    for _ in range(3):
        sess_fp32.run(None, {input_name: dummy_input})
        sess_int8.run(None, {input_name: dummy_input})

    runs = 15
    t_start = time.perf_counter()
    for _ in range(runs):
        sess_fp32.run(None, {input_name: dummy_input})
    fp32_latency_ms = (time.perf_counter() - t_start) / runs * 1000.0

    t_start = time.perf_counter()
    for _ in range(runs):
        sess_int8.run(None, {input_name: dummy_input})
    int8_latency_ms = (time.perf_counter() - t_start) / runs * 1000.0

    profile = {
        "model_name": "ParakhMaanDefectNet v1.0 (INT8 Quantized)",
        "fp32_model_path": str(input_p),
        "int8_model_path": str(output_p),
        "fp32_size_kb": round(fp32_size_bytes / 1024.0, 2),
        "int8_size_kb": round(int8_size_bytes / 1024.0, 2),
        "compression_ratio": round(compression_ratio, 2),
        "size_reduction_pct": round(reduction_pct, 1),
        "quantization_type": "dynamic_int8",
        "weight_type": "qint8",
        "input_resolution": "640x640",
        "cpu_benchmarks": {
            "fp32_mean_latency_ms": round(fp32_latency_ms, 2),
            "fp32_throughput_fps": round(1000.0 / max(fp32_latency_ms, 0.001), 1),
            "int8_mean_latency_ms": round(int8_latency_ms, 2),
            "int8_throughput_fps": round(1000.0 / max(int8_latency_ms, 0.001), 1),
        },
        "jetson_orin_nano_specifications": {
            "target_device": "NVIDIA Jetson Orin Nano (8GB / 4GB)",
            "gpu_architecture": "NVIDIA Ampere (1024 CUDA Cores, 32 Tensor Cores)",
            "ai_performance_tops": 40.0,
            "recommended_execution_providers": [
                "TensorrtExecutionProvider",
                "CUDAExecutionProvider",
                "CPUExecutionProvider"
            ],
            "tensorrt_precision": "INT8 / FP16 hybrid",
            "dp4a_support": True,
            "estimated_jetson_tensorrt_latency_ms": round(fp32_latency_ms * 0.18, 2),
            "estimated_jetson_throughput_fps": round((1000.0 / (fp32_latency_ms * 0.18)), 1),
            "power_profiles": ["7W (Low Power)", "15W (Standard)", "20W (High Performance)"]
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    profile_path = output_p.parent / "jetson_orin_nano_profile.json"
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    print(f"[+] Jetson Orin Nano edge profile saved: {profile_path}")
    return profile


if __name__ == "__main__":
    fp32_path = backend_dir / "app" / "models_cv" / "parakhmaan_defect_v1.onnx"
    int8_path = backend_dir / "app" / "models_cv" / "parakhmaan_defect_v1_int8.onnx"
    quantize_fp32_to_int8(str(fp32_path), str(int8_path))
