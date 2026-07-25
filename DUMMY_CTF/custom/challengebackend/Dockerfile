# Alpine UV Python Base Image
FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app

# Virtuelle Umgebung
RUN uv venv .venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Dependencies installieren
COPY requirements.txt .
RUN uv pip install --no-cache-dir -r requirements.txt

# Source kopieren
COPY . .

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD wget -nv -t1 --spider http://127.0.0.1:8000/ping/ || exit 1

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
