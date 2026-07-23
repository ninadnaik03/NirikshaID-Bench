import io
import json
import os
import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError

from niriksha_bench.generator.schemas import DocumentLabel
from niriksha_bench.models.mock import MockAdapter
from niriksha_bench.utils.paths import resolve_project_path

app = FastAPI(
    title="NirikshaID Bench API",
    version="1.1.0",
    description="Local-first synthetic document intelligence benchmark API.",
)
origins = [value.strip() for value in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _stats() -> dict:
    path = resolve_project_path("data/generated/manifests/stats.json")
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"total": 0}


def _summary() -> dict:
    path = resolve_project_path("data/results/summary.json")
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"status": "not_executed", "runs": []}


def _diagnostic_summary() -> dict:
    path = resolve_project_path(
        "data/diagnostics/results/template-aware-tesseract-ocr/metrics.json"
    )
    return (
        json.loads(path.read_text(encoding="utf-8"))
        if path.exists()
        else {"status": "not_executed"}
    )


def _gallery_labels() -> list[DocumentLabel]:
    path = resolve_project_path("data/generated/manifests/demo_gallery.jsonl")
    if not path.exists():
        return []
    return [DocumentLabel.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _gallery_item(label: DocumentLabel) -> dict:
    record = MockAdapter().predict(
        resolve_project_path("data/generated") / label.image_path, label.model_dump(mode="json")
    )
    return {
        "doc_id": label.doc_id,
        "image_url": f"/api/assets/{label.doc_id}.jpg",
        "split": label.split,
        "tampered": label.tampered,
        "tamper_type": label.tamper_type,
        "degradations": [item.model_dump() for item in label.degradations],
        "ground_truth": label.model_dump(mode="json"),
        "predictions": [record.model_dump(mode="json")],
    }


@app.get("/api/health")
def health() -> dict:
    stats = _stats()
    tesseract_cmd = os.getenv("TESSERACT_CMD")
    tesseract_available = bool(
        (tesseract_cmd and Path(tesseract_cmd).is_file())
        or shutil.which("tesseract")
        or Path("C:/Program Files/Tesseract-OCR/tesseract.exe").is_file()
    )
    ollama_available = shutil.which("ollama") is not None
    return {
        "status": "ok",
        "service": "NirikshaID Bench",
        "models": [
            {"id": "demo-stub", "available": True, "benchmarkable": False, "live_vlm": False},
            {
                "id": "template-aware-tesseract-ocr",
                "available": tesseract_available,
                "benchmarkable": True,
                "live_vlm": False,
            },
            {
                "id": "qwen2.5-vl-3b-instruct-ollama",
                "available": ollama_available,
                "benchmarkable": True,
                "live_vlm": True,
            },
        ],
        "dataset": {"available": stats.get("total", 0) > 0, "documents": stats.get("total", 0)},
        "results": {"available": _summary()["status"] == "completed"},
    }


@app.get("/api/project")
def project() -> dict:
    return {
        "name": "NirikshaID Bench",
        "tagline": "A reproducible synthetic benchmark for identity-document extraction, tamper detection, and VLM robustness.",
        "status": "Research Demo — Not a Production KYC System",
        "author": {
            "name": "Ninad Naik",
            "role": "CS Student | AI/ML Research and Engineering",
            "github": "https://github.com/ninadnaik03",
            "linkedin": "https://www.linkedin.com/in/ninad-naik-274883262/",
        },
        "scope": ["one original layout", "English fields", "synthetic identities", "four tamper labels"],
        "limitations": [
            "Synthetic-to-real domain gap",
            "Single document layout",
            "English-only fields",
            "No production-security claim",
        ],
    }


@app.get("/api/dataset/stats")
def dataset_stats() -> dict:
    return _stats()


@app.get("/api/benchmark/summary")
def benchmark_summary() -> dict:
    return _summary()


@app.get("/api/benchmark/models")
def benchmark_models() -> dict:
    runs = _summary().get("runs", [])
    seen = {}
    for run in runs:
        seen[run["model"]["id"]] = run["model"]
    return {"models": list(seen.values())}


@app.get("/api/benchmark/failures")
def benchmark_failures(
    tamper_type: str | None = None,
    split: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
) -> dict:
    items: list[dict] = []
    for path in resolve_project_path("data/results").glob("*/*/failures.json"):
        items.extend(json.loads(path.read_text(encoding="utf-8")))
    if tamper_type:
        items = [item for item in items if item["tamper_type"] == tamper_type]
    if split:
        items = [item for item in items if item["split"] == split]
    start = (page - 1) * page_size
    return {"items": items[start : start + page_size], "total": len(items), "page": page}


@app.get("/api/diagnostics/summary")
def diagnostics_summary() -> dict:
    return _diagnostic_summary()


@app.get("/api/diagnostics/pairs")
def diagnostics_pairs(limit: int = Query(12, ge=1, le=30)) -> dict:
    path = resolve_project_path(
        "data/diagnostics/results/template-aware-tesseract-ocr/pair-results.json"
    )
    items = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    return {"items": items[:limit], "total": len(items)}


@app.get("/api/diagnostics/hard-negatives")
def diagnostics_hard_negatives(limit: int = Query(12, ge=1, le=40)) -> dict:
    path = resolve_project_path(
        "data/diagnostics/results/template-aware-tesseract-ocr/hard-negative-results.json"
    )
    items = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    return {"items": items[:limit], "total": len(items)}


@app.get("/api/diagnostics/failures")
def diagnostics_failures(limit: int = Query(12, ge=1, le=24)) -> dict:
    path = resolve_project_path(
        "data/diagnostics/results/template-aware-tesseract-ocr/failures.json"
    )
    items = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    return {"items": items[:limit], "total": len(items)}


@app.get("/api/demo/gallery")
def gallery() -> dict:
    labels = _gallery_labels()
    return {"items": [_gallery_item(label) for label in labels[:12]], "total": len(labels)}


@app.get("/api/demo/gallery/{doc_id}")
def gallery_detail(doc_id: str) -> dict:
    for label in _gallery_labels():
        if label.doc_id == doc_id:
            return _gallery_item(label)
    raise HTTPException(404, "Gallery sample not found")


@app.get("/api/assets/{filename}")
def asset(filename: str) -> FileResponse:
    safe_name = Path(filename).name
    if safe_name != filename or not safe_name.endswith((".jpg", ".png")):
        raise HTTPException(400, "Invalid asset name")
    path = resolve_project_path("data/generated/images") / safe_name
    if not path.exists():
        raise HTTPException(404, "Asset not found")
    return FileResponse(path)


@app.get("/api/diagnostic-assets/{asset_path:path}")
def diagnostic_asset(asset_path: str) -> FileResponse:
    root = resolve_project_path("data/diagnostics").resolve()
    candidate = (root / asset_path).resolve()
    if root not in candidate.parents or candidate.suffix.lower() not in {".jpg", ".png"}:
        raise HTTPException(400, "Invalid diagnostic asset path")
    if not candidate.exists():
        raise HTTPException(404, "Diagnostic asset not found")
    return FileResponse(candidate)


@app.post("/api/demo/analyze")
async def analyze(file: UploadFile = File(...)) -> dict:
    max_bytes = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(415, "Only JPEG, PNG, and WebP images are accepted")
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(413, "Image exceeds the configured upload limit")
    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "Uploaded content is not a valid image")
    return {
        "status": "live_model_unavailable",
        "message": "Live VLM inference is not configured. Use the precomputed gallery for reproducible results.",
    }
