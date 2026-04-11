"use client";

import { useState } from "react";
import { startPipeline } from "@/lib/api";

interface Upload {
  id: string;
  filename: string;
  media_type: string;
  style: string;
}

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
        <h2 className="text-2xl font-bold mb-2">Review & Start</h2>
        <p className="text-white/50">
          Confirm everything looks good. Friday will start working once you hit
          the button.
        </p>
      </div>

      <div className="space-y-4 p-5 rounded-xl border border-white/10 bg-white/5">
        <div>
          <p className="text-xs text-white/30 uppercase tracking-wider mb-1">
            Project
          </p>
          <p className="font-semibold">{title}</p>
        </div>

        <div>
          <p className="text-xs text-white/30 uppercase tracking-wider mb-1">
            Brief
          </p>
          <p className="text-sm text-white/70">{brief}</p>
        </div>

        <div>
          <p className="text-xs text-white/30 uppercase tracking-wider mb-1">
            Media
          </p>
          <p className="text-sm text-white/70">
            {photoCount} photo{photoCount !== 1 ? "s" : ""}
            {videoCount > 0 &&
              `, ${videoCount} video${videoCount !== 1 ? "s" : ""}`}
          </p>
          <div className="flex gap-3 mt-1">
            {animeCount > 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">
                {animeCount} anime
              </span>
            )}
            {pixarCount > 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">
                {pixarCount} pixar
              </span>
            )}
            {originalCount > 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-white/10 text-white/50">
                {originalCount} original
              </span>
            )}
          </div>
        </div>

        <div>
          <p className="text-xs text-white/30 uppercase tracking-wider mb-1">
            Soundtrack
          </p>
          <p className="text-sm text-white/70">
            {soundtrackMode === "ai_generate"
              ? "AI-generated (Suno)"
              : "User-uploaded"}
          </p>
        </div>
      </div>

      {error && (
        <p className="text-red-400 text-sm">{error}</p>
      )}

      <button
        onClick={handleStart}
        disabled={starting}
        className="w-full px-6 py-4 bg-white text-black rounded-lg font-bold text-lg hover:bg-white/90 transition disabled:opacity-50"
      >
        {starting ? "Starting Friday..." : "Start Production"}
      </button>
    </div>
  );
}
