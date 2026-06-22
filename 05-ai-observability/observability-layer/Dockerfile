FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ai_observability.py evaluator.py metrics_server.py example_usage.py ./

ENV METRICS_PORT=8000
EXPOSE 8000

CMD ["python", "metrics_server.py", "--port", "8000"]