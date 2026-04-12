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
        <h2 className="text-2xl font-bold text-[#1a1a1a] mb-2">Soundtrack</h2>
        <p className="text-[#8C7E6F]">
          Upload your own music or let Friday generate an AI soundtrack after
          the video is ready.
        </p>
      </div>

      <div className="space-y-3">
        <label
          className={`flex items-start gap-4 p-4 rounded-xl border cursor-pointer transition ${
            mode === "ai_generate"
              ? "border-[#6B5B4E] bg-white shadow-sm"
              : "border-[#E8E0D6] bg-white hover:border-[#D4C9BC]"
          }`}
          onClick={() => setMode("ai_generate")}
        >
          <input
            type="radio"
            checked={mode === "ai_generate"}
            onChange={() => setMode("ai_generate")}
            className="mt-1 accent-[#6B5B4E]"
          />
          <div>
            <p className="font-medium text-[#1a1a1a]">AI-Generated Soundtrack</p>
            <p className="text-sm text-[#8C7E6F]">
              Friday will compose an instrumental score that matches
              your video&apos;s mood and pacing. You&apos;ll review and approve
              it before final assembly.
            </p>
          </div>
        </label>

        <label
          className={`flex items-start gap-4 p-4 rounded-xl border cursor-pointer transition ${
            mode === "upload"
              ? "border-[#6B5B4E] bg-white shadow-sm"
              : "border-[#E8E0D6] bg-white hover:border-[#D4C9BC]"
          }`}
          onClick={() => setMode("upload")}
        >
          <input
            type="radio"
            checked={mode === "upload"}
            onChange={() => setMode("upload")}
            className="mt-1 accent-[#6B5B4E]"
          />
          <div>
            <p className="font-medium text-[#1a1a1a]">Upload My Own</p>
            <p className="text-sm text-[#8C7E6F]">
              Use your own audio file. MP3, WAV, AAC, M4A, or FLAC.
            </p>
          </div>
        </label>
      </div>

      {mode === "upload" && (
        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-[#D4C9BC] rounded-xl p-6 text-center cursor-pointer hover:border-[#6B5B4E] transition bg-white"
        >
          {file ? (
            <p className="text-[#1a1a1a]">{file.name}</p>
          ) : (
            <p className="text-[#8C7E6F]">Click to select audio file</p>
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
        className="px-6 py-3 bg-[#6B5B4E] text-white rounded-lg font-medium hover:bg-[#5A4A3E] transition disabled:opacity-30 disabled:cursor-not-allowed"
      >
        {saving ? "Saving..." : "Continue"}
      </button>
    </div>
  );
}
