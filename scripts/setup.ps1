$ErrorActionPreference = "Stop"
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -e ".[eval,dev,ocr]"
Push-Location frontend
npm install
Pop-Location
Write-Host "Setup complete. Run: python scripts/run_local.py"
