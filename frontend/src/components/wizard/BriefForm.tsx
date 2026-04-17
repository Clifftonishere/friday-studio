"use client";

import { useState } from "react";

interface Props {
  onSubmit: (title: string, brief: string) => void;
}

export default function BriefForm({ onSubmit }: Props) {
  const [title, setTitle] = useState("");
  const [brief, setBrief] = useState("");

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#1a1a1a] mb-2">What are we making?</h2>
        <p className="text-[#8C7E6F]">
          Describe your video project. Wedding highlights, birthday
          celebrations, business promos — anything goes.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#1a1a1a] mb-2">Project Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Our Beach Wedding Highlights"
          className="w-full px-4 py-3 bg-white border border-[#E8E0D6] rounded-lg focus:outline-none focus:border-[#6B5B4E] focus:ring-1 focus:ring-[#6B5B4E] placeholder:text-[#B0A396]"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-[#1a1a1a] mb-2">Brief</label>
        <textarea
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          rows={6}
          placeholder="Describe what you want. Include details like: the occasion, tone/mood, key moments to highlight, any specific scenes you envision, and the desired length."
          className="w-full px-4 py-3 bg-white border border-[#E8E0D6] rounded-lg focus:outline-none focus:border-[#6B5B4E] focus:ring-1 focus:ring-[#6B5B4E] placeholder:text-[#B0A396] resize-none"
        />
      </div>

      <button
        onClick={() => onSubmit(title, brief)}
        disabled={!title.trim() || !brief.trim()}
        className="px-6 py-3 bg-[#6B5B4E] text-white rounded-lg font-medium hover:bg-[#5A4A3E] transition disabled:opacity-30 disabled:cursor-not-allowed"
      >
        Continue
      </button>
    </div>
  );
}
