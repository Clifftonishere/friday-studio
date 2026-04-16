"use client";

import { useState, useEffect, useCallback } from "react";
import { getProject, API_URL } from "./api";

interface SSEEvent {
  type: string;
  data: Record<string, unknown>;
}

function useProjectEvents(projectId: string | null) {
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const source = new EventSource(`${API_URL}/api/projects/${projectId}/events`);

    const handleEvent = (type: string) => (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data);
        setLastEvent({ type, data });
      } catch {}
    };

    const eventTypes = [
      "stage_started",
      "asset_generated",
      "stage_complete",
      "stage_approved",
      "error",
    ];
    eventTypes.forEach((t) => source.addEventListener(t, handleEvent(t)));

    return () => source.close();
  }, [projectId]);

  return lastEvent;
}

export function useProject(projectId: string | null) {
  const [project, setProject] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const lastEvent = useProjectEvents(projectId);

  const refresh = useCallback(async () => {
    if (!projectId) return;
    try {
      const data = await getProject(projectId);
      setProject(data);
    } catch (err) {
      console.error("Failed to fetch project:", err);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Refetch on SSE events
  useEffect(() => {
    if (lastEvent) refresh();
  }, [lastEvent, refresh]);

  return { project, loading, refresh, lastEvent };
}
