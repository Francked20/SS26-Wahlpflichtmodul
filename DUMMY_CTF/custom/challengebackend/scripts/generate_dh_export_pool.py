"""Seeding-Skript: (re)baut den weak-DH (Logjam) Varianten-Pool in MongoDB.

Usage: python scripts/generate_dh_export_pool.py
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
