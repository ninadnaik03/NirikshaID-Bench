import json
from pathlib import Path


def export_markdown(metrics_path: Path, destination: Path) -> None:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    destination.write_text(
        f"# Benchmark report\n\nModel: {metrics['model']['display_name']}\n\n"
        f"Split: {metrics['split']}\n\nSamples: {metrics['samples']}\n",
        encoding="utf-8",
    )

