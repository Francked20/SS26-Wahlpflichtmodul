#!/usr/bin/env python3
"""Seeding-Skript: (re)baut den Export-Cipher (day-3) Varianten-Pool in MongoDB.

Usage: docker compose exec challenge python3 scripts/generate_export_cipher_pool.py
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
