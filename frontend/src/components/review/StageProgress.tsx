"use client";

interface Stage {
  stage_number: number;
  stage_name: string;
  status: string;
}

interface Props {
  stages: Stage[];
  activeStage: number;
  onStageClick: (num: number) => void;
}

const STATUS_ICON: Record<string, string> = {
  pending: "\u25cb",        // empty circle
  running: "\u25d4",        // half circle (spinner)
  awaiting_review: "\u25c9", // eye-like
  approved: "\u2713",       // checkmark
  failed: "\u2717",         // x mark
};

const STATUS_COLOR: Record<string, string> = {
  pending: "text-white/20",
  running: "text-blue-400",
  awaiting_review: "text-yellow-400",
  approved: "text-green-400",
  failed: "text-red-400",
};

export default function StageProgress({ stages, activeStage, onStageClick }: Props) {
  return (
    <div className="space-y-1">
      {stages.map((s, i) => (
        <button
          key={s.stage_number}
          onClick={() => onStageClick(s.stage_number)}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition ${
            activeStage === s.stage_number
              ? "bg-white/10 border border-white/20"
              : "hover:bg-white/5"
          }`}
        >
          {/* Connector line */}
          <div className="flex flex-col items-center w-6">
            <span
              className={`text-lg ${STATUS_COLOR[s.status] || "text-white/20"} ${
                s.status === "running" ? "animate-pulse" : ""
              }`}
            >
              {STATUS_ICON[s.status] || "\u25cb"}
            </span>
            {i < stages.length - 1 && (
              <div
                className={`w-px h-4 mt-1 ${
                  s.status === "approved" ? "bg-green-400/30" : "bg-white/10"
                }`}
              />
            )}
          </div>

          <div className="min-w-0">
            <p className="text-sm font-medium truncate">{s.stage_name}</p>
            <p
              className={`text-xs capitalize ${
                STATUS_COLOR[s.status] || "text-white/30"
              }`}
            >
              {s.status.replace("_", " ")}
            </p>
          </div>
        </button>
      ))}
    </div>
  );
}
