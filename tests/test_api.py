from fastapi.testclient import TestClient
import pytest

from niriksha_bench.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_summary():
    response = client.get("/api/benchmark/summary")
    assert response.status_code == 200
    assert "runs" in response.json()


@pytest.mark.local_artifacts
def test_gallery():
    response = client.get("/api/demo/gallery")
    assert response.status_code == 200
    assert response.json()["total"] >= 8


def test_upload_rejects_text():
    response = client.post("/api/demo/analyze", files={"file": ("x.txt", b"hello", "text/plain")})
    assert response.status_code == 415


def test_diagnostic_summary():
    response = client.get("/api/diagnostics/summary")
    assert response.status_code == 200
    assert response.json()["hard_negatives"]["samples"] == 40


def test_diagnostic_asset_blocks_traversal():
    response = client.get("/api/diagnostic-assets/../../README.md")
    assert response.status_code in {400, 404}
