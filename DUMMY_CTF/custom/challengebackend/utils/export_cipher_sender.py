"""Sendet die client-role TLS-Flights einer Variante an die Trainings-VM"""

import asyncio
import socket
import struct

from database import ExportCipherVariant

CONNECT_TIMEOUT_SECONDS = 5
READ_TIMEOUT_SECONDS = 2


async def send_variant_to_vm(host: str, port: int, variant: ExportCipherVariant) -> None:
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port), timeout=CONNECT_TIMEOUT_SECONDS
    )
    try:
        sock = writer.get_extra_info("socket")
        if sock is not None:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        writer.write(struct.pack("!H", variant.index))
        await writer.drain()
        await asyncio.sleep(0.05)
        writer.write(bytes.fromhex(variant.client_flight_1_hex))
        await writer.drain()
        try:
            await asyncio.wait_for(reader.read(4096), timeout=READ_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.05)

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
