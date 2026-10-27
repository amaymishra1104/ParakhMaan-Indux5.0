'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { defectApi } from '@/lib/api';
import { DefectAnalytics, DefectLogItem } from '@/lib/types';
import { DEFECT_TYPES, SEVERITY_STYLES, defectColor, defectLabel } from '@/lib/defects';
import { formatDateTime } from '@/lib/formatters';
import {
  DefectTypeBars, SeverityBreakdown, DefectTrendChart, HotspotGrid, ProductBreakdown
} from '@/components/DefectCharts';
import {
  BarChart3, RefreshCw, ScanSearch, AlertOctagon, Activity, Gauge, Target, Lightbulb,
  TrendingUp, Grid3x3, Package, ListChecks, ChevronRight, PieChart
} from 'lucide-react';

const LOG_PAGE = 25;

export default function DefectAnalyticsPage() {
  const [days, setDays] = useState(30);
  const [product, setProduct] = useState('');
  const [data, setData] = useState<DefectAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  const [logFilters, setLogFilters] = useState({ defect_type: '', severity: '', reviewer_status: '' });
  const [log, setLog] = useState<{ total: number; items: DefectLogItem[] }>({ total: 0, items: [] });
  const [logLoading, setLogLoading] = useState(false);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      setData(await defectApi.getAnalytics({ days, product: product || undefined }));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadLog = async (offset: number) => {
    setLogLoading(true);
    try {
      const res = await defectApi.getLog({ ...logFilters, product: product || undefined, limit: LOG_PAGE, offset });
      setLog((prev) => (offset === 0 ? res : { total: res.total, items: [...prev.items, ...res.items] }));
    } catch (e) {
      console.error(e);
    } finally {
      setLogLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [days, product]);

  useEffect(() => {
    loadLog(0);
  }, [logFilters, product]);

  if (loading && !data) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <RefreshCw className="w-8 h-8 text-[#0075de] animate-spin mb-3" />
        <p className="text-sm font-semibold text-[#000000]">Loading defect analytics…</p>
      </div>
    );
  }
  if (!data) {
    return (
      <div className="bg-white rounded-xl border border-[#e6e6e6] p-12 text-center text-xs text-[#615d59]">
        Analytics unavailable. Is the backend running?
      </div>
    );
  }

  const t = data.totals;
  const kpis = [
    { label: 'Products Inspected', value: t.inspections, sub: `${t.pass} pass · ${t.review} review`, icon: ScanSearch, tone: 'text-[#0075de] bg-[#f6f5f4]' },
    { label: 'Defective Rate', value: `${Math.round(t.defect_rate * 100)}%`, sub: `${t.defective} rejected / rework`, icon: AlertOctagon, tone: 'text-[#991B1B] bg-red-50' },
    { label: 'Defects Logged', value: t.detections, sub: data.most_frequent_type ? `Most frequent: ${defectLabel(data.most_frequent_type)}` : 'None yet', icon: Activity, tone: 'text-[#dd5b00] bg-amber-50' },
    {
      label: 'Edge Performance',
      value: data.performance.avg_latency_ms !== null ? `${data.performance.avg_latency_ms} ms` : '—',
      sub: data.performance.throughput_fps ? `≈ ${data.performance.throughput_fps} FPS · ${data.performance.frames_analyzed} frames` : 'No scans',
      icon: Gauge,
      tone: 'text-[#2a9d99] bg-teal-50',
    },
    {
      label: 'Detector Precision',
      value: data.feedback.precision_estimate !== null ? `${Math.round(data.feedback.precision_estimate * 100)}%` : '—',
      sub: `${data.feedback.confirmed + data.feedback.relabeled} confirmed · ${data.feedback.rejected} rejected`,
      icon: Target,
      tone: 'text-[#6b21a8] bg-purple-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-[#000000]">Defect Analytics &amp; Root-Cause Insights</h1>
          <p className="text-xs text-[#615d59] mt-0.5">
            Frequency, trends, locations and likely causes of product defects for process improvement
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <select
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            className="px-3 py-2 border border-[#e6e6e6] rounded-full bg-white font-semibold text-[#31302e]"
          >
            <option value="">All products</option>
            {data.by_product.map((p) => (
              <option key={p.product_name} value={p.product_name}>{p.product_name}</option>
            ))}
          </select>
          <div className="flex items-center rounded-full border border-[#e6e6e6] bg-white p-0.5">
            {[7, 30, 90].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDays(d)}
                className={`px-3 py-1.5 rounded-full font-semibold transition-colors ${
                  days === d ? 'bg-[#0075de] text-white' : 'text-[#31302e] hover:bg-[#f6f5f4]'
                }`}
              >
                {d}d
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={loadAnalytics}
            className="p-2 rounded-full bg-white border border-[#e6e6e6] hover:bg-[#f6f5f4]"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 text-[#0075de] ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {kpis.map((k) => {
          const Icon = k.icon;
          return (
            <div key={k.label} className="bg-white rounded-xl border border-[#e6e6e6] p-4 elevation-0">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-[#615d59]">{k.label}</span>
                <div className={`p-2 rounded-lg ${k.tone}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <p className="text-2xl font-bold text-[#000000] mt-2">{k.value}</p>
              <p className="text-[11px] text-[#615d59] mt-1 truncate">{k.sub}</p>
            </div>
          );
        })}
      </div>

      {/* Frequency + severity */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0">
          <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider flex items-center gap-1.5 mb-4">
            <BarChart3 className="w-4 h-4 text-[#dd5b00]" />
            Defect Frequency by Type
          </h3>
          <DefectTypeBars byType={data.by_type} />
        </div>
        <div className="lg:col-span-5 bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0">
          <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider flex items-center gap-1.5 mb-4">
            <PieChart className="w-4 h-4 text-[#0075de]" />
            Severity Distribution
          </h3>
          <SeverityBreakdown bySeverity={data.by_severity} />
        </div>
      </div>

      {/* Trend */}
      <div className="bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0">
        <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider flex items-center gap-1.5 mb-4">
          <TrendingUp className="w-4 h-4 text-[#0075de]" />
          Daily Defect Trend ({data.window_days} days)
        </h3>
        <DefectTrendChart trend={data.trend} />
      </div>

      {/* Root causes */}
      <div className="bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0">
        <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider flex items-center gap-1.5 mb-4">
          <Lightbulb className="w-4 h-4 text-[#dd5b00]" />
          Root-Cause Analysis Hints
        </h3>
        {data.root_causes.length === 0 ? (
          <p className="text-xs text-[#615d59] py-4 text-center">Root-cause hints appear once defects are logged.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {data.root_causes.map((rc) => (
              <div key={rc.defect_type} className="rounded-lg border border-[#e6e6e6] p-4 bg-[#f6f5f4]/60 space-y-2.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2 font-bold text-[#000000]">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ background: defectColor(rc.defect_type) }} />
                    {defectLabel(rc.defect_type)}
                    <span className="font-normal text-[#615d59]">× {rc.count}</span>
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      rc.priority === 'HIGH' ? 'bg-red-100 text-[#991B1B]' : 'bg-amber-100 text-[#854D0E]'
                    }`}
                  >
                    {rc.priority} PRIORITY
                  </span>
                </div>
                {rc.evidence.length > 0 && (
                  <ul className="space-y-1 text-[11px] text-[#213183]">
                    {rc.evidence.map((e) => (
                      <li key={e} className="flex gap-1.5">
                        <span>•</span>
                        <span>{e}</span>
                      </li>
                    ))}
                  </ul>
                )}
                <div>
                  <p className="text-[10px] font-bold uppercase text-[#615d59] mb-0.5">Likely causes</p>
                  <ul className="list-disc pl-4 space-y-0.5 text-[#31302e]">
                    {rc.likely_causes.map((c) => (
                      <li key={c}>{c}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase text-[#615d59] mb-0.5">Recommended actions</p>
                  <ul className="space-y-0.5 text-[#166534]">
                    {rc.recommended_actions.map((a) => (
                      <li key={a}>→ {a}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Hotspots + products */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0">
          <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider flex items-center gap-1.5 mb-1">
            <Grid3x3 className="w-4 h-4 text-[#0075de]" />
            Defect Location Hotspots
          </h3>
          <p className="text-[11px] text-[#615d59] mb-4">Where on the product each defect type appears (3×3 zones)</p>
          {Object.keys(data.hotspots).length === 0 ? (
            <p className="text-xs text-[#615d59] py-6 text-center">No location data yet.</p>
          ) : (
            <div className="flex flex-wrap gap-5">
              {Object.entries(data.hotspots).map(([type, hs]) => (
                <HotspotGrid key={type} defectType={type} hotspot={hs} />
              ))}
            </div>
          )}
        </div>
        <div className="lg:col-span-7 bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0">
          <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider flex items-center gap-1.5 mb-4">
            <Package className="w-4 h-4 text-[#0075de]" />
            Per-Product Breakdown
          </h3>
          <ProductBreakdown byProduct={data.by_product} />
        </div>
      </div>

      {/* Detection log */}
      <div className="bg-white rounded-xl border border-[#e6e6e6] overflow-hidden elevation-0">
        <div className="p-4 border-b border-[#e6e6e6] bg-[#f6f5f4] flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div className="flex items-center gap-2">
            <ListChecks className="w-4 h-4 text-[#0075de]" />
            <div>
              <h3 className="font-bold text-sm text-[#000000]">Defect Log</h3>
              <p className="text-xs text-[#615d59]">{log.total} logged detection{log.total !== 1 ? 's' : ''}</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <select
              value={logFilters.defect_type}
              onChange={(e) => setLogFilters((f) => ({ ...f, defect_type: e.target.value }))}
              className="px-2.5 py-1.5 border border-[#e6e6e6] rounded-md bg-white"
            >
              <option value="">All types</option>
              {DEFECT_TYPES.map((d) => (
                <option key={d} value={d}>{defectLabel(d)}</option>
              ))}
            </select>
            <select
              value={logFilters.severity}
              onChange={(e) => setLogFilters((f) => ({ ...f, severity: e.target.value }))}
              className="px-2.5 py-1.5 border border-[#e6e6e6] rounded-md bg-white"
            >
              <option value="">All severities</option>
              {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <select
              value={logFilters.reviewer_status}
              onChange={(e) => setLogFilters((f) => ({ ...f, reviewer_status: e.target.value }))}
              className="px-2.5 py-1.5 border border-[#e6e6e6] rounded-md bg-white"
            >
              <option value="">All review states</option>
              {['PENDING', 'CONFIRMED', 'RELABELED', 'REJECTED'].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#f6f5f4] border-b border-[#e6e6e6] text-[10px] font-bold text-[#615d59] uppercase tracking-wider">
                <th className="py-2.5 px-4">Time</th>
                <th className="py-2.5 px-4">Inspection</th>
                <th className="py-2.5 px-4">Product / Batch</th>
                <th className="py-2.5 px-4">Type</th>
                <th className="py-2.5 px-4">Severity</th>
                <th className="py-2.5 px-4">Conf.</th>
                <th className="py-2.5 px-4">Review</th>
                <th className="py-2.5 px-4 text-right" />
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e6e6e6] text-xs">
              {log.items.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-[#615d59]">
                    {logLoading ? 'Loading…' : 'No detections match these filters.'}
                  </td>
                </tr>
              ) : (
                log.items.map((item) => (
                  <tr key={item.id} className="hover:bg-[#f6f5f4]/80">
                    <td className="py-2.5 px-4 text-[#615d59] font-mono text-[11px]">{formatDateTime(item.created_at)}</td>
                    <td className="py-2.5 px-4 font-mono font-bold text-[#213183]">{item.inspection_number}</td>
                    <td className="py-2.5 px-4">
                      <span className="font-semibold text-[#000000]">{item.product_name || 'Unnamed'}</span>
                      {item.batch && <span className="text-[#615d59]"> · {item.batch}</span>}
                    </td>
                    <td className="py-2.5 px-4">
                      <span className="flex items-center gap-1.5 font-semibold">
                        <span className="w-2 h-2 rounded-full" style={{ background: defectColor(item.defect_type) }} />
                        {defectLabel(item.defect_type)}
                      </span>
                    </td>
                    <td className="py-2.5 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${SEVERITY_STYLES[item.severity] || ''}`}>
                        {item.severity}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 font-mono">{Math.round(item.confidence * 100)}%</td>
                    <td className="py-2.5 px-4 text-[11px] text-[#615d59]">{item.reviewer_status}</td>
                    <td className="py-2.5 px-4 text-right">
                      <Link
                        href={`/defects/${item.inspection_id}`}
                        className="inline-flex items-center gap-0.5 text-[11px] font-semibold text-[#0075de] hover:underline"
                      >
                        Open <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {log.items.length < log.total && (
          <div className="p-3 border-t border-[#e6e6e6] text-center">
            <button
              type="button"
              onClick={() => loadLog(log.items.length)}
              disabled={logLoading}
              className="text-xs font-semibold text-[#0075de] hover:underline disabled:opacity-50"
            >
              {logLoading ? 'Loading…' : `Load more (${log.total - log.items.length} remaining)`}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
