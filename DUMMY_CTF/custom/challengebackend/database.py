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
        await init_beanie(
            database=self._database,
            document_models=[DhExportVariant],
        )

    async def disconnect(self):
        self._client.close()


class DhExportVariant(Document):
    """One entry of the fixed ~100-variant pool for the day-4 weak-DH
    (Logjam-style) challenge chain. Populated by
    scripts/generate_dh_export_pool.py. See utils/dh_export_pool.py for how a
    username is mapped to a variant index.

    The public DH values (p, g, Ys, Yc) are also on the wire in the player's
    pcap; server_secret is private and used only by /check_answer."""

    index: typing.Annotated[int, Indexed(unique=True)]

    p: str
    g: str
    Ys: str
    Yc: str

    server_secret: str
    factors: typing.List[str]
    flag: str
    master_secret_hex: str

    client_flight_1_hex: str
    client_flight_2_hex: str
    server_flight_1_hex: str
    server_flight_2_hex: str

    class Settings:
        name = "dh_export_variants"
        indexes = ["index"]
