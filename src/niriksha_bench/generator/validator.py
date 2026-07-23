import argparse
import json
from collections import Counter
from pathlib import Path

from PIL import Image
from pydantic import ValidationError

from niriksha_bench.utils.paths import resolve_project_path

from .schemas import DocumentLabel


def validate_dataset(root: str | Path = "data/generated") -> dict:
    root_path = resolve_project_path(root)
    errors: list[dict] = []
    labels: list[DocumentLabel] = []
    for label_path in sorted((root_path / "labels").glob("*.json")):
        try:
            label = DocumentLabel.model_validate_json(label_path.read_text(encoding="utf-8"))
            image_path = root_path / label.image_path
            if not image_path.exists():
                errors.append({"doc_id": label.doc_id, "error": "missing_image"})
                continue
            with Image.open(image_path) as image:
                width, height = image.size
            for name, bbox in label.field_bboxes.items():
                if len(bbox) != 4 or not (0 <= bbox[0] < bbox[2] <= width and 0 <= bbox[1] < bbox[3] <= height):
                    errors.append({"doc_id": label.doc_id, "error": "invalid_field_bbox", "field": name})
            if label.tamper_bbox and not (
                0 <= label.tamper_bbox[0] < label.tamper_bbox[2] <= width
                and 0 <= label.tamper_bbox[1] < label.tamper_bbox[3] <= height
            ):
                errors.append({"doc_id": label.doc_id, "error": "invalid_tamper_bbox"})
            labels.append(label)
        except (ValidationError, OSError, json.JSONDecodeError) as exc:
            errors.append({"file": str(label_path), "error": str(exc)})
    if any(label.tamper_type == "digit_edit" for label in labels if label.split in {"train", "validation"}):
        errors.append({"error": "held_out_leakage"})
    unseen = [label for label in labels if label.split == "eval_unseen"]
    if unseen and not any(label.tamper_type == "digit_edit" for label in unseen):
        errors.append({"error": "missing_held_out_digit_edit"})
    for split in ("eval_seen", "eval_unseen"):
        subset = [label for label in labels if label.split == split]
        if subset:
            ratio = sum(label.tampered for label in subset) / len(subset)
            if abs(ratio - 0.5) > 0.06:
                errors.append({"error": "evaluation_imbalance", "split": split, "ratio": ratio})
    report = {
        "valid": not errors,
        "documents": len(labels),
        "errors": errors,
        "splits": dict(Counter(label.split for label in labels)),
        "tamper_types": dict(Counter(label.tamper_type for label in labels)),
    }
    report_path = root_path / "manifests" / "validation-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data/generated")
    args = parser.parse_args()
    report = validate_dataset(args.root)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()

