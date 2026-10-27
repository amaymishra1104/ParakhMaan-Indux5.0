'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import {
  Scale, BookOpen, ShieldCheck, Calculator, Search, Filter,
  CheckCircle2, AlertTriangle, XCircle, Info, ExternalLink,
  Layers, Package, Ruler, ArrowRight, RefreshCw, FileText
} from 'lucide-react';

export default function StatutoryRulesPage() {
  const [activeTab, setActiveTab] = useState<'RULES' | 'MPE' | 'SAMPLING' | 'SCHEDULES' | 'PDP'>('RULES');

  // Rules Explorer State
  const [rulesData, setRulesData] = useState<any>({ rules: [], sources: [] });
  const [loadingRules, setLoadingRules] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLayer, setSelectedLayer] = useState('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');

  // MPE Calculator State
  const [mpeQty, setMpeQty] = useState<number>(500);
  const [mpeUnit, setMpeUnit] = useState<string>('g');
  const [mpeResult, setMpeResult] = useState<any>(null);

  // Lot Sampling State
  const [lotSize, setLotSize] = useState<number>(500);
  const [sampleDeclaredQty, setSampleDeclaredQty] = useState<number>(500);
  const [sampleUnit, setSampleUnit] = useState<string>('g');
  const [sampleWeightsText, setSampleWeightsText] = useState<string>(
    '502.0, 500.5, 501.5, 500.0, 498.0, 503.0, 502.0, 502.5, 501.0, 500.0, 499.5, 502.0, 501.0, 500.5, 499.0, 503.0, 502.0, 501.5, 500.0, 502.0, 501.0, 500.5, 499.0, 503.0, 502.0, 501.0, 500.0, 502.5, 501.0, 500.5, 502.0, 501.5'
  );
  const [samplingResult, setSamplingResult] = useState<any>(null);

  // Second Schedule State
  const [schedulesData, setSchedulesData] = useState<any>(null);
  const [selectedCommodity, setSelectedCommodity] = useState<string>('BISCUITS');
  const [packCheckQty, setPackCheckQty] = useState<number>(100);
  const [packCheckUnit, setPackCheckUnit] = useState<string>('g');
  const [packCheckResult, setPackCheckResult] = useState<any>(null);

  // PDP Font Calculator State
  const [pdpShape, setPdpShape] = useState<string>('RECTANGULAR');
  const [pdpHeight, setPdpHeight] = useState<number>(15);
  const [pdpWidth, setPdpWidth] = useState<number>(10);
  const [pdpDepth, setPdpDepth] = useState<number>(5);
  const [pdpResult, setPdpResult] = useState<any>(null);

  useEffect(() => {
    loadRules();
    loadSchedules();
    handleCalculateMPE(500, 'g');
    handleCalculatePDP();
  }, []);

  const loadRules = async () => {
    setLoadingRules(true);
    try {
      const data = await api.getRulesDatabase();
      setRulesData(data);
    } catch (err) {
      console.error('Error loading rules:', err);
    } finally {
      setLoadingRules(false);
    }
  };

  const loadSchedules = async () => {
    try {
      const data = await api.getSchedules();
      setSchedulesData(data);
    } catch (err) {
      console.error('Error loading schedules:', err);
    }
  };

  const handleCalculateMPE = async (qty: number, unit: string) => {
    try {
      const res = await api.calculateMPE(qty, unit);
      setMpeResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunSamplingEvaluation = async () => {
    try {
      const weights = sampleWeightsText
        .split(',')
        .map((w) => parseFloat(w.trim()))
        .filter((w) => !isNaN(w));

      const res = await api.evaluateLotSampling({
        lot_size: lotSize,
        declared_quantity: sampleDeclaredQty,
        unit: sampleUnit,
        measured_weights: weights,
      });
      setSamplingResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  const handleValidatePackSize = () => {
    if (!schedulesData?.commodities?.[selectedCommodity]) return;
    const entry = schedulesData.commodities[selectedCommodity];
    let qty_g = packCheckQty;
    if (['kg', 'l', 'litre'].includes(packCheckUnit.toLowerCase())) {
      qty_g = packCheckQty * 1000;
    }
    const isStandard = entry.permitted_mass_grams.some((p: number) => Math.abs(p - qty_g) < 0.01);
    setPackCheckResult({
      is_standard: isStandard,
      commodity_name: entry.name,
      declared: `${packCheckQty} ${packCheckUnit}`,
      permitted_sizes: entry.permitted_mass_grams,
      legal_note: entry.legal_note,
    });
  };

  const handleCalculatePDP = async () => {
    try {
      const res = await api.calculatePDPFont({
        package_shape: pdpShape,
        height_cm: pdpHeight,
        width_cm: pdpWidth,
        depth_or_diameter_cm: pdpDepth,
      });
      setPdpResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  // Filter rules
  const filteredRules = (rulesData.rules || []).filter((r: any) => {
    const matchSearch =
      !searchTerm ||
      r.rule_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.requirement?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.what_to_detect?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchLayer = selectedLayer === 'ALL' || r.layer === selectedLayer;
    const matchSeverity = selectedSeverity === 'ALL' || r.severity === selectedSeverity;
    return matchSearch && matchLayer && matchSeverity;
  });

  const allLayers = Array.from(new Set((rulesData.rules || []).map((r: any) => r.layer))).filter(Boolean);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-xl border border-[#e6e6e6] p-6 elevation-0">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#e6f2ff] text-[#0075de] border border-blue-200">
                SIH26034 STATUTORY ARCHITECTURE
              </span>
              <span className="text-xs text-[#615d59]">As of 2026-09-08 (G.S.R. 418(E) Third Amendment)</span>
            </div>
            <h1 className="text-xl font-bold text-[#000000]">
              Legal Metrology Statutory Rule Book & Inspector Engine
            </h1>
            <p className="text-xs text-[#615d59] mt-1 max-w-3xl">
              Deterministic statutory rules, tolerance matrices, Second Schedule permitted pack sizes, and First Schedule Maximum Permissible Error (MPE) calculations derived from the Legal Metrology (Packaged Commodities) Rules, 2011 with all Gazette Amendments.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('MPE')}
              className="flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-semibold bg-[#0075de] text-white hover:bg-[#005bab] transition-all shadow-xs"
            >
              <Calculator className="w-4 h-4" />
              <span>Launch Field Calculators</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 mt-6 border-b border-[#e6e6e6] overflow-x-auto pb-0.5">
          <button
            onClick={() => setActiveTab('RULES')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all shrink-0 ${
              activeTab === 'RULES'
                ? 'border-[#0075de] text-[#0075de]'
                : 'border-transparent text-[#615d59] hover:text-[#000000]'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Statutory Rule Catalog (40+ Rules)</span>
          </button>

          <button
            onClick={() => setActiveTab('MPE')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all shrink-0 ${
              activeTab === 'MPE'
                ? 'border-[#0075de] text-[#0075de]'
                : 'border-transparent text-[#615d59] hover:text-[#000000]'
            }`}
          >
            <Scale className="w-4 h-4" />
            <span>First Schedule MPE Calculator (Rule 22)</span>
          </button>

          <button
            onClick={() => setActiveTab('SAMPLING')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all shrink-0 ${
              activeTab === 'SAMPLING'
                ? 'border-[#0075de] text-[#0075de]'
                : 'border-transparent text-[#615d59] hover:text-[#000000]'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Fifth Schedule Lot Sampling Protocol (Rule 19)</span>
          </button>

          <button
            onClick={() => setActiveTab('SCHEDULES')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all shrink-0 ${
              activeTab === 'SCHEDULES'
                ? 'border-[#0075de] text-[#0075de]'
                : 'border-transparent text-[#615d59] hover:text-[#000000]'
            }`}
          >
            <Package className="w-4 h-4" />
            <span>Second Schedule Standard Pack Sizes (Rule 5)</span>
          </button>

          <button
            onClick={() => setActiveTab('PDP')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all shrink-0 ${
              activeTab === 'PDP'
                ? 'border-[#0075de] text-[#0075de]'
                : 'border-transparent text-[#615d59] hover:text-[#000000]'
            }`}
          >
            <Ruler className="w-4 h-4" />
            <span>Rule 7 PDP & Font Area Standards</span>
          </button>
        </div>
      </div>

      {/* TAB 1: RULES CATALOG */}
      {activeTab === 'RULES' && (
        <div className="space-y-4">
          {/* Filter Toolbar */}
          <div className="bg-white rounded-xl border border-[#e6e6e6] p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-[#a39e98] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search rule code, declaration field, or requirement..."
                className="w-full pl-9 pr-4 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-[#f6f5f4] focus:bg-white focus:outline-hidden focus:border-[#0075de]"
              />
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              {/* Layer Filter */}
              <select
                value={selectedLayer}
                onChange={(e) => setSelectedLayer(e.target.value)}
                className="px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-white focus:outline-hidden"
              >
                <option value="ALL">All Statutory Layers</option>
                {allLayers.map((layer: any) => (
                  <option key={layer} value={layer}>
                    Layer: {layer}
                  </option>
                ))}
              </select>

              {/* Severity Filter */}
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-white focus:outline-hidden"
              >
                <option value="ALL">All Severities</option>
                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
              </select>
            </div>
          </div>

          {/* Rules Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {loadingRules ? (
              <div className="col-span-full py-16 text-center text-xs text-[#615d59]">
                <RefreshCw className="w-6 h-6 animate-spin text-[#0075de] mx-auto mb-2" />
                Loading Official Rule Book Architecture...
              </div>
            ) : filteredRules.length === 0 ? (
              <div className="col-span-full py-16 text-center text-xs text-[#615d59]">
                No rules match the selected filters.
              </div>
            ) : (
              filteredRules.map((rule: any) => (
                <div
                  key={rule.rule_id}
                  className="bg-white rounded-xl border border-[#e6e6e6] p-4.5 flex flex-col justify-between hover:border-[#0075de]/50 transition-all elevation-0"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-xs font-bold text-[#0075de] bg-blue-50 px-2.5 py-0.5 rounded border border-blue-100">
                        {rule.rule_id}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          rule.severity === 'CRITICAL'
                            ? 'bg-red-100 text-[#991B1B]'
                            : rule.severity === 'HIGH'
                            ? 'bg-amber-100 text-[#854D0E]'
                            : 'bg-blue-100 text-[#0075de]'
                        }`}
                      >
                        {rule.severity}
                      </span>
                    </div>

                    <h3 className="font-bold text-xs text-[#000000] mb-1">{rule.requirement}</h3>
                    <p className="text-[11px] text-[#615d59] leading-relaxed mb-3">
                      {rule.what_to_detect}
                    </p>
                  </div>

                  <div className="border-t border-[#e6e6e6] pt-2.5 mt-2 space-y-1 text-[10px] text-[#615d59]">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">Layer:</span>
                      <span className="font-mono text-[#31302e]">{rule.layer}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">Validation:</span>
                      <span className="font-mono text-[#31302e]">{rule.validation_logic}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">Source Gazette:</span>
                      <span className="font-mono text-[#0075de]">{rule.source_ids}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* TAB 2: MPE CALCULATOR */}
      {activeTab === 'MPE' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-5 bg-white rounded-xl border border-[#e6e6e6] p-6 space-y-4">
            <h2 className="font-bold text-sm text-[#000000] flex items-center gap-2">
              <Scale className="w-4 h-4 text-[#0075de]" />
              <span>Statutory Maximum Permissible Error (MPE) Input</span>
            </h2>
            <p className="text-xs text-[#615d59]">
              Enter the declared quantity on the package to calculate the legal tolerance band defined under the First Schedule of PCR 2011.
            </p>

            <div>
              <label className="block text-xs font-semibold text-[#000000] mb-1">Declared Quantity</label>
              <input
                type="number"
                value={mpeQty}
                onChange={(e) => {
                  const val = parseFloat(e.target.value) || 0;
                  setMpeQty(val);
                  handleCalculateMPE(val, mpeUnit);
                }}
                className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-[#f6f5f4] focus:bg-white focus:outline-hidden font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#000000] mb-1">Unit of Measure</label>
              <select
                value={mpeUnit}
                onChange={(e) => {
                  setMpeUnit(e.target.value);
                  handleCalculateMPE(mpeQty, e.target.value);
                }}
                className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-white focus:outline-hidden"
              >
                <option value="g">Grams (g)</option>
                <option value="kg">Kilograms (kg)</option>
                <option value="ml">Millilitres (ml)</option>
                <option value="L">Litres (L)</option>
              </select>
            </div>

            {/* Quick Presets */}
            <div className="pt-2">
              <p className="text-[11px] font-semibold text-[#615d59] mb-1.5">Common Pack Presets:</p>
              <div className="flex items-center gap-1.5 flex-wrap">
                {[
                  { q: 50, u: 'g' },
                  { q: 100, u: 'g' },
                  { q: 250, u: 'g' },
                  { q: 500, u: 'g' },
                  { q: 1, u: 'kg' },
                  { q: 5, u: 'kg' },
                  { q: 200, u: 'ml' },
                  { q: 1, u: 'L' },
                ].map((p) => (
                  <button
                    key={`${p.q}${p.u}`}
                    onClick={() => {
                      setMpeQty(p.q);
                      setMpeUnit(p.u);
                      handleCalculateMPE(p.q, p.u);
                    }}
                    className="px-2.5 py-1 rounded bg-[#f6f5f4] hover:bg-[#e6e6e6] border border-[#e6e6e6] text-[11px] font-mono text-[#31302e]"
                  >
                    {p.q} {p.u}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* MPE Output Card */}
          <div className="lg:col-span-7 bg-white rounded-xl border border-[#e6e6e6] p-6 flex flex-col justify-between">
            {mpeResult ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-[#e6e6e6]">
                  <div>
                    <h3 className="font-bold text-sm text-[#000000]">Statutory Tolerance Matrix</h3>
                    <p className="text-xs text-[#0075de] font-mono mt-0.5">{mpeResult.tier_description}</p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-[#166534] border border-green-200">
                    FIRST SCHEDULE COMPLIANT
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="p-3 bg-[#f6f5f4] rounded-lg border border-[#e6e6e6]">
                    <p className="text-[10px] text-[#615d59] uppercase font-semibold">Declared Quantity</p>
                    <p className="text-sm font-bold font-mono text-[#000000] mt-1">
                      {mpeResult.declared_quantity_base} {mpeResult.base_unit}
                    </p>
                  </div>

                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-[10px] text-[#0075de] uppercase font-semibold">Max Permissible Error (MPE)</p>
                    <p className="text-sm font-bold font-mono text-[#0075de] mt-1">
                      ± {mpeResult.mpe_absolute} {mpeResult.base_unit} ({mpeResult.mpe_percent}%)
                    </p>
                  </div>

                  <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                    <p className="text-[10px] text-[#166534] uppercase font-semibold">Min Permitted (T1 Limit)</p>
                    <p className="text-sm font-bold font-mono text-[#166534] mt-1">
                      {mpeResult.t1_limit} {mpeResult.base_unit}
                    </p>
                  </div>

                  <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                    <p className="text-[10px] text-[#991B1B] uppercase font-semibold">Fatal 2x MPE (T2 Limit)</p>
                    <p className="text-sm font-bold font-mono text-[#991B1B] mt-1">
                      {mpeResult.t2_limit} {mpeResult.base_unit}
                    </p>
                  </div>

                  <div className="p-3 bg-[#f6f5f4] rounded-lg border border-[#e6e6e6] col-span-2">
                    <p className="text-[10px] text-[#615d59] uppercase font-semibold">Legal Rule Reference</p>
                    <p className="text-[11px] font-mono text-[#31302e] mt-1">
                      {mpeResult.legal_reference}
                    </p>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-[#854D0E]">
                  <p className="font-semibold flex items-center gap-1.5">
                    <Info className="w-3.5 h-3.5 shrink-0" />
                    <span>Statutory Note on Retail vs Lot Enforcement</span>
                  </p>
                  <p className="text-[11px] mt-1">
                    No individual prepackaged unit may contain less than the $T_2$ threshold ({mpeResult.t2_limit} {mpeResult.base_unit}). When sampling lots under Fifth Schedule, the sample average must satisfy the declared weight after applying Student's t-correction.
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-xs text-[#615d59]">Calculating tolerance...</p>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: LOT SAMPLING PROTOCOL */}
      {activeTab === 'SAMPLING' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-[#e6e6e6] p-6 space-y-4">
            <h2 className="font-bold text-sm text-[#000000] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#0075de]" />
              <span>Fifth Schedule Lot Sampling & Average Net Quantity Verification</span>
            </h2>
            <p className="text-xs text-[#615d59]">
              Evaluates factory / warehouse batch inspection under Rules 19–22. Enter lot size and measured sample draw weights.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#000000] mb-1">Lot Size (Total Packages)</label>
                <input
                  type="number"
                  value={lotSize}
                  onChange={(e) => setLotSize(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-[#f6f5f4] focus:bg-white focus:outline-hidden font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#000000] mb-1">Declared Net Quantity</label>
                <input
                  type="number"
                  value={sampleDeclaredQty}
                  onChange={(e) => setSampleDeclaredQty(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-[#f6f5f4] focus:bg-white focus:outline-hidden font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#000000] mb-1">Unit</label>
                <select
                  value={sampleUnit}
                  onChange={(e) => setSampleUnit(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-white focus:outline-hidden"
                >
                  <option value="g">Grams (g)</option>
                  <option value="kg">Kilograms (kg)</option>
                  <option value="ml">Millilitres (ml)</option>
                  <option value="L">Litres (L)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#000000] mb-1">
                Sample Measured Weights (Comma-separated individual sample draws in {sampleUnit})
              </label>
              <textarea
                rows={3}
                value={sampleWeightsText}
                onChange={(e) => setSampleWeightsText(e.target.value)}
                className="w-full p-3 rounded-lg border border-[#e6e6e6] text-xs bg-[#f6f5f4] focus:bg-white focus:outline-hidden font-mono leading-relaxed"
              />
            </div>

            <button
              onClick={handleRunSamplingEvaluation}
              className="px-5 py-2.5 rounded-full text-xs font-bold bg-[#0075de] text-white hover:bg-[#005bab] transition-all shadow-xs"
            >
              Evaluate Fifth Schedule Compliance
            </button>
          </div>

          {/* Results Display */}
          {samplingResult && (
            <div
              className={`rounded-xl border p-6 space-y-4 ${
                samplingResult.outcome === 'PASS'
                  ? 'bg-green-50/70 border-green-200'
                  : 'bg-red-50/70 border-red-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {samplingResult.outcome === 'PASS' ? (
                    <CheckCircle2 className="w-5 h-5 text-[#1aae39]" />
                  ) : (
                    <XCircle className="w-5 h-5 text-[#991B1B]" />
                  )}
                  <h3 className="font-bold text-sm text-[#000000]">
                    Lot Inspection Outcome: {samplingResult.outcome === 'PASS' ? 'COMPLIANT (PASS)' : 'NON-COMPLIANT (FAIL)'}
                  </h3>
                </div>
                <span className="font-mono text-xs font-bold px-2.5 py-0.5 rounded bg-white border border-current">
                  Draw: {samplingResult.sample_size} / {samplingResult.recommended_sample_size} units
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="bg-white p-3 rounded-lg border border-[#e6e6e6]">
                  <p className="text-[10px] text-[#615d59] font-semibold">Mean Measured Weight</p>
                  <p className="font-mono font-bold text-sm mt-0.5">{samplingResult.mean_weight} {sampleUnit}</p>
                </div>

                <div className="bg-white p-3 rounded-lg border border-[#e6e6e6]">
                  <p className="text-[10px] text-[#615d59] font-semibold">Corrected Average (t-stat)</p>
                  <p className="font-mono font-bold text-sm mt-0.5">{samplingResult.corrected_mean} {sampleUnit}</p>
                </div>

                <div className="bg-white p-3 rounded-lg border border-[#e6e6e6]">
                  <p className="text-[10px] text-[#615d59] font-semibold">T1 Defectives (Deficiency &gt; MPE)</p>
                  <p className="font-mono font-bold text-sm mt-0.5">
                    {samplingResult.t1_defectives_count} (Max allowed: {samplingResult.max_allowable_t1})
                  </p>
                </div>

                <div className="bg-white p-3 rounded-lg border border-[#e6e6e6]">
                  <p className="text-[10px] text-[#615d59] font-semibold">T2 Defectives (Fatal &gt; 2x MPE)</p>
                  <p className="font-mono font-bold text-sm mt-0.5 text-red-600">
                    {samplingResult.t2_defectives_count} (0 permitted)
                  </p>
                </div>
              </div>

              <div className="bg-white p-3.5 rounded-lg border border-[#e6e6e6] text-xs">
                <p className="font-bold text-[#000000] mb-1">Statutory Determination:</p>
                <ul className="list-disc list-inside space-y-1 text-[#31302e]">
                  {samplingResult.reasons.map((r: string, idx: number) => (
                    <li key={idx}>{r}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: SECOND SCHEDULE STANDARD PACK SIZES */}
      {activeTab === 'SCHEDULES' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-5 bg-white rounded-xl border border-[#e6e6e6] p-6 space-y-4">
            <h2 className="font-bold text-sm text-[#000000] flex items-center gap-2">
              <Package className="w-4 h-4 text-[#0075de]" />
              <span>Second Schedule Pack Size Validator (Rule 5)</span>
            </h2>
            <p className="text-xs text-[#615d59]">
              Commodities listed under the Second Schedule must strictly be packaged in prescribed standard sizes.
            </p>

            <div>
              <label className="block text-xs font-semibold text-[#000000] mb-1">Select Scheduled Commodity</label>
              <select
                value={selectedCommodity}
                onChange={(e) => {
                  setSelectedCommodity(e.target.value);
                  setPackCheckResult(null);
                }}
                className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-white focus:outline-hidden"
              >
                {Object.keys(schedulesData?.commodities || {}).map((key) => (
                  <option key={key} value={key}>
                    {schedulesData.commodities[key].name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-[#000000] mb-1">Declared Quantity</label>
                <input
                  type="number"
                  value={packCheckQty}
                  onChange={(e) => setPackCheckQty(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-[#f6f5f4] focus:bg-white focus:outline-hidden font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#000000] mb-1">Unit</label>
                <select
                  value={packCheckUnit}
                  onChange={(e) => setPackCheckUnit(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-white focus:outline-hidden"
                >
                  <option value="g">Grams (g)</option>
                  <option value="kg">Kilograms (kg)</option>
                  <option value="ml">Millilitres (ml)</option>
                  <option value="L">Litres (L)</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleValidatePackSize}
              className="w-full py-2 rounded-full text-xs font-bold bg-[#0075de] text-white hover:bg-[#005bab] transition-all shadow-xs"
            >
              Verify Standard Pack Compliance
            </button>
          </div>

          {/* Schedule Lookup Output */}
          <div className="lg:col-span-7 bg-white rounded-xl border border-[#e6e6e6] p-6 space-y-4">
            {schedulesData?.commodities?.[selectedCommodity] && (
              <div>
                <h3 className="font-bold text-sm text-[#000000]">
                  {schedulesData.commodities[selectedCommodity].name}
                </h3>
                <p className="text-xs text-[#0075de] font-mono mt-0.5">
                  {schedulesData.commodities[selectedCommodity].legal_note}
                </p>

                <div className="mt-4">
                  <p className="text-xs font-semibold text-[#000000] mb-2">Permitted Statutory Pack Sizes:</p>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {schedulesData.commodities[selectedCommodity].permitted_mass_grams.map((size: number) => (
                      <span
                        key={size}
                        className="px-3 py-1 rounded bg-[#f6f5f4] border border-[#e6e6e6] font-mono text-xs font-bold text-[#31302e]"
                      >
                        {size >= 1000 ? `${size / 1000} kg` : `${size} g`}
                      </span>
                    ))}
                  </div>
                </div>

                {packCheckResult && (
                  <div
                    className={`mt-5 p-4 rounded-xl border ${
                      packCheckResult.is_standard
                        ? 'bg-green-50 border-green-200 text-[#166534]'
                        : 'bg-red-50 border-red-200 text-[#991B1B]'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {packCheckResult.is_standard ? (
                        <CheckCircle2 className="w-5 h-5 text-[#1aae39]" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-[#dd5b00]" />
                      )}
                      <p className="font-bold text-xs">
                        {packCheckResult.is_standard
                          ? `COMPLIANT: ${packCheckResult.declared} is a prescribed standard pack size.`
                          : `NON-STANDARD PACK: ${packCheckResult.declared} is not in Second Schedule.`}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 5: RULE 7 PDP & FONT CALCULATOR */}
      {activeTab === 'PDP' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-5 bg-white rounded-xl border border-[#e6e6e6] p-6 space-y-4">
            <h2 className="font-bold text-sm text-[#000000] flex items-center gap-2">
              <Ruler className="w-4 h-4 text-[#0075de]" />
              <span>Principal Display Panel (PDP) Dimensions</span>
            </h2>
            <p className="text-xs text-[#615d59]">
              Calculates statutory minimum character and numeral heights under Rule 7, Table 1.
            </p>

            <div>
              <label className="block text-xs font-semibold text-[#000000] mb-1">Package Shape</label>
              <select
                value={pdpShape}
                onChange={(e) => {
                  setPdpShape(e.target.value);
                  handleCalculatePDP();
                }}
                className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-white focus:outline-hidden"
              >
                <option value="RECTANGULAR">Rectangular Box / Flat Pouch</option>
                <option value="CYLINDRICAL">Cylindrical Bottle / Can</option>
                <option value="OTHER_3D">Other 3D Shape</option>
              </select>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-xs font-semibold text-[#000000] mb-1">Height (cm)</label>
                <input
                  type="number"
                  value={pdpHeight}
                  onChange={(e) => {
                    setPdpHeight(parseFloat(e.target.value) || 0);
                    handleCalculatePDP();
                  }}
                  className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-[#f6f5f4] font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#000000] mb-1">Width (cm)</label>
                <input
                  type="number"
                  value={pdpWidth}
                  onChange={(e) => {
                    setPdpWidth(parseFloat(e.target.value) || 0);
                    handleCalculatePDP();
                  }}
                  className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-[#f6f5f4] font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#000000] mb-1">Depth/Dia (cm)</label>
                <input
                  type="number"
                  value={pdpDepth}
                  onChange={(e) => {
                    setPdpDepth(parseFloat(e.target.value) || 0);
                    handleCalculatePDP();
                  }}
                  className="w-full px-3 py-2 rounded-lg border border-[#e6e6e6] text-xs bg-[#f6f5f4] font-mono"
                />
              </div>
            </div>
          </div>

          {/* PDP Output */}
          <div className="lg:col-span-7 bg-white rounded-xl border border-[#e6e6e6] p-6 space-y-4">
            {pdpResult && (
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-[#e6e6e6]">
                  <div>
                    <h3 className="font-bold text-sm text-[#000000]">Rule 7 Statutory Font Standards</h3>
                    <p className="text-xs text-[#0075de] font-mono mt-0.5">{pdpResult.area_band}</p>
                  </div>
                  <span className="font-mono text-xs font-bold px-2.5 py-1 rounded bg-[#f6f5f4] border border-[#e6e6e6]">
                    PDP: {pdpResult.pdp_area_cm2} cm²
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4">
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-[10px] text-[#0075de] font-semibold uppercase">Min Numeral Height</p>
                    <p className="font-mono text-base font-bold text-[#0075de] mt-1">
                      ≥ {pdpResult.min_numeral_height_mm} mm
                    </p>
                  </div>

                  <div className="p-3 bg-[#f6f5f4] rounded-lg border border-[#e6e6e6]">
                    <p className="text-[10px] text-[#615d59] font-semibold uppercase">Blown / Molded Height</p>
                    <p className="font-mono text-base font-bold text-[#31302e] mt-1">
                      ≥ {pdpResult.min_blown_or_molded_height_mm} mm
                    </p>
                  </div>

                  <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                    <p className="text-[10px] text-[#166534] font-semibold uppercase">Other Letters Height</p>
                    <p className="font-mono text-base font-bold text-[#166534] mt-1">
                      ≥ {pdpResult.min_other_declarations_height_mm} mm
                    </p>
                  </div>
                </div>

                <p className="text-[11px] text-[#615d59] mt-3 font-mono">
                  {pdpResult.legal_reference}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
