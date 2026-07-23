import contextlib
import logging

import fastapi

from database import MongoDB


@contextlib.asynccontextmanager
async def challenge_backend_lifespan(app: fastapi.FastAPI):
    """Connects Mongo (needed for the export-cipher variant pool). Everything
    else in this service (primes.py, ecbcbcwtf.py, ecb_oracle.py) is stateless
    and doesn't need any of this."""

    if MongoDB.instance is None:
        MongoDB.instance = MongoDB()

    await MongoDB.instance.connect_mapper()
    logging.info("Connected to database, Beanie mapper loaded")

    yield

    await MongoDB.instance.disconnect()
    logging.info("Disconnected from database")
