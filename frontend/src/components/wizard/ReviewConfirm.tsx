"use client";

import { useState } from "react";
import { startPipeline } from "@/lib/api";
import type { Upload } from "@/lib/types";

interface Props {
  projectId: string;
  title: string;
  brief: string;
  uploads: Upload[];
  soundtrackMode: string;
  onStarted: () => void;
}

export default function ReviewConfirm({
  projectId,
  title,
  brief,
  uploads,
  soundtrackMode,
  onStarted,
}: Props) {
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  const handleStart = async () => {
    setStarting(true);
    setError("");
    try {
      await startPipeline(projectId);
      onStarted();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start");
    } finally {
      setStarting(false);
    }
  };

  const photoCount = uploads.filter((u) => u.media_type === "photo").length;
  const videoCount = uploads.filter((u) => u.media_type === "video").length;
  const animeCount = uploads.filter((u) => u.style === "anime").length;
  const pixarCount = uploads.filter((u) => u.style === "pixar").length;
  const originalCount = uploads.filter((u) => u.style === "original").length;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#1a1a1a] mb-2">Review & Start</h2>
        <p className="text-[#8C7E6F]">
          Confirm everything looks good. Friday will start working once you hit
          the button.
        </p>
      </div>

      <div className="space-y-4 p-5 rounded-xl bg-white border border-[#E8E0D6]">
        <div>
          <p className="text-xs text-[#B0A396] uppercase tracking-wider mb-1">
            Project
          </p>
          <p className="font-semibold text-[#1a1a1a]">{title}</p>
        </div>

        <div>
          <p className="text-xs text-[#B0A396] uppercase tracking-wider mb-1">
            Brief
          </p>
          <p className="text-sm text-[#6B5B4E]">{brief}</p>
        </div>

        <div>
          <p className="text-xs text-[#B0A396] uppercase tracking-wider mb-1">
            Media
          </p>
          <p className="text-sm text-[#6B5B4E]">
            {photoCount} photo{photoCount !== 1 ? "s" : ""}
            {videoCount > 0 &&
              `, ${videoCount} video${videoCount !== 1 ? "s" : ""}`}
          </p>
          <div className="flex gap-3 mt-1">
            {animeCount > 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-purple-100 text-purple-700">
                {animeCount} anime
              </span>
            )}
            {pixarCount > 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">
                {pixarCount} pixar
              </span>
            )}
            {originalCount > 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-[#F5F0EA] text-[#8C7E6F]">
                {originalCount} original
              </span>
            )}
          </div>
        </div>

        <div>
          <p className="text-xs text-[#B0A396] uppercase tracking-wider mb-1">
            Soundtrack
          </p>
          <p className="text-sm text-[#6B5B4E]">
            {soundtrackMode === "ai_generate"
              ? "AI-generated"
              : "User-uploaded"}
          </p>
        </div>
      </div>

      {error && (
        <p className="text-red-600 text-sm">{error}</p>
      )}

      <button
        onClick={handleStart}
        disabled={starting}
        className="w-full px-6 py-4 bg-[#6B5B4E] text-white rounded-lg font-bold text-lg hover:bg-[#5A4A3E] transition disabled:opacity-50"
      >
        {starting ? "Starting Friday..." : "Start Production"}
      </button>
    </div>
  );
}
