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
    <div className="space-y-3 pt-2 border-t border-white/10">
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        rows={3}
        placeholder="What would you like changed?"
        className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm focus:outline-none focus:border-white/30 placeholder:text-white/20 resize-none"
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
          className="px-4 py-2 text-white/50 text-sm hover:text-white transition"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
