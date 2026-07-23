import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
env = os.environ.copy()
env.setdefault("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000")
backend = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "niriksha_bench.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=ROOT,
    env=env,
)
frontend = subprocess.Popen(["npm.cmd" if os.name == "nt" else "npm", "run", "dev"], cwd=ROOT / "frontend", env=env)
print("Frontend: http://localhost:3000")
print("Backend:  http://localhost:8000/docs")
try:
    raise SystemExit(frontend.wait())
finally:
    backend.terminate()

