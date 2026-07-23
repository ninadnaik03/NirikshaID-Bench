# GitHub release checklist

Nothing in this checklist is automated. Review each group before staging or pushing.

## Suggested first public batch

Start with the files that establish the project identity and repository rules:

```text
README.md
LICENSE
CITATION.cff
CONTRIBUTING.md
SECURITY.md
.gitignore
.gitattributes
.editorconfig
.env.example
docs/
```

## Suggested second batch

Add the reproducible research implementation:

```text
configs/
src/
scripts/
tests/
pyproject.toml
requirements.txt
Makefile
```

## Suggested third batch

Add the application and deployment surface:

```text
frontend/
Dockerfile
docker-compose.yml
.dockerignore
.github/
```

## Suggested final evidence batch

Review and add only the compact result artifacts that are not ignored:

```text
data/generated/manifests/stats.json
data/generated/manifests/validation-report.json
data/diagnostics/manifests/
data/diagnostics/results/
data/results/
```

Generated images, per-document labels, raw prediction JSONL, model weights, local caches, and secrets must remain untracked.

## Before any push

```bash
git status --short
python -m pytest
python -m ruff check --no-cache src tests scripts
cd frontend
npm run lint
npm run build
```

Also verify:

- no `.env` file is staged;
- no model weights are staged;
- no real identity document or personal data is present;
- result tables match the saved metrics;
- the repository URL in `CITATION.cff` and `pyproject.toml` matches the repository you create.
