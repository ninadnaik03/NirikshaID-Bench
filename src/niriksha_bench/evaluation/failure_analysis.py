import json
from pathlib import Path


def load_failures(path: Path, tamper_type: str | None = None) -> list[dict]:
    failures = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    return [item for item in failures if not tamper_type or item["tamper_type"] == tamper_type]

