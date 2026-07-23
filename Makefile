install:
	python -m pip install -e ".[eval,dev,ocr]"
	cd frontend && npm install
generate:
	python scripts/generate_dataset.py --config configs/dataset.yaml --clean
validate:
	python scripts/validate_dataset.py
benchmark:
	python scripts/run_benchmark.py --model mock --split eval_seen
	python scripts/run_benchmark.py --model mock --split eval_unseen
test:
	python -m pytest
build:
	cd frontend && npm run build
