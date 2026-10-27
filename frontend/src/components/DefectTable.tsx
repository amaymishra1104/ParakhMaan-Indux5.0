'use client';

import React, { useState } from 'react';
import { Check, X, Tag, ListChecks, RefreshCw } from 'lucide-react';
import { DefectDetection } from '@/lib/types';
import { DEFECT_TYPES, SEVERITY_STYLES, defectColor, defectLabel } from '@/lib/defects';

type FeedbackAction = 'CONFIRM' | 'REJECT' | 'RELABEL';

interface DefectTableProps {
  detections: DefectDetection[];
  selectedId?: string | null;
  onSelect?: (d: DefectDetection) => void;
  onFeedback?: (d: DefectDetection, action: FeedbackAction, defectType?: string) => Promise<void>;
  readOnly?: boolean;
  title?: string;
}

function keyMetric(d: DefectDetection): string {
  const m = d.metrics || {};
  switch (m.method) {
    case 'morphological_line_extraction':
      return `${m.length_px}px long · tortuosity ${m.tortuosity}`;
    case 'shading_anomaly':
      return `depth ${m.shading_depth} · ${(m.surface_area_ratio * 100).toFixed(1)}% area`;
    case 'cielab_colour_deviation':
      return `ΔE ${m.mean_delta_e} vs ${m.reference === 'GOLDEN_SAMPLE' ? 'golden sample' : 'surface median'}`;
    case 'golden_contour_comparison':
      return `aspect Δ ${(m.aspect_deviation * 100).toFixed(1)}% · area Δ ${(m.area_deviation * 100).toFixed(1)}%`;
    case 'contour_convexity_defect':
      return `notch ${m.notch_depth_px}px (${(m.notch_depth_ratio * 100).toFixed(1)}%)`;
    case 'yolo_onnx':
      return `model class: ${m.model_class}`;
    default:
      return '—';
  }
}

const STATUS_STYLES: Record<string, string> = {
  CONFIRMED: 'bg-green-100 text-[#166534]',
  RELABELED: 'bg-blue-100 text-[#0075de]',
  REJECTED: 'bg-gray-200 text-gray-600 line-through',
  PENDING: 'bg-[#f6f5f4] text-[#615d59]',
};

export default function DefectTable({
  detections,
  selectedId,
  onSelect,
  onFeedback,
  readOnly = false,
  title = 'Detected Defects',
}: DefectTableProps) {
  const [busyId, setBusyId] = useState<string | null>(null);
  const [relabelId, setRelabelId] = useState<string | null>(null);

  const act = async (d: DefectDetection, action: FeedbackAction, defectType?: string) => {
    if (!onFeedback || !d.id) return;
    setBusyId(d.id);
    try {
      await onFeedback(d, action, defectType);
      setRelabelId(null);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-[#e6e6e6] overflow-hidden elevation-0">
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#e6e6e6] bg-[#f6f5f4]">
        <div className="flex items-center gap-2">
          <ListChecks className="w-4 h-4 text-[#0075de]" />
          <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider">{title}</h3>
        </div>
        <span className="text-[11px] text-[#615d59]">
          {detections.filter((d) => d.reviewer_status !== 'REJECTED').length} active · {detections.length} total
        </span>
      </div>

      {detections.length === 0 ? (
        <p className="py-10 text-center text-xs text-[#615d59]">No defects detected on the analysed surfaces.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#f6f5f4] border-b border-[#e6e6e6] text-[10px] font-bold text-[#615d59] uppercase tracking-wider">
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Conf.</th>
                <th className="py-2.5 px-3">Measurement</th>
                <th className="py-2.5 px-3">Source</th>
                <th className="py-2.5 px-3">Review</th>
                {!readOnly && <th className="py-2.5 px-3 text-right">Feedback</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e6e6e6] text-xs">
              {detections.map((d, idx) => {
                const isSelected = !!selectedId && selectedId === d.id;
                const status = d.reviewer_status || 'PENDING';
                const busy = busyId === d.id;
                return (
                  <tr
                    key={d.id || idx}
                    onClick={() => onSelect?.(d)}
                    className={`transition-colors ${onSelect ? 'cursor-pointer' : ''} ${
                      isSelected ? 'bg-[#f0f7ff]' : 'hover:bg-[#f6f5f4]/80'
                    }`}
                  >
                    <td className="py-2.5 px-3">
                      <span className="flex items-center gap-2 font-semibold text-[#000000]">
                        <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: defectColor(d.defect_type) }} />
                        {defectLabel(d.defect_type)}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${SEVERITY_STYLES[d.severity] || 'bg-gray-100 text-gray-700 border-gray-200'}`}>
                        {d.severity}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[#31302e]">{Math.round(d.confidence * 100)}%</td>
                    <td className="py-2.5 px-3 text-[11px] text-[#31302e]">{keyMetric(d)}</td>
                    <td className="py-2.5 px-3 text-[11px] text-[#615d59]">
                      {d.detector}
                      {d.frame_index !== null && d.frame_index !== undefined && (
                        <span className="block font-mono text-[10px]">
                          frame {d.frame_index}
                          {d.frame_timestamp_ms ? ` · ${(d.frame_timestamp_ms / 1000).toFixed(1)}s` : ''}
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${STATUS_STYLES[status] || STATUS_STYLES.PENDING}`}>
                        {status}
                      </span>
                    </td>
                    {!readOnly && (
                      <td className="py-2.5 px-3 text-right" onClick={(e) => e.stopPropagation()}>
                        {busy ? (
                          <RefreshCw className="w-3.5 h-3.5 text-[#0075de] animate-spin inline-block" />
                        ) : relabelId === d.id ? (
                          <select
                            autoFocus
                            defaultValue=""
                            onChange={(e) => e.target.value && act(d, 'RELABEL', e.target.value)}
                            onBlur={() => setRelabelId(null)}
                            className="px-2 py-1 border border-[#e6e6e6] rounded-md text-[11px] bg-white"
                          >
                            <option value="" disabled>Relabel as…</option>
                            {DEFECT_TYPES.filter((t) => t !== d.defect_type).map((t) => (
                              <option key={t} value={t}>{defectLabel(t)}</option>
                            ))}
                          </select>
                        ) : (
                          <div className="inline-flex items-center gap-1">
                            <button
                              type="button"
                              title="Confirm defect (saved as a training sample)"
                              onClick={() => act(d, 'CONFIRM')}
                              disabled={status === 'CONFIRMED'}
                              className="p-1.5 rounded-md border border-[#e6e6e6] text-[#1aae39] hover:bg-green-50 disabled:opacity-30"
                            >
                              <Check className="w-3.5 h-3.5" />
                            </button>
                            <button
                              type="button"
                              title="Reject as false positive (saved as a hard negative)"
                              onClick={() => act(d, 'REJECT')}
                              disabled={status === 'REJECTED'}
                              className="p-1.5 rounded-md border border-[#e6e6e6] text-[#991B1B] hover:bg-red-50 disabled:opacity-30"
                            >
                              <X className="w-3.5 h-3.5" />
                            </button>
                            <button
                              type="button"
                              title="Relabel defect type"
                              onClick={() => setRelabelId(d.id || null)}
                              className="p-1.5 rounded-md border border-[#e6e6e6] text-[#0075de] hover:bg-[#f0f7ff]"
                            >
                              <Tag className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
