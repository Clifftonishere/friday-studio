import type {
  Project,
  Upload,
  Asset,
  OkResponse,
  ApproveResponse,
  RejectResponse,
  PipelineStartResponse,
} from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// Projects
export async function createProject(title: string, brief: string): Promise<Project> {
  return request<Project>("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, brief }),
  });
}

export async function listProjects(): Promise<Project[]> {
  return request<Project[]>("/api/projects");
}

export async function getProject(id: string): Promise<Project> {
  return request<Project>(`/api/projects/${id}`);
}

// Uploads
export async function uploadMedia(projectId: string, file: File, style: string): Promise<Upload> {
  const form = new FormData();
  form.append("file", file);
  form.append("style", style);
  return request<Upload>(`/api/projects/${projectId}/uploads`, {
    method: "POST",
    body: form,
  });
}

export async function updateUploadStyle(projectId: string, uploadId: string, style: string): Promise<OkResponse> {
  return request<OkResponse>(`/api/projects/${projectId}/uploads/${uploadId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ style }),
  });
}

export async function bulkUpdateStyle(projectId: string, style: string): Promise<OkResponse> {
  return request<OkResponse>(`/api/projects/${projectId}/uploads/bulk-style`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ style }),
  });
}

export async function deleteUpload(projectId: string, uploadId: string): Promise<OkResponse> {
  return request<OkResponse>(`/api/projects/${projectId}/uploads/${uploadId}`, {
    method: "DELETE",
  });
}

// Soundtrack
export async function setSoundtrack(projectId: string, mode: string, file?: File): Promise<OkResponse> {
  const form = new FormData();
  form.append("mode", mode);
  if (file) form.append("file", file);
  return request<OkResponse>(`/api/projects/${projectId}/soundtrack`, {
    method: "POST",
    body: form,
  });
}

// Pipeline
export async function startPipeline(projectId: string): Promise<PipelineStartResponse> {
  return request<PipelineStartResponse>(`/api/projects/${projectId}/start`, { method: "POST" });
}

export async function getStageAssets(projectId: string, stageNum: number): Promise<Asset[]> {
  return request<Asset[]>(`/api/projects/${projectId}/stages/${stageNum}/assets`);
}

// Feedback
export async function approveAsset(assetId: string): Promise<ApproveResponse> {
  return request<ApproveResponse>(`/api/assets/${assetId}/approve`, { method: "POST" });
}

export async function rejectAsset(assetId: string, comment: string): Promise<RejectResponse> {
  return request<RejectResponse>(`/api/assets/${assetId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment }),
  });
}

export async function approveAllStage(projectId: string, stageNum: number): Promise<OkResponse> {
  return request<OkResponse>(`/api/projects/${projectId}/stages/${stageNum}/approve-all`, {
    method: "POST",
  });
}

// File URLs
export function fileUrl(path: string): string {
  if (!path) return "";
  // Extract the project-relative path from absolute path
  const match = path.match(/projects\/(.+)/);
  if (match) return `${API_URL}/files/${match[1]}`;
  return path;
}
