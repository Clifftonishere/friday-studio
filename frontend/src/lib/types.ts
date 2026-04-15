// Shared API/domain types used across the Friday Studio frontend.

export interface Asset {
  id: string;
  asset_type: string;
  file_path: string | null;
  text_content: string | null;
  version: number;
  status: string;
  metadata: string | null;
}

export interface Stage {
  stage_number: number;
  stage_name: string;
  status: string;
}

export interface Upload {
  id: string;
  filename: string;
  media_type: string;
  style: string;
  url?: string;
}
