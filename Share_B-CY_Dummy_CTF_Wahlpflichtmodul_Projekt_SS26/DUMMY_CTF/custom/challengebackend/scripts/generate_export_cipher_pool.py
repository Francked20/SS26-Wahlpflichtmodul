#!/usr/bin/env python3
"""One-off operator script: (re)populates the ExportCipherVariant pool for the
day-3 export-cipher challenge chain. REPLACES all existing variants - since a
participant's variant is a deterministic function of their username (see
utils/export_cipher_pool.variant_index_for_user), rotating the pool changes
what every in-progress participant is working on.

Run inside the `challenge` container:
    docker compose exec challenge python3 scripts/generate_export_cipher_pool.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database import MongoDB, ExportCipherVariant
from utils.export_cipher_pool import generate_variant, POOL_SIZE


async def main():
    mongo = MongoDB()
    await mongo.connect_mapper()

    await ExportCipherVariant.delete_all()

    for index in range(POOL_SIZE):
        variant = generate_variant(index)
        await ExportCipherVariant(
            index=variant.index,
            n256=str(variant.n256), p256=str(variant.p256), q256=str(variant.q256),
            n512=str(variant.n512), p512=str(variant.p512), q512=str(variant.q512),
            flag=variant.flag,
            pre_master_secret_hex=variant.pre_master_secret.hex(),
            master_secret_hex=variant.master_secret.hex(),
            client_flight_1_hex=variant.client_flight_1.hex(),
            client_flight_2_hex=variant.client_flight_2.hex(),
            server_flight_1_hex=variant.server_flight_1.hex(),
            server_flight_2_hex=variant.server_flight_2.hex(),
        ).insert()
        print(f"  variant {index + 1}/{POOL_SIZE} generated")

    await mongo.disconnect()
    print(f"Done: {POOL_SIZE} export-cipher variants written.")


if __name__ == "__main__":
    asyncio.run(main())
