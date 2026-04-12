"use client";

import { useEffect, useState } from "react";
import { listProjects } from "@/lib/api";

interface Project {
  id: string;
  title: string;
  brief: string;
  status: string;
  current_stage: number;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-amber-100 text-amber-700",
  processing: "bg-blue-100 text-blue-700",
  review: "bg-purple-100 text-purple-700",
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function HomePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProjects()
      .then(setProjects)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-[#1a1a1a]">Projects</h1>
        <a
          href="/new"
          className="px-5 py-2.5 bg-[#6B5B4E] text-white rounded-lg font-medium hover:bg-[#5A4A3E] transition"
        >
          New Project
        </a>
      </div>

      {loading ? (
        <p className="text-[#8C7E6F]">Loading...</p>
      ) : projects.length === 0 ? (
        <div className="text-center py-20 text-[#8C7E6F]">
          <p className="text-lg mb-2">No projects yet</p>
          <p>Create your first animated video project</p>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((p) => (
            <a
              key={p.id}
              href={`/project?id=${p.id}`}
              className="block p-5 rounded-xl bg-white border border-[#E8E0D6] hover:border-[#D4C9BC] hover:shadow-sm transition"
            >
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-semibold text-[#1a1a1a]">{p.title}</h2>
                <span
                  className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[p.status] || ""}`}
                >
                  {p.status}
                </span>
              </div>
              <p className="text-sm text-[#8C7E6F] line-clamp-2">{p.brief}</p>
              <p className="text-xs text-[#B0A396] mt-2">
                {new Date(p.created_at).toLocaleDateString()}
                {p.current_stage > 0 && ` \u00b7 Stage ${p.current_stage}/6`}
              </p>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
