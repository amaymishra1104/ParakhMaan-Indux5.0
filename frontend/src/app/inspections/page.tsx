'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Inspection } from '@/lib/types';
import {
  Search, PlusCircle, Filter, FileText, CheckCircle2,
  AlertTriangle, XCircle, ChevronRight, RefreshCw
} from 'lucide-react';
import { formatDate } from '@/lib/formatters';

export default function InspectionsListPage() {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [outcomeFilter, setOutcomeFilter] = useState('');

  useEffect(() => {
    fetchList();
  }, [outcomeFilter]);

  const fetchList = async () => {
    setLoading(true);
    try {
      const data = await api.listInspections({
        outcome: outcomeFilter || undefined,
        search: search || undefined
      });
      setInspections(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchList();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-[#000000]">
            Legal Metrology Inspections
          </h1>
          <p className="text-xs text-[#615d59] mt-0.5">
            Full registry of audited packaged commodities and compliance certificates
          </p>
        </div>

        <Link
          href="/inspections/new"
          className="flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold bg-[#0075de] text-white hover:bg-[#005bab] transition-all shadow-xs self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Inspection</span>
        </Link>
      </div>

      {/* Filters Bar */}
      <div className="bg-white rounded-xl border border-[#e6e6e6] p-4 elevation-0 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="flex-1 flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#615d59] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by product name, brand, or inspection #..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs border border-[#e6e6e6] rounded-md focus:outline-none focus:border-[#0075de] bg-[#f6f5f4]"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-[#f6f5f4] text-[#31302e] border border-[#e6e6e6] rounded-md text-xs font-semibold hover:bg-white transition-colors"
          >
            Search
          </button>
        </form>

        {/* Status Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          <button
            onClick={() => setOutcomeFilter('')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap ${
              outcomeFilter === ''
                ? 'bg-[#0075de] text-white'
                : 'bg-[#f6f5f4] text-[#31302e] hover:bg-[#e6e6e6]'
            }`}
          >
            All Statuses
          </button>
          <button
            onClick={() => setOutcomeFilter('PASS')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap ${
              outcomeFilter === 'PASS'
                ? 'bg-[#166534] text-white'
                : 'bg-[#f6f5f4] text-[#166534] hover:bg-green-50'
            }`}
          >
            Compliant
          </button>
          <button
            onClick={() => setOutcomeFilter('REVIEW')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap ${
              outcomeFilter === 'REVIEW'
                ? 'bg-[#854D0E] text-white'
                : 'bg-[#f6f5f4] text-[#854D0E] hover:bg-amber-50'
            }`}
          >
            Review Queue
          </button>
          <button
            onClick={() => setOutcomeFilter('POSSIBLE_NON_COMPLIANCE')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all whitespace-nowrap ${
              outcomeFilter === 'POSSIBLE_NON_COMPLIANCE'
                ? 'bg-[#991B1B] text-white'
                : 'bg-[#f6f5f4] text-[#991B1B] hover:bg-red-50'
            }`}
          >
            Non-Compliance
          </button>
        </div>
      </div>

      {/* Table List */}
      <div className="bg-white rounded-xl border border-[#e6e6e6] overflow-hidden elevation-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#f6f5f4] border-b border-[#e6e6e6] text-[11px] font-bold text-[#615d59] uppercase tracking-wider">
                <th className="py-3 px-4">Inspection #</th>
                <th className="py-3 px-4">Product Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Surfaces</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Outcome</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e6e6e6] text-xs">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-[#615d59]">
                    <RefreshCw className="w-6 h-6 text-[#0075de] animate-spin mx-auto mb-2" />
                    Loading inspections...
                  </td>
                </tr>
              ) : inspections.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-[#615d59]">
                    No inspections found. Try adjusting filters or create a new inspection.
                  </td>
                </tr>
              ) : (
                inspections.map((insp) => (
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
                      {insp.image_count || 0} photo{(insp.image_count || 0) > 1 ? 's' : ''}
                    </td>
                    <td className="py-3 px-4 text-[#615d59] font-mono text-[11px]">
                      {formatDate(insp.created_at)}
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
                        className="inline-flex items-center gap-1 px-3 py-1 bg-[#f6f5f4] text-[#0075de] hover:bg-white border border-[#e6e6e6] rounded-md text-[11px] font-semibold transition-colors"
                      >
                        <span>Open Details</span>
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
