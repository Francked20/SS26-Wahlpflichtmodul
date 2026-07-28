"""Generates the fixed pool of weak-DH (Logjam) challenge variants, and the
pure per-stage answer comparators used by endpoints/dh_export.py's
`/check_answer` (called from core/backend's Challenge.check_answer
`dynamic_check` branch over HTTP).

Companion to Jonas' export_cipher_pool.py (RSA export / FREAK). Same design:
kept independent of Beanie/Mongo — DB lookups happen in the endpoint module,
this module only does crypto + plain-value comparisons so it stays unit-testable
in isolation (see verify_dh_export_crypto.py).

The weakness: a weak prime p = 2q+1 with q = q_1*...*q_n (p-1 fully smooth), so
the discrete log breaks via yafu (factor p-1) + Pohlig-Hellman. Calibrated to
p = 512 bits with ~24-bit factors -> factorisation + PH resolvable in seconds.
"""

import hashlib
import random
from dataclasses import dataclass

from utils.dh_export_crypto import (
    craft_dh_variant, gen_weak_dh_params, generate_rsa_primes, mod_inverse, E,
)

POOL_SIZE = 100
FLAG_PREFIX = "crypto"          # project-wide flag prefix (matches export_cipher_pool.py)

# Weak DH parameters (empirically calibrated: see test_dhe_e2e).
DH_PRIME_BITS = 512            # size of p (real Logjam scale)
DH_FACTOR_BITS = 24           # size of the small primes of p-1 (fast factorisation)
RSA_CERT_PRIME_BITS = 256     # 2x256 -> 512-bit server certificate (like FREAK)


def variant_index_for_user(username: str) -> int:
    """Pure function username -> pool index. Stateless: binds every step of the
    chain to the same pool entry without extra per-user persistence."""
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
    """Build the full weak-DH challenge data for one pool index (deterministic)."""
    # Deterministic RNG per index (reproducible pool).
    rng = random.Random(f"kap-dh-logjam|{index}")

    # 1) weak DH parameters
    p, g, factors = gen_weak_dh_params(DH_PRIME_BITS, DH_FACTOR_BITS, rng)

    # 2) RSA key of the server certificate (to sign the ServerKeyExchange)
    pr, qr = generate_rsa_primes(RSA_CERT_PRIME_BITS)
    n_rsa = pr * qr
    d_rsa = mod_inverse(E, (pr - 1) * (qr - 1))

    # 3) flag
    flag = f"{FLAG_PREFIX}{{logjam_weak_dh_{index:03d}_{rng.randint(100000, 999999)}}}"

    # 4) complete TLS DHE_EXPORT handshake
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


# --- per-stage answer comparators (pure, no DB access) ---
# Map the 9 exercise steps onto server-side validations (dynamic_check).

def check_factors(stored_factors: list, answer: str) -> bool:
    """Step 5: the student supplies the prime factors of p-1 (comma-separated).
    We accept the set of factors of q = (p-1)/2 (the 2 is trivial and optional)."""
    try:
        parts = {int(x.strip()) for x in answer.replace(" ", "").split(",") if x.strip()}
    except ValueError:
        return False
    expected = {int(f) for f in stored_factors}
    # tolerate the presence or absence of the trivial factor 2
    parts.discard(2)
    return parts == expected


def check_server_secret(stored_secret: str, answer: str) -> bool:
    """Step 7: the student supplies s (the discrete log of Ys)."""
    try:
        return int(answer.strip()) == int(stored_secret)
    except ValueError:
        return False


def check_master_secret(stored_master_secret_hex: str, answer: str) -> bool:
    """Step 8: the TLS master secret (48 bytes) in hex."""
    cleaned = answer.strip().lower().replace(" ", "").replace("0x", "")
    return cleaned == stored_master_secret_hex.lower()


def check_flag(stored_flag: str, answer: str) -> bool:
    """Step 9: the flag extracted from the application traffic."""
    return answer.strip() == stored_flag
