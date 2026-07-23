import argparse
import json
import random
from collections import Counter
import yaml

from niriksha_bench.utils.paths import resolve_project_path

from .degradations import apply_degradations
from .diagnostic_schemas import CounterfactualPair, HardNegativeRecord
from .fields import generate_fields
from .hard_negatives import apply_hard_negative
from .renderer import render
from .tampers import apply_tamper


def generate_diagnostics(config_path: str = "configs/diagnostics.yaml") -> dict:
    config = yaml.safe_load(resolve_project_path(config_path).read_text(encoding="utf-8"))
    root = resolve_project_path(config["output_dir"])
    pair_dir = root / "pairs"
    hard_dir = root / "hard_negatives"
    for directory in (pair_dir, hard_dir, root / "manifests"):
        directory.mkdir(parents=True, exist_ok=True)
    degradation_config = {"blur_probability": 0.45, "noise_probability": 0.4, "jpeg_probability": 0.55}
    pairs = []
    tamper_types = config["counterfactual_pairs"]["tamper_types"]
    for index in range(config["counterfactual_pairs"]["count"]):
        seed = config["seed"] + index
        fields = generate_fields(10_000 + index, random.Random(seed))
        clean, bboxes = render(fields, seed)
        tamper_type = tamper_types[index % len(tamper_types)]
        intervention_seed = seed + 100_000
        tampered, displayed, field, bbox = apply_tamper(
            clean, fields, bboxes, tamper_type, random.Random(intervention_seed)
        )
        degradation_seed = seed + 200_000
        genuine_final, degradations = apply_degradations(
            clean, random.Random(degradation_seed), degradation_config
        )
        tampered_final, tampered_degradations = apply_degradations(
            tampered, random.Random(degradation_seed), degradation_config
        )
        if degradations != tampered_degradations:
            raise RuntimeError("Pair degradation replay diverged")
        pair_id = f"pair_{index:04d}"
        genuine_name, tampered_name = f"{pair_id}_genuine.jpg", f"{pair_id}_tampered.jpg"
        genuine_final.save(pair_dir / genuine_name, quality=92)
        tampered_final.save(pair_dir / tampered_name, quality=92)
        pairs.append(
            CounterfactualPair(
                pair_id=pair_id,
                genuine_doc_id=f"{pair_id}_genuine",
                tampered_doc_id=f"{pair_id}_tampered",
                genuine_image_path=f"pairs/{genuine_name}",
                tampered_image_path=f"pairs/{tampered_name}",
                source_fields=fields,
                tampered_displayed_fields=displayed,
                tamper_type=tamper_type,
                tampered_field=field,
                tamper_bbox=bbox,
                degradations=degradations,
                intervention_seed=intervention_seed,
                degradation_seed=degradation_seed,
                generator_version=config["version"],
            )
        )
    hard_negatives = []
    kinds = config["hard_negatives"]["types"]
    for index in range(config["hard_negatives"]["count"]):
        seed = config["seed"] + 500_000 + index
        rng = random.Random(seed)
        fields = generate_fields(20_000 + index, rng)
        image, bboxes = render(fields, seed)
        kind = kinds[index % len(kinds)]
        image, suspicious_bbox = apply_hard_negative(
            image, kind, fields.model_dump(), bboxes, rng
        )
        doc_id = f"hardneg_{index:04d}"
        filename = f"{doc_id}.jpg"
        image.save(hard_dir / filename, quality=92)
        hard_negatives.append(
            HardNegativeRecord(
                doc_id=doc_id,
                image_path=f"hard_negatives/{filename}",
                fields=fields,
                hard_negative_type=kind,
                suspicious_bbox=suspicious_bbox,
                seed=seed,
                generator_version=config["version"],
            )
        )
    manifests = root / "manifests"
    (manifests / "counterfactual_pairs.jsonl").write_text(
        "\n".join(item.model_dump_json() for item in pairs) + "\n", encoding="utf-8"
    )
    (manifests / "hard_negatives.jsonl").write_text(
        "\n".join(item.model_dump_json() for item in hard_negatives) + "\n", encoding="utf-8"
    )
    stats = {
        "version": config["version"],
        "counterfactual_pairs": len(pairs),
        "paired_images": len(pairs) * 2,
        "pair_tamper_types": dict(Counter(item.tamper_type for item in pairs)),
        "hard_negatives": len(hard_negatives),
        "hard_negative_types": dict(Counter(item.hard_negative_type for item in hard_negatives)),
    }
    (manifests / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/diagnostics.yaml")
    args = parser.parse_args()
    print(json.dumps(generate_diagnostics(args.config), indent=2))


if __name__ == "__main__":
    main()
