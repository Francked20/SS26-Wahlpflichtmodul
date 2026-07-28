#!/usr/bin/env python3
"""One-off operator script: (re)populates the DhExportVariant pool for the
weak-DH (Logjam) challenge chain. REPLACES all existing variants - since a
participant's variant is a deterministic function of their username (see
utils/dh_export_pool.variant_index_for_user), rotating the pool changes what
every in-progress participant is working on.

Companion to Jonas' generate_export_cipher_pool.py. Run inside the `challenge`
container:
    docker compose exec challenge python3 scripts/generate_dh_export_pool.py

Requires a Beanie document `DhExportVariant` registered in database/models.py
(alongside ExportCipherVariant). Suggested schema (all big ints stored as str):

    class DhExportVariant(Document):
        index: int
        p: str
        g: str
        Ys: str
        Yc: str
        server_secret: str            # s (private; used only by /check_answer)
        factors: List[str]            # prime factors of q=(p-1)/2
        flag: str
        master_secret_hex: str
        client_flight_1_hex: str
        client_flight_2_hex: str
        server_flight_1_hex: str
        server_flight_2_hex: str
        class Settings:
            name = "dh_export_variants"
            indexes = ["index"]
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database import MongoDB, DhExportVariant          # noqa: E402
from utils.dh_export_pool import generate_variant, POOL_SIZE   # noqa: E402


async def main():
    mongo = MongoDB()
    await mongo.connect_mapper()

    await DhExportVariant.delete_all()

    for index in range(POOL_SIZE):
        v = generate_variant(index)
        await DhExportVariant(
            index=v.index,
            p=str(v.p), g=str(v.g), Ys=str(v.Ys), Yc=str(v.Yc),
            server_secret=str(v.server_secret),
            factors=[str(f) for f in v.factors],
            flag=v.flag,
            master_secret_hex=v.master_secret.hex(),
            client_flight_1_hex=v.client_flight_1.hex(),
            client_flight_2_hex=v.client_flight_2.hex(),
            server_flight_1_hex=v.server_flight_1.hex(),
            server_flight_2_hex=v.server_flight_2.hex(),
        ).insert()
        print(f"  variant {index + 1}/{POOL_SIZE} generated")

    await mongo.disconnect()
    print(f"Done: {POOL_SIZE} weak-DH variants written.")


if __name__ == "__main__":
    asyncio.run(main())
