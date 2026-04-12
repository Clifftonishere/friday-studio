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
  pending: "\u25cb",
  running: "\u25d4",
  awaiting_review: "\u25c9",
  approved: "\u2713",
  failed: "\u2717",
};

const STATUS_COLOR: Record<string, string> = {
  pending: "text-[#B0A396]",
  running: "text-blue-500",
  awaiting_review: "text-amber-600",
  approved: "text-green-600",
  failed: "text-red-600",
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
              ? "bg-white border border-[#D4C9BC] shadow-sm"
              : "hover:bg-white/60"
          }`}
        >
          <div className="flex flex-col items-center w-6">
            <span
              className={`text-lg ${STATUS_COLOR[s.status] || "text-[#B0A396]"} ${
                s.status === "running" ? "animate-pulse" : ""
              }`}
            >
              {STATUS_ICON[s.status] || "\u25cb"}
            </span>
            {i < stages.length - 1 && (
              <div
                className={`w-px h-4 mt-1 ${
                  s.status === "approved" ? "bg-green-300" : "bg-[#E8E0D6]"
                }`}
              />
            )}
          </div>

          <div className="min-w-0">
            <p className="text-sm font-medium text-[#1a1a1a] truncate">{s.stage_name}</p>
            <p
              className={`text-xs capitalize ${
                STATUS_COLOR[s.status] || "text-[#B0A396]"
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
