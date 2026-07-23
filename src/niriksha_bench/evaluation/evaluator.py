import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from datetime import UTC, datetime

from niriksha_bench.generator.schemas import DocumentLabel
from niriksha_bench.models.qwen_vl import QwenVLAdapter
from niriksha_bench.models.tesseract_ocr import TesseractOCRAdapter
from niriksha_bench.utils.paths import resolve_project_path

from .extraction_metrics import field_scores
from .localization_metrics import bbox_iou
from .tamper_metrics import binary_metrics

FIELDS = ["full_name", "guardian_name", "date_of_birth", "identity_number", "document_id"]


def _read_manifest(split: str) -> list[DocumentLabel]:
    path = resolve_project_path(f"data/generated/manifests/{split}.jsonl")
    return [DocumentLabel.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _adapter(model: str):
    if model == "qwen":
        return QwenVLAdapter()
    if model == "ocr":
        adapter = TesseractOCRAdapter()
        training = _read_manifest("train")
        adapter.fit(
            [
                (resolve_project_path("data/generated") / label.image_path, label)
                for label in training
            ]
        )
        return adapter
    raise ValueError("Benchmark models are 'qwen' and 'ocr'. The Demo Stub is not benchmarkable.")


def _wilson(successes: int, total: int, z: float = 1.96) -> list[float] | None:
    if not total:
        return None
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0, centre - margin), min(1, centre + margin)]


def _failure_category(label: DocumentLabel, prediction, parse_failure: bool) -> str:
    if parse_failure:
        return "formatting"
    if prediction.tampered != label.tampered:
        return "perception"
    if prediction.tamper_type != label.tamper_type:
        return "reasoning"
    if label.tamper_bbox and prediction.tamper_bbox and (bbox_iou(label.tamper_bbox, prediction.tamper_bbox) or 0) < 0.5:
        return "localization"
    return "extraction"


def evaluate(split: str, model: str, limit: int | None = None, offset: int = 0) -> dict:
    adapter = _adapter(model)
    all_labels = _read_manifest(split)
    labels = all_labels[offset : offset + limit if limit else None]
    run_name = f"{split}-n{len(labels)}-o{offset}" if limit or offset else split
    result_dir = resolve_project_path(f"data/results/{adapter.name}/{run_name}")
    result_dir.mkdir(parents=True, exist_ok=True)
    records = []
    field_rows: list[dict] = []
    ious: list[float] = []
    truths: list[bool] = []
    predictions: list[bool] = []
    type_truth: list[str] = []
    type_pred: list[str] = []
    failures: list[dict] = []
    clean_doc_scores: list[float] = []
    degraded_doc_scores: list[float] = []

    for label in labels:
        image_path = resolve_project_path("data/generated") / label.image_path
        # Critical isolation boundary: only the image path enters prediction.
        record = adapter.predict(image_path)
        records.append(record)
        prediction = record.prediction
        if not prediction:
            failures.append(
                {
                    "doc_id": label.doc_id,
                    "split": label.split,
                    "image_url": f"/api/assets/{label.doc_id}.jpg",
                    "tamper_type": label.tamper_type,
                    "degradations": [item.model_dump() for item in label.degradations],
                    "ground_truth": label.model_dump(mode="json"),
                    "prediction": None,
                    "raw_response": record.raw_response,
                    "reason": record.failure or "Missing structured prediction",
                    "failure_category": "formatting",
                }
            )
            continue
        truths.append(label.tampered)
        predictions.append(prediction.tampered)
        type_truth.append(label.tamper_type)
        type_pred.append(prediction.tamper_type)
        doc_score = 0.0
        for field in FIELDS:
            scores = field_scores(getattr(label.displayed_fields, field), getattr(prediction.fields, field))
            field_rows.append(
                {
                    "doc_id": label.doc_id,
                    "field": field,
                    "degraded": bool(label.degradations),
                    **scores,
                }
            )
            doc_score += scores["normalized_exact_match"]
        normalized_doc_score = doc_score / len(FIELDS)
        (degraded_doc_scores if label.degradations else clean_doc_scores).append(normalized_doc_score)
        iou = bbox_iou(label.tamper_bbox, prediction.tamper_bbox)
        if iou is not None:
            ious.append(iou)
        if normalized_doc_score < 1 or label.tampered != prediction.tampered or label.tamper_type != prediction.tamper_type or (iou is not None and iou < 0.5):
            failures.append(
                {
                    "doc_id": label.doc_id,
                    "split": label.split,
                    "image_url": f"/api/assets/{label.doc_id}.jpg",
                    "tamper_type": label.tamper_type,
                    "degradations": [item.model_dump() for item in label.degradations],
                    "ground_truth": label.model_dump(mode="json"),
                    "prediction": prediction.model_dump(mode="json"),
                    "raw_response": record.raw_response,
                    "field_score": normalized_doc_score,
                    "reason": "Prediction differs from the injected label or visible field transcription.",
                    "failure_category": _failure_category(label, prediction, False),
                }
            )

    grouped = defaultdict(list)
    for row in field_rows:
        grouped[row["field"]].append(row)
    per_field = {
        field: {
            metric: statistics.mean(row[metric] for row in rows)
            for metric in ("exact_match", "normalized_exact_match", "cer", "fuzzy_score")
        }
        for field, rows in grouped.items()
    }
    types = sorted(set(type_truth) | set(type_pred))
    type_per_class = {}
    for kind in types:
        type_per_class[kind] = binary_metrics(
            [value == kind for value in type_truth],
            [value == kind for value in type_pred],
        )
    held_truth = [truth == "digit_edit" for truth in type_truth]
    held_pred = [pred == "digit_edit" for pred in type_pred]
    held = binary_metrics(held_truth, held_pred) if any(held_truth) else None
    clean_em = statistics.mean(clean_doc_scores) if clean_doc_scores else None
    degraded_em = statistics.mean(degraded_doc_scores) if degraded_doc_scores else None
    model_metadata = {
        "id": adapter.name,
        "display_name": "Qwen2.5-VL-3B-Instruct" if model == "qwen" else "Template-Aware Tesseract OCR + Visual RF",
        "version": adapter.version,
        "kind": "zero-shot local VLM" if model == "qwen" else "classical OCR + trained image features",
        "mode": "Zero-shot local inference via Ollama" if model == "qwen" else "Fixed-region OCR; RF fit on train pixels/labels",
        "quantization": "Ollama Q4_K_M" if model == "qwen" else "not applicable",
        "is_vlm": model == "qwen",
    }
    summary = {
        "status": "completed",
        "model": model_metadata,
        "dataset_version": labels[0].generator_version if labels else "unknown",
        "split": split,
        "run_name": run_name,
        "samples": len(labels),
        "sample_offset": offset,
        "timestamp": datetime.now(UTC).isoformat(),
        "prompt_version": records[0].prompt_version if records else None,
        "field_extraction": {
            "macro_normalized_exact_match": statistics.mean(
                score["normalized_exact_match"] for score in per_field.values()
            ) if per_field else 0,
            "per_field": per_field,
        },
        "robustness": {
            "clean_field_em": clean_em,
            "clean_support": len(clean_doc_scores),
            "degraded_field_em": degraded_em,
            "degraded_support": len(degraded_doc_scores),
            "performance_drop": clean_em - degraded_em if clean_em is not None and degraded_em is not None else None,
        },
        "tamper_detection": binary_metrics(truths, predictions),
        "tamper_type": {
            "macro_f1": statistics.mean(metrics["f1"] for metrics in type_per_class.values()) if type_per_class else 0,
            "per_class": type_per_class,
        },
        "localization": {
            "mean_iou": statistics.mean(ious) if ious else None,
            "iou_at_0_5": sum(value >= 0.5 for value in ious) / len(ious) if ious else None,
            "localized_samples": len(ious),
        },
        "held_out_digit_edit": {
            "recall": held["recall"],
            "support": sum(held_truth),
            "wilson_95_ci": _wilson(sum(t and p for t, p in zip(held_truth, held_pred)), sum(held_truth)),
        } if held else None,
        "efficiency": {
            "median_latency_ms": statistics.median(record.latency_ms for record in records) if records else 0,
            "failure_rate": sum(record.failure is not None for record in records) / len(records) if records else 0,
            "parse_success_rate": sum(record.prediction is not None for record in records) / len(records) if records else 0,
        },
        "small_sample_warning": len(labels) < 80,
    }
    (result_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (result_dir / "predictions.jsonl").write_text(
        "\n".join(record.model_dump_json() for record in records) + "\n", encoding="utf-8"
    )
    (result_dir / "failures.json").write_text(json.dumps(failures[:36], indent=2), encoding="utf-8")
    if field_rows:
        with (result_dir / "per-field.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=field_rows[0].keys())
            writer.writeheader()
            writer.writerows(field_rows)
    return summary


def combined_summary() -> dict:
    summaries = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in resolve_project_path("data/results").glob("*/*/metrics.json")
        if "demo-stub" not in str(path)
        and "deterministic-local-baseline" not in str(path)
        and json.loads(path.read_text(encoding="utf-8")).get("samples", 0) >= 20
    ]
    payload = {"status": "completed" if summaries else "not_executed", "runs": summaries}
    resolve_project_path("data/results").mkdir(parents=True, exist_ok=True)
    resolve_project_path("data/results/summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["qwen", "ocr"], required=True)
    parser.add_argument("--split", choices=["validation", "eval_seen", "eval_unseen"], required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.split, args.model, args.limit, args.offset), indent=2))
    combined_summary()


if __name__ == "__main__":
    main()
