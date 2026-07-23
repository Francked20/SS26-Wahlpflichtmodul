# Alpine UV Python Base Image
FROM ghcr.io/astral-sh/uv:python3.13-alpine           

# Set working directory
WORKDIR /app

# Create and activate virtual environment
RUN uv venv .venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies with cache busting
COPY requirements.txt ./
RUN uv pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Define a Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD wget -nv -t1 --spider http://127.0.0.1:8000/ || exit 1

# Default command: starts the FastAPI             
CMD ["uvicorn", "main:app", "--log-config", "logging.yaml", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
