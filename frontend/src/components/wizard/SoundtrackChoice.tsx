"use client";

import { useState, useRef } from "react";
import { setSoundtrack } from "@/lib/api";

interface Props {
  projectId: string;
  onContinue: () => void;
}

export default function SoundtrackChoice({ projectId, onContinue }: Props) {
  const [mode, setMode] = useState<"ai_generate" | "upload">("ai_generate");
  const [file, setFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleContinue = async () => {
    setSaving(true);
    try {
      await setSoundtrack(projectId, mode, file || undefined);
      onContinue();
    } catch (err) {
      console.error("Failed to set soundtrack:", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Soundtrack</h2>
        <p className="text-white/50">
          Upload your own music or let Friday generate an AI soundtrack after
          the video is ready.
        </p>
      </div>

      <div className="space-y-3">
        <label
          className={`flex items-start gap-4 p-4 rounded-xl border cursor-pointer transition ${
            mode === "ai_generate"
              ? "border-white/30 bg-white/5"
              : "border-white/10 hover:border-white/20"
          }`}
          onClick={() => setMode("ai_generate")}
        >
          <input
            type="radio"
            checked={mode === "ai_generate"}
            onChange={() => setMode("ai_generate")}
            className="mt-1"
          />
          <div>
            <p className="font-medium">AI-Generated Soundtrack</p>
            <p className="text-sm text-white/50">
              Friday will compose an instrumental score via Suno that matches
              your video&apos;s mood and pacing. You&apos;ll review and approve
              it before final assembly.
            </p>
          </div>
        </label>

        <label
          className={`flex items-start gap-4 p-4 rounded-xl border cursor-pointer transition ${
            mode === "upload"
              ? "border-white/30 bg-white/5"
              : "border-white/10 hover:border-white/20"
          }`}
          onClick={() => setMode("upload")}
        >
          <input
            type="radio"
            checked={mode === "upload"}
            onChange={() => setMode("upload")}
            className="mt-1"
          />
          <div>
            <p className="font-medium">Upload My Own</p>
            <p className="text-sm text-white/50">
              Use your own audio file. MP3, WAV, AAC, M4A, or FLAC.
            </p>
          </div>
        </label>
      </div>

      {mode === "upload" && (
        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-white/10 rounded-xl p-6 text-center cursor-pointer hover:border-white/20 transition"
        >
          {file ? (
            <p className="text-white/70">{file.name}</p>
          ) : (
            <p className="text-white/40">Click to select audio file</p>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="audio/*"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </div>
      )}

      <button
        onClick={handleContinue}
        disabled={saving || (mode === "upload" && !file)}
        className="px-6 py-3 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition disabled:opacity-30 disabled:cursor-not-allowed"
      >
        {saving ? "Saving..." : "Continue"}
      </button>
    </div>
  );
}
