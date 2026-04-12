"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useProject } from "@/lib/hooks";
import { getStageAssets, approveAllStage } from "@/lib/api";
import StageProgress from "@/components/review/StageProgress";
import AssetCard from "@/components/review/AssetCard";

interface Asset {
  id: string;
  asset_type: string;
  file_path: string | null;
  text_content: string | null;
  version: number;
  status: string;
  metadata: string | null;
}

interface Stage {
  stage_number: number;
  stage_name: string;
  status: string;
}

function ProjectDashboardInner() {
  const searchParams = useSearchParams();
  const id = searchParams.get("id") || "";
  const { project, loading, refresh, lastEvent } = useProject(id || null);
  const [activeStage, setActiveStage] = useState(1);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loadingAssets, setLoadingAssets] = useState(false);

  const stages = (project?.stages as Stage[]) || [];
  const currentStage = stages.find(
    (s: Stage) => s.stage_number === activeStage
  );

  useEffect(() => {
    if (!id) return;
    setLoadingAssets(true);
    getStageAssets(id, activeStage)
      .then(setAssets)
      .catch(console.error)
      .finally(() => setLoadingAssets(false));
  }, [id, activeStage, lastEvent]);

  useEffect(() => {
    if (project?.current_stage) {
      setActiveStage(project.current_stage as number);
    }
  }, [project?.current_stage]);

  const handleApproveAll = async () => {
    await approveAllStage(id, activeStage);
    refresh();
  };

  const pendingCount = assets.filter(
    (a) => a.status === "pending_review"
  ).length;

  if (!id) {
    return (
      <div className="flex items-center justify-center h-96 text-[#8C7E6F]">
        No project ID provided
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-[#8C7E6F]">
        Loading project...
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex items-center justify-center h-96 text-[#8C7E6F]">
        Project not found
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#1a1a1a]">
            {project.title as string}
          </h1>
          <p className="text-sm text-[#8C7E6F] mt-1">
            {project.status as string} &middot; Stage{" "}
            {project.current_stage as number}/6
          </p>
        </div>
        {lastEvent && (
          <div
            className={`px-3 py-1.5 rounded-lg text-xs ${
              lastEvent.type === "error"
                ? "bg-red-100 text-red-700"
                : "bg-blue-100 text-blue-700"
            }`}
          >
            {lastEvent.type.replace("_", " ")}
          </div>
        )}
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left: Stage Progress */}
        <div className="col-span-3">
          <StageProgress
            stages={stages}
            activeStage={activeStage}
            onStageClick={setActiveStage}
          />
        </div>

        {/* Right: Asset Review */}
        <div className="col-span-9">
          {currentStage && (
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-[#1a1a1a]">
                  {currentStage.stage_name}
                </h2>
                <p className="text-sm text-[#8C7E6F] capitalize">
                  {currentStage.status.replace("_", " ")}
                </p>
              </div>
              {pendingCount > 1 && (
                <button
                  onClick={handleApproveAll}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-500 transition"
                >
                  Approve All ({pendingCount})
                </button>
              )}
            </div>
          )}

          {currentStage?.status === "running" && (
            <div className="flex items-center justify-center h-64 text-[#8C7E6F]">
              <div className="text-center">
                <div className="animate-pulse text-4xl mb-4 text-[#6B5B4E]">&#x25D4;</div>
                <p>Friday is working on {currentStage.stage_name}...</p>
              </div>
            </div>
          )}

          {currentStage?.status === "pending" && (
            <div className="flex items-center justify-center h-64 text-[#B0A396]">
              <p>Waiting for previous stages to complete</p>
            </div>
          )}

          {loadingAssets ? (
            <p className="text-[#8C7E6F]">Loading assets...</p>
          ) : assets.length === 0 &&
            currentStage?.status !== "running" &&
            currentStage?.status !== "pending" ? (
            <p className="text-[#B0A396]">No assets generated yet</p>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {assets.map((asset) => (
                <AssetCard key={asset.id} asset={asset} onUpdate={refresh} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ProjectDashboard() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-96 text-[#8C7E6F]">
          Loading...
        </div>
      }
    >
      <ProjectDashboardInner />
    </Suspense>
  );
}
