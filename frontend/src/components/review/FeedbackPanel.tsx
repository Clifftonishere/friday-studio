"use client";

import { useState } from "react";

interface Props {
  onSubmit: (comment: string) => void;
  onCancel: () => void;
  submitting: boolean;
}

export default function FeedbackPanel({ onSubmit, onCancel, submitting }: Props) {
  const [comment, setComment] = useState("");

  return (
    <div className="space-y-3 pt-2 border-t border-[#E8E0D6]">
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        rows={3}
        placeholder="What would you like changed?"
        className="w-full px-3 py-2 bg-[#FAF6F1] border border-[#E8E0D6] rounded-lg text-sm focus:outline-none focus:border-[#6B5B4E] placeholder:text-[#B0A396] resize-none"
        autoFocus
      />
      <div className="flex gap-2">
        <button
          onClick={() => onSubmit(comment)}
          disabled={!comment.trim() || submitting}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-500 transition disabled:opacity-50"
        >
          {submitting ? "Submitting..." : "Submit Feedback"}
        </button>
        <button
          onClick={onCancel}
          className="px-4 py-2 text-[#8C7E6F] text-sm hover:text-[#1a1a1a] transition"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
