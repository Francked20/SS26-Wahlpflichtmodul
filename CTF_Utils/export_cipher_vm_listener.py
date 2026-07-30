#!/usr/bin/env python3
"""Server-role Companion-Skript fuer die day-3 export-cipher Trainings-VM.

Usage:
    CHALLENGE_API_KEY=<Wert aus DUMMY_CTF/.env> \\
        python3 export_cipher_vm_listener.py --challenge-domain challenge.yourevent.example
"""
import argparse
import json
import os
import socket
import ssl
import struct
import sys
import urllib.request


def fetch_replay_data(challenge_domain: str, api_key: str, insecure: bool) -> dict[int, dict]:
    url = f"https://{challenge_domain}/export_cipher/vm_replay_data"
    req = urllib.request.Request(url, headers={"X-Challenge-Api-Key": api_key})
    context = ssl._create_unverified_context() if insecure else None

    with urllib.request.urlopen(req, timeout=10, context=context) as resp:
        data = json.loads(resp.read())

    variants = data["variants"]
    if not variants:
        print("No variants returned - has the pool been generated on the challenge backend yet? "
              "(scripts/generate_export_cipher_pool.py)", file=sys.stderr)
        sys.exit(1)
    return {v["index"]: v for v in variants}


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

            conn.sendall(bytes.fromhex(variant["server_flight_1_hex"]))
            try:
                conn.recv(4096)
            except socket.timeout:
                pass
            conn.sendall(bytes.fromhex(variant["server_flight_2_hex"]))
        except OSError as e:
            print(f"Connection to {addr} failed mid-replay: {e}", file=sys.stderr)
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--challenge-domain", required=True,
                         help="CHALLENGE_DOMAIN from DUMMY_CTF/.env, e.g. challenge.yourevent.example")
    parser.add_argument("--listen-port", type=int, default=4433,
                         help="Must match EXPORT_CIPHER_VM_PORT in DUMMY_CTF/.env (default: 4433)")
    parser.add_argument("--insecure", action="store_true",
                         help="Skip TLS certificate verification (self-signed dev certs)")
    args = parser.parse_args()

    api_key = os.getenv("CHALLENGE_API_KEY")
    if not api_key:
        print("Set CHALLENGE_API_KEY (same value as in DUMMY_CTF/.env) before running this script.", file=sys.stderr)
        sys.exit(1)

    variants = fetch_replay_data(args.challenge_domain, api_key, args.insecure)
    print(f"Fetched {len(variants)} variants from the challenge backend.")
    serve(args.listen_port, variants)


if __name__ == "__main__":
    main()
