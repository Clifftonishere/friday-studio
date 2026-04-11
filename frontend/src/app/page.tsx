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
  draft: "bg-yellow-500/20 text-yellow-400",
  processing: "bg-blue-500/20 text-blue-400",
  review: "bg-purple-500/20 text-purple-400",
  completed: "bg-green-500/20 text-green-400",
  failed: "bg-red-500/20 text-red-400",
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
        <h1 className="text-3xl font-bold">Projects</h1>
        <a
          href="/new"
          className="px-5 py-2.5 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition"
        >
          New Project
        </a>
      </div>

      {loading ? (
        <p className="text-white/50">Loading...</p>
      ) : projects.length === 0 ? (
        <div className="text-center py-20 text-white/40">
          <p className="text-lg mb-2">No projects yet</p>
          <p>Create your first animated video project</p>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((p) => (
            <a
              key={p.id}
              href={`/project?id=${p.id}`}
              className="block p-5 rounded-xl border border-white/10 hover:border-white/20 transition"
            >
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-semibold">{p.title}</h2>
                <span
                  className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[p.status] || ""}`}
                >
                  {p.status}
                </span>
              </div>
              <p className="text-sm text-white/50 line-clamp-2">{p.brief}</p>
              <p className="text-xs text-white/30 mt-2">
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
