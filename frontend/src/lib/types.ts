// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

export type AssetType =
  | "script"
  | "character_sheet"
  | "keyframe"
  | "clip"
  | "audio"
  | "final_video";

export type AssetStatus = "pending_review" | "approved" | "rejected";

export type StageStatus =
  | "pending"
  | "running"
  | "awaiting_review"
  | "approved"
  | "failed";

export type MediaType = "photo" | "video";

export type StyleType = "original" | "anime" | "pixar";

export type SoundtrackMode = "upload" | "ai_generate";

export type ProjectStatus = "draft" | "processing" | "completed";

// ---------------------------------------------------------------------------
// Resource interfaces
// ---------------------------------------------------------------------------

export interface Asset {
  id: string;
  project_id: string;
  stage_id: string;
  asset_type: AssetType;
  file_path: string | null;
  text_content: string | null;
  version: number;
  status: AssetStatus;
  metadata: string | null;
  created_at: string;
}

export interface Stage {
  id: string;
  project_id: string;
  stage_number: number;
  stage_name: string;
  status: StageStatus;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface Upload {
  id: string;
  project_id: string;
  filename: string;
  file_path: string;
  media_type: MediaType;
  style: StyleType;
  sort_order: number;
  created_at: string;
  /** Added by the upload API route, not present in DB rows. */
  url?: string;
}

export interface SoundtrackConfig {
  project_id: string;
  mode: SoundtrackMode;
  uploaded_path: string | null;
}

export interface Project {
  id: string;
  title: string;
  brief: string;
  status: ProjectStatus;
  current_stage: number;
  created_at: string;
  updated_at: string;
  uploads: Upload[] | null;
  stages: Stage[] | null;
  soundtrack: SoundtrackConfig | null;
}

// ---------------------------------------------------------------------------
// SSE event data shapes
// ---------------------------------------------------------------------------

export interface StageStartedData {
  stage: number;
  name: string;
}

export interface StageCompleteData {
  stage: number;
  asset_count: number;
}

export interface StageApprovedData {
  stage: number;
}

export interface ErrorData {
  stage: number;
  message: string;
}

export type SSEEventData =
  | StageStartedData
  | StageCompleteData
  | StageApprovedData
  | ErrorData;

export interface SSEEvent {
  type: "stage_started" | "asset_generated" | "stage_complete" | "stage_approved" | "error";
  data: SSEEventData;
}

// ---------------------------------------------------------------------------
// API response shapes
// ---------------------------------------------------------------------------

export interface OkResponse {
  ok: boolean;
}

export interface ApproveResponse extends OkResponse {
  status: "approved";
}

export interface RejectResponse extends OkResponse {
  status: "rejected";
  comment: string | null;
}

export interface PipelineStartResponse extends OkResponse {
  stages: Stage[];
}
