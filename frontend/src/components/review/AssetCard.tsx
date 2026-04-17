"use client";

import { useState } from "react";
import { approveAsset, rejectAsset } from "@/lib/api";
import { fileUrl } from "@/lib/api";
import type { Asset } from "@/lib/types";
import FeedbackPanel from "./FeedbackPanel";

interface Props {
  asset: Asset;
  onUpdate: () => void;
}

export default function AssetCard({ asset, onUpdate }: Props) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [acting, setActing] = useState(false);

  const isImage = ["character_sheet", "keyframe"].includes(asset.asset_type);
  const isVideo = ["clip", "final_video"].includes(asset.asset_type);
  const isAudio = asset.asset_type === "audio";
  const isText = asset.asset_type === "script";

  const handleApprove = async () => {
    setActing(true);
    try {
      await approveAsset(asset.id);
      onUpdate();
    } finally {
      setActing(false);
    }
  };

  const handleReject = async (comment: string) => {
    setActing(true);
    try {
      await rejectAsset(asset.id, comment);
      setShowFeedback(false);
      onUpdate();
    } finally {
      setActing(false);
    }
  };

  const meta = asset.metadata ? JSON.parse(asset.metadata) : {};
  const url = asset.file_path ? fileUrl(asset.file_path) : "";

  return (
    <div className="rounded-xl bg-white border border-[#E8E0D6] overflow-hidden shadow-sm">
      {/* Preview */}
      <div className="relative">
        {isImage && url && (
          <img
            src={url}
            alt={asset.asset_type}
            className="w-full aspect-[9/16] object-cover"
          />
        )}
        {isVideo && url && (
          <video src={url} controls className="w-full aspect-video" />
        )}
        {isAudio && url && (
          <div className="p-6 flex items-center justify-center bg-[#FAF6F1]">
            <audio src={url} controls className="w-full" />
          </div>
        )}
        {isText && asset.text_content && (
          <div className="p-4 max-h-64 overflow-y-auto bg-[#FAF6F1]">
            <pre className="text-xs text-[#6B5B4E] whitespace-pre-wrap font-mono">
              {asset.text_content}
            </pre>
          </div>
        )}

        {/* Version badge */}
        {asset.version > 1 && (
          <span className="absolute top-2 right-2 px-2 py-0.5 rounded bg-white/80 text-xs text-[#6B5B4E] border border-[#E8E0D6]">
            v{asset.version}
          </span>
        )}
      </div>

      {/* Info + Actions */}
      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-[#1a1a1a] capitalize">
              {asset.asset_type.replace("_", " ")}
            </p>
            {meta.scene_number && (
              <p className="text-xs text-[#B0A396]">
                Scene {meta.scene_number}
              </p>
            )}
          </div>
          <span
            className={`text-xs px-2 py-0.5 rounded ${
              asset.status === "approved"
                ? "bg-green-100 text-green-700"
                : asset.status === "rejected"
                  ? "bg-red-100 text-red-700"
                  : "bg-amber-100 text-amber-700"
            }`}
          >
            {asset.status.replace("_", " ")}
          </span>
        </div>

        {asset.status === "pending_review" && (
          <div className="flex gap-2">
            <button
              onClick={handleApprove}
              disabled={acting}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-500 transition disabled:opacity-50"
            >
              Approve
            </button>
            <button
              onClick={() => setShowFeedback(true)}
              disabled={acting}
              className="flex-1 px-4 py-2 bg-[#F5F0EA] text-[#6B5B4E] rounded-lg text-sm font-medium hover:bg-[#EDE6DD] transition disabled:opacity-50"
            >
              Request Changes
            </button>
          </div>
        )}

        {showFeedback && (
          <FeedbackPanel
            onSubmit={handleReject}
            onCancel={() => setShowFeedback(false)}
            submitting={acting}
          />
        )}
      </div>
    </div>
  );
}
