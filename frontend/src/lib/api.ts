export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request(path: string, options?: RequestInit) {
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

// Projects
export async function createProject(title: string, brief: string) {
  return request("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, brief }),
  });
}

export async function listProjects() {
  return request("/api/projects");
}

export async function getProject(id: string) {
  return request(`/api/projects/${id}`);
}

// Uploads
export async function uploadMedia(projectId: string, file: File, style: string) {
  const form = new FormData();
  form.append("file", file);
  form.append("style", style);
  return request(`/api/projects/${projectId}/uploads`, {
    method: "POST",
    body: form,
  });
}

export async function updateUploadStyle(projectId: string, uploadId: string, style: string) {
  return request(`/api/projects/${projectId}/uploads/${uploadId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ style }),
  });
}

export async function bulkUpdateStyle(projectId: string, style: string) {
  return request(`/api/projects/${projectId}/uploads/bulk-style`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ style }),
  });
}

export async function deleteUpload(projectId: string, uploadId: string) {
  return request(`/api/projects/${projectId}/uploads/${uploadId}`, {
    method: "DELETE",
  });
}

// Soundtrack
export async function setSoundtrack(projectId: string, mode: string, file?: File) {
  const form = new FormData();
  form.append("mode", mode);
  if (file) form.append("file", file);
  return request(`/api/projects/${projectId}/soundtrack`, {
    method: "POST",
    body: form,
  });
}

// Pipeline
export async function startPipeline(projectId: string) {
  return request(`/api/projects/${projectId}/start`, { method: "POST" });
}

export async function getStageAssets(projectId: string, stageNum: number) {
  return request(`/api/projects/${projectId}/stages/${stageNum}/assets`);
}

// Feedback
export async function approveAsset(assetId: string) {
  return request(`/api/assets/${assetId}/approve`, { method: "POST" });
}

export async function rejectAsset(assetId: string, comment: string) {
  return request(`/api/assets/${assetId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment }),
  });
}

export async function approveAllStage(projectId: string, stageNum: number) {
  return request(`/api/projects/${projectId}/stages/${stageNum}/approve-all`, {
    method: "POST",
  });
}

// File URLs
export function fileUrl(path: string) {
  if (!path) return "";
  // Extract the project-relative path from absolute path
  const match = path.match(/projects\/(.+)/);
  if (match) return `${API_URL}/files/${match[1]}`;
  return path;
}
