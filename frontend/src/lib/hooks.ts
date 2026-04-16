"use client";

import { useState, useEffect, useCallback } from "react";
import { getProject, API_URL } from "./api";
import type { Project, SSEEvent, SSEEventData } from "./types";

function useProjectEvents(projectId: string | null): SSEEvent | null {
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const source = new EventSource(`${API_URL}/api/projects/${projectId}/events`);

    const handleEvent = (type: SSEEvent["type"]) => (e: MessageEvent) => {
      const data: SSEEventData = JSON.parse(e.data);
      setLastEvent({ type, data });
    };

    const eventTypes: SSEEvent["type"][] = [
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
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const lastEvent = useProjectEvents(projectId);

  const refresh = useCallback(async () => {
    if (!projectId) return;
    const data = await getProject(projectId);
    setProject(data);
    setLoading(false);
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
