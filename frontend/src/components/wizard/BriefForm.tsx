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
        <h2 className="text-2xl font-bold mb-2">What are we making?</h2>
        <p className="text-white/50">
          Describe your video project. Wedding highlights, birthday
          celebrations, business promos — anything goes.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Project Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Our Beach Wedding Highlights"
          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-white/30 placeholder:text-white/20"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Brief</label>
        <textarea
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          rows={6}
          placeholder="Describe what you want. Include details like: the occasion, tone/mood, key moments to highlight, any specific scenes you envision, and the desired length."
          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-white/30 placeholder:text-white/20 resize-none"
        />
      </div>

      <button
        onClick={() => onSubmit(title, brief)}
        disabled={!title.trim() || !brief.trim()}
        className="px-6 py-3 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition disabled:opacity-30 disabled:cursor-not-allowed"
      >
        Continue
      </button>
    </div>
  );
}
