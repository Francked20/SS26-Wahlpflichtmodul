"""Mongo connection + models fuer diesen Service."""

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
            document_models=[DhExportVariant, ExportCipherVariant],
        )

    async def disconnect(self):
        self._client.close()


class DhExportVariant(Document):
    """Ein Eintrag des Varianten-Pools fuer day-4 (weak DH / Logjam)."""

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


class ExportCipherVariant(Document):
    """Ein Eintrag des Varianten-Pools fuer day-3 (Export Cipher / FREAK)."""

    index: typing.Annotated[int, Indexed(unique=True)]

    n256: str
    p256: str
    q256: str

    n512: str
    p512: str
    q512: str

    flag: str
    master_secret_hex: str

    client_flight_1_hex: str
    client_flight_2_hex: str
    server_flight_1_hex: str
    server_flight_2_hex: str

    class Settings:
        name = "export_cipher_variants"
        indexes = ["index"]
