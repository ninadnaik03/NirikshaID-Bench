#!/usr/bin/env sh
set -eu
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[eval,dev,ocr]"
(cd frontend && npm install)
echo "Setup complete. Run: python scripts/run_local.py"
