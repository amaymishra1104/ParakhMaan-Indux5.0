from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.services.defect_detection_service import DEFECT_TYPES, SEVERITY_ORDER

# Process knowledge used to turn defect frequencies into actionable root-cause hints.
ROOT_CAUSE_KB: Dict[str, Dict[str, List[str]]] = {
    "SCRATCH": {
        "causes": [
            "Abrasive contact during conveyor transfer or manual handling",
            "Burrs or debris on guide rails, fixtures, or tooling",
            "Insufficient protective film / interleaving between stacked parts",
        ],
        "actions": [
            "Inspect and deburr guide rails, grippers, and transfer chutes",
            "Add protective film or separators at stacking and packing stations",
        ],
    },
    "CRACK": {
        "causes": [
            "Excessive forming / press force or tight bend radius",
            "Thermal stress from uneven heating or rapid cooling",
            "Raw-material inclusions or fatigue in the base material",
        ],
        "actions": [
            "Verify press tonnage and die clearance against the process sheet",
            "Review cooling rate and heat-treatment profile; audit incoming material certificates",
        ],
    },
    "DENT": {
        "causes": [
            "Impact during handling, drops at transfer points, or improper stacking",
            "Foreign particles trapped between die and workpiece",
        ],
        "actions": [
            "Add cushioning at drop points and check palletisation load limits",
            "Clean dies / moulds and add air-blow before forming",
        ],
    },
    "DISCOLOURATION": {
        "causes": [
            "Inconsistent curing, heat treatment, or coating thickness",
            "Oxidation / corrosion from moisture exposure or contamination",
            "Raw-material or paint batch variation",
        ],
        "actions": [
            "Check oven / curing temperature uniformity and dwell time",
            "Review storage humidity and batch traceability of coating material",
        ],
    },
    "DIMENSIONAL_ANOMALY": {
        "causes": [
            "Tool or die wear, mould shrinkage, or fixture misalignment",
            "Machine calibration drift or incorrect program offsets",
        ],
        "actions": [
            "Run tool-wear inspection and re-calibrate the machine against the master gauge",
            "Increase in-process gauging frequency until the deviation is resolved",
        ],
    },
}
GENERIC_KB = {
    "causes": ["Process variation not covered by the built-in knowledge base"],
    "actions": ["Collect confirmed samples and perform a 5-Why / fishbone analysis with the line team"],
}

GRID_LABELS = [
    ["top-left", "top-centre", "top-right"],
    ["middle-left", "centre", "middle-right"],
    ["bottom-left", "bottom-centre", "bottom-right"],
]


def _as_aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _hotspot(detections: List[Dict[str, Any]]) -> Dict[str, Any]:
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for d in detections:
        bn = (d.get("metrics") or {}).get("bbox_norm")
        if not bn or len(bn) != 4:
            continue
        cx, cy = (bn[0] + bn[2]) / 2, (bn[1] + bn[3]) / 2
        grid[min(2, int(cy * 3))][min(2, int(cx * 3))] += 1
    total = sum(sum(r) for r in grid)
    best_r, best_c, best = 0, 0, 0
    for r in range(3):
        for c in range(3):
            if grid[r][c] > best:
                best_r, best_c, best = r, c, grid[r][c]
    return {
        "grid": grid,
        "dominant_region": GRID_LABELS[best_r][best_c] if best else None,
        "dominant_share": round(best / total, 3) if total else 0.0,
    }


def build_defect_analytics(
    inspections: List[Dict[str, Any]],
    detections: List[Dict[str, Any]],
    images: Optional[List[Dict[str, Any]]] = None,
    days: int = 30,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    now = _as_aware(now) or datetime.now(timezone.utc)
    window_start = (now - timedelta(days=days - 1)).date()

    active = [d for d in detections if d.get("reviewer_status") != "REJECTED"]
    insp_by_id = {i["id"]: i for i in inspections}

    outcomes = Counter(i.get("overall_outcome", "PENDING") for i in inspections)
    total_insp = len(inspections)

    # Frequency by type and severity
    type_counts = Counter(d["defect_type"] for d in active)
    severity_counts = Counter(d.get("severity", "MEDIUM") for d in active)
    by_type = []
    for dtype, count in type_counts.most_common():
        group = [d for d in active if d["defect_type"] == dtype]
        sev = Counter(d.get("severity", "MEDIUM") for d in group)
        by_type.append({
            "defect_type": dtype,
            "count": count,
            "share": round(count / len(active), 3) if active else 0.0,
            "avg_confidence": round(sum(d.get("confidence", 0) for d in group) / count, 3),
            "severities": {s: sev.get(s, 0) for s in SEVERITY_ORDER},
        })

    # Daily trend inside the window
    trend_map: Dict[str, Counter] = {}
    for offset in range(days):
        trend_map[(window_start + timedelta(days=offset)).isoformat()] = Counter()
    for d in active:
        created = _as_aware(d.get("created_at"))
        if created is None:
            continue
        key = created.date().isoformat()
        if key in trend_map:
            trend_map[key][d["defect_type"]] += 1
    trend = [{"date": k, "total": sum(v.values()), "by_type": dict(v)} for k, v in trend_map.items()]

    # Per-product breakdown
    product_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"inspections": 0, "defective": 0, "detections": Counter()})
    for i in inspections:
        name = i.get("product_name") or "Unnamed Product"
        product_stats[name]["inspections"] += 1
        if i.get("overall_outcome") == "DEFECTIVE":
            product_stats[name]["defective"] += 1
    for d in active:
        insp = insp_by_id.get(d.get("inspection_id"))
        if insp:
            product_stats[insp.get("product_name") or "Unnamed Product"]["detections"][d["defect_type"]] += 1
    by_product = []
    for name, st in product_stats.items():
        top = st["detections"].most_common(1)
        by_product.append({
            "product_name": name,
            "inspections": st["inspections"],
            "defective": st["defective"],
            "defect_rate": round(st["defective"] / st["inspections"], 3) if st["inspections"] else 0.0,
            "detections": sum(st["detections"].values()),
            "top_defect_type": top[0][0] if top else None,
        })
    by_product.sort(key=lambda p: (p["detections"], p["defect_rate"]), reverse=True)

    # Spatial hotspots per type
    hotspots = {dtype: _hotspot([d for d in active if d["defect_type"] == dtype]) for dtype in type_counts}

    # Reviewer feedback → precision estimate for the detector
    fb = Counter(d.get("reviewer_status", "PENDING") for d in detections)
    reviewed_true = fb.get("CONFIRMED", 0) + fb.get("RELABELED", 0)
    reviewed_total = reviewed_true + fb.get("REJECTED", 0)
    feedback = {
        "confirmed": fb.get("CONFIRMED", 0),
        "relabeled": fb.get("RELABELED", 0),
        "rejected": fb.get("REJECTED", 0),
        "pending": fb.get("PENDING", 0),
        "precision_estimate": round(reviewed_true / reviewed_total, 3) if reviewed_total else None,
    }

    # Throughput (edge-computing view)
    latencies = [
        (img.get("quality_metadata") or {}).get("defect_scan", {}).get("latency_ms")
        for img in (images or [])
    ]
    latencies = [l for l in latencies if isinstance(l, (int, float))]
    avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else None
    performance = {
        "frames_analyzed": len(latencies),
        "avg_latency_ms": avg_latency,
        "throughput_fps": round(1000.0 / avg_latency, 1) if avg_latency else None,
    }

    # Root-cause hints, ranked by frequency, with trend and hotspot evidence
    last7_start = now.date() - timedelta(days=6)
    prev7_start = now.date() - timedelta(days=13)
    root_causes = []
    for dtype, count in type_counts.most_common():
        group = [d for d in active if d["defect_type"] == dtype]
        recent = sum(1 for d in group if _as_aware(d.get("created_at")) and _as_aware(d["created_at"]).date() >= last7_start)
        previous = sum(
            1 for d in group
            if _as_aware(d.get("created_at")) and prev7_start <= _as_aware(d["created_at"]).date() < last7_start
        )
        evidence = [f"{count} occurrence{'s' if count != 1 else ''} ({round(count / len(active) * 100)}% of all defects)"]
        if previous and recent >= 1.5 * previous:
            evidence.append(f"Rising trend: {recent} in the last 7 days vs {previous} in the 7 days before — check recent shift, batch, or tool changes")
        elif not previous and recent >= 3:
            evidence.append(f"New pattern: {recent} occurrences in the last 7 days with none the week before")
        hs = hotspots.get(dtype, {})
        if count >= 3 and hs.get("dominant_share", 0) >= 0.5:
            evidence.append(
                f"{round(hs['dominant_share'] * 100)}% located in the {hs['dominant_region']} region — "
                "a repeated position points to a fixed contact point (fixture, guide rail, gripper)"
            )
        products = Counter(
            (insp_by_id.get(d.get("inspection_id")) or {}).get("product_name") or "Unnamed Product" for d in group
        )
        top_product, top_count = products.most_common(1)[0]
        if len(products) > 1 and top_count / count >= 0.6:
            evidence.append(f"Concentrated on '{top_product}' ({top_count}/{count}) — product-specific process issue likely")
        critical = sum(1 for d in group if d.get("severity") in ("CRITICAL", "HIGH"))
        kb = ROOT_CAUSE_KB.get(dtype, GENERIC_KB)
        root_causes.append({
            "defect_type": dtype,
            "count": count,
            "high_severity_count": critical,
            "priority": "HIGH" if critical / count >= 0.5 or dtype in ("CRACK", "DIMENSIONAL_ANOMALY") else "MEDIUM",
            "likely_causes": kb["causes"],
            "recommended_actions": kb["actions"],
            "evidence": evidence,
        })

    return {
        "window_days": days,
        "totals": {
            "inspections": total_insp,
            "defective": outcomes.get("DEFECTIVE", 0),
            "review": outcomes.get("REVIEW", 0),
            "pass": outcomes.get("PASS", 0),
            "pending": outcomes.get("PENDING", 0),
            "defect_rate": round(outcomes.get("DEFECTIVE", 0) / total_insp, 3) if total_insp else 0.0,
            "detections": len(active),
        },
        "most_frequent_type": by_type[0]["defect_type"] if by_type else None,
        "by_type": by_type,
        "by_severity": {s: severity_counts.get(s, 0) for s in SEVERITY_ORDER},
        "trend": trend,
        "by_product": by_product[:10],
        "hotspots": hotspots,
        "feedback": feedback,
        "performance": performance,
        "root_causes": root_causes,
        "known_defect_types": DEFECT_TYPES,
    }
