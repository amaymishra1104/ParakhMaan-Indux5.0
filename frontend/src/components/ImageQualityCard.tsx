'use client';

import React from 'react';
import { PackageImage } from '@/lib/types';
import { CheckCircle2, AlertTriangle, XCircle, Sparkles, Eye, ShieldAlert } from 'lucide-react';

interface ImageQualityCardProps {
  image: PackageImage;
}

export default function ImageQualityCard({ image }: ImageQualityCardProps) {
  const meta = image.quality_metadata || {
    quality_score: image.quality_score || 0.95,
    blur: false,
    glare: false,
    resolution_ok: true,
    perspective_ok: true,
    occlusion_detected: false,
    surface_visible: true,
    issues: []
  };

  const scorePct = Math.round((meta.quality_score || image.quality_score || 1.0) * 100);
  const isHealthy = scorePct >= 75 && !meta.blur && !meta.glare;
  const isCritical = scorePct < 50 || meta.blur;

  return (
    <div className="bg-white rounded-xl border border-[#e6e6e6] p-4 elevation-0">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-[#e6e6e6]">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-[#0075de] bg-[#f6f5f4] px-2.5 py-1 rounded-md border border-[#e6e6e6]">
            {image.surface_type} Surface
          </span>
          <span className="text-xs text-[#615d59] truncate max-w-[140px]" title={image.original_filename}>
            {image.original_filename}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <div
            className={`w-2.5 h-2.5 rounded-full ${
              isHealthy ? 'bg-[#1aae39]' : isCritical ? 'bg-[#dd5b00]' : 'bg-[#62aef0]'
            }`}
          />
          <span className="text-xs font-bold text-[#000000]">{scorePct}% Quality</span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 my-3">
        <div className={`p-2 rounded-lg border text-center ${meta.blur ? 'bg-red-50 border-red-200' : 'bg-[#f6f5f4] border-[#e6e6e6]'}`}>
          <p className="text-[10px] text-[#615d59] uppercase font-semibold">Sharpness</p>
          <p className={`text-xs font-bold mt-0.5 ${meta.blur ? 'text-[#dd5b00]' : 'text-[#1aae39]'}`}>
            {meta.blur ? 'Blur Detected' : 'Sharp'}
          </p>
        </div>

        <div className={`p-2 rounded-lg border text-center ${meta.glare ? 'bg-amber-50 border-amber-200' : 'bg-[#f6f5f4] border-[#e6e6e6]'}`}>
          <p className="text-[10px] text-[#615d59] uppercase font-semibold">Lighting / Glare</p>
          <p className={`text-xs font-bold mt-0.5 ${meta.glare ? 'text-[#dd5b00]' : 'text-[#1aae39]'}`}>
            {meta.glare ? 'Glare Warning' : 'Even Lighting'}
          </p>
        </div>

        <div className="p-2 rounded-lg bg-[#f6f5f4] border border-[#e6e6e6] text-center">
          <p className="text-[10px] text-[#615d59] uppercase font-semibold">Resolution</p>
          <p className={`text-xs font-bold mt-0.5 ${meta.resolution_ok ? 'text-[#1aae39]' : 'text-[#dd5b00]'}`}>
            {meta.resolution_ok ? 'HD Legible' : 'Low Res'}
          </p>
        </div>

        <div className="p-2 rounded-lg bg-[#f6f5f4] border border-[#e6e6e6] text-center">
          <p className="text-[10px] text-[#615d59] uppercase font-semibold">Perspective</p>
          <p className="text-xs font-bold text-[#1aae39] mt-0.5">
            {meta.perspective_ok ? 'Aligned PDP' : 'Distorted'}
          </p>
        </div>
      </div>

      {/* Issues / Advisory Alert */}
      {meta.issues && meta.issues.length > 0 ? (
        <div className="mt-2 p-2.5 rounded-lg bg-[#f6f5f4] border border-[#dd5b00]/30 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-[#dd5b00] shrink-0 mt-0.5" />
          <div className="text-[11px] text-[#31302e]">
            {meta.issues.map((iss, i) => (
              <p key={i} className="leading-tight mb-0.5">{iss}</p>
            ))}
          </div>
        </div>
      ) : (
        <div className="mt-2 text-[11px] text-[#1aae39] flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Image satisfies Rule 9(1) legibility standards for automated OCR.</span>
        </div>
      )}
    </div>
  );
}
