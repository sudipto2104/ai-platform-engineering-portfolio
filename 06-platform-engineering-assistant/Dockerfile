FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY config ./config
COPY data ./data
COPY scripts ./scripts

ENV PYTHONPATH=/app/src
ENV K8S_DRY_RUN=true
ENV VAULT_USE_LOCAL=true

RUN python scripts/ingest_docs.py

EXPOSE 8080 8000

CMD ["python", "scripts/run_gateway.py"]