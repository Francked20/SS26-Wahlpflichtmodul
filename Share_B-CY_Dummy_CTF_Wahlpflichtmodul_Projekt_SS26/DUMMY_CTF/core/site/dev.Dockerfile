# user time limit -> credits

FROM ghcr.io/astral-sh/uv:python3.13-bookworm

WORKDIR /app

# install dependencies
COPY ./core/site/requirements.txt .
RUN uv pip install --system -r requirements.txt


RUN mkdir /reflex
ENV REFLEX_DIR=/reflex

RUN yes "1" | reflex init
RUN rm -rf /app/app

# copy core
# COPY ./core/site/ .
ENV PYTHONPATH=/app:/custom

# Copy the custom content
# COPY ./custom/assets/ ./assets/
# COPY ./custom/sites/ ./sites/

# fix reflex path resolution
# RUN echo "from .app import app" >> website/website.py
COPY ./core/site/rxconfig.py .
COPY ./core/site/assets ./assets/

HEALTHCHECK --start-period=80s --retries=10 \
   CMD curl -f http://localhost:8000/ping/ || exit 1

# CMD ["sh", "-c", "sleep 3600"]
CMD ["reflex", "run", "--env", "dev", "--loglevel", "debug"]
# CMD ["reflex", "run", "--env", "prod", "--loglevel", "info"]