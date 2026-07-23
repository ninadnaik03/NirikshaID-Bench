# Architecture

NirikshaID Bench is a local-first monorepo. YAML configuration drives a deterministic Pillow/NumPy generator. Pydantic labels and independent integrity checks produce split JSONL manifests. Model adapters share one inference record contract. The evaluator writes immutable-by-run JSON/JSONL/CSV artifacts consumed by FastAPI. A strictly typed Next.js client reads those endpoints and never imports dataset files directly.

The critical path has no model-weight or API dependency. Optional providers are isolated behind adapters.

