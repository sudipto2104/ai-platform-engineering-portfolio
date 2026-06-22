FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY src ./src
COPY mcp_server ./mcp_server
COPY scripts ./scripts

ENV PYTHONPATH=/app/src:/app
ENV MCP_PORT=8090

EXPOSE 8090

CMD ["python", "scripts/run_mcp_server.py"]