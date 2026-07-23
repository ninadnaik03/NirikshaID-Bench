FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY configs ./configs
COPY data ./data
EXPOSE 8000
CMD ["uvicorn", "niriksha_bench.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

