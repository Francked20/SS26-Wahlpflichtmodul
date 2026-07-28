#!/usr/bin/env python3
"""Offline alternative to the day-3 export-cipher (FREAK-style) challenge's
live VM capture (see export_cipher_vm_listener.py): writes a single .pcap
file instead of requiring a player to sniff a live connection.

Proof of concept / not wired into the challenge flow yet.

The challenge backend's HTTP API never exposes client-role flight bytes
(GET /export_cipher/vm_replay_data only returns server-role hex), so this
reads the export_cipher_variants collection directly via pymongo - same
approach as reset_task_progress.py, host's published 27017.

The output pcap contains one TCP conversation carrying the real 4-flight TLS
handshake for the given --index, plus a couple of synthetic decoy
conversations (plain HTTP, one DNS query/response) so the TLS flow isn't the
only traffic in the capture.

Usage:
    python3 pcap_generator.py --index 42 --out capture.pcap
"""
import argparse
import os
import random

from pymongo import MongoClient  # pip install pymongo
from scapy.all import IP, TCP, UDP, Ether, Raw, wrpcap  # pip install scapy

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "admin")
MONGO_DB = os.getenv("MONGO_DB", "ctf_database")

TLS_CLIENT_IP, TLS_SERVER_IP = "10.0.0.10", "10.0.0.20"
TLS_CLIENT_PORT, TLS_SERVER_PORT = 51000, 443


def fetch_variant(index: int) -> dict:
    client = MongoClient(
        host=MONGO_HOST, port=MONGO_PORT,
        username=MONGO_USER, password=MONGO_PASSWORD,
        authSource="admin",
    )
    variant = client[MONGO_DB].export_cipher_variants.find_one({"index": index})
    if variant is None:
        raise SystemExit(f"No export_cipher_variants doc with index={index}")
    return variant


def tcp_conversation(src_ip: str, dst_ip: str, sport: int, dport: int, flights: list) -> list:
    """Builds a 3-way handshake, one PSH+ACK segment (+ ACK) per flight in
    order, and a FIN teardown. flights: list of (is_from_client, payload)."""
    packets = []
    seq_c, seq_s = 1000, 5000

    def segment(src, dst, sport_, dport_, flags, seq, ack, payload=b""):
        pkt = (Ether(src="02:00:00:00:00:01", dst="02:00:00:00:00:02") /
               IP(src=src, dst=dst) / TCP(sport=sport_, dport=dport_, flags=flags, seq=seq, ack=ack))
        return pkt / Raw(payload) if payload else pkt

    packets.append(segment(src_ip, dst_ip, sport, dport, "S", seq_c, 0))
    seq_c += 1
    packets.append(segment(dst_ip, src_ip, dport, sport, "SA", seq_s, seq_c))
    seq_s += 1
    packets.append(segment(src_ip, dst_ip, sport, dport, "A", seq_c, seq_s))

    for is_client, payload in flights:
        if is_client:
            packets.append(segment(src_ip, dst_ip, sport, dport, "PA", seq_c, seq_s, payload))
            seq_c += len(payload)
            packets.append(segment(dst_ip, src_ip, dport, sport, "A", seq_s, seq_c))
        else:
            packets.append(segment(dst_ip, src_ip, dport, sport, "PA", seq_s, seq_c, payload))
            seq_s += len(payload)
            packets.append(segment(src_ip, dst_ip, sport, dport, "A", seq_c, seq_s))

    packets.append(segment(src_ip, dst_ip, sport, dport, "FA", seq_c, seq_s))
    seq_c += 1
    packets.append(segment(dst_ip, src_ip, dport, sport, "FA", seq_s, seq_c))
    seq_s += 1
    packets.append(segment(src_ip, dst_ip, sport, dport, "A", seq_c, seq_s))

    return packets


def decoy_http() -> list:
    """Synthetic HTTP GET/response between unrelated IPs - no real semantics,
    just filler so the TLS flow isn't the only conversation in the capture."""
    req = b"GET /index.html HTTP/1.1\r\nHost: example.local\r\n\r\n"
    resp = b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello world!\n"
    return tcp_conversation("10.0.0.30", "10.0.0.40", 52000, 80, [(True, req), (False, resp)])

def gen_random_ip() -> str:
    """Pseudo random IP generator. Always of format: 192.rand.rand.rand"""
    first_three = "192"
    second_three = str(random.randint(1,254))
    third_three = str(random.randint(1,254))
    fourth_three = str(random.randint(1,254))
    return first_three + "." + second_three + "." + third_three + "." + fourth_three

def generator_decoy_http() -> list:
    http_conv_list = []
    count = random.randint(1, 500) #randomly generates between 1 and 500 conversations.
    for i in range(0, count):
        ip_d = gen_random_ip()
        ip_s = gen_random_ip()
        req = b"GET /index.html HTTP/1.1\r\nHost: example.local\r\n\r\n"
        resp = b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello world!\n"
        http_conv_list.append(tcp_conversation(f"{ip_s}", f"{ip_d}", 52000, 80, [(True, req), (False, resp)]))
    return http_conv_list

def decoy_dns() -> list:
    """Single synthetic DNS query/response pair over UDP - filler traffic."""
    eth = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
    query = (Ether(**eth) / IP(src="10.0.0.30", dst="10.0.0.1") / UDP(sport=53000, dport=53) /
              Raw(bytes.fromhex("aaaa01000001000000000000") + b"\x07example\x03com\x00\x00\x01\x00\x01"))
    response = (Ether(**eth) / IP(src="10.0.0.1", dst="10.0.0.30") / UDP(sport=53, dport=53000) /
                 Raw(bytes.fromhex("aaaa81800001000100000000") +
                     b"\x07example\x03com\x00\x00\x01\x00\x01" +
                     b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04\x5d\xb8\xd8\x22"))
    return [query, response]


def gen_pcap(index: int) -> list:
    variant = fetch_variant(index)
    tls_packets = tcp_conversation(
        TLS_CLIENT_IP, TLS_SERVER_IP, TLS_CLIENT_PORT, TLS_SERVER_PORT,
        [
            (True, bytes.fromhex(variant["client_flight_1_hex"])),
            (False, bytes.fromhex(variant["server_flight_1_hex"])),
            (True, bytes.fromhex(variant["client_flight_2_hex"])),
            (False, bytes.fromhex(variant["server_flight_2_hex"])),
        ],
    )
    return decoy_dns() + generator_decoy_http() + tls_packets + generator_decoy_http()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--index", type=int, required=True,
                         help="export_cipher variant index (0-99) to embed as real TLS traffic")
    parser.add_argument("--out", default="capture.pcap", help="output .pcap path (default: capture.pcap)")
    args = parser.parse_args()

    packets = gen_pcap(args.index)
    wrpcap(args.out, packets)
    print(f"Wrote {len(packets)} packets to {args.out} (TLS traffic = variant index {args.index})")


if __name__ == "__main__":
    main()
