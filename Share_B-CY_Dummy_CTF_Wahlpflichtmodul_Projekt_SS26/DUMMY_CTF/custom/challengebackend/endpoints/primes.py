import math
from fastapi import APIRouter

router = APIRouter()

# Beispiel-Flags für die Randomisierung
FLAGS_PRIME = [
    "crypto{num3ru5_pr1mu5_d13_3r573_z4hl}",
    "crypto{numeru5_pr1mu5_d13_3r573_z4hl}",
    "crypto{num3rus_pr1mu5_d13_3r573_z4hl}",
    "crypto{num3ru5_primu5_d13_3r573_z4hl}",
    "crypto{num3ru5_pr1mus_d13_3r573_z4hl}",
    "crypto{num3ru5_pr1mu5_di3_3r573_z4hl}",
    "crypto{num3ru5_pr1mu5_d1e_3r573_z4hl}",
    "crypto{num3ru5_pr1mu5_d13_er573_z4hl}",
    "crypto{num3ru5_pr1mu5_d13_3rs73_z4hl}",
    "crypto{num3ru5_pr1mu5_d13_3r5t3_z4hl}",
]

FLAGS_SAFEPRIME = [
    "crypto{s4f3_pr1m3s_s1nd_c00l}",
    "crypto{saf3_pr1m3s_s1nd_c00l}",
    "crypto{s4fe_pr1m3s_s1nd_c00l}",
    "crypto{s4f3_prim3s_s1nd_c00l}",
    "crypto{s4f3_pr1mes_s1nd_c00l}",
    "crypto{s4f3_pr1m3s_sind_c00l}",
    "crypto{s4f3_pr1m3s_s1nd_co0l}",
    "crypto{s4f3_pr1m3s_s1nd_c0ol}",
    "crypto{s4f3_pr1m3s_s1nd_cool}",
    "crypto{saf3_pr1m3s_s1nd_c0ol}",
]

# --- Hilfsfunktionen ---
def is_probable_prime(n: int, k: int = 10) -> bool:
    """Miller-Rabin Primality Test"""
    if n < 2:
        return False
    # kleine Primzahlen direkt prüfen
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    if n in small_primes:
        return True
    if any(n % p == 0 for p in small_primes):
        return False

    # Schreibe n-1 als 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    import random
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def bit_length(n: int) -> int:
    return n.bit_length()

# --- Routen ---
@router.get("/{index}/prime/{prime}/")
def check_prime(index: int, prime: str):
    if index < 0 or index >= len(FLAGS_PRIME):
        return {"error": "invalid index"}

    try:
        p = int(prime)
    except ValueError:
        return {"error": "prime must be an integer"}

    required_bits = 4120 + index  # 4120 .. 4129
    if bit_length(p) != required_bits:
        return {"error": f"prime must have exactly {required_bits} bits"}

    if not is_probable_prime(p):
        return {"error": "number is not prime"}

    return {"flag": FLAGS_PRIME[index]}

@router.get("/{index}/safe_prime/{safe_prime}/")
def check_safe_prime(index: int, safe_prime: str):
    if index < 0 or index >= len(FLAGS_SAFEPRIME):
        return {"error": "invalid index"}

    try:
        p = int(safe_prime)
    except ValueError:
        return {"error": "safe_prime must be an integer"}

    required_bits = 1120 + index  # 1120 .. 1129
    if bit_length(p) != required_bits:
        return {"error": f"safe_prime must have exactly {required_bits} bits"}

    # Safe Prime: p ist prim und (p-1)/2 ist ebenfalls prim
    if not is_probable_prime(p):
        return {"error": "number is not prime"}
    if not is_probable_prime((p - 1) // 2):
        return {"error": "number is not a safe prime"}

    return {"flag": FLAGS_SAFEPRIME[index]}
