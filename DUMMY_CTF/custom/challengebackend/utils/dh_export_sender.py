"""Sendet die client-role TLS-Flights einer Variante an die Trainings-VM"""

import asyncio
import socket
import struct

from database import DhExportVariant

CONNECT_TIMEOUT_SECONDS = 5
READ_TIMEOUT_SECONDS = 2
IDLE_TIMEOUT_SECONDS = 0.3


async def _drain_until_idle(reader: asyncio.StreamReader, idle_timeout: float = IDLE_TIMEOUT_SECONDS) -> None:
    """Liest bis idle_timeout Sekunden nichts mehr ankommt"""
    while True:
        try:
            data = await asyncio.wait_for(reader.read(4096), timeout=idle_timeout)
        except asyncio.TimeoutError:
            return
        if not data:
            return


async def send_variant_to_vm(host: str, port: int, variant: DhExportVariant) -> None:
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
        await _drain_until_idle(reader)
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
