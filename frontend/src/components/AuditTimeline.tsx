'use client';

import React from 'react';
import { AuditEvent } from '@/lib/types';
import { Clock, ShieldCheck, Camera, FileCheck2, Cpu, UserCheck } from 'lucide-react';
import { formatTime, formatDateTime } from '@/lib/formatters';

interface AuditTimelineProps {
  events: AuditEvent[];
}

export default function AuditTimeline({ events = [] }: AuditTimelineProps) {
  if (events.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-[#e6e6e6] p-6 text-center text-xs text-[#615d59]">
        No audit log entries recorded yet.
      </div>
    );
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'INSPECTION_CREATED':
        return <FileCheck2 className="w-3.5 h-3.5 text-[#0075de]" />;
      case 'IMAGE_UPLOADED':
      case 'CAMERA_CAPTURED':
        return <Camera className="w-3.5 h-3.5 text-[#2a9d99]" />;
      case 'RULE_ENGINE_EVALUATED':
        return <Cpu className="w-3.5 h-3.5 text-[#d6b6f6]" />;
      case 'REVIEWER_ACTION':
        return <UserCheck className="w-3.5 h-3.5 text-[#dd5b00]" />;
      case 'INSPECTION_FINALIZED':
        return <ShieldCheck className="w-3.5 h-3.5 text-[#1aae39]" />;
      default:
        return <Clock className="w-3.5 h-3.5 text-[#615d59]" />;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0">
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[#e6e6e6]">
        <Clock className="w-4 h-4 text-[#0075de]" />
        <h3 className="font-bold text-xs text-[#000000] uppercase tracking-wider">
          Statutory Audit Trail & Chain of Custody
        </h3>
      </div>

      <div className="space-y-4 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-[#e6e6e6]">
        {events.map((evt, idx) => (
          <div key={evt.id || idx} className="relative flex items-start gap-3.5 pl-1">
            <div className="w-6 h-6 rounded-full bg-white border border-[#e6e6e6] flex items-center justify-center shrink-0 z-10 shadow-2xs">
              {getEventIcon(evt.event_type)}
            </div>
            <div className="flex-1 bg-[#f6f5f4] rounded-lg p-2.5 border border-[#e6e6e6] text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="font-bold text-[#000000] text-[11px]">{evt.event_type}</span>
                <span className="text-[10px] text-[#615d59] font-mono" title={formatDateTime(evt.created_at)}>
                  {formatTime(evt.created_at)}
                </span>
              </div>
              <p className="text-[#31302e] text-[11px] mt-1">{evt.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
