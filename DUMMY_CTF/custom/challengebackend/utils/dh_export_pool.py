"""Pool der weak-DH (Logjam) Varianten + Answer-Comparators fuer dynamic_check"""

import hashlib
import random
from dataclasses import dataclass

from utils.dh_export_crypto import (
    craft_dh_variant, gen_weak_dh_params, generate_rsa_primes, mod_inverse, E,
)

POOL_SIZE = 100
FLAG_PREFIX = "crypto"          # project-wide flag prefix (matches export_cipher_pool.py)

# Weak DH parameters (empirically calibrated: see test_dhe_e2e)
DH_PRIME_BITS = 512            # size of p (real Logjam scale)
DH_FACTOR_BITS = 24           # size of the small primes of p-1 (fast factorisation)
RSA_CERT_PRIME_BITS = 256     # 2x256 -> 512-bit server certificate (like FREAK)


def variant_index_for_user(username: str) -> int:
    """Pure function username -> pool index"""
    digest = hashlib.sha256(username.lower().encode()).hexdigest()
    return int(digest, 16) % POOL_SIZE


@dataclass
class DhVariantData:
    index: int
    p: int
    g: int
    Ys: int
    Yc: int
    server_secret: int          # s (to be recovered; never exposed to the student)
    Z: int                      # DH shared secret
    factors: list               # prime factors of q = (p-1)/2
    flag: str
    client_flight_1: bytes
    client_flight_2: bytes
    server_flight_1: bytes
    server_flight_2: bytes
    master_secret: bytes


def generate_variant(index: int) -> DhVariantData:
    rng = random.Random(f"kap-dh-logjam|{index}")

    p, g, factors = gen_weak_dh_params(DH_PRIME_BITS, DH_FACTOR_BITS, rng)

    pr, qr = generate_rsa_primes(RSA_CERT_PRIME_BITS)
    n_rsa = pr * qr
    d_rsa = mod_inverse(E, (pr - 1) * (qr - 1))

    flag = f"{FLAG_PREFIX}{{logjam_weak_dh_{index:03d}_{rng.randint(100000, 999999)}}}"

    vb = craft_dh_variant(p, g, factors, n_rsa, d_rsa, flag.encode(), rng)

    return DhVariantData(
        index=index,
        p=vb.p, g=vb.g, Ys=vb.Ys, Yc=vb.Yc,
        server_secret=vb.server_secret, Z=vb.Z, factors=vb.factors,
        flag=flag,
        client_flight_1=vb.client_flight_1,
        client_flight_2=vb.client_flight_2,
        server_flight_1=vb.server_flight_1,
        server_flight_2=vb.server_flight_2,
        master_secret=vb.master_secret,
    )


# per-stage answer comparators (pure, no DB access)

def check_factors(stored_factors: list, answer: str) -> bool:
    """Primfaktoren von p-1, comma-separated"""
    try:
        parts = {int(x.strip()) for x in answer.replace(" ", "").split(",") if x.strip()}
    except ValueError:
        return False
    expected = {int(f) for f in stored_factors}
    parts.discard(2)
    return parts == expected


def check_server_secret(stored_secret: str, answer: str) -> bool:
    try:
        return int(answer.strip()) == int(stored_secret)
    except ValueError:
        return False


def check_master_secret(stored_master_secret_hex: str, answer: str) -> bool:
    cleaned = answer.strip().lower().replace(" ", "").replace("0x", "")
    return cleaned == stored_master_secret_hex.lower()


def check_flag(stored_flag: str, answer: str) -> bool:
    return answer.strip() == stored_flag
