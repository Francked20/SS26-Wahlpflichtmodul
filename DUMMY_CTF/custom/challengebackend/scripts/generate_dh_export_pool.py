"""One-off seeding script: (re)builds the fixed pool of weak-DH (Logjam)
challenge variants in MongoDB.

Run manually to populate the `DhExportVariant` collection that the
`/check_answer` endpoint reads at runtime. Each variant is deterministic in its
index (see utils.dh_export_pool.generate_variant), so re-running reproduces the
same pool. Usage: `python scripts/generate_dh_export_pool.py`.
"""

import asyncio
import os
import sys

# Make the package root (challengebackend/) importable so `database` and
# `utils` resolve when this script is run directly from the scripts/ folder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load DB connection settings (e.g. Mongo URI) from the .env file.
from dotenv import load_dotenv
load_dotenv()

from database import MongoDB, DhExportVariant          # noqa: E402
from utils.dh_export_pool import generate_variant, POOL_SIZE   # noqa: E402


async def main():
    # Connect and register the Beanie document models with Mongo.
    mongo = MongoDB()
    await mongo.connect_mapper()

    # Wipe the existing pool so re-running yields a clean, deterministic set.
    await DhExportVariant.delete_all()

    for index in range(POOL_SIZE):
        # Generate the full weak-DH handshake data for this pool index.
        v = generate_variant(index)
        # Persist it. Big integers are stored as strings (Mongo has no native
        # bignum) and byte flights are stored hex-encoded.
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

    # Close the connection cleanly.
    await mongo.disconnect()
    print(f"Done: {POOL_SIZE} weak-DH variants written.")


if __name__ == "__main__":
    asyncio.run(main())
