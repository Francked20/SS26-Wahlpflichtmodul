"""Pool der Export-Cipher (day 3) Varianten + Answer-Comparators fuer dynamic_check"""

import hashlib
import random
from dataclasses import dataclass

from utils.export_cipher_crypto import craft_variant, generate_rsa_primes

POOL_SIZE = 100
FLAG_PREFIX = "crypto"

BITS_256_PRIME = 128  # two 128-bit primes -> a 256-bit practice modulus
BITS_512_PRIME = 256  # two 256-bit primes -> the "captured" 512-bit modulus


def variant_index_for_user(username: str) -> int:
    """Pure function username -> pool index"""
    digest = hashlib.sha256(username.lower().encode()).hexdigest()
    return int(digest, 16) % POOL_SIZE


@dataclass
class VariantData:
    index: int
    n256: int
    p256: int
    q256: int
    n512: int
    p512: int
    q512: int
    flag: str
    client_flight_1: bytes
    client_flight_2: bytes
    server_flight_1: bytes
    server_flight_2: bytes
    master_secret: bytes


def generate_variant(index: int) -> VariantData:
    p256, q256 = generate_rsa_primes(BITS_256_PRIME)
    n256 = p256 * q256

    p512, q512 = generate_rsa_primes(BITS_512_PRIME)
    n512 = p512 * q512

    flag = f"{FLAG_PREFIX}{{export_cipher_freak_{index:03d}_{random.randint(100000, 999999)}}}"

    variant_bytes = craft_variant(n512, p512, q512, flag.encode())

    return VariantData(
        index=index,
        n256=n256, p256=p256, q256=q256,
        n512=n512, p512=p512, q512=q512,
        flag=flag,
        client_flight_1=variant_bytes.client_flight_1,
        client_flight_2=variant_bytes.client_flight_2,
        server_flight_1=variant_bytes.server_flight_1,
        server_flight_2=variant_bytes.server_flight_2,
        master_secret=variant_bytes.master_secret,
    )


# per-stage answer comparators (pure, no DB access)

def check_factor256(stored_p256: str, stored_q256: str, answer: str) -> bool:
    try:
        parts = [int(x.strip()) for x in answer.replace(" ", "").split(",") if x.strip()]
    except ValueError:
        return False
    if len(parts) != 2:
        return False
    return set(parts) == {int(stored_p256), int(stored_q256)}


def check_factor512(stored_q512: str, answer: str) -> bool:
    try:
        return int(answer.strip()) == int(stored_q512)
    except ValueError:
        return False


def check_master_secret(stored_master_secret_hex: str, answer: str) -> bool:
    cleaned = answer.strip().lower().replace(" ", "").replace("0x", "")
    return cleaned == stored_master_secret_hex.lower()


def check_flag(stored_flag: str, answer: str) -> bool:
    return answer.strip() == stored_flag
