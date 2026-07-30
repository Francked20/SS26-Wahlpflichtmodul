#!/usr/bin/env python3
"""Server-role Companion-Skript fuer die day-4 weak-DH Trainings-VM.

Usage:
    CHALLENGE_API_KEY=<Wert aus DUMMY_CTF/.env> \\
        python3 dh_export_vm_listener.py --challenge-domain challenge.yourevent.example
"""
import argparse
import json
import os
import socket
import ssl
import struct
import sys
import time
import urllib.request


def fetch_replay_data(challenge_domain: str, api_key: str, insecure: bool,
                      resolve_ip: str | None = None) -> dict[int, dict]:
    url = f"https://{challenge_domain}/dh_export/vm_replay_data"
    req = urllib.request.Request(url, headers={"X-Challenge-Api-Key": api_key})
    context = ssl._create_unverified_context() if insecure else None

    if resolve_ip:
        # wie `curl --resolve`: Socket verbindet zu resolve_ip, TLS SNI/Host bleiben challenge_domain
        _orig_getaddrinfo = socket.getaddrinfo

        def _patched_getaddrinfo(host, *args, **kwargs):
            if host == challenge_domain:
                host = resolve_ip
            return _orig_getaddrinfo(host, *args, **kwargs)

        socket.getaddrinfo = _patched_getaddrinfo
        try:
            with urllib.request.urlopen(req, timeout=10, context=context) as resp:
                data = json.loads(resp.read())
        finally:
            socket.getaddrinfo = _orig_getaddrinfo
    else:
        with urllib.request.urlopen(req, timeout=10, context=context) as resp:
            data = json.loads(resp.read())

    variants = data["variants"]
    if not variants:
        print("No variants returned - has the pool been generated on the challenge backend yet? "
              "(scripts/generate_dh_export_pool.py)", file=sys.stderr)
        sys.exit(1)
    return {v["index"]: v for v in variants}


def split_records(buf: bytes) -> list[bytes]:
    """Splits a flight blob into one byte-string per TLS record (5-byte
    header + that many fragment bytes), so each lands in its own frame"""
    records = []
    i = 0
    while i < len(buf):
        length = int.from_bytes(buf[i + 3:i + 5], "big")
        records.append(buf[i:i + 5 + length])
        i += 5 + length
    return records


def serve(listen_port: int, variants_by_index: dict[int, dict]) -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", listen_port))
    server.listen(5)
    print(f"Listening on 0.0.0.0:{listen_port} ...")

    while True:
        conn, addr = server.accept()
        try:
            conn.settimeout(2)
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            index_bytes = conn.recv(2)
            if len(index_bytes) != 2:
                print(f"Connection from {addr} closed before sending a variant index", file=sys.stderr)
                continue
            index = struct.unpack("!H", index_bytes)[0]
            variant = variants_by_index.get(index)
            if variant is None:
                print(f"Connection from {addr} asked for unknown variant #{index}", file=sys.stderr)
                continue
            print(f"Connection from {addr}, replaying variant #{index}")

            # wait for ClientHello first, else server appears to reply before it
            try:
                conn.recv(4096)
            except socket.timeout:
                pass

            # real sleep between sends - NODELAY alone still let vpnkit merge them
            for record in split_records(bytes.fromhex(variant["server_flight_1_hex"])):
                conn.sendall(record)
                time.sleep(0.05)
            try:
                conn.recv(4096)
            except socket.timeout:
                pass
            for record in split_records(bytes.fromhex(variant["server_flight_2_hex"])):
                conn.sendall(record)
                time.sleep(0.05)
        except OSError as e:
            print(f"Connection to {addr} failed mid-replay: {e}", file=sys.stderr)
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--challenge-domain", required=True,
                         help="CHALLENGE_DOMAIN from DUMMY_CTF/.env, e.g. challenge.yourevent.example")
    parser.add_argument("--listen-port", type=int, default=4434,
                         help="Must match DH_EXPORT_VM_PORT in DUMMY_CTF/.env (default: 4434)")
    parser.add_argument("--insecure", action="store_true",
                         help="Skip TLS certificate verification (self-signed dev certs)")
    parser.add_argument("--resolve-ip", default=None,
                         help="Force --challenge-domain to resolve to this IP, e.g. --resolve-ip 192.168.56.1")
    args = parser.parse_args()

    api_key = os.getenv("CHALLENGE_API_KEY")
    if not api_key:
        print("Set CHALLENGE_API_KEY (same value as in DUMMY_CTF/.env) before running this script.", file=sys.stderr)
        sys.exit(1)

    variants = fetch_replay_data(args.challenge_domain, api_key, args.insecure, args.resolve_ip)
    print(f"Fetched {len(variants)} variants from the challenge backend.")
    serve(args.listen_port, variants)


if __name__ == "__main__":
    main()
