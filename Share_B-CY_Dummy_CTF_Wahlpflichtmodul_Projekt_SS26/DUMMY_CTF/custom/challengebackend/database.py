"""Mongo connection + models for this service's own state. Uses Motor (not
pymongo's newer async client) because that's what this service's
requirements.txt pins beanie==1.30.0 against.
"""

import os
import typing

from beanie import Document, Indexed, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    instance: typing.Optional["MongoDB"] = None

    def __init__(self):
        uri = (
            f"mongodb://{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
            f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@mongo/?authSource=admin"
        )
        self._client = AsyncIOMotorClient(uri)
        self._database = self._client.get_database(os.getenv("MONGO_DB"))

    async def connect_mapper(self):
        await init_beanie(database=self._database, document_models=[ExportCipherVariant])

    async def disconnect(self):
        self._client.close()


class ExportCipherVariant(Document):
    """One entry of the fixed ~100-variant pool for the day-3 export-cipher
    (FREAK-style) challenge chain. Populated by
    scripts/generate_export_cipher_pool.py. See utils/export_cipher_pool.py
    for how a username is mapped to a variant index."""

    index: typing.Annotated[int, Indexed(unique=True)]

    n256: str
    p256: str
    q256: str

    n512: str
    p512: str
    q512: str

    flag: str
    pre_master_secret_hex: str
    master_secret_hex: str

    client_flight_1_hex: str
    client_flight_2_hex: str
    server_flight_1_hex: str
    server_flight_2_hex: str

    class Settings:
        name = "export_cipher_variants"
        indexes = ["index"]
