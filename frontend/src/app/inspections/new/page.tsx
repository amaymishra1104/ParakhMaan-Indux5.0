'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import CameraCaptureModal from '@/components/CameraCaptureModal';
import {
  Upload, Camera, Trash2, CheckCircle2, AlertCircle,
  FileText, ShieldCheck, ArrowRight, RefreshCw, Layers
} from 'lucide-react';

interface UploadedSurface {
  id?: string;
  file?: File;
  previewUrl: string;
  surfaceType: string;
  isBase64?: boolean;
  base64Data?: string;
}

export default function NewInspectionPage() {
  const router = useRouter();

  // Form State
  const [productName, setProductName] = useState('');
  const [brandName, setBrandName] = useState('');
  const [category, setCategory] = useState('PACKAGED_FOOD');
  const [location, setLocation] = useState('Retail Store Shelf, Sector 12');
  const [notes, setNotes] = useState('');

  // Surfaces State (1 to 4 images)
  const [surfaces, setSurfaces] = useState<UploadedSurface[]>([]);
  const [activeSurfaceTab, setActiveSurfaceTab] = useState('FRONT');

  // Camera Modal
  const [cameraOpen, setCameraOpen] = useState(false);

  // Submission / Processing
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // File Input Handler
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    const previewUrl = URL.createObjectURL(file);

    // Remove existing surface of this type if any, or add
    setSurfaces((prev) => [
      ...prev.filter((s) => s.surfaceType !== activeSurfaceTab),
      {
        file,
        previewUrl,
        surfaceType: activeSurfaceTab,
        isBase64: false
      }
    ]);
  };

  // Camera Capture Handler
  const handleCameraCapture = async (base64Data: string, surfaceType: string) => {
    setSurfaces((prev) => [
      ...prev.filter((s) => s.surfaceType !== surfaceType),
      {
        previewUrl: base64Data,
        surfaceType: surfaceType,
        isBase64: true,
        base64Data
      }
    ]);
  };

  const removeSurface = (surfaceType: string) => {
    setSurfaces((prev) => prev.filter((s) => s.surfaceType !== surfaceType));
  };

  // Submit and Run Pipeline
  const handleRunInspection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (surfaces.length === 0) {
      setError('Please upload or capture at least one package surface image (Front or Back).');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      // 1. Create Inspection Draft
      const insp = await api.createInspection({
        product_name: productName || 'Packaged Commodity',
        brand_name: brandName || undefined,
        category,
        location,
        notes
      });

      // 2. Upload/Attach each surface image
      for (const surf of surfaces) {
        if (surf.isBase64 && surf.base64Data) {
          await api.captureCameraImage(insp.id, surf.base64Data, surf.surfaceType);
        } else if (surf.file) {
          await api.uploadImage(insp.id, surf.file, surf.surfaceType);
        }
      }

      // 3. Trigger Deterministic AI Compliance Engine
      const processedInsp = await api.processInspection(insp.id);

      // 4. Redirect to Detail / Evidence Viewer
      router.push(`/inspections/${processedInsp.id}`);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to complete inspection processing.');
      setProcessing(false);
    }
  };

  const surfaceTypes = ['FRONT', 'BACK', 'SIDE', 'TOP', 'BOTTOM'];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold tracking-tight text-[#000000]">
          New Legal Metrology Inspection
        </h1>
        <p className="text-xs text-[#615d59] mt-0.5">
          Capture or upload 1–4 package surfaces to run deterministic statutory compliance checks
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-xs text-[#991B1B]">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleRunInspection} className="space-y-6">
        {/* Step 1: Package Metadata */}
        <div className="bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-[#e6e6e6]">
            <FileText className="w-4 h-4 text-[#0075de]" />
            <h2 className="font-bold text-xs text-[#000000] uppercase tracking-wider">
              1. Package & Sampling Metadata
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-[#31302e] mb-1">Product / Commodity Name</label>
              <input
                type="text"
                placeholder="e.g. Crunchy Potato Wafers / Whole Wheat Atta"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                className="w-full px-3 py-2 border border-[#e6e6e6] rounded-md focus:outline-none focus:border-[#0075de] bg-[#f6f5f4]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#31302e] mb-1">Brand Name / Manufacturer</label>
              <input
                type="text"
                placeholder="e.g. Tasty Bites / Pure Foods Ltd"
                value={brandName}
                onChange={(e) => setBrandName(e.target.value)}
                className="w-full px-3 py-2 border border-[#e6e6e6] rounded-md focus:outline-none focus:border-[#0075de] bg-[#f6f5f4]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#31302e] mb-1">Statutory Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 border border-[#e6e6e6] rounded-md focus:outline-none focus:border-[#0075de] bg-[#f6f5f4]"
              >
                <option value="PACKAGED_FOOD">Packaged Food (Schedule II / FSSAI aligned)</option>
                <option value="COSMETICS">Cosmetics & Personal Care</option>
                <option value="MEDICAL_DEVICE">Medical Device</option>
                <option value="ELECTRONICS">Electronics & Electrical Goods</option>
                <option value="HOUSEHOLD_GOODS">Household Goods & Cleaning</option>
                <option value="TOYS">Toys & Educational Kits</option>
                <option value="PACKAGED_COMMODITY">General Packaged Commodity</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-[#31302e] mb-1">Sampling Location</label>
              <input
                type="text"
                placeholder="e.g. Supermarket Aisle 4, Warehouse Bay 2"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full px-3 py-2 border border-[#e6e6e6] rounded-md focus:outline-none focus:border-[#0075de] bg-[#f6f5f4]"
              />
            </div>
          </div>
        </div>

        {/* Step 2: Multi-Surface Image Ingestion & Live Camera */}
        <div className="bg-white rounded-xl border border-[#e6e6e6] p-5 elevation-0 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#e6e6e6]">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#0075de]" />
              <h2 className="font-bold text-xs text-[#000000] uppercase tracking-wider">
                2. Package Surface Images (1–4 Surfaces)
              </h2>
            </div>
            <span className="text-[11px] text-[#615d59]">
              {surfaces.length} surface photo{surfaces.length !== 1 ? 's' : ''} attached
            </span>
          </div>

          {/* Surface Selection Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {surfaceTypes.map((st) => {
              const hasImg = surfaces.some((s) => s.surfaceType === st);
              const isSelected = activeSurfaceTab === st;
              return (
                <button
                  key={st}
                  type="button"
                  onClick={() => setActiveSurfaceTab(st)}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                    isSelected
                      ? 'bg-[#0075de] text-white shadow-xs'
                      : hasImg
                      ? 'bg-green-50 text-[#166534] border border-green-200'
                      : 'bg-[#f6f5f4] text-[#31302e] border border-[#e6e6e6] hover:bg-[#e6e6e6]'
                  }`}
                >
                  {hasImg && <CheckCircle2 className="w-3.5 h-3.5" />}
                  <span>{st} Surface</span>
                </button>
              );
            })}
          </div>

          {/* Dropzone & Camera Trigger for Active Surface */}
          <div className="border-2 border-dashed border-[#e6e6e6] rounded-xl p-6 text-center bg-[#f6f5f4]/50 hover:bg-[#f6f5f4] transition-colors">
            {surfaces.some((s) => s.surfaceType === activeSurfaceTab) ? (
              <div className="space-y-3">
                <div className="relative inline-block max-h-56 overflow-hidden rounded-lg border border-[#e6e6e6] shadow-sm">
                  <img
                    src={surfaces.find((s) => s.surfaceType === activeSurfaceTab)?.previewUrl}
                    alt={`${activeSurfaceTab} preview`}
                    className="max-h-56 w-auto object-contain"
                  />
                  <div className="absolute top-2 right-2">
                    <button
                      type="button"
                      onClick={() => removeSurface(activeSurfaceTab)}
                      className="p-1.5 bg-red-600 text-white rounded-full shadow-md hover:bg-red-700 transition-colors"
                      title="Remove image"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
                <p className="text-xs font-bold text-[#166534]">
                  {activeSurfaceTab} surface attached successfully
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-center gap-3">
                  <div className="p-3 bg-white rounded-full border border-[#e6e6e6] shadow-2xs text-[#0075de]">
                    <Upload className="w-6 h-6" />
                  </div>
                </div>
                <div>
                  <p className="text-xs font-bold text-[#000000]">
                    Upload or capture <span className="text-[#0075de]">{activeSurfaceTab}</span> surface
                  </p>
                  <p className="text-[11px] text-[#615d59] mt-0.5">
                    Clear lighting, no heavy glare, minimum 600×600px resolution
                  </p>
                </div>

                {/* Upload & Camera Buttons */}
                <div className="flex items-center justify-center gap-3 pt-2">
                  <label className="cursor-pointer px-4 py-2 bg-white text-[#31302e] border border-[#e6e6e6] rounded-full text-xs font-semibold hover:bg-[#f6f5f4] transition-all shadow-xs inline-flex items-center gap-1.5">
                    <Upload className="w-3.5 h-3.5 text-[#0075de]" />
                    <span>Upload File</span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                  </label>

                  <button
                    type="button"
                    onClick={() => setCameraOpen(true)}
                    className="px-4 py-2 bg-[#0075de] text-white rounded-full text-xs font-bold hover:bg-[#005bab] transition-all shadow-xs inline-flex items-center gap-1.5"
                  >
                    <Camera className="w-3.5 h-3.5" />
                    <span>Live Camera Capture</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            type="submit"
            disabled={processing || surfaces.length === 0}
            className="flex items-center gap-2 px-6 py-3 rounded-full text-xs font-bold bg-[#0075de] text-white hover:bg-[#005bab] transition-all shadow-md active:scale-95 disabled:opacity-50"
          >
            {processing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Executing AI OCR & Rule Engine...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />
                <span>Run Statutory Compliance Analysis</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>

      {/* Camera Capture Modal */}
      <CameraCaptureModal
        isOpen={cameraOpen}
        onClose={() => setCameraOpen(false)}
        onCapture={handleCameraCapture}
        defaultSurface={activeSurfaceTab}
      />
    </div>
  );
}
