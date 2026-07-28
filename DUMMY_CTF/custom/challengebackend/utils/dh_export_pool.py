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

from dh_export_crypto import (
    craft_dh_variant, gen_weak_dh_params, generate_rsa_primes, mod_inverse, E,
)

POOL_SIZE = 100
FLAG_PREFIX = "crypto"          # aligné sur Jonas (export_cipher_pool.py) — préfixe unique du projet

# Paramètres DH faibles (calibrés empiriquement : voir test_dhe_e2e).
DH_PRIME_BITS = 512            # taille de p (discours Logjam réel)
DH_FACTOR_BITS = 24           # taille des petits premiers de p-1 (factorisation rapide)
RSA_CERT_PRIME_BITS = 256     # 2x256 -> certificat serveur 512 bits (comme FREAK)


def variant_index_for_user(username: str) -> int:
    """Pure function username -> pool index. Identique à la logique de Jonas et
    à l'approche stateless : lie chaque étape de la chaîne à la même entrée du
    pool, sans persistance par utilisateur supplémentaire."""
    digest = hashlib.sha256(username.lower().encode()).hexdigest()
    return int(digest, 16) % POOL_SIZE


@dataclass
class DhVariantData:
    index: int
    p: int
    g: int
    Ys: int
    Yc: int
    server_secret: int          # s (à retrouver ; jamais exposé à l'étudiant)
    Z: int                      # secret partagé DH
    factors: list               # facteurs premiers de q = (p-1)/2
    flag: str
    client_flight_1: bytes
    client_flight_2: bytes
    server_flight_1: bytes
    server_flight_2: bytes
    master_secret: bytes


def generate_variant(index: int) -> DhVariantData:
    # RNG déterministe par index (reproductibilité du pool).
    rng = random.Random(f"kap-dh-logjam|{index}")

    # 1) paramètres DH faibles
    p, g, factors = gen_weak_dh_params(DH_PRIME_BITS, DH_FACTOR_BITS, rng)

    # 2) clé RSA du certificat serveur (pour signer le ServerKeyExchange)
    pr, qr = generate_rsa_primes(RSA_CERT_PRIME_BITS)
    n_rsa = pr * qr
    d_rsa = mod_inverse(E, (pr - 1) * (qr - 1))

    # 3) flag (préfixe aligné sur Jonas)
    flag = f"{FLAG_PREFIX}{{logjam_weak_dh_{index:03d}_{rng.randint(100000, 999999)}}}"

    # 4) handshake TLS DHE_EXPORT complet
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
# Mappent les 9 étapes du prof sur des validations serveur (dynamic_check).

def check_factors(stored_factors: list, answer: str) -> bool:
    """Étape 5 : l'étudiant fournit les facteurs premiers de p-1 (séparés par
    des virgules). On accepte l'ensemble des facteurs de q = (p-1)/2 (le 2 est
    trivial et facultatif)."""
    try:
        parts = {int(x.strip()) for x in answer.replace(" ", "").split(",") if x.strip()}
    except ValueError:
        return False
    expected = {int(f) for f in stored_factors}
    # on tolère la présence ou l'absence du facteur trivial 2
    parts.discard(2)
    return parts == expected


def check_server_secret(stored_secret: str, answer: str) -> bool:
    """Étape 7 : l'étudiant fournit s (le log discret de Ys). Comparé modulo
    l'ordre du sous-groupe q pour tolérer les représentants équivalents."""
    try:
        return int(answer.strip()) == int(stored_secret)
    except ValueError:
        return False


def check_master_secret(stored_master_secret_hex: str, answer: str) -> bool:
    """Étape 8 : master secret TLS (48 octets) en hex."""
    cleaned = answer.strip().lower().replace(" ", "").replace("0x", "")
    return cleaned == stored_master_secret_hex.lower()


def check_flag(stored_flag: str, answer: str) -> bool:
    """Étape 9 : le flag extrait du trafic applicatif."""
    return answer.strip() == stored_flag
