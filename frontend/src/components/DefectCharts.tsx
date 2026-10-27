'use client';

import React, { useState } from 'react';
import { DefectAnalytics } from '@/lib/types';
import { defectColor, defectLabel } from '@/lib/defects';

export function DefectTypeBars({ byType }: { byType: DefectAnalytics['by_type'] }) {
  if (byType.length === 0) {
    return <p className="text-xs text-[#615d59] py-10 text-center">No defects logged in this period.</p>;
  }
  const max = Math.max(...byType.map((t) => t.count), 1);
  return (
    <div className="space-y-3">
      {byType.map((t) => (
        <div key={t.defect_type} className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-2 font-semibold text-[#000000]">
              <span className="w-2.5 h-2.5 rounded-full" style={{ background: defectColor(t.defect_type) }} />
              {defectLabel(t.defect_type)}
            </span>
            <span className="text-[#615d59]">
              <b className="text-[#000000]">{t.count}</b> · {Math.round(t.share * 100)}% · avg conf {Math.round(t.avg_confidence * 100)}%
            </span>
          </div>
          <div className="w-full bg-[#f6f5f4] rounded-full h-2.5 overflow-hidden border border-[#e6e6e6]">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${(t.count / max) * 100}%`, background: defectColor(t.defect_type) }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

const SEVERITY_COLOURS: Record<string, string> = {
  CRITICAL: '#991B1B',
  HIGH: '#d9381e',
  MEDIUM: '#dd5b00',
  LOW: '#1aae39',
};

export function SeverityBreakdown({ bySeverity }: { bySeverity: Record<string, number> }) {
  const order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const total = order.reduce((s, k) => s + (bySeverity[k] || 0), 0);
  return (
    <div className="space-y-3">
      <div className="flex w-full h-4 rounded-full overflow-hidden border border-[#e6e6e6] bg-[#f6f5f4]">
        {total > 0 &&
          order.map((k) =>
            bySeverity[k] ? (
              <div
                key={k}
                title={`${k}: ${bySeverity[k]}`}
                style={{ width: `${(bySeverity[k] / total) * 100}%`, background: SEVERITY_COLOURS[k] }}
              />
            ) : null
          )}
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        {order.map((k) => (
          <div key={k} className="flex items-center justify-between px-2.5 py-1.5 rounded-md bg-[#f6f5f4] border border-[#e6e6e6]">
            <span className="flex items-center gap-1.5 text-[#31302e]">
              <span className="w-2 h-2 rounded-full" style={{ background: SEVERITY_COLOURS[k] }} />
              {k}
            </span>
            <b className="text-[#000000]">{bySeverity[k] || 0}</b>
          </div>
        ))}
      </div>
    </div>
  );
}

export function DefectTrendChart({ trend }: { trend: DefectAnalytics['trend'] }) {
  const [hover, setHover] = useState<number | null>(null);
  const types = Array.from(new Set(trend.flatMap((d) => Object.keys(d.by_type))));
  const max = Math.max(...trend.map((d) => d.total), 1);
  const W = 640;
  const H = 180;
  const pad = { l: 28, r: 8, t: 10, b: 22 };
  const plotW = W - pad.l - pad.r;
  const plotH = H - pad.t - pad.b;
  const slot = plotW / Math.max(trend.length, 1);
  const barW = Math.max(2, slot * 0.7);
  const labelEvery = Math.ceil(trend.length / 8);
  const hovered = hover !== null ? trend[hover] : null;

  return (
    <div className="space-y-2">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" onMouseLeave={() => setHover(null)}>
        {[0, 0.5, 1].map((f) => {
          const y = pad.t + plotH * (1 - f);
          return (
            <g key={f}>
              <line x1={pad.l} x2={W - pad.r} y1={y} y2={y} stroke="#e6e6e6" strokeDasharray="3 3" />
              <text x={pad.l - 6} y={y + 3} fontSize={9} textAnchor="end" fill="#615d59">
                {Math.round(max * f)}
              </text>
            </g>
          );
        })}
        {trend.map((d, i) => {
          const x = pad.l + i * slot + (slot - barW) / 2;
          let yCursor = pad.t + plotH;
          return (
            <g key={d.date} onMouseEnter={() => setHover(i)}>
              <rect x={pad.l + i * slot} y={pad.t} width={slot} height={plotH} fill={hover === i ? '#f0f7ff' : 'transparent'} />
              {types.map((t) => {
                const v = d.by_type[t] || 0;
                if (!v) return null;
                const h = (v / max) * plotH;
                yCursor -= h;
                return <rect key={t} x={x} y={yCursor} width={barW} height={h} fill={defectColor(t)} rx={1} />;
              })}
              {i % labelEvery === 0 && (
                <text x={x + barW / 2} y={H - 6} fontSize={9} textAnchor="middle" fill="#615d59">
                  {d.date.slice(5)}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#615d59] min-h-5">
        <div className="flex flex-wrap gap-3">
          {types.map((t) => (
            <span key={t} className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-sm" style={{ background: defectColor(t) }} />
              {defectLabel(t)}
            </span>
          ))}
        </div>
        {hovered && (
          <span className="font-mono">
            {hovered.date}: {hovered.total} defect{hovered.total !== 1 ? 's' : ''}
          </span>
        )}
      </div>
    </div>
  );
}

export function HotspotGrid({
  defectType,
  hotspot,
}: {
  defectType: string;
  hotspot: { grid: number[][]; dominant_region: string | null; dominant_share: number };
}) {
  const max = Math.max(...hotspot.grid.flat(), 1);
  const color = defectColor(defectType);
  return (
    <div className="space-y-1.5">
      <p className="text-[11px] font-semibold text-[#31302e]">{defectLabel(defectType)}</p>
      <div className="grid grid-cols-3 gap-0.5 w-24 h-24 p-0.5 rounded-md border border-[#e6e6e6] bg-[#f6f5f4]">
        {hotspot.grid.flat().map((v, i) => (
          <div
            key={i}
            title={`${v} defect${v !== 1 ? 's' : ''}`}
            className="rounded-sm flex items-center justify-center text-[9px] font-bold text-white"
            style={{ background: v ? color : 'transparent', opacity: v ? 0.25 + 0.75 * (v / max) : 1 }}
          >
            {v || ''}
          </div>
        ))}
      </div>
      <p className="text-[10px] text-[#615d59]">
        {hotspot.dominant_region ? `${Math.round(hotspot.dominant_share * 100)}% ${hotspot.dominant_region}` : 'no data'}
      </p>
    </div>
  );
}

export function ProductBreakdown({ byProduct }: { byProduct: DefectAnalytics['by_product'] }) {
  if (byProduct.length === 0) {
    return <p className="text-xs text-[#615d59] py-6 text-center">No products inspected in this period.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead>
          <tr className="text-[10px] font-bold text-[#615d59] uppercase tracking-wider border-b border-[#e6e6e6]">
            <th className="py-2 pr-3">Product</th>
            <th className="py-2 pr-3">Inspections</th>
            <th className="py-2 pr-3">Defects</th>
            <th className="py-2 pr-3">Top Defect</th>
            <th className="py-2 w-40">Defective Rate</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#e6e6e6]">
          {byProduct.map((p) => (
            <tr key={p.product_name}>
              <td className="py-2 pr-3 font-semibold text-[#000000]">{p.product_name}</td>
              <td className="py-2 pr-3 text-[#31302e]">{p.inspections}</td>
              <td className="py-2 pr-3 text-[#31302e]">{p.detections}</td>
              <td className="py-2 pr-3">
                {p.top_defect_type ? (
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full" style={{ background: defectColor(p.top_defect_type) }} />
                    {defectLabel(p.top_defect_type)}
                  </span>
                ) : (
                  '—'
                )}
              </td>
              <td className="py-2">
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-[#f6f5f4] rounded-full h-2 overflow-hidden border border-[#e6e6e6]">
                    <div className="h-full bg-gradient-to-r from-amber-500 to-red-500" style={{ width: `${p.defect_rate * 100}%` }} />
                  </div>
                  <span className="font-bold text-[#000000] w-9 text-right">{Math.round(p.defect_rate * 100)}%</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
