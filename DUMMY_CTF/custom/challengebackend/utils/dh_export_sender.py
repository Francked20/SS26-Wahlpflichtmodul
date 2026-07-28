"""Replays one variant's client-role TLS flights over a real TCP connection
toward the training VM, on demand, so a participant can capture it live with
Wireshark. Point DH_EXPORT_VM_HOST/PORT (env) at the VM once it exists, no
other change needed.

Same pattern as Jonas' export_cipher_sender.py for the FREAK chapter. The VM
side needs CTF_Utils/dh_export_vm_listener.py running to play back the
matching server-role flights. A 2-byte big-endian variant index is sent
first, before any TLS bytes, so the listener knows which variant's server
flights to reply with - without it, an on-demand trigger for variant #7 could
race against another player's #3 and the listener has no other way to tell
connections apart.
"""

import asyncio
import struct

from database import DhExportVariant

CONNECT_TIMEOUT_SECONDS = 5
READ_TIMEOUT_SECONDS = 2


async def send_variant_to_vm(host: str, port: int, variant: DhExportVariant) -> None:
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port), timeout=CONNECT_TIMEOUT_SECONDS
    )
    try:
        writer.write(struct.pack("!H", variant.index))
        writer.write(bytes.fromhex(variant.client_flight_1_hex))
        await writer.drain()
        try:
            await asyncio.wait_for(reader.read(4096), timeout=READ_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            pass

        writer.write(bytes.fromhex(variant.client_flight_2_hex))
        await writer.drain()
        try:
            await asyncio.wait_for(reader.read(4096), timeout=READ_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
