"""Generates one downloadable .pcap per weak-DH (day-94 beginner Logjam)
pool variant, served statically from custom/assets/0400/<index>/capture.pcap
(see challenge_04_beginner.py's download_button).

Own script, own output folder (0400) - does not touch or depend on Francks's
CTF_Utils/dh_pcap_generator.py (which the advanced chapter references but
which isn't wired into any download button yet). Reads the same
dh_export_variants collection Francks's challengebackend already populates
(scripts/generate_dh_export_pool.py) - read-only, no schema changes.

Usage (from repo root, needs `pip install scapy pymongo`):
    MONGO_HOST=localhost python3 tools/generate_dh_export_beginner_pcaps.py
"""
import os

from pymongo import MongoClient
from scapy.all import IP, TCP, UDP, Ether, Raw, wrpcap

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "admin")
MONGO_DB = os.getenv("MONGO_DB", "ctf_database")

TLS_CLIENT_IP, TLS_SERVER_IP = "10.0.0.10", "10.0.0.20"
TLS_CLIENT_PORT, TLS_SERVER_PORT = 51000, 443

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "custom", "assets", "0400")


def fetch_variants():
    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USER,
                          password=MONGO_PASSWORD, authSource="admin")
    return list(client[MONGO_DB].dh_export_variants.find({}))


def tcp_conversation(src_ip, dst_ip, sport, dport, flights):
    """3-way handshake, one PSH+ACK segment (+ACK) per flight, FIN teardown."""
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


def decoy_http():
    req = b"GET /index.html HTTP/1.1\r\nHost: example.local\r\n\r\n"
    resp = b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello world!\n"
    return tcp_conversation("10.0.0.30", "10.0.0.40", 52000, 80, [(True, req), (False, resp)])


def decoy_dns():
    eth = dict(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
    query = (Ether(**eth) / IP(src="10.0.0.30", dst="10.0.0.1") / UDP(sport=53000, dport=53) /
             Raw(bytes.fromhex("aaaa01000001000000000000") + b"\x07example\x03com\x00\x00\x01\x00\x01"))
    response = (Ether(**eth) / IP(src="10.0.0.1", dst="10.0.0.30") / UDP(sport=53, dport=53000) /
                Raw(bytes.fromhex("aaaa81800001000100000000") +
                    b"\x07example\x03com\x00\x00\x01\x00\x01" +
                    b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04\x5d\xb8\xd8\x22"))
    return [query, response]


def build_pcap_packets(variant: dict) -> list:
    tls_packets = tcp_conversation(
        TLS_CLIENT_IP, TLS_SERVER_IP, TLS_CLIENT_PORT, TLS_SERVER_PORT,
        [
            (True, bytes.fromhex(variant["client_flight_1_hex"])),
            (False, bytes.fromhex(variant["server_flight_1_hex"])),
            (True, bytes.fromhex(variant["client_flight_2_hex"])),
            (False, bytes.fromhex(variant["server_flight_2_hex"])),
        ],
    )
    return decoy_dns() + decoy_http() + tls_packets + decoy_http()


def main():
    variants = fetch_variants()
    if not variants:
        raise SystemExit(
            "No dh_export_variants found - run "
            "custom/challengebackend/scripts/generate_dh_export_pool.py first."
        )
    for v in variants:
        index = v["index"]
        out_dir = os.path.join(OUT_DIR, str(index))
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "capture.pcap")
        wrpcap(out_path, build_pcap_packets(v))
        print(f"  variant {index + 1}/{len(variants)}: wrote {out_path}")
    print(f"Done: {len(variants)} pcaps written to {OUT_DIR}")


if __name__ == "__main__":
    main()
