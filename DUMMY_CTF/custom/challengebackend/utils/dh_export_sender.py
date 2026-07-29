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
import socket
import struct

from database import DhExportVariant

CONNECT_TIMEOUT_SECONDS = 5
READ_TIMEOUT_SECONDS = 2


async def send_variant_to_vm(host: str, port: int, variant: DhExportVariant) -> None:
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port), timeout=CONNECT_TIMEOUT_SECONDS
    )
    try:
        # See export_cipher_sender.py for why this is split into separate
        # write()+drain() calls with a real sleep in between, and why
        # TCP_NODELAY is set: sending the 2-byte index and client_flight_1
        # in one flush lets the OS (or, for local dev, Docker Desktop's
        # vpnkit relay to the LAN) coalesce them into a single TCP segment,
        # which shifts the TLS record header 2 bytes into that segment -
        # Wireshark's heuristic TLS dissector then fails to recognize it and
        # ClientHello never shows up. TCP_NODELAY alone wasn't enough to fix
        # this reliably in testing (vpnkit still merged sends sometimes);
        # the sleep forces enough real separation to survive that relay too.
        sock = writer.get_extra_info("socket")
        if sock is not None:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        writer.write(struct.pack("!H", variant.index))
        await writer.drain()
        await asyncio.sleep(0.05)
        writer.write(bytes.fromhex(variant.client_flight_1_hex))
        await writer.drain()
        # Not a reliable pacing mechanism on its own (see listener - it
        # replies almost immediately after the index, not after a real
        # round-trip), same coalescing risk as above, same fix.
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
