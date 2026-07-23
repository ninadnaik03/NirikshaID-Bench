# Deployment

Local verification comes first.

## Containers

```bash
docker compose up --build
```

## Backend host

Build the repository-root Dockerfile, expose port 8000, persist or include `data/`, and configure:

```text
CORS_ORIGINS=https://your-frontend.example
MODEL_PROVIDER=ocr
MAX_UPLOAD_MB=10
```

## Frontend host

Set the project root to `frontend`, use `npm run build`, and configure:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-backend.example
```

Because Next.js public variables are embedded at build time, rebuild after changing the API URL. No deployment or Git push is performed by project scripts.

Generated image bulk is excluded from Git and the default Docker build context. For the complete gallery, generate the dataset before deployment and mount `data/generated/images` into the backend container, or create a private deployment artifact containing only synthetic gallery images. Aggregate result pages work from the compact versioned metrics committed with the repository.
