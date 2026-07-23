export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function fetchApi<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export type Stats = {
  total: number;
  splits?: Record<string, number>;
  tamper_types?: Record<string, number>;
  tampered?: Record<string, number>;
  degradations?: Record<string, number>;
  seed?: number;
};

export type BenchmarkRun = {
  split: string;
  samples: number;
  model: { id: string; display_name: string; version: string; kind: string; mode: string; quantization: string; is_vlm: boolean };
  dataset_version: string;
  run_name: string;
  prompt_version: string;
  small_sample_warning: boolean;
  field_extraction: {
    macro_normalized_exact_match: number;
    per_field: Record<string, { normalized_exact_match: number; cer: number }>;
  };
  tamper_detection: { precision: number; recall: number; f1: number; confusion_matrix: number[][] };
  tamper_type: { macro_f1: number };
  localization: { mean_iou: number | null; iou_at_0_5: number | null };
  held_out_digit_edit: { recall: number; support: number; wilson_95_ci: number[] | null } | null;
  robustness: { clean_field_em: number | null; clean_support: number; degraded_field_em: number | null; degraded_support: number; performance_drop: number | null };
  efficiency: { median_latency_ms: number; parse_success_rate: number; failure_rate: number };
};

export type GalleryItem = {
  doc_id: string;
  image_url: string;
  tampered: boolean;
  tamper_type: string;
  degradations: { type: string; severity: number }[];
  ground_truth: {
    displayed_fields: Record<string, string>;
    tamper_bbox: number[] | null;
    tampered_field: string | null;
  };
  predictions: {
    latency_ms: number;
    parser_repaired: boolean;
    prediction: {
      fields: Record<string, string>;
      tampered: boolean;
      tamper_type: string;
      tamper_bbox: number[] | null;
      confidence: number;
      reason: string;
    };
  }[];
};
