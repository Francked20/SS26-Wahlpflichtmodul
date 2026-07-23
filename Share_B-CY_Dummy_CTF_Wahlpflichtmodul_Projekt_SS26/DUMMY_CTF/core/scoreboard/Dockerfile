FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN uv venv .venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Dependencies installieren
COPY ./core/scoreboard/requirements.txt .
RUN uv pip install --system -r requirements.txt

# Reflex-Basisverzeichnis
RUN mkdir /reflex
ENV REFLEX_DIR=/reflex

# Reflex-Projekt initialisieren (nur Struktur)
RUN yes "1" | reflex init
RUN rm -rf /app/app

# Scoreboard-Code kopieren
COPY ./core/scoreboard/ .

# Custom-Assets kopieren
COPY ./core/site/assets ./assets/

# RUN reflex export --frontend-only --no-zip

STOPSIGNAL SIGKILL

HEALTHCHECK --start-period=30s \
  CMD curl -f http://localhost:8000/ping/ || exit 1

CMD ["reflex", "run", "--env", "prod", "--loglevel", "info"]
