import logging
import os
import typing

# import motor.motor_asyncio as motor
from pymongo import AsyncMongoClient
from beanie import Document, Link, init_beanie
# from beanie.odm.actions import Insert, Replace, Save,  before_event
from website.engine.site import User
from website.engine.tasks.models import BackendRegister


class MongoDB:
    instance: "MongoDB" = None

    def __init__(self):
        uri = (
            f"mongodb://{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
            f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@mongo/?authSource=admin"
        )
        self._client = AsyncMongoClient(uri)
        self._database = self._client.get_database(os.getenv("MONGO_DB"))

    async def ping(self):
        ping = await self._database.command("ping")
        logging.info(f"Pinged database: {{'ok': {ping['ok']}}}")

    async def connect_mapper(self):
        await init_beanie(
            database=self._database,
            document_models=[Challenge],  # Add others if needed
        )

    async def disconnect(self):
        await self._client.close()


class Challenge(Document, BackendRegister):
    """This acts as the shared DB model"""

    first_solved: typing.Optional[Link[User]] = None

    class Settings:
        name = "challenges"
        indexes = ["day_id", "task_id"]
