import json
from pathlib import Path

from PIL import Image, ImageChops

from niriksha_bench.utils.paths import resolve_project_path

from .diagnostic_schemas import CounterfactualPair, HardNegativeRecord


def _records(path: Path, schema):
    return [schema.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()]


def validate_diagnostics(root: str = "data/diagnostics") -> dict:
    base = resolve_project_path(root)
    pairs = _records(base / "manifests/counterfactual_pairs.jsonl", CounterfactualPair)
    hard_negatives = _records(base / "manifests/hard_negatives.jsonl", HardNegativeRecord)
    errors = []
    for pair in pairs:
        genuine_path, tampered_path = base / pair.genuine_image_path, base / pair.tampered_image_path
        if not genuine_path.exists() or not tampered_path.exists():
            errors.append({"pair_id": pair.pair_id, "error": "missing_pair_image"})
            continue
        with Image.open(genuine_path) as genuine, Image.open(tampered_path) as tampered:
            if genuine.size != tampered.size:
                errors.append({"pair_id": pair.pair_id, "error": "pair_size_mismatch"})
            if ImageChops.difference(genuine.convert("RGB"), tampered.convert("RGB")).getbbox() is None:
                errors.append({"pair_id": pair.pair_id, "error": "intervention_has_no_pixel_effect"})
            width, height = genuine.size
        box = pair.tamper_bbox
        if not (0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height):
            errors.append({"pair_id": pair.pair_id, "error": "invalid_tamper_bbox"})
    for record in hard_negatives:
        path = base / record.image_path
        if not path.exists():
            errors.append({"doc_id": record.doc_id, "error": "missing_hard_negative"})
        if record.tampered:
            errors.append({"doc_id": record.doc_id, "error": "hard_negative_marked_tampered"})
    report = {
        "valid": not errors,
        "pairs": len(pairs),
        "hard_negatives": len(hard_negatives),
        "errors": errors,
    }
    (base / "manifests/validation-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
