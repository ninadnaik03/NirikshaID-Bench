import argparse
import json
import random
import shutil
from collections import Counter
from pathlib import Path

import yaml
from PIL import Image

from niriksha_bench.utils.paths import resolve_project_path

from .degradations import apply_degradations
from .fields import generate_fields
from .renderer import draw_bbox_overlay, render
from .schemas import DocumentLabel
from .tampers import apply_tamper


def load_config(path: str | Path) -> dict:
    with resolve_project_path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def split_sequence(config: dict, total: int | None = None) -> list[str]:
    counts = config["splits"]
    if total is None:
        total = config["total_samples"]
    order = ["train", "validation", "eval_seen", "eval_unseen", "demo_gallery"]
    if total == sum(counts.values()):
        return [split for split in order for _ in range(counts[split])]
    weights = [counts[key] / sum(counts.values()) for key in order]
    allocated = [int(total * weight) for weight in weights]
    for index in range(total - sum(allocated)):
        allocated[index % len(allocated)] += 1
    return [split for split, count in zip(order, allocated) for _ in range(count)]


def tamper_for(split: str, position: int, rng: random.Random) -> str:
    tampered = position % 2 == 1
    if not tampered:
        return "none"
    if split == "eval_unseen":
        return "digit_edit"
    return ["font_swap", "copy_paste_splice"][position % 4 // 2]


def _contact_sheet(items: list[tuple[Image.Image, DocumentLabel]], destination: Path, overlay: bool) -> None:
    if not items:
        return
    thumb_size = (384, 240)
    sheet = Image.new("RGB", (thumb_size[0] * 4, thumb_size[1] * 3), "#0C1720")
    for index, (image, label) in enumerate(items[:12]):
        rendered = draw_bbox_overlay(image, label.tamper_bbox) if overlay else image
        thumb = rendered.copy()
        thumb.thumbnail(thumb_size)
        sheet.paste(thumb, ((index % 4) * thumb_size[0], (index // 4) * thumb_size[1]))
    sheet.save(destination, quality=90)


def generate(config_path: str = "configs/dataset.yaml", total: int | None = None, clean: bool = False) -> dict:
    config = load_config(config_path)
    output = resolve_project_path(config["output_dir"])
    if clean and output.exists():
        shutil.rmtree(output)
    images_dir = output / "images"
    labels_dir = output / "labels"
    manifests_dir = output / "manifests"
    debug_dir = output / "debug"
    for directory in (images_dir, labels_dir, manifests_dir, debug_dir):
        directory.mkdir(parents=True, exist_ok=True)
    splits = split_sequence(config, total)
    labels: list[DocumentLabel] = []
    gallery: list[tuple[Image.Image, DocumentLabel]] = []
    manifest_handles = {
        split: (manifests_dir / f"{split}.jsonl").open("w", encoding="utf-8")
        for split in sorted(set(splits))
    }
    try:
        per_split_index: Counter[str] = Counter()
        for index, split in enumerate(splits):
            seed = config["seed"] + index
            rng = random.Random(seed)
            fields = generate_fields(index, rng)
            image, bboxes = render(fields, seed)
            position = per_split_index[split]
            per_split_index[split] += 1
            tamper_type = tamper_for(split, position, rng)
            displayed = fields
            tampered_field = None
            tamper_bbox = None
            if tamper_type != "none":
                image, displayed, tampered_field, tamper_bbox = apply_tamper(
                    image, fields, bboxes, tamper_type, rng
                )
            image, degradations = apply_degradations(image, rng, config["degradations"])
            doc_id = f"nid_{index:06d}"
            relative_path = f"images/{doc_id}.jpg"
            image.save(images_dir / f"{doc_id}.jpg", quality=config["image"]["quality"])
            label = DocumentLabel(
                doc_id=doc_id,
                image_path=relative_path,
                fields=fields,
                displayed_fields=displayed,
                field_bboxes=bboxes,
                tampered=tamper_type != "none",
                tamper_type=tamper_type,
                tampered_field=tampered_field,
                tamper_bbox=tamper_bbox,
                degradations=degradations,
                split=split,
                seed=seed,
                generator_version=config["version"],
            )
            payload = label.model_dump(mode="json")
            (labels_dir / f"{doc_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
            manifest_handles[split].write(json.dumps(payload) + "\n")
            labels.append(label)
            if split == "demo_gallery" or len(gallery) < 12:
                gallery.append((image.copy(), label))
    finally:
        for handle in manifest_handles.values():
            handle.close()
    _contact_sheet(gallery[-12:], debug_dir / "contact-sheet.jpg", overlay=False)
    _contact_sheet(gallery[-12:], debug_dir / "bbox-overlay-sheet.jpg", overlay=True)
    summary = {
        "total": len(labels),
        "splits": dict(Counter(label.split for label in labels)),
        "tamper_types": dict(Counter(label.tamper_type for label in labels)),
        "tampered": dict(Counter(str(label.tampered).lower() for label in labels)),
        "degradations": dict(Counter(d.type for label in labels for d in label.degradations)),
        "seed": config["seed"],
        "generator_version": config["version"],
    }
    (manifests_dir / "stats.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/dataset.yaml")
    parser.add_argument("--total", type=int)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate(args.config, args.total, args.clean), indent=2))


if __name__ == "__main__":
    main()
