import contextlib
import logging

import fastapi

from database import MongoDB


@contextlib.asynccontextmanager
async def challenge_backend_lifespan(app: fastapi.FastAPI):
    if MongoDB.instance is None:
        MongoDB.instance = MongoDB()

    await MongoDB.instance.connect_mapper()
    logging.info("Connected to database, Beanie mapper loaded")

    yield

    await MongoDB.instance.disconnect()
    logging.info("Disconnected from database")
