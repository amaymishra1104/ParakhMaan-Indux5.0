'use client';

import React, { useState } from 'react';
import { ComplianceResult } from '@/lib/types';
import { X, CheckCircle2, Edit3, XCircle, Camera, AlertCircle } from 'lucide-react';

interface ReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: ComplianceResult | null;
  onSubmitAction: (action: {
    target_field: string;
    action_type: 'CONFIRM' | 'CORRECT' | 'REJECT' | 'REQUEST_NEW_IMAGE';
    previous_value?: string;
    new_value?: string;
    reason?: string;
  }) => Promise<void>;
}

export default function ReviewModal({
  isOpen,
  onClose,
  result,
  onSubmitAction
}: ReviewModalProps) {
  if (!isOpen || !result) return null;

  const [actionType, setActionType] = useState<'CONFIRM' | 'CORRECT' | 'REJECT' | 'REQUEST_NEW_IMAGE'>('CONFIRM');
  const [correctedValue, setCorrectedValue] = useState(result.normalized_value || result.detected_value || '');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmitAction({
        target_field: result.field,
        action_type: actionType,
        previous_value: result.normalized_value || result.detected_value || '',
        new_value: actionType === 'CORRECT' ? correctedValue : undefined,
        reason: reason || `Manual inspection decision: ${actionType}`
      });
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="bg-white rounded-xl max-w-lg w-full overflow-hidden elevation-2">
        {/* Header */}
        <div className="px-5 py-4 border-b border-[#e6e6e6] bg-[#f6f5f4] flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-[#000000]">Inspector Manual Review</h3>
            <p className="text-xs text-[#615d59]">Field: {result.field.replace('_', ' ').toUpperCase()} ({result.rule_id})</p>
          </div>
          <button onClick={onClose} className="p-1 rounded-md text-[#615d59] hover:bg-[#e6e6e6]">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
          {/* Detected AI Finding */}
          <div className="p-3 bg-[#f6f5f4] rounded-lg border border-[#e6e6e6]">
            <p className="text-[10px] text-[#615d59] uppercase font-bold">OCR Detected Value</p>
            <p className="text-xs font-mono font-semibold text-[#000000] mt-0.5">
              {result.detected_value || 'None (Missing from surface)'}
            </p>
            <p className="text-[11px] text-[#31302e] mt-1.5">
              <b>Rule Check:</b> {result.explanation}
            </p>
          </div>

          {/* Action Choice */}
          <div>
            <label className="block text-xs font-semibold text-[#31302e] mb-1.5">Select Inspector Action:</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setActionType('CONFIRM')}
                className={`p-2.5 rounded-lg border flex items-center gap-2 text-left transition-all ${
                  actionType === 'CONFIRM'
                    ? 'bg-green-50 border-green-500 text-[#166534] font-bold shadow-xs'
                    : 'bg-white border-[#e6e6e6] text-[#31302e] hover:bg-[#f6f5f4]'
                }`}
              >
                <CheckCircle2 className="w-4 h-4 text-[#1aae39]" />
                <div>
                  <p className="text-xs">Confirm Valid</p>
                  <p className="text-[10px] font-normal text-[#615d59]">Mark as compliant</p>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setActionType('CORRECT')}
                className={`p-2.5 rounded-lg border flex items-center gap-2 text-left transition-all ${
                  actionType === 'CORRECT'
                    ? 'bg-blue-50 border-[#0075de] text-[#0075de] font-bold shadow-xs'
                    : 'bg-white border-[#e6e6e6] text-[#31302e] hover:bg-[#f6f5f4]'
                }`}
              >
                <Edit3 className="w-4 h-4 text-[#0075de]" />
                <div>
                  <p className="text-xs">Correct Value</p>
                  <p className="text-[10px] font-normal text-[#615d59]">Override OCR reading</p>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setActionType('REJECT')}
                className={`p-2.5 rounded-lg border flex items-center gap-2 text-left transition-all ${
                  actionType === 'REJECT'
                    ? 'bg-red-50 border-red-500 text-[#991B1B] font-bold shadow-xs'
                    : 'bg-white border-[#e6e6e6] text-[#31302e] hover:bg-[#f6f5f4]'
                }`}
              >
                <XCircle className="w-4 h-4 text-[#dd5b00]" />
                <div>
                  <p className="text-xs">Reject / Violation</p>
                  <p className="text-[10px] font-normal text-[#615d59]">Mark non-compliant</p>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setActionType('REQUEST_NEW_IMAGE')}
                className={`p-2.5 rounded-lg border flex items-center gap-2 text-left transition-all ${
                  actionType === 'REQUEST_NEW_IMAGE'
                    ? 'bg-amber-50 border-amber-500 text-[#854D0E] font-bold shadow-xs'
                    : 'bg-white border-[#e6e6e6] text-[#31302e] hover:bg-[#f6f5f4]'
                }`}
              >
                <Camera className="w-4 h-4 text-[#dd5b00]" />
                <div>
                  <p className="text-xs">Request Photo</p>
                  <p className="text-[10px] font-normal text-[#615d59]">Unclear surface</p>
                </div>
              </button>
            </div>
          </div>

          {/* Corrected Value Input */}
          {actionType === 'CORRECT' && (
            <div>
              <label className="block text-xs font-semibold text-[#31302e] mb-1">
                Inspector Verified Value:
              </label>
              <input
                type="text"
                required
                value={correctedValue}
                onChange={(e) => setCorrectedValue(e.target.value)}
                placeholder="e.g. ₹ 60.00 (Inclusive of all taxes)"
                className="w-full px-3 py-2 border border-[#e6e6e6] rounded-md text-xs focus:outline-none focus:border-[#0075de] font-mono"
              />
            </div>
          )}

          {/* Remarks / Reason */}
          <div>
            <label className="block text-xs font-semibold text-[#31302e] mb-1">
              Statutory Justification / Audit Notes:
            </label>
            <textarea
              rows={2}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Visual verification confirms statutory wording present on side fold."
              className="w-full px-3 py-2 border border-[#e6e6e6] rounded-md text-xs focus:outline-none focus:border-[#0075de]"
            />
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#e6e6e6]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-full text-xs font-medium bg-white text-[#31302e] border border-[#e6e6e6] hover:bg-[#f6f5f4]"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 rounded-full text-xs font-bold bg-[#0075de] text-white hover:bg-[#005bab] disabled:opacity-50 shadow-xs"
            >
              {submitting ? 'Applying Decision...' : 'Save Decision to Audit Log'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
