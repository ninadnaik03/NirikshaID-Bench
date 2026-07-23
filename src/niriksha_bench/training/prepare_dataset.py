from pathlib import Path

from niriksha_bench.generator.schemas import DocumentLabel


def allowed_training_examples(manifest: Path) -> list[DocumentLabel]:
    labels = [DocumentLabel.model_validate_json(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
    if any(label.tamper_type == "digit_edit" for label in labels):
        raise ValueError("Held-out digit_edit examples cannot be used for tuning")
    return labels

