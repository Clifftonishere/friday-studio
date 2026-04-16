"use client";

import { useState, useRef } from "react";
import {
  uploadMedia,
  updateUploadStyle,
  bulkUpdateStyle,
  deleteUpload,
} from "@/lib/api";
import type { Upload, StyleType } from "@/lib/types";

interface Props {
  projectId: string;
  onContinue: () => void;
}

const STYLES = ["original", "anime", "pixar"] as const;

export default function MediaUpload({ projectId, onContinue }: Props) {
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [uploading, setUploading] = useState(false);
  const [globalStyle, setGlobalStyle] = useState<string>("original");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList) => {
    setUploading(true);
    for (const file of Array.from(files)) {
      const result = await uploadMedia(projectId, file, globalStyle);
      setUploads((prev) => [...prev, result]);
    }
    setUploading(false);
  };

  const handleStyleChange = async (uploadId: string, style: StyleType) => {
    await updateUploadStyle(projectId, uploadId, style);
    setUploads((prev) =>
      prev.map((u) => (u.id === uploadId ? { ...u, style } : u))
    );
  };

  const handleBulkStyle = async (style: StyleType) => {
    setGlobalStyle(style);
    await bulkUpdateStyle(projectId, style);
    setUploads((prev) => prev.map((u) => ({ ...u, style })));
  };

  const handleDelete = async (uploadId: string) => {
    await deleteUpload(projectId, uploadId);
    setUploads((prev) => prev.filter((u) => u.id !== uploadId));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#1a1a1a] mb-2">Upload your media</h2>
        <p className="text-[#8C7E6F]">
          Add photos and videos. Choose a style for each — or apply one style to
          all.
        </p>
      </div>

      {/* Global style selector */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-[#8C7E6F]">Apply to all:</span>
        {STYLES.map((s) => (
          <button
            key={s}
            onClick={() => handleBulkStyle(s)}
            className={`px-3 py-1.5 rounded-lg text-sm capitalize transition ${
              globalStyle === s
                ? "bg-[#6B5B4E] text-white"
                : "bg-white border border-[#E8E0D6] text-[#1a1a1a] hover:border-[#D4C9BC]"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Drop zone */}
      <div
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
        }}
        className="border-2 border-dashed border-[#D4C9BC] rounded-xl p-10 text-center cursor-pointer hover:border-[#6B5B4E] hover:bg-white transition"
      >
        <p className="text-[#8C7E6F] mb-1">
          {uploading ? "Uploading..." : "Drop files here or click to browse"}
        </p>
        <p className="text-xs text-[#B0A396]">
          JPG, PNG, WEBP, MP4, MOV supported
        </p>
        <input
          ref={fileRef}
          type="file"
          multiple
          accept="image/*,video/*"
          className="hidden"
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
        />
      </div>

      {/* Upload list */}
      {uploads.length > 0 && (
        <div className="space-y-2">
          {uploads.map((u) => (
            <div
              key={u.id}
              className="flex items-center justify-between p-3 rounded-lg bg-white border border-[#E8E0D6]"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span
                  className={`text-xs px-2 py-0.5 rounded ${
                    u.media_type === "photo"
                      ? "bg-blue-100 text-blue-700"
                      : "bg-purple-100 text-purple-700"
                  }`}
                >
                  {u.media_type}
                </span>
                <span className="text-sm truncate text-[#1a1a1a]">{u.filename}</span>
              </div>
              <div className="flex items-center gap-2">
                <select
                  value={u.style}
                  onChange={(e) => handleStyleChange(u.id, e.target.value as StyleType)}
                  className="bg-white border border-[#E8E0D6] rounded px-2 py-1 text-sm text-[#1a1a1a]"
                >
                  {STYLES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => handleDelete(u.id)}
                  className="text-[#B0A396] hover:text-red-500 transition text-sm"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={onContinue}
        disabled={uploads.length === 0}
        className="px-6 py-3 bg-[#6B5B4E] text-white rounded-lg font-medium hover:bg-[#5A4A3E] transition disabled:opacity-30 disabled:cursor-not-allowed"
      >
        Continue
      </button>
    </div>
  );
}
