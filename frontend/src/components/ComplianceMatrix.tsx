'use client';

import React, { useState } from 'react';
import { ComplianceResult } from '@/lib/types';
import { CheckCircle2, AlertTriangle, XCircle, Eye, Edit3, ShieldAlert, Check } from 'lucide-react';

interface ComplianceMatrixProps {
  results: ComplianceResult[];
  onSelectResult: (result: ComplianceResult) => void;
  selectedResultId?: string;
  onOpenReviewModal: (result: ComplianceResult) => void;
}

export default function ComplianceMatrix({
  results,
  onSelectResult,
  selectedResultId,
  onOpenReviewModal
}: ComplianceMatrixProps) {
  const [filter, setFilter] = useState<'ALL' | 'PASS' | 'REVIEW' | 'POSSIBLE_NON_COMPLIANCE'>('ALL');

  const filteredResults = results.filter((r) => {
    if (filter === 'ALL') return true;
    return r.outcome === filter;
  });

  const passCount = results.filter((r) => r.outcome === 'PASS').length;
  const reviewCount = results.filter((r) => r.outcome === 'REVIEW').length;
  const failCount = results.filter((r) => r.outcome === 'POSSIBLE_NON_COMPLIANCE').length;

  return (
    <div className="bg-white rounded-xl border border-[#e6e6e6] overflow-hidden elevation-0">
      {/* Header with Filters */}
      <div className="p-4 border-b border-[#e6e6e6] bg-[#f6f5f4] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h3 className="font-bold text-sm text-[#000000]">Statutory Compliance Evaluation Matrix</h3>
          <p className="text-xs text-[#615d59] mt-0.5">
            Deterministic evaluation against Legal Metrology (Packaged Commodities) Rules, 2011
          </p>
        </div>

        {/* Status Filter Badges */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            onClick={() => setFilter('ALL')}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
              filter === 'ALL'
                ? 'bg-[#0075de] text-white shadow-xs'
                : 'bg-white text-[#31302e] border border-[#e6e6e6] hover:bg-[#f6f5f4]'
            }`}
          >
            All ({results.length})
          </button>
          <button
            onClick={() => setFilter('PASS')}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
              filter === 'PASS'
                ? 'bg-[#166534] text-white shadow-xs'
                : 'bg-white text-[#166534] border border-green-200 hover:bg-green-50'
            }`}
          >
            Pass ({passCount})
          </button>
          <button
            onClick={() => setFilter('REVIEW')}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
              filter === 'REVIEW'
                ? 'bg-[#854D0E] text-white shadow-xs'
                : 'bg-white text-[#854D0E] border border-amber-200 hover:bg-amber-50'
            }`}
          >
            Review ({reviewCount})
          </button>
          <button
            onClick={() => setFilter('POSSIBLE_NON_COMPLIANCE')}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
              filter === 'POSSIBLE_NON_COMPLIANCE'
                ? 'bg-[#991B1B] text-white shadow-xs'
                : 'bg-white text-[#991B1B] border border-red-200 hover:bg-red-50'
            }`}
          >
            Non-Compliant ({failCount})
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#f6f5f4] border-b border-[#e6e6e6] text-[11px] font-bold text-[#615d59] uppercase tracking-wider">
              <th className="py-3 px-4">Statutory Field</th>
              <th className="py-3 px-4">Detected Value</th>
              <th className="py-3 px-4">Rule Code</th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4">Outcome</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#e6e6e6] text-xs">
            {filteredResults.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-[#615d59]">
                  No compliance results match the selected filter.
                </td>
              </tr>
            ) : (
              filteredResults.map((r) => {
                const isSelected = selectedResultId === r.id;
                return (
                  <tr
                    key={r.id}
                    onClick={() => onSelectResult(r)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-blue-50/70 border-l-4 border-l-[#0075de]'
                        : 'hover:bg-[#f6f5f4]/80'
                    }`}
                  >
                    <td className="py-3 px-4 font-semibold text-[#000000]">
                      {r.field.replace('_', ' ').toUpperCase()}
                    </td>
                    <td className="py-3 px-4 text-[#31302e] font-mono text-[11px] max-w-xs truncate" title={r.detected_value || 'Missing'}>
                      {r.normalized_value || r.detected_value || (
                        <span className="text-red-500 font-sans italic font-normal">Missing Declaration</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-[#213183] bg-[#f6f5f4] px-2 py-0.5 rounded border border-[#e6e6e6] text-[11px]">
                        {r.rule_id}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-1.5">
                        <div className="w-12 bg-[#e6e6e6] rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              (r.confidence ?? 0) === 0
                                ? 'bg-gray-300'
                                : (r.confidence ?? 0) < 0.6
                                ? 'bg-amber-500'
                                : 'bg-[#0075de]'
                            }`}
                            style={{ width: `${Math.round((r.confidence !== undefined && r.confidence !== null ? r.confidence : 0.0) * 100)}%` }}
                          />
                        </div>
                        <span className="text-[10px] font-mono text-[#615d59]">
                          {Math.round((r.confidence !== undefined && r.confidence !== null ? r.confidence : 0.0) * 100)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {r.outcome === 'PASS' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-[#166534] border border-green-200">
                          <CheckCircle2 className="w-3 h-3" />
                          COMPLIANT
                        </span>
                      )}
                      {r.outcome === 'REVIEW' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-[#854D0E] border border-amber-200">
                          <AlertTriangle className="w-3 h-3" />
                          NEEDS REVIEW
                        </span>
                      )}
                      {r.outcome === 'POSSIBLE_NON_COMPLIANCE' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-[#991B1B] border border-red-200">
                          <XCircle className="w-3 h-3" />
                          POSSIBLE NON-COMPLIANCE
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => onSelectResult(r)}
                          className="p-1 rounded-md text-[#0075de] hover:bg-blue-50 transition-colors"
                          title="View on Package Surface"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onOpenReviewModal(r)}
                          className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-[#f6f5f4] text-[#31302e] border border-[#e6e6e6] hover:bg-white hover:text-[#0075de] transition-colors"
                          title="Review / Correct Declaration"
                        >
                          Review
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
