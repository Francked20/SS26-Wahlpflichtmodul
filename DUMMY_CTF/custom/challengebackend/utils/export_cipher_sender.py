"""Replays one variant's client-role TLS flights over a real TCP connection
toward the training VM, on demand, so a participant can capture it live with
Wireshark. Point EXPORT_CIPHER_VM_HOST/PORT (env) at the VM once it exists,
no other change needed.

The VM side needs CTF_Utils/export_cipher_vm_listener.py running to play back
the matching server-role flights. A 2-byte big-endian variant index is sent
first, before any TLS bytes, so the listener knows which variant's server
flights to reply with - without it, an on-demand trigger for variant #7 could
race against another player's #3 and the listener has no other way to tell
connections apart.
"""

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
        # Disable Nagle: the 2-byte index prefix and the ClientHello below
        # are sent as two separate write()+drain() calls specifically so
        # each becomes its own TCP segment (a TLS record must start at the
        # beginning of a segment for Wireshark's heuristic TLS dissector to
        # recognize it, since this isn't a standard TLS port). With Nagle
        # enabled, the OS can still merge two fast back-to-back small sends
        # into one segment depending on timing, silently reintroducing the
        # same misalignment - TCP_NODELAY makes each write leave immediately.
        sock = writer.get_extra_info("socket")
        if sock is not None:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        writer.write(struct.pack("!H", variant.index))
        await writer.drain()
        # Extra real-time gap (not just a second drain()): Docker Desktop's
        # virtualized networking (vpnkit) relays container traffic to the
        # LAN through a userspace layer that can still coalesce two sends
        # back into one TCP segment even with TCP_NODELAY set on the
        # container's own socket, if they land close enough together. A
        # small sleep forces enough real separation to survive that relay.
        await asyncio.sleep(0.05)
        writer.write(bytes.fromhex(variant.client_flight_1_hex))
        await writer.drain()
        # This read is NOT a reliable pacing mechanism on its own: the
        # listener sends server_flight_1 immediately after seeing the 2-byte
        # index, before it has read client_flight_1 at all, so this often
        # returns almost instantly rather than after a real round-trip -
        # same coalescing risk as above, same fix.
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
