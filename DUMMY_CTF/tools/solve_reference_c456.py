"""Reference solver fuer C4, C5, C6."""

import base64
import json
import math
import time
from functools import reduce
from sympy import factorint
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HKDF_INFO = b"kapitel-02-dh-aead-v1"


def parse_cap(path):
    d = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
    return d


def derive_key(s, p):
    nbytes = (p.bit_length() + 7) // 8
    ikm = s.to_bytes(nbytes, "big")
    return HKDF(algorithm=hashes.SHA256(), length=32,
                salt=None, info=HKDF_INFO).derive(ikm)


def decrypt(key, nonce_b64, ct_b64):
    nonce = base64.b64decode(nonce_b64)
    ct = base64.b64decode(ct_b64)
    return AESGCM(key).decrypt(nonce, ct, None)


def bsgs(g, h, p, order):
    m = int(math.isqrt(order)) + 1
    table, e = {}, 1
    for j in range(m):
        table.setdefault(e, j)
        e = (e * g) % p
    gm_inv = pow(pow(g, m, p), p - 2, p)
    gamma = h
    for i in range(m):
        if gamma in table:
            return i * m + table[gamma]
        gamma = (gamma * gm_inv) % p
    return None


def crt(res, mod):
    N = reduce(lambda a, b: a * b, mod)
    x = 0
    for r, m in zip(res, mod):
        Ni = N // m
        x += r * Ni * pow(Ni, -1, m)
    return x % N


def element_order_divisors(g, p, phi_factors):
    """Ordnung von g anhand der Primfaktoren von p-1."""
    order = p - 1
    for q, e in phi_factors.items():
        for _ in range(e):
            if pow(g, order // q, p) == 1:
                order //= q
    return order


# ---------------------------------------------------------------- C4
def solve_c4(cap):
    p = int(cap["PARAM_P"]); g = int(cap["PARAM_G"])
    A = int(cap["ALICE_PUBLIC_A"]); B = int(cap["BOB_PUBLIC_B"])
    phi_fac = factorint(p - 1)
    q = element_order_divisors(g, p, phi_fac)
    t = time.time()
    a = bsgs(g, A, p, q)
    dt = time.time() - t
    s = pow(B, a, p)
    pt = decrypt(derive_key(s, p), cap["RECORD_NONCE_B64"], cap["RECORD_CIPHERTEXT_B64"])
    return json.loads(pt)["flag"], {"order_q": q, "q_bits": q.bit_length(), "bsgs_time": round(dt, 3)}


# ---------------------------------------------------------------- C5
def solve_c5(cap):
    p = int(cap["PARAM_P"]); g = int(cap["PARAM_G"])
    A = int(cap["ALICE_PUBLIC_A"]); B = int(cap["BOB_PUBLIC_B"])
    phi_fac = factorint(p - 1)
    primes = list(phi_fac.keys())
    t = time.time()
    res, mod = [], []
    order = p - 1
    for q in primes:
        cof = order // q
        res.append(bsgs(pow(g, cof, p), pow(A, cof, p), p, q))
        mod.append(q)
    a = crt(res, mod)
    dt = time.time() - t
    s = pow(B, a, p)
    pt = decrypt(derive_key(s, p), cap["RECORD_NONCE_B64"], cap["RECORD_CIPHERTEXT_B64"])
    return json.loads(pt)["flag"], {"n_factors": len(primes), "ph_time": round(dt, 3), "bits_p": p.bit_length()}


# ---------------------------------------------------------------- C6
def solve_c6(cap):
    p = int(cap["PARAM_P"]); g = int(cap["PARAM_G"])
    A = int(cap["ALICE_PUBLIC_A"]); B = int(cap["BOB_PUBLIC_B"])
    M1 = int(cap["MALLORY_TO_ALICE_M1"]); M2 = int(cap["MALLORY_TO_BOB_M2"])
    m1 = int(cap["MALLORY_SECRET_M1"]); m2 = int(cap["MALLORY_SECRET_M2"])
    s_left = pow(A, m1, p)
    s_right = pow(B, m2, p)
    pt_ab = decrypt(derive_key(s_left, p), cap["RECORD_AB_NONCE_B64"], cap["RECORD_AB_CIPHERTEXT_B64"])
    pt_ba = decrypt(derive_key(s_right, p), cap["RECORD_BA_NONCE_B64"], cap["RECORD_BA_CIPHERTEXT_B64"])
    j_ab = json.loads(pt_ab); j_ba = json.loads(pt_ba)
    flag = j_ab["flag_teil_1"] + j_ba["flag_teil_2"]
    detection = (M1 != B)
    return flag, {"detection_M1_ne_B": detection, "bits_p": p.bit_length(),
                  "frag1": j_ab["flag_teil_1"], "frag2": j_ba["flag_teil_2"]}


FLAGS = {
    "challenge_4": "hiy{dh_small_subgroup_the_generator_betrayed_you_5150}",
    "challenge_5": "hiy{dh_logjam_export_grade_is_a_backdoor_1996}",
    "challenge_6": "hiy{dh_mitm_you_are_the_man_in_the_middle_2a2b}",
}

if __name__ == "__main__":
    base = "custom/assets/0200"
    for index in range(3):
        print(f"\n########## Variante {index} ##########")
        for name, solver in [("challenge_4", solve_c4), ("challenge_5", solve_c5), ("challenge_6", solve_c6)]:
            cap = parse_cap(f"{base}/{index}/{name}.tcvcap")
            flag, info = solver(cap)
            ok = flag == FLAGS[name]
            mark = "OK " if ok else "FAIL"
            print(f"  [{mark}] {name}: {info}")
            if not ok:
                print(f"        got={flag!r} expected={FLAGS[name]!r}")
