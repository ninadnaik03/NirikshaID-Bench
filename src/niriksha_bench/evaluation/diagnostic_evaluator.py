import json
import statistics
from collections import defaultdict

from niriksha_bench.generator.diagnostic_schemas import CounterfactualPair, HardNegativeRecord
from niriksha_bench.generator.schemas import DocumentLabel
from niriksha_bench.models.tesseract_ocr import TesseractOCRAdapter
from niriksha_bench.utils.paths import resolve_project_path

from .calibration_metrics import (
    brier_score,
    expected_calibration_error,
    risk_coverage_curve,
    selective_operating_points,
    tamper_probability,
)
from .localization_metrics import bbox_iou
from .tamper_metrics import binary_metrics


def _jsonl(path, schema):
    return [schema.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _field_stability(genuine, tampered, excluded: str) -> float:
    fields = ["full_name", "guardian_name", "date_of_birth", "identity_number", "document_id"]
    considered = [field for field in fields if field != excluded]
    return sum(getattr(genuine.fields, field) == getattr(tampered.fields, field) for field in considered) / len(considered)


def evaluate_diagnostics(model: str = "ocr") -> dict:
    if model != "ocr":
        raise ValueError("The CPU diagnostic runner currently supports the image-only OCR baseline")
    generated = resolve_project_path("data/generated")
    diagnostic_root = resolve_project_path("data/diagnostics")
    train = _jsonl(generated / "manifests/train.jsonl", DocumentLabel)
    base_seen = _jsonl(generated / "manifests/eval_seen.jsonl", DocumentLabel)[:20]
    pairs = _jsonl(diagnostic_root / "manifests/counterfactual_pairs.jsonl", CounterfactualPair)
    hard_negatives = _jsonl(diagnostic_root / "manifests/hard_negatives.jsonl", HardNegativeRecord)
    adapter = TesseractOCRAdapter()
    adapter.fit([(generated / label.image_path, label) for label in train])

    base_truth, base_pred = [], []
    degradation_confusions: dict[str, list[bool]] = defaultdict(list)
    calibration_truth: list[bool] = []
    calibration_pred: list[bool] = []
    calibration_confidence: list[float] = []
    all_records = []
    failures = []

    for label in base_seen:
        record = adapter.predict(generated / label.image_path)
        all_records.append(record)
        prediction = record.prediction
        if not prediction or prediction.tampered is None:
            continue
        base_truth.append(label.tampered)
        base_pred.append(prediction.tampered)
        calibration_truth.append(label.tampered)
        calibration_pred.append(prediction.tampered)
        calibration_confidence.append(prediction.confidence)
        if not label.tampered:
            kinds = [item.type for item in label.degradations] or ["clean"]
            for kind in kinds:
                degradation_confusions[kind].append(prediction.tampered)

    hard_rows = []
    for item in hard_negatives:
        record = adapter.predict(diagnostic_root / item.image_path)
        all_records.append(record)
        prediction = record.prediction
        verdict = bool(prediction and prediction.tampered)
        hard_rows.append(
            {
                "doc_id": item.doc_id,
                "hard_negative_type": item.hard_negative_type,
                "false_positive": verdict,
                "confidence": prediction.confidence if prediction else None,
                "prediction": prediction.model_dump(mode="json") if prediction else None,
                "image_url": f"/api/diagnostic-assets/{item.image_path}",
            }
        )
        calibration_truth.append(False)
        calibration_pred.append(verdict)
        calibration_confidence.append(prediction.confidence if prediction else 0)
        if verdict:
            failures.append(
                {
                    "doc_id": item.doc_id,
                    "image_url": f"/api/diagnostic-assets/{item.image_path}",
                    "failure_category": "hard-negative false positive",
                    "tamper_type": "none",
                    "reason": f"Legitimate {item.hard_negative_type.replace('_', ' ')} was confused with manipulation.",
                    "ground_truth": {"tamper_type": "none", "hard_negative_type": item.hard_negative_type},
                    "prediction": prediction.model_dump(mode="json") if prediction else None,
                }
            )

    pair_rows = []
    for pair in pairs:
        genuine_record = adapter.predict(diagnostic_root / pair.genuine_image_path)
        tampered_record = adapter.predict(diagnostic_root / pair.tampered_image_path)
        all_records.extend([genuine_record, tampered_record])
        genuine, tampered = genuine_record.prediction, tampered_record.prediction
        if not genuine or not tampered:
            continue
        genuine_verdict, tampered_verdict = bool(genuine.tampered), bool(tampered.tampered)
        genuine_probability = tamper_probability(genuine.tampered, genuine.confidence, genuine.abstain)
        tampered_probability = tamper_probability(tampered.tampered, tampered.confidence, tampered.abstain)
        localization = bbox_iou(pair.tamper_bbox, tampered.tamper_bbox)
        row = {
            "pair_id": pair.pair_id,
            "tamper_type": pair.tamper_type,
            "genuine_image_url": f"/api/diagnostic-assets/{pair.genuine_image_path}",
            "tampered_image_url": f"/api/diagnostic-assets/{pair.tampered_image_path}",
            "genuine_tamper_probability": genuine_probability,
            "tampered_tamper_probability": tampered_probability,
            "confidence_change": tampered_probability - genuine_probability,
            "verdict_flip": genuine_verdict != tampered_verdict,
            "correct_verdict_flip": not genuine_verdict and tampered_verdict,
            "outside_field_extraction_stability": _field_stability(genuine, tampered, pair.tampered_field),
            "localization_iou": localization,
            "genuine_prediction": genuine.model_dump(mode="json"),
            "tampered_prediction": tampered.model_dump(mode="json"),
        }
        pair_rows.append(row)
        calibration_truth.extend([False, True])
        calibration_pred.extend([genuine_verdict, tampered_verdict])
        calibration_confidence.extend([genuine.confidence, tampered.confidence])
        if not row["correct_verdict_flip"]:
            failures.append(
                {
                    "doc_id": pair.pair_id,
                    "image_url": row["tampered_image_url"],
                    "failure_category": "counterfactual sensitivity",
                    "tamper_type": pair.tamper_type,
                    "reason": "The verdict did not correctly change when only the tamper intervention changed.",
                    "ground_truth": {"tamper_type": pair.tamper_type, "paired_genuine": True},
                    "prediction": tampered.model_dump(mode="json"),
                }
            )

    by_hard_type = {}
    for kind in sorted({row["hard_negative_type"] for row in hard_rows}):
        subset = [row for row in hard_rows if row["hard_negative_type"] == kind]
        by_hard_type[kind] = {
            "false_positive_rate": sum(row["false_positive"] for row in subset) / len(subset),
            "support": len(subset),
        }
    before = binary_metrics(base_truth, base_pred)
    after = binary_metrics(base_truth + [False] * len(hard_rows), base_pred + [row["false_positive"] for row in hard_rows])
    curve = risk_coverage_curve(calibration_truth, calibration_pred, calibration_confidence)
    probabilities = [
        confidence if prediction else 1 - confidence
        for prediction, confidence in zip(calibration_pred, calibration_confidence)
    ]
    report = {
        "status": "completed",
        "model": {
            "id": adapter.name,
            "display_name": "Template-Aware Tesseract OCR + Visual RF",
            "version": adapter.version,
        },
        "diagnostic_version": "1.1.0",
        "hard_negatives": {
            "samples": len(hard_rows),
            "false_positive_rate": sum(row["false_positive"] for row in hard_rows) / len(hard_rows),
            "by_type": by_hard_type,
            "tamper_f1_before": before["f1"],
            "tamper_f1_after": after["f1"],
            "degradation_false_positive_rate": {
                kind: {
                    "rate": sum(values) / len(values),
                    "support": len(values),
                }
                for kind, values in degradation_confusions.items()
            },
        },
        "counterfactual_pairs": {
            "pairs": len(pair_rows),
            "pairwise_tamper_sensitivity": statistics.mean(row["confidence_change"] for row in pair_rows),
            "verdict_flip_rate": statistics.mean(row["verdict_flip"] for row in pair_rows),
            "correct_verdict_flip_rate": statistics.mean(row["correct_verdict_flip"] for row in pair_rows),
            "outside_field_extraction_stability": statistics.mean(
                row["outside_field_extraction_stability"] for row in pair_rows
            ),
            "mean_localization_iou": statistics.mean(
                row["localization_iou"] for row in pair_rows if row["localization_iou"] is not None
            ) if any(row["localization_iou"] is not None for row in pair_rows) else None,
            "by_tamper_type": {
                kind: {
                    "support": len(subset),
                    "correct_verdict_flip_rate": statistics.mean(row["correct_verdict_flip"] for row in subset),
                    "mean_confidence_change": statistics.mean(row["confidence_change"] for row in subset),
                }
                for kind in sorted({row["tamper_type"] for row in pair_rows})
                if (subset := [row for row in pair_rows if row["tamper_type"] == kind])
            },
        },
        "calibration": {
            "samples": len(calibration_truth),
            "brier_score": brier_score(calibration_truth, probabilities),
            **expected_calibration_error(calibration_truth, calibration_pred, calibration_confidence),
            "risk_coverage_curve": curve,
            "selective_operating_points": selective_operating_points(curve),
            "native_abstentions": sum(
                bool(record.prediction and record.prediction.abstain) for record in all_records
            ),
        },
    }
    results = diagnostic_root / "results" / adapter.name
    results.mkdir(parents=True, exist_ok=True)
    (results / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (results / "pair-results.json").write_text(json.dumps(pair_rows, indent=2), encoding="utf-8")
    (results / "hard-negative-results.json").write_text(json.dumps(hard_rows, indent=2), encoding="utf-8")
    (results / "failures.json").write_text(json.dumps(failures[:24], indent=2), encoding="utf-8")
    (results / "predictions.jsonl").write_text(
        "\n".join(record.model_dump_json() for record in all_records) + "\n", encoding="utf-8"
    )
    return report
