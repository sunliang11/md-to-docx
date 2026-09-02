# Build from repo root: docker compose -f web/docker-compose.yml up --build
FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir "/app[web]" \
    && PYTHONPATH=scripts python -m md_to_docx.presets_build

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8080"]
