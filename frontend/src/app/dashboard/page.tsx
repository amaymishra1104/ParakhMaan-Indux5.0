'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { DashboardSummary } from '@/lib/types';
import {
  ShieldCheck, AlertTriangle, XCircle, FileText, PlusCircle,
  ArrowRight, RefreshCw, Layers, CheckCircle2, ChevronRight,
  TrendingUp, PieChart, BarChart3, Activity, Sparkles, Scale, ShieldAlert
} from 'lucide-react';

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardSummary();
      setSummary(data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !summary) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <RefreshCw className="w-8 h-8 text-[#0075de] animate-spin mb-3" />
        <p className="text-sm font-semibold text-[#000000]">Loading Legal Metrology Dashboard...</p>
      </div>
    );
  }

  const s = summary || {
    total_inspections: 0,
    compliant_count: 0,
    needs_review_count: 0,
    non_compliance_count: 0,
    draft_count: 0,
    recent_inspections: [],
    common_violations: [],
    category_distribution: []
  };

  const passPct = s.total_inspections ? Math.round((s.compliant_count / s.total_inspections) * 100) : 0;
  const reviewPct = s.total_inspections ? Math.round((s.needs_review_count / s.total_inspections) * 100) : 0;
  const nonCompPct = s.total_inspections ? Math.round((s.non_compliance_count / s.total_inspections) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-[#000000]">
              Legal Metrology Inspection Command Center
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-[#0075de] border border-blue-200">
              SIH26034 v2.4
            </span>
          </div>
          <p className="text-xs text-[#615d59] mt-0.5">
            Packaged Commodities Rules (2011) AI Compliance & Deterministic Rule Engine
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/rules"
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs font-semibold bg-white text-[#31302e] border border-[#e6e6e6] hover:bg-[#f6f5f4] transition-all shadow-xs"
          >
            <Scale className="w-4 h-4 text-[#0075de]" />
            <span>Statutory Tools & Rules</span>
          </Link>
          <Link
            href="/inspections/new"
            className="flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold bg-[#0075de] text-white hover:bg-[#005bab] transition-all shadow-xs"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Package Inspection</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Card */}
        <div className="bg-white rounded-xl border border-[#e6e6e6] p-4 elevation-0">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#615d59]">Total Audited</span>
            <div className="p-2 rounded-lg bg-[#f6f5f4] text-[#0075de]">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-[#000000] mt-2">{s.total_inspections}</p>
          <p className="text-[11px] text-[#615d59] mt-1">Packaged Commodities Ingested</p>
        </div>

        {/* Compliant Card */}
        <div className="bg-white rounded-xl border border-[#e6e6e6] p-4 elevation-0">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#166534]">Compliant (Pass)</span>
            <div className="p-2 rounded-lg bg-green-50 text-[#1aae39]">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2 mt-2">
            <p className="text-2xl font-bold text-[#166534]">{s.compliant_count}</p>
            <span className="text-xs font-bold text-[#1aae39]">{passPct}%</span>
          </div>
          <p className="text-[11px] text-[#615d59] mt-1">Full statutory compliance</p>
        </div>

        {/* Review Card */}
        <div className="bg-white rounded-xl border border-[#e6e6e6] p-4 elevation-0">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#854D0E]">Manual Review</span>
            <div className="p-2 rounded-lg bg-amber-50 text-[#dd5b00]">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2 mt-2">
            <p className="text-2xl font-bold text-[#854D0E]">{s.needs_review_count}</p>
            <span className="text-xs font-bold text-[#dd5b00]">{reviewPct}%</span>
          </div>
          <p className="text-[11px] text-[#615d59] mt-1">Low contrast / missing surfaces</p>
        </div>

        {/* Possible Non-Compliance Card */}
        <div className="bg-white rounded-xl border border-[#e6e6e6] p-4 elevation-0">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#991B1B]">Non-Compliance</span>
            <div className="p-2 rounded-lg bg-red-50 text-[#991B1B]">
              <XCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2 mt-2">
            <p className="text-2xl font-bold text-[#991B1B]">{s.non_compliance_count}</p>
            <span className="text-xs font-bold text-[#991B1B]">{nonCompPct}%</span>
          </div>
          <p className="text-[11px] text-[#615d59] mt-1">Statutory omissions (Sec 36)</p>
        </div>
      </div>

      {/* Visual Analytics & Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Chart 1: Compliance Outcome Donut & Distribution (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider flex items-center gap-1.5">
                <PieChart className="w-4 h-4 text-[#0075de]" />
                Compliance Distribution
              </h3>
              <span className="text-[10px] text-[#615d59] font-mono">Real-time</span>
            </div>

            {/* Circular Donut Visual */}
            <div className="flex flex-col items-center justify-center my-4">
              <div className="relative w-36 h-36 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  {/* Background Circle */}
                  <path
                    className="text-gray-100"
                    strokeWidth="4"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  {/* Pass Segment */}
                  <path
                    className="text-[#1aae39]"
                    strokeDasharray={`${passPct}, 100`}
                    strokeWidth="4"
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  {/* Review Segment */}
                  <path
                    className="text-[#dd5b00]"
                    strokeDasharray={`${reviewPct}, 100`}
                    strokeDashoffset={`-${passPct}`}
                    strokeWidth="4"
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  {/* Non-compliance Segment */}
                  <path
                    className="text-[#d9381e]"
                    strokeDasharray={`${nonCompPct}, 100`}
                    strokeDashoffset={`-${passPct + reviewPct}`}
                    strokeWidth="4"
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <div className="absolute flex flex-col items-center justify-center">
                  <span className="text-xl font-extrabold text-[#000000]">{passPct}%</span>
                  <span className="text-[10px] text-[#615d59] font-medium">Compliance</span>
                </div>
              </div>
            </div>

            {/* Legend & Breakdown */}
            <div className="space-y-2 mt-4 pt-3 border-t border-[#e6e6e6] text-xs">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-[#31302e]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#1aae39]" />
                  Compliant (Pass)
                </span>
                <span className="font-bold text-[#166534]">{s.compliant_count} ({passPct}%)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-[#31302e]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#dd5b00]" />
                  Needs Manual Review
                </span>
                <span className="font-bold text-[#854D0E]">{s.needs_review_count} ({reviewPct}%)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-[#31302e]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#d9381e]" />
                  Possible Non-Compliance
                </span>
                <span className="font-bold text-[#991B1B]">{s.non_compliance_count} ({nonCompPct}%)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Chart 2: Top Statutory Violations Bar Chart (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider flex items-center gap-1.5">
                <BarChart3 className="w-4 h-4 text-[#dd5b00]" />
                Top Statutory Violations & Exceptions
              </h3>
              <span className="text-[10px] text-[#615d59]">Legal Metrology Rules 2011</span>
            </div>

            {s.common_violations.length === 0 ? (
              <p className="text-xs text-[#615d59] py-12 text-center">No statutory defects logged yet.</p>
            ) : (
              <div className="space-y-3.5">
                {s.common_violations.map((viol, idx) => {
                  const maxViol = Math.max(...s.common_violations.map((v) => v.count), 1);
                  const barWidth = Math.round((viol.count / maxViol) * 100);
                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                            {viol.rule_id}
                          </span>
                          <span className="font-semibold text-[#000000]">
                            {viol.field.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                        <span className="font-bold text-[#dd5b00]">
                          {viol.count} exception{viol.count > 1 ? 's' : ''}
                        </span>
                      </div>
                      <div className="w-full bg-[#f6f5f4] rounded-full h-2.5 overflow-hidden border border-[#e6e6e6]">
                        <div
                          className="bg-gradient-to-r from-amber-500 to-red-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${barWidth}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-[#e6e6e6] flex items-center justify-between text-[11px] text-[#615d59]">
            <span>Enforcement focus area</span>
            <span className="font-semibold text-amber-800">Rule 6(1) Declarations</span>
          </div>
        </div>

        {/* Chart 3: Commodity Category Split (3 cols) */}
        <div className="lg:col-span-3 bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-[#0075de]" />
                Category Volume
              </h3>
              <span className="text-[10px] text-[#615d59]">{s.category_distribution.length} classes</span>
            </div>

            <div className="space-y-3">
              {s.category_distribution.length === 0 ? (
                <p className="text-xs text-[#615d59] py-8 text-center">No category data yet</p>
              ) : (
                s.category_distribution.map((cat) => (
                  <div key={cat.category} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-medium text-[#31302e] truncate max-w-[120px]">
                        {cat.category.replace('_', ' ')}
                      </span>
                      <span className="font-bold text-[#000000]">{cat.count}</span>
                    </div>
                    <div className="w-full bg-[#f6f5f4] rounded-full h-2 overflow-hidden border border-[#e6e6e6]">
                      <div
                        className="bg-[#0075de] h-full rounded-full"
                        style={{
                          width: `${s.total_inspections ? Math.min(100, (cat.count / s.total_inspections) * 100) : 0}%`
                        }}
                      />
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#e6e6e6] text-[11px] text-[#615d59]">
            Second Schedule commodity checks active
          </div>
        </div>
      </div>

      {/* Recent Inspections Table */}
      <div className="bg-white rounded-xl border border-[#e6e6e6] overflow-hidden elevation-0">
        <div className="p-4 border-b border-[#e6e6e6] bg-[#f6f5f4] flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-[#000000]">Recent Package Inspections</h3>
            <p className="text-xs text-[#615d59]">Latest commodities evaluated by the rule engine</p>
          </div>
          <Link
            href="/inspections"
            className="flex items-center gap-1 text-xs font-semibold text-[#0075de] hover:underline"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#f6f5f4] border-b border-[#e6e6e6] text-[11px] font-bold text-[#615d59] uppercase tracking-wider">
                <th className="py-3 px-4">Inspection #</th>
                <th className="py-3 px-4">Product / Commodity</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Surfaces</th>
                <th className="py-3 px-4">Statutory Outcome</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e6e6e6] text-xs">
              {s.recent_inspections.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-[#615d59]">
                    No inspections recorded yet. Click "New Package Inspection" or "Load Demo Data" to begin.
                  </td>
                </tr>
              ) : (
                s.recent_inspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-[#f6f5f4]/80 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-[#213183]">
                      {insp.inspection_number}
                    </td>
                    <td className="py-3 px-4 font-semibold text-[#000000]">
                      {insp.product_name || 'Packaged Commodity'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-[11px] px-2 py-0.5 rounded bg-[#f6f5f4] border border-[#e6e6e6] text-[#31302e]">
                        {insp.category.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-[#615d59]">
                      {insp.image_count || 0} surface photo{(insp.image_count || 0) > 1 ? 's' : ''}
                    </td>
                    <td className="py-3 px-4">
                      {insp.overall_outcome === 'PASS' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-[#166534]">
                          COMPLIANT
                        </span>
                      )}
                      {insp.overall_outcome === 'REVIEW' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-[#854D0E]">
                          NEEDS REVIEW
                        </span>
                      )}
                      {insp.overall_outcome === 'POSSIBLE_NON_COMPLIANCE' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-[#991B1B]">
                          NON-COMPLIANCE
                        </span>
                      )}
                      {insp.overall_outcome === 'PENDING' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-700">
                          PENDING
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        href={`/inspections/${insp.id}`}
                        className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#0075de] hover:underline"
                      >
                        <span>Audit Details</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
