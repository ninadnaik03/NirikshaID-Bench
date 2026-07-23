# Contributing

NirikshaID Bench is currently a focused research-engineering demonstration. Contributions should preserve its central constraints: reproducibility, synthetic-only identities, explicit model provenance, and no fabricated benchmark values.

## Development workflow

1. Create a Python environment and install `.[eval,dev,ocr]`.
2. Install frontend dependencies with `npm install` inside `frontend/`.
3. Make a narrow, documented change.
4. Run:

```bash
python -m pytest
python -m ruff check --no-cache src tests scripts
cd frontend
npm run lint
npm run build
```

## Research-result policy

- Predictions must be produced from image pixels only.
- Ground-truth labels may enter only after inference for scoring or approved training splits.
- Record model version, prompt version, quantization, sample count, and failures.
- Never add illustrative numbers to result files.
- Keep diagnostic runs separate from headline benchmark runs.

## Data and safety

Do not submit real identity documents, real identity numbers, scraped portraits, official logos, seals, signatures, or government-layout replicas. Generated cards must remain visibly synthetic and invalid for identification.
