"""
tools/generate_dh_variants.py  —  VAGUE 1 (refonte ohne Backend)

Générateur ré-exécutable des variantes du Kapitel 02.

NOUVEAU MODÈLE (THM/HTB-style) :
  - Pas de backend. Validation 100% statique côté framework.
  - Le FLAG est COMMUN par challenge (le même dans toutes les variantes d'un
    challenge). L'étudiant l'obtient en déchiffrant SA variante (params uniques),
    puis le colle dans la task. Un voisin ne peut pas deviner le flag sans
    résoudre sa propre instance.
  - Chaque variante garde des paramètres (p,g,A,B) et un trafic chiffré UNIQUES,
    dérivés de l'index (lui-même dérivé du username côté frontend).

Sorties :
  1) custom/assets/0200/<index>/<challenge>.tcvcap   (captures publiques)
  2) tools/solution_data.json                        (corrigé complet, privé)

  (Plus de dh_weak_data.json : le backend est supprimé.)

Reproductibilité : committer ce script + la seed. Régénérable à l'identique.

Calibrage (mesuré) :
  challenge_1  p-1 = 2*[12,13,14]           -> bits(p)~39,  BSGS/Brute-Force
  challenge_2  p-1 = 2*[40,40,41]           -> bits(p)~121, yafu+PH+CRT
  challenge_3  p-1 = 2*[30,32,34]*Q(80)     -> bits(p)~176, presque smooth, a<M
"""

import argparse
import base64
import hashlib
import json
import os
import random

from sympy import isprime, nextprime
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ======================================================================
# Challenges de la Vague 1
# ======================================================================
CHALLENGES = {
    "challenge_1": {"kind": "smooth",        "factor_bits": [12, 13, 14]},
    "challenge_2": {"kind": "smooth",        "factor_bits": [40, 40, 41]},
    "challenge_3": {"kind": "almost_smooth", "smooth_bits": [30, 32, 34],
                                             "big_bits": 80},
    # --- Akt II ---
    # C4 small subgroup : p-1 = 2*q*R, ord(g)=q (petit), a < q. Attaque BSGS
    #    dans la sous-groupe d'ordre q. q=36 bits -> BSGS ~0.4 s (mesuré).
    "challenge_4": {"kind": "small_subgroup", "q_bits": 36, "r_bits": 180},
    # C5 Logjam/export : p ~508 bits, p-1 = 2*prod(16 facteurs de 32 bits),
    #    ordre pleinement smooth -> Pohlig-Hellman + CRT ~2 s (mesuré).
    "challenge_5": {"kind": "smooth",        "factor_bits": [32] * 16},
    # C6 MITM : safe prime 256 bits (p = 2q+1). Le DLP est INFAISABLE — c'est
    #    le message pédagogique. L'étudiant est Mallory : il a m1,m2 dans la
    #    capture et recalcule les deux secrets de session directement.
    "challenge_6": {"kind": "mitm",          "prime_bits": 256},
    # --- Akt II (courbes elliptiques) ---
    # C7 ECDH intro : courbe de la banque pré-vérifiée (ordre premier, 40 bits).
    #    L'ECDLP y est cassable par BSGS sur courbe (~3-6 s en Python pur, mesuré).
    #    Écho de C1 (petit ordre -> log discret cassable), transposé sur courbe.
    "challenge_7": {"kind": "ecdh"},
    # C8 Invalid Curve : vraie courbe sûre (ordre premier 80 bits), mais Bob
    #    calcule d*P sans vérifier P sur la courbe. b n'intervient pas dans
    #    l'addition -> l'attaquant fait vivre P sur des courbes faibles E'(b').
    #    Extraction d mod q_i (petit BSGS) + CRT -> d. Banque + sondes figées.
    "challenge_8": {"kind": "invalid_curve"},
    # --- Akt III : systèmes dérivés (nonce) ---
    # C9 ElGamal nonce réutilisé : (c1,c2)=(g^k, m*y^k). Même k pour deux
    #    messages -> le second fuit via c2_2*m1/c2_1. DLP intact (p 256 bits).
    "challenge_9": {"kind": "elgamal_reuse", "prime_bits": 256},
    # C10 DSA nonce réutilisé : deux signatures avec le même k (donc même r)
    #    -> on retrouve k puis la clé privée x (faille PS3/Bitcoin). q 160 bits.
    "challenge_10": {"kind": "dsa_reuse", "q_bits": 160},
}
CHALLENGE_ORDER = ["challenge_1", "challenge_2", "challenge_3",
                   "challenge_4", "challenge_5", "challenge_6",
                   "challenge_7", "challenge_8",
                   "challenge_9", "challenge_10"]

# FLAGS COMMUNS par challenge (identiques pour toutes les variantes).
# Obtenus en déchiffrant sa propre variante. Non-devinables.
FLAGS = {
    "challenge_1": "hiy{dh_warmup_discrete_log_c0ffee}",
    "challenge_2": "hiy{dh_smooth_order_pohlig_hellman_1337}",
    "challenge_3": "hiy{dh_almost_smooth_the_prime_is_a_lie_4200}",
    "challenge_4": "hiy{dh_small_subgroup_the_generator_betrayed_you_5150}",
    "challenge_5": "hiy{dh_logjam_export_grade_is_a_backdoor_1996}",
    # C6 : deux directions déchiffrées -> deux fragments qui composent le flag.
    "challenge_6": "hiy{dh_mitm_you_are_the_man_in_the_middle_2a2b}",
    "challenge_7": "hiy{ecdh_small_curve_order_bsgs_on_the_curve_e11c}",
    "challenge_8": "hiy{invalid_curve_bob_forgot_to_check_the_point_cr7}",
    "challenge_9": "hiy{elgamal_nonce_reuse_two_ciphertexts_one_secret_a9f0}",
    "challenge_10": "hiy{dsa_nonce_reuse_ps3_style_private_key_recovery_beef}",
}

HKDF_INFO = b"kapitel-02-dh-aead-v1"

SENDER = "m.keller@nordwind.example"
RECIPIENT = "a.bauer@nordwind.example"
TIMESTAMP = "2026-01-15T09:24:11Z"


# ======================================================================
# Sous-seed déterministe par (master_seed, index, challenge)
# ======================================================================
def subseed(master_seed: int, index: int, challenge: str) -> int:
    h = hashlib.sha256(f"{master_seed}|{index}|{challenge}".encode()).digest()
    return int.from_bytes(h, "big")


# ======================================================================
# Primitives crypto (validées)
# ======================================================================
def rand_prime(bits, rng):
    return nextprime(rng.randrange(1 << (bits - 1), (1 << bits) - 1))


def gen_smooth(factor_bits, rng):
    while True:
        factors, m, ok = [2], 2, True
        for b in factor_bits:
            q = rand_prime(b, rng)
            if q in factors:
                ok = False
                break
            factors.append(q)
            m *= q
        if ok and isprime(m + 1):
            return m + 1, factors


def gen_almost_smooth(smooth_bits, big_bits, rng):
    while True:
        factors, m, ok = [2], 2, True
        for b in smooth_bits:
            q = rand_prime(b, rng)
            if q in factors:
                ok = False
                break
            factors.append(q)
            m *= q
        if not ok:
            continue
        Q = rand_prime(big_bits, rng)
        if isprime(m * Q + 1):
            return m * Q + 1, factors, Q


def find_generator(p, all_factors):
    phi = p - 1
    for g in range(2, p):
        if all(pow(g, phi // q, p) != 1 for q in set(all_factors)):
            return g
    raise RuntimeError("pas de générateur")


def gen_small_subgroup(q_bits, r_bits, rng):
    """
    C4 : p-1 = 2*q*R avec q petit (l'ordre du sous-groupe) et R grand premier.
    Renvoie (p, g, q, R) où g a exactement l'ordre q.
    """
    while True:
        q = rand_prime(q_bits, rng)
        R = rand_prime(r_bits, rng)
        p = 2 * q * R + 1
        if not isprime(p):
            continue
        # g d'ordre exactement q : élever une base à (p-1)/q, vérifier != 1
        for base in range(2, 200):
            g = pow(base, (p - 1) // q, p)
            if g != 1 and pow(g, q, p) == 1:
                return p, g, q, R


def gen_safe_prime(prime_bits, rng):
    """
    C6 : safe prime p = 2q+1 avec p et q premiers. Le DLP y est infaisable
    (pas de raccourci Pohlig-Hellman : ordre = 2q, q grand premier).
    Renvoie (p, q).
    """
    while True:
        q = rand_prime(prime_bits - 1, rng)
        p = 2 * q + 1
        if isprime(p):
            return p, q


# ======================================================================
# AEAD pédagogique
# ======================================================================
def shared_secret_bytes(s, p):
    nbytes = (p.bit_length() + 7) // 8
    return s.to_bytes(nbytes, "big")


def derive_key(s, p):
    ikm = shared_secret_bytes(s, p)
    return HKDF(algorithm=hashes.SHA256(), length=32,
                salt=None, info=HKDF_INFO).derive(ikm)


def build_capture(index, challenge, p, g, A, B, nonce, ct):
    payload = base64.b64encode(ct).decode()
    nonce_b = base64.b64encode(nonce).decode()
    lines = [
        "# ==== TCV-CAP v1 : abgefangener DH-Handshake ====",
        "# Format: KEY: WERT  (eine Angabe pro Zeile, # = Kommentar)",
        f"# Challenge: Kapitel 02 / {challenge} / Variante {index}",
        "CAPTURE_VERSION: 1",
        "SCHEME: Diffie-Hellman (multiplikativ, mod p)",
        f"PARAM_P: {p}",
        f"PARAM_G: {g}",
        "# --- oeffentliche Schluessel der beiden Parteien ---",
        f"ALICE_PUBLIC_A: {A}",
        f"BOB_PUBLIC_B: {B}",
        "# --- verschluesselter Datensatz ---",
        "KEY_DERIVATION: HKDF-SHA256( shared_secret_bytes )  info=kapitel-02-dh-aead-v1",
        "SHARED_SECRET_ENCODING: big-endian, Laenge = ceil(bits(p)/8) Bytes",
        "RECORD_CIPHER: AES-256-GCM",
        f"RECORD_NONCE_B64: {nonce_b}",
        f"RECORD_CIPHERTEXT_B64: {payload}",
        "# ==== Ende der Capture ====",
    ]
    return "\n".join(lines) + "\n"


def build_mitm_capture(index, p, g, A, B, M1, M2, m1, m2,
                       nonce_ab, ct_ab, nonce_ba, ct_ba):
    """
    C6 — capture MITM : DEUX handshakes interceptés.

    Setup : l'étudiant est Mallory, aktiv zwischen Anna und Bob. Anna glaubt,
    mit Bob zu sprechen, tauscht aber in Wahrheit mit Mallory (öffentlicher
    Wert M1). Ebenso Bob mit M2. Mallory kennt m1, m2 und entschlüsselt beide
    Richtungen.

    Enthält:
      - die echten öffentlichen Werte A (Anna) und B (Bob)
      - Mallorys eingeschleuste Werte M1 (Richtung Anna) und M2 (Richtung Bob)
      - Mallorys Geheimnisse m1, m2 (nur DIESE Capture; im echten Angriff wählt
        Mallory sie selbst — hier vorgegeben, damit ohne DLP entschlüsselt wird)
      - zwei verschlüsselte Datensätze: Anna->Bob (AB) und Bob->Anna (BA)
    """
    lines = [
        "# ==== TCV-CAP v1 : abgefangener MITM-Handshake ====",
        "# Format: KEY: WERT  (eine Angabe pro Zeile, # = Kommentar)",
        f"# Challenge: Kapitel 02 / challenge_6 / Variante {index}",
        "# SZENARIO: Sie sind Mallory und sitzen aktiv zwischen Anna und Bob.",
        "CAPTURE_VERSION: 1",
        "SCHEME: Diffie-Hellman (multiplikativ, mod p) — MITM",
        f"PARAM_P: {p}",
        f"PARAM_G: {g}",
        "# --- echte oeffentliche Werte der beiden Parteien ---",
        f"ALICE_PUBLIC_A: {A}",
        f"BOB_PUBLIC_B: {B}",
        "# --- von Mallory eingeschleuste Werte ---",
        "# M1 sieht Anna (sie haelt es fuer Bobs Schluessel);",
        "# M2 sieht Bob  (er haelt es fuer Annas Schluessel).",
        f"MALLORY_TO_ALICE_M1: {M1}",
        f"MALLORY_TO_BOB_M2: {M2}",
        "# --- Mallorys Geheimnisse (in dieser Uebung vorgegeben) ---",
        f"MALLORY_SECRET_M1: {m1}",
        f"MALLORY_SECRET_M2: {m2}",
        "# --- Ableitung & Chiffre (identisch zu den frueheren Challenges) ---",
        "KEY_DERIVATION: HKDF-SHA256( shared_secret_bytes )  info=kapitel-02-dh-aead-v1",
        "SHARED_SECRET_ENCODING: big-endian, Laenge = ceil(bits(p)/8) Bytes",
        "RECORD_CIPHER: AES-256-GCM",
        "# --- Datensatz 1 : Anna -> Bob (mit Schluessel der Anna-Seite) ---",
        f"RECORD_AB_NONCE_B64: {base64.b64encode(nonce_ab).decode()}",
        f"RECORD_AB_CIPHERTEXT_B64: {base64.b64encode(ct_ab).decode()}",
        "# --- Datensatz 2 : Bob -> Anna (mit Schluessel der Bob-Seite) ---",
        f"RECORD_BA_NONCE_B64: {base64.b64encode(nonce_ba).decode()}",
        f"RECORD_BA_CIPHERTEXT_B64: {base64.b64encode(ct_ba).decode()}",
        "# ==== Ende der Capture ====",
    ]
    return "\n".join(lines) + "\n"




# ======================================================================
# Challenge 7 — ECDH : banque de courbes + arithmétique elliptique
# ======================================================================
# Banque de courbes short-Weierstrass y^2 = x^3 + a*x + b (mod p) à ORDRE
# PREMIER n, pré-vérifiées hors ligne (comptage de points via PARI/Schoof) puis
# figées ici. p ~ 40 bits, p % 4 == 3 (racine carrée rapide). Comme #E = n est
# premier, TOUT point != O engendre le groupe entier. L'ECDLP y est cassable
# par BSGS sur courbe (~sqrt(n) ~ 2^20 pas) : quelques secondes.
#
# Reproductibilité : la banque est une constante committée. Les variantes
# tournent sur ces courbes (index % len(banque)) et diffèrent par le générateur
# G, les secrets a,b et le trafic chiffré.
CURVE_BANK = [
    {"p": 914179260187, "a": 240540860885, "b": 646526210858, "n": 914178540103},
    {"p": 648230001359, "a": 509558997370, "b": 207237248286, "n": 648229382629},
    {"p": 1006568713987, "a": 940867919128, "b": 50526976099, "n": 1006570272601},
    {"p": 853643047787, "a": 434622348559, "b": 769493624754, "n": 853642074401},
    {"p": 1011922880207, "a": 602581363848, "b": 21792701757, "n": 1011923768797},
    {"p": 563417083451, "a": 294057547147, "b": 52841301666, "n": 563417485307},
    {"p": 1003992667199, "a": 725491880233, "b": 727459747506, "n": 1003993311781},
    {"p": 1088067673183, "a": 752219914094, "b": 976994057422, "n": 1088067207187},
    {"p": 587329111723, "a": 24832935840, "b": 215683673685, "n": 587329938337},
    {"p": 819138846443, "a": 169885286262, "b": 498055269591, "n": 819137966599},
    {"p": 802178994439, "a": 436816199693, "b": 31920236524, "n": 802178205307},
    {"p": 642494676191, "a": 617824382694, "b": 460772819131, "n": 642494640727},
]



def ec_add(a, p, P, Q):
    """Addition de points sur y^2 = x^3 + a*x + b (mod p). O = None."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None                      # P + (-P) = O
    if x1 == x2 and y1 == y2:
        if y1 % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_mul(a, p, k, P):
    """Multiplication scalaire k*P (double-and-add)."""
    R = None
    if k < 0:
        k = -k
        P = (P[0], (-P[1]) % p)
    while k > 0:
        if k & 1:
            R = ec_add(a, p, R, P)
        P = ec_add(a, p, P, P)
        k >>= 1
    return R


def ec_find_generator(a, b, p, rng):
    """
    Trouve un point G sur la courbe (ordre premier -> ord(G) = n pour tout
    G != O). Utilise p % 4 == 3 : racine carrée = rhs^((p+1)/4) mod p.
    """
    for _ in range(10000):
        x = rng.randrange(0, p)
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            continue
        if pow(rhs, (p - 1) // 2, p) != 1:
            continue                     # pas un résidu quadratique
        y = pow(rhs, (p + 1) // 4, p)
        if (y * y) % p == rhs:
            return (x, y)
    raise RuntimeError("aucun générateur trouvé")


def ec_shared_secret_bytes(x_coord, p):
    """IKM pour HKDF = coordonnée x du point partagé, big-endian (ECDH standard)."""
    nbytes = (p.bit_length() + 7) // 8
    return x_coord.to_bytes(nbytes, "big")


def build_ecdh_capture(index, curve_idx, a, b, p, n, G, A, B, nonce, ct):
    payload = base64.b64encode(ct).decode()
    nonce_b = base64.b64encode(nonce).decode()
    lines = [
        "# ==== TCV-CAP v1 : abgefangener ECDH-Handshake ====",
        "# Format: KEY: WERT  (eine Angabe pro Zeile, # = Kommentar)",
        f"# Challenge: Kapitel 02 / challenge_7 / Variante {index}",
        "CAPTURE_VERSION: 1",
        "SCHEME: ECDH (Elliptische Kurve, kurze Weierstrass-Form)",
        "# --- Kurve: y^2 = x^3 + a*x + b (mod p) ---",
        f"CURVE_A: {a}",
        f"CURVE_B: {b}",
        f"CURVE_P: {p}",
        f"CURVE_ORDER_N: {n}",
        "# --- Basispunkt (Generator) G = (x, y) ---",
        f"GENERATOR_GX: {G[0]}",
        f"GENERATOR_GY: {G[1]}",
        "# --- oeffentliche Punkte der beiden Parteien ---",
        f"ALICE_PUBLIC_AX: {A[0]}",
        f"ALICE_PUBLIC_AY: {A[1]}",
        f"BOB_PUBLIC_BX: {B[0]}",
        f"BOB_PUBLIC_BY: {B[1]}",
        "# --- verschluesselter Datensatz ---",
        "KEY_DERIVATION: HKDF-SHA256( x-Koordinate des gemeinsamen Punktes )  info=kapitel-02-dh-aead-v1",
        "SHARED_SECRET_ENCODING: x(S) big-endian, Laenge = ceil(bits(p)/8) Bytes",
        "RECORD_CIPHER: AES-256-GCM",
        f"RECORD_NONCE_B64: {nonce_b}",
        f"RECORD_CIPHERTEXT_B64: {payload}",
        "# ==== Ende der Capture ====",
    ]
    return "\n".join(lines) + "\n"


def _make_ecdh_instance(index, rng, flag):
    """
    C7 — ECDH sur courbe à petit ordre premier.
      G basispunkt ; Alice a, Bob b ; A=a*G, B=b*G ; S = a*B = b*A.
      Cle = HKDF(x(S)). Attaque : BSGS sur courbe -> a (a < n), puis S=a*B.
    """
    curve = CURVE_BANK[index % len(CURVE_BANK)]
    a_c, b_c, p, n = curve["a"], curve["b"], curve["p"], curve["n"]

    G = ec_find_generator(a_c, b_c, p, rng)
    a_sec = rng.randrange(2, n)
    b_sec = rng.randrange(2, n)
    A = ec_mul(a_c, p, a_sec, G)
    B = ec_mul(a_c, p, b_sec, G)
    S = ec_mul(a_c, p, a_sec, B)
    assert S == ec_mul(a_c, p, b_sec, A), "incohérence ECDH"

    ikm = ec_shared_secret_bytes(S[0], p)
    key = HKDF(algorithm=hashes.SHA256(), length=32,
               salt=None, info=HKDF_INFO).derive(ikm)
    record = json.dumps({
        "from": SENDER, "to": RECIPIENT, "ts": TIMESTAMP,
        "betreff": "Zugangsdaten", "flag": flag,
    }, ensure_ascii=False).encode()
    nonce = bytes(rng.getrandbits(8) for _ in range(12))
    ct = AESGCM(key).encrypt(nonce, record, None)
    capture = build_ecdh_capture(index, index % len(CURVE_BANK),
                                 a_c, b_c, p, n, G, A, B, nonce, ct)

    solution = {
        "index": index, "challenge": "challenge_7",
        "curve_index": index % len(CURVE_BANK),
        "a_curve": str(a_c), "b_curve": str(b_c), "p": str(p), "n": str(n),
        "G": [str(G[0]), str(G[1])],
        "A": [str(A[0]), str(A[1])], "B": [str(B[0]), str(B[1])],
        "a_secret": str(a_sec), "b_secret": str(b_sec),
        "S": [str(S[0]), str(S[1])],
        "bits_p": p.bit_length(), "flag": flag,
    }
    return capture, solution




# ======================================================================
# Challenge 8 — Invalid Curve Attack : banque de courbes + sondes figées
# ======================================================================
# Vraie courbe E : y^2 = x^3 + a*x + b (mod p), ORDRE PREMIER 80 bits ->
# l'ECDLP direct est infaisable (BSGS ~ 2^40). Bob a une clé longue durée d.
# Vulnérabilité : Bob calcule d*P sans vérifier que P est sur E. Comme b
# n'intervient PAS dans les formules d'addition, un point sur une courbe
# invalide E'(b') (même a, b différent) est traité avec la même arithmétique.
# Sur E', l'ordre a de petits facteurs -> on extrait d mod q_i par petit BSGS,
# puis CRT. Les courbes + sondes (b', point P d'ordre q) sont pré-calculées
# (PARI/Schoof hors ligne) et figées ; seul R_i = d*P_i est calculé ici.
C8_CURVE_BANK = [
    {
        "p": 709293641283581964155779, "a": 328433133229914153312022, "b": 474564864168908699848805, "n": 709293641283431154916751,
        "probes": [
            {"b_invalid": 475835592184291301765023, "q": 2, "Px": 219691352789787076340968, "Py": 0},
            {"b_invalid": 221295591698698060825764, "q": 5, "Px": 473569289121510053680504, "Py": 140465460257527183726446},
            {"b_invalid": 28153439437970409307112, "q": 3, "Px": 268461658476182757422382, "Py": 355981676438352618072293},
            {"b_invalid": 1256091566856025156530, "q": 642151, "Px": 464203940426456726623679, "Py": 698026024508874245554374},
            {"b_invalid": 143968501347437069190744, "q": 29, "Px": 227856747040800751324470, "Py": 458155450607821518217564},
            {"b_invalid": 66076457602509671538447, "q": 13, "Px": 598645434447529564744913, "Py": 523740014860706139282908},
            {"b_invalid": 608719477089583324192737, "q": 7, "Px": 700242816997412073288061, "Py": 294285634825254325778390},
            {"b_invalid": 482416881766190690711064, "q": 11, "Px": 177728676461334238031106, "Py": 229329122970239831107252},
            {"b_invalid": 493219565051580453459056, "q": 31, "Px": 582106318244503710464287, "Py": 452508600951724337984940},
            {"b_invalid": 627750017354905061455539, "q": 211, "Px": 113920775120102552528467, "Py": 451634926494935397060255},
            {"b_invalid": 89948139535657186380722, "q": 251, "Px": 180064872766715943160383, "Py": 588361526258691234436575},
            {"b_invalid": 19509500544722549658627, "q": 101, "Px": 636051626299187187868872, "Py": 200113849208271621430827},
            {"b_invalid": 641423006320343963914105, "q": 277, "Px": 409915465085264411543936, "Py": 58424018310593247193242},
            {"b_invalid": 38311096933763198071916, "q": 17, "Px": 620394551979241682378353, "Py": 437367822202595511201142},
            {"b_invalid": 29076101330797160676586, "q": 4673, "Px": 258594470655703714700834, "Py": 293437114242313011189281},
        ],
    },
    {
        "p": 1155713804542602557806219, "a": 455523069420282178558128, "b": 911959436571614171072424, "n": 1155713804542510467381073,
        "probes": [
            {"b_invalid": 70889520156800376197457, "q": 71, "Px": 158934540104341107583644, "Py": 808177326049434956420245},
            {"b_invalid": 491645578650563078290413, "q": 29, "Px": 769178797391088143713899, "Py": 239734334373262979695517},
            {"b_invalid": 240666776769379471949613, "q": 2, "Px": 978981712256775532326241, "Py": 0},
            {"b_invalid": 605091581712848556130916, "q": 2039, "Px": 474902584208771304887564, "Py": 796277143048177549487596},
            {"b_invalid": 348806374322326523680266, "q": 109, "Px": 949464379307091077354097, "Py": 223187448651125329563527},
            {"b_invalid": 412741847444415208154872, "q": 17, "Px": 349346380449550921573989, "Py": 503578286474530367592727},
            {"b_invalid": 732841959581426314245819, "q": 79, "Px": 691791367636795177328308, "Py": 563817411125136192367983},
            {"b_invalid": 887036778213487197597865, "q": 13, "Px": 963977019732653936542656, "Py": 421595071517614113292689},
            {"b_invalid": 168945657939269246503698, "q": 3, "Px": 958922694666133249849150, "Py": 729615707568847852193333},
            {"b_invalid": 519337535123749538700175, "q": 5, "Px": 106127027735997420234421, "Py": 565343554803644685457161},
            {"b_invalid": 59664907066415275688600, "q": 769, "Px": 893379908837449256957021, "Py": 600956631325686557276532},
            {"b_invalid": 484612317683232788906132, "q": 67, "Px": 613283127824901846946758, "Py": 52435707838210395716483},
            {"b_invalid": 600894354818095015668213, "q": 2927, "Px": 803500364537094697840368, "Py": 250333218228098600876963},
            {"b_invalid": 858245853367736531501010, "q": 11, "Px": 1122678355850440737638067, "Py": 892436658659481377473925},
            {"b_invalid": 364126200483672674705083, "q": 7, "Px": 141404238819337697461343, "Py": 671235193810030318488168},
        ],
    },
    {
        "p": 677848992799463436012319, "a": 572991846146757319957351, "b": 237334632365501671698187, "n": 677848992800017300991107,
        "probes": [
            {"b_invalid": 509270252365648322420729, "q": 2, "Px": 299654165170488164279333, "Py": 0},
            {"b_invalid": 156699121618479401680681, "q": 3, "Px": 183520314867412015862407, "Py": 218340308696853376593982},
            {"b_invalid": 636820069081582157836051, "q": 7, "Px": 108058516562686952056602, "Py": 487607135557348726445621},
            {"b_invalid": 217638508262466341470029, "q": 37223, "Px": 446382869983499904769819, "Py": 120334981696719768897283},
            {"b_invalid": 100351983021276401601625, "q": 19, "Px": 401574627897704521092817, "Py": 656009100513767670409480},
            {"b_invalid": 480217332167737035437361, "q": 299393, "Px": 258538130497596488154766, "Py": 538468547988769098624777},
            {"b_invalid": 140952223072954538445575, "q": 5, "Px": 375466620695189063040291, "Py": 618755650089804114732808},
            {"b_invalid": 365721505101106487871098, "q": 1531, "Px": 512700675401420403871478, "Py": 323504312908165591121946},
            {"b_invalid": 349657387856185594803031, "q": 47, "Px": 316286296719380151793991, "Py": 625039071323599801023118},
            {"b_invalid": 414529011638197893022678, "q": 17, "Px": 348209470997617198825723, "Py": 623451597119565695179244},
            {"b_invalid": 422452169231953108884232, "q": 277, "Px": 58470926400275115801023, "Py": 463259913141498504235459},
            {"b_invalid": 322170691114188676105108, "q": 11, "Px": 129320612154949881513899, "Py": 461415297684202096771928},
            {"b_invalid": 414978003804667705414673, "q": 379, "Px": 393745047927153490543383, "Py": 609982862484709084072827},
        ],
    },
    {
        "p": 975983469488751989593123, "a": 326561703779951848369735, "b": 46899558147623953283595, "n": 975983469489999947183059,
        "probes": [
            {"b_invalid": 435205894818254573126767, "q": 2, "Px": 136368182765434948509962, "Py": 0},
            {"b_invalid": 516423564262843059452677, "q": 3, "Px": 886946158755669511538973, "Py": 179151491849124083753079},
            {"b_invalid": 549108960374077961605784, "q": 7, "Px": 168782336855452821374460, "Py": 304833351210840425018798},
            {"b_invalid": 245108913300817470038528, "q": 443, "Px": 759058440101320042223040, "Py": 88092967133549286075640},
            {"b_invalid": 180194525191965002265050, "q": 3943, "Px": 972956361484002211418424, "Py": 721198528310223424662232},
            {"b_invalid": 289660145897592602590942, "q": 440183, "Px": 700528646357311135376940, "Py": 650709289542840290594279},
            {"b_invalid": 391291986713620690502833, "q": 23, "Px": 860181799813491641266375, "Py": 566916553630505608565582},
            {"b_invalid": 666593893649984008337844, "q": 31, "Px": 329943623727983053314189, "Py": 108284806078930983167576},
            {"b_invalid": 14913474091982146845947, "q": 41, "Px": 232229988964233586401338, "Py": 747495285278575254052225},
            {"b_invalid": 609432168255769706230218, "q": 73, "Px": 211925311255658315350661, "Py": 19184676380422073799501},
            {"b_invalid": 855865025047872813712762, "q": 491, "Px": 425766084908011789243595, "Py": 307093011434722942135977},
            {"b_invalid": 63768107612168828796775, "q": 86587, "Px": 444949576645518037356419, "Py": 832548092585178698290435},
        ],
    },
    {
        "p": 1001664716436127772390143, "a": 787560410467243285136995, "b": 401335434930899976138054, "n": 1001664716434651113871633,
        "probes": [
            {"b_invalid": 652454204162695759937683, "q": 7, "Px": 696507242244326493288378, "Py": 913936873270497916888850},
            {"b_invalid": 934072797428179606339403, "q": 2, "Px": 167214862500088839146052, "Py": 0},
            {"b_invalid": 83054059459446200118690, "q": 739, "Px": 747137538217822814318897, "Py": 940856320145920876450939},
            {"b_invalid": 366212720012992230142399, "q": 67, "Px": 10027494387250767732234, "Py": 530791589011460355638192},
            {"b_invalid": 70733008011556205250276, "q": 3, "Px": 887733753035089392154627, "Py": 947871446109776827936392},
            {"b_invalid": 565267915800656199592465, "q": 5, "Px": 351479107141915064343791, "Py": 258888119994198051130773},
            {"b_invalid": 923387166765588332478780, "q": 37, "Px": 179780583641605954053289, "Py": 722646634826011071870709},
            {"b_invalid": 393369566656080653680642, "q": 23, "Px": 360821408717550727319387, "Py": 348253841743728621601848},
            {"b_invalid": 267600569345880913461777, "q": 59, "Px": 515973038668896907323325, "Py": 387208473518714676052558},
            {"b_invalid": 433746302659549883239306, "q": 3409409, "Px": 199277545482975547991878, "Py": 511894591149778251216177},
            {"b_invalid": 263734985641171624901209, "q": 11, "Px": 891722842773860546750372, "Py": 844748301822177403906555},
            {"b_invalid": 600754896301641261499376, "q": 29, "Px": 458966379691726730520447, "Py": 162554019418801751462717},
            {"b_invalid": 153761688966093985431154, "q": 43, "Px": 819698922247095108985312, "Py": 819350374651021288849818},
            {"b_invalid": 236875150735502878927193, "q": 193, "Px": 154934878607538107436543, "Py": 248233661106382850443483},
        ],
    },
]


def _make_invalid_curve_instance(index, rng, flag):
    """
    C8 — Invalid Curve. Bob: clé longue durée d, courbe sûre E (ordre premier).
      Sondes figées : pour chaque courbe invalide E'(b'), un point P d'ordre q.
      Oracle : R = d*P (calculé avec l'arithmétique de Bob -> pur Python ici).
      Finalité : d récupéré -> S = d*A_eph (Alice éphémère sur E) -> déchiffre.
    """
    curve = C8_CURVE_BANK[index % len(C8_CURVE_BANK)]
    a, b, p, n = curve["a"], curve["b"], curve["p"], curve["n"]

    # Bob's long-term secret d and public key B = d*G
    G = ec_find_generator(a, b, p, rng)
    d = rng.randrange(2, n)
    Bpub = ec_mul(a, p, d, G)

    # Oracle answers on the frozen probes: R_i = d * P_i (Bob's arithmetic).
    probes_out = []
    for pr in curve["probes"]:
        P = (pr["Px"], pr["Py"])
        R = ec_mul(a, p, d, P)          # d*P using curve E's `a` (b unused)
        probes_out.append({
            "b_invalid": pr["b_invalid"], "q": pr["q"],
            "Px": pr["Px"], "Py": pr["Py"],
            "Rx": (R[0] if R else 0), "Ry": (R[1] if R else 0),
        })

    # Traffic on the REAL curve: Alice ephemeral A_eph = e*G, S = d*A_eph.
    e = rng.randrange(2, n)
    A_eph = ec_mul(a, p, e, G)
    S = ec_mul(a, p, d, A_eph)          # = e * Bpub
    assert S == ec_mul(a, p, e, Bpub), "incohérence ECDH C8"

    ikm = ec_shared_secret_bytes(S[0], p)
    key = HKDF(algorithm=hashes.SHA256(), length=32,
               salt=None, info=HKDF_INFO).derive(ikm)
    record = json.dumps({
        "from": SENDER, "to": RECIPIENT, "ts": TIMESTAMP,
        "betreff": "Zugangsdaten", "flag": flag,
    }, ensure_ascii=False).encode()
    nonce = bytes(rng.getrandbits(8) for _ in range(12))
    ct = AESGCM(key).encrypt(nonce, record, None)

    capture = _build_c8_capture(index, a, b, p, n, G, Bpub, A_eph,
                                probes_out, nonce, ct)

    solution = {
        "index": index, "challenge": "challenge_8",
        "curve_index": index % len(C8_CURVE_BANK),
        "a": str(a), "b": str(b), "p": str(p), "n": str(n),
        "G": [str(G[0]), str(G[1])], "B": [str(Bpub[0]), str(Bpub[1])],
        "d_secret": str(d), "e_alice": str(e),
        "A_eph": [str(A_eph[0]), str(A_eph[1])], "S": [str(S[0]), str(S[1])],
        "n_probes": len(probes_out),
        "probe_qs": [pr["q"] for pr in probes_out],
        "bits_p": p.bit_length(), "flag": flag,
    }
    return capture, solution


def _build_c8_capture(index, a, b, p, n, G, Bpub, A_eph, probes_out, nonce, ct):
    payload = base64.b64encode(ct).decode()
    nonce_b = base64.b64encode(nonce).decode()
    lines = [
        "# ==== TCV-CAP v1 : Invalid-Curve-Angriff ====",
        "# Format: KEY: WERT  (eine Angabe pro Zeile, # = Kommentar)",
        f"# Challenge: Kapitel 02 / challenge_8 / Variante {index}",
        "# SZENARIO: Bob nutzt eine sichere Kurve E und einen festen geheimen",
        "# Schluessel d. ABER Bob prueft eingehende Punkte NICHT. Man schickt",
        "# ihm Punkte P auf schwachen Kurven E'(b') und beobachtet R = d*P.",
        "CAPTURE_VERSION: 1",
        "SCHEME: ECDH (Elliptische Kurve) — Invalid-Curve-Angriff",
        "# --- Bobs echte, sichere Kurve E: y^2 = x^3 + a*x + b (mod p) ---",
        f"CURVE_A: {a}",
        f"CURVE_B: {b}",
        f"CURVE_P: {p}",
        f"CURVE_ORDER_N: {n}",
        f"GENERATOR_GX: {G[0]}",
        f"GENERATOR_GY: {G[1]}",
        "# --- Bobs oeffentlicher Langzeit-Schluessel B = d*G ---",
        f"BOB_PUBLIC_BX: {Bpub[0]}",
        f"BOB_PUBLIC_BY: {Bpub[1]}",
        "# --- Orakel-Antworten: Punkte P auf schwachen Kurven E'(b') + R=d*P ---",
        "# ACHTUNG: Diese P liegen NICHT auf E, sondern auf E'(b') mit anderem b'.",
        f"N_PROBES: {len(probes_out)}",
    ]
    for i, pr in enumerate(probes_out):
        lines.append(f"PROBE_{i}_BINVALID: {pr['b_invalid']}")
        lines.append(f"PROBE_{i}_Q: {pr['q']}")
        lines.append(f"PROBE_{i}_PX: {pr['Px']}")
        lines.append(f"PROBE_{i}_PY: {pr['Py']}")
        lines.append(f"PROBE_{i}_RX: {pr['Rx']}")
        lines.append(f"PROBE_{i}_RY: {pr['Ry']}")
    lines += [
        "# --- verschluesselter Datensatz (ECDH auf der ECHTEN Kurve E) ---",
        "# Alices ephemerer Punkt A_eph liegt auf E; S = d*A_eph.",
        f"ALICE_EPH_AX: {A_eph[0]}",
        f"ALICE_EPH_AY: {A_eph[1]}",
        "KEY_DERIVATION: HKDF-SHA256( x-Koordinate von S = d*A_eph )  info=kapitel-02-dh-aead-v1",
        "SHARED_SECRET_ENCODING: x(S) big-endian, Laenge = ceil(bits(p)/8) Bytes",
        "RECORD_CIPHER: AES-256-GCM",
        f"RECORD_NONCE_B64: {nonce_b}",
        f"RECORD_CIPHERTEXT_B64: {payload}",
        "# ==== Ende der Capture ====",
    ]
    return "\n".join(lines) + "\n"




# ======================================================================
# Challenge 9 — ElGamal avec nonce réutilisé
# ======================================================================
def _make_elgamal_instance(index, cfg, rng, flag):
    """
    ElGamal : (c1, c2) = (g^k, m * y^k mod p). Le MÊME nonce k chiffre deux
    messages m1 (connu, "en-tête") et m2 (secret, sert de clé AES). Comme c1 et
    y^k sont identiques, on retrouve m2 = c2_2 * m1 * inv(c2_1) sans casser le DLP.
    Finalité : clé = HKDF(m2) -> AES-256-GCM -> flag.
    """
    bits = cfg["prime_bits"]
    # safe prime p = 2q+1 : DLP infaisable
    while True:
        q = rand_prime(bits - 1, rng)
        p = 2 * q + 1
        if isprime(p):
            break
    g = 2 if pow(2, q, p) != 1 else 3
    x = rng.randrange(2, p - 1)
    y = pow(g, x, p)                       # clé publique
    k = rng.randrange(2, p - 1)            # nonce RÉUTILISÉ
    m1 = rng.randrange(2, p - 1)           # message connu (en-tête)
    m2 = rng.randrange(2, p - 1)           # message secret (matériel de clé)
    yk = pow(y, k, p)
    c1 = pow(g, k, p)
    c2_1 = (m1 * yk) % p
    c2_2 = (m2 * yk) % p

    nbytes = (p.bit_length() + 7) // 8
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
               info=HKDF_INFO).derive(m2.to_bytes(nbytes, "big"))
    record = json.dumps({
        "from": SENDER, "to": RECIPIENT, "ts": TIMESTAMP,
        "betreff": "Zugangsdaten", "flag": flag,
    }, ensure_ascii=False).encode()
    nonce = bytes(rng.getrandbits(8) for _ in range(12))
    ct = AESGCM(key).encrypt(nonce, record, None)

    lines = [
        "# ==== TCV-CAP v1 : abgefangene ElGamal-Nachrichten ====",
        "# Format: KEY: WERT  (eine Angabe pro Zeile, # = Kommentar)",
        f"# Challenge: Kapitel 02 / challenge_9 / Variante {index}",
        "# SZENARIO: Zwei ElGamal-Chiffrate desselben Absenders. Achten Sie auf c1!",
        "CAPTURE_VERSION: 1",
        "SCHEME: ElGamal (multiplikativ, mod p)",
        f"PARAM_P: {p}",
        f"PARAM_G: {g}",
        f"PUBLIC_KEY_Y: {y}",
        "# --- Nachricht 1 : Klartext m1 ist BEKANNT (Header) ---",
        f"MESSAGE1_KNOWN_M1: {m1}",
        f"MESSAGE1_C1: {c1}",
        f"MESSAGE1_C2: {c2_1}",
        "# --- Nachricht 2 : m2 ist geheim und liefert den AES-Schluessel ---",
        f"MESSAGE2_C1: {c1}",
        f"MESSAGE2_C2: {c2_2}",
        "# --- verschluesselter Datensatz (Schluessel = HKDF(m2)) ---",
        "KEY_DERIVATION: HKDF-SHA256( m2 als big-endian, ceil(bits(p)/8) Bytes )  info=kapitel-02-dh-aead-v1",
        "RECORD_CIPHER: AES-256-GCM",
        f"RECORD_NONCE_B64: {base64.b64encode(nonce).decode()}",
        f"RECORD_CIPHERTEXT_B64: {base64.b64encode(ct).decode()}",
        "# ==== Ende der Capture ====",
    ]
    capture = "\n".join(lines) + "\n"
    solution = {
        "index": index, "challenge": "challenge_9",
        "p": str(p), "g": str(g), "y": str(y), "x": str(x), "k": str(k),
        "m1": str(m1), "m2": str(m2),
        "c1": str(c1), "c2_1": str(c2_1), "c2_2": str(c2_2),
        "bits_p": p.bit_length(), "flag": flag,
    }
    return capture, solution


# ======================================================================
# Challenge 10 — DSA avec nonce réutilisé (faille PS3 / Bitcoin)
# ======================================================================
def _dsa_hash(msg_bytes, q):
    return int.from_bytes(hashlib.sha256(msg_bytes).digest(), "big") % q


def _make_dsa_instance(index, cfg, rng, flag):
    """
    DSA : s = k^-1 (H(m) + x*r) mod q, r = (g^k mod p) mod q. Deux signatures
    avec le MÊME k (donc même r) -> k = (H(m1)-H(m2)) / (s1-s2) mod q, puis
    x = (s1*k - H(m1)) / r mod q. x = clé privée -> HKDF(x) -> AES -> flag.
    """
    qbits = cfg["q_bits"]
    q = rand_prime(qbits, rng)
    # p = q*t + 1 premier
    while True:
        t = rng.randrange(1 << 100, 1 << 101)
        p = q * t + 1
        if isprime(p):
            break
    h = rng.randrange(2, p - 1)
    g = pow(h, (p - 1) // q, p)
    if g == 1:
        g = pow(h + 1, (p - 1) // q, p)
    x = rng.randrange(2, q)                # clé privée
    y = pow(g, x, p)                       # clé publique
    k = rng.randrange(2, q)                # nonce RÉUTILISÉ
    r = pow(g, k, p) % q

    msg1 = b"UEBERWEISUNG-KONTO-A-2026"
    msg2 = b"UEBERWEISUNG-KONTO-B-2026"
    h1 = _dsa_hash(msg1, q)
    h2 = _dsa_hash(msg2, q)
    s1 = (pow(k, -1, q) * (h1 + x * r)) % q
    s2 = (pow(k, -1, q) * (h2 + x * r)) % q

    qbytes = (q.bit_length() + 7) // 8
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
               info=HKDF_INFO).derive(x.to_bytes(qbytes, "big"))
    record = json.dumps({
        "from": SENDER, "to": RECIPIENT, "ts": TIMESTAMP,
        "betreff": "Zugangsdaten", "flag": flag,
    }, ensure_ascii=False).encode()
    nonce = bytes(rng.getrandbits(8) for _ in range(12))
    ct = AESGCM(key).encrypt(nonce, record, None)

    lines = [
        "# ==== TCV-CAP v1 : abgefangene DSA-Signaturen ====",
        "# Format: KEY: WERT  (eine Angabe pro Zeile, # = Kommentar)",
        f"# Challenge: Kapitel 02 / challenge_10 / Variante {index}",
        "# SZENARIO: Zwei DSA-Signaturen desselben Schluessels. Achten Sie auf r!",
        "CAPTURE_VERSION: 1",
        "SCHEME: DSA (Signatur)",
        f"PARAM_P: {p}",
        f"PARAM_Q: {q}",
        f"PARAM_G: {g}",
        f"PUBLIC_KEY_Y: {y}",
        "HASH: SHA-256, dann mod q",
        "# --- Signatur 1 ---",
        f"SIG1_MESSAGE_UTF8: {msg1.decode()}",
        f"SIG1_R: {r}",
        f"SIG1_S: {s1}",
        "# --- Signatur 2 ---",
        f"SIG2_MESSAGE_UTF8: {msg2.decode()}",
        f"SIG2_R: {r}",
        f"SIG2_S: {s2}",
        "# --- verschluesselter Datensatz (Schluessel = HKDF(x), x = privater Schluessel) ---",
        "KEY_DERIVATION: HKDF-SHA256( x als big-endian, ceil(bits(q)/8) Bytes )  info=kapitel-02-dh-aead-v1",
        "RECORD_CIPHER: AES-256-GCM",
        f"RECORD_NONCE_B64: {base64.b64encode(nonce).decode()}",
        f"RECORD_CIPHERTEXT_B64: {base64.b64encode(ct).decode()}",
        "# ==== Ende der Capture ====",
    ]
    capture = "\n".join(lines) + "\n"
    solution = {
        "index": index, "challenge": "challenge_10",
        "p": str(p), "q": str(q), "g": str(g), "y": str(y),
        "x": str(x), "k": str(k), "r": str(r), "s1": str(s1), "s2": str(s2),
        "msg1": msg1.decode(), "msg2": msg2.decode(),
        "bits_q": q.bit_length(), "flag": flag,
    }
    return capture, solution


# ======================================================================
# Génération d'une instance (index, challenge)
# ======================================================================
def make_instance(master_seed, index, challenge):
    cfg = CHALLENGES[challenge]
    rng = random.Random(subseed(master_seed, index, challenge))
    flag = FLAGS[challenge]

    # ------------------------------------------------------------------
    # C6 — MITM : structure différente (deux handshakes, deux messages,
    # aucun DLP à casser). Traité à part, avec return anticipé.
    # ------------------------------------------------------------------
    if cfg["kind"] == "mitm":
        return _make_mitm_instance(index, cfg, rng, flag)

    # ------------------------------------------------------------------
    # C7 — ECDH : points sur courbe elliptique. Structure différente
    # (courbe + points (x,y) au lieu de scalaires). Return anticipé.
    # ------------------------------------------------------------------
    if cfg["kind"] == "ecdh":
        return _make_ecdh_instance(index, rng, flag)

    # ------------------------------------------------------------------
    # C8 — Invalid Curve : sondes sur courbes faibles + trafic sur la vraie
    # courbe. Structure dédiée (return anticipé).
    # ------------------------------------------------------------------
    if cfg["kind"] == "invalid_curve":
        return _make_invalid_curve_instance(index, rng, flag)

    # ------------------------------------------------------------------
    # Akt III — ElGamal (C9) et DSA (C10), nonce réutilisé. Return anticipé.
    # ------------------------------------------------------------------
    if cfg["kind"] == "elgamal_reuse":
        return _make_elgamal_instance(index, cfg, rng, flag)
    if cfg["kind"] == "dsa_reuse":
        return _make_dsa_instance(index, cfg, rng, flag)

    # ------------------------------------------------------------------
    # C1/C2/C5 (smooth), C3 (almost_smooth), C4 (small_subgroup)
    # ------------------------------------------------------------------
    Q = None
    if cfg["kind"] == "smooth":
        p, factors = gen_smooth(cfg["factor_bits"], rng)
        all_factors = factors
        a = rng.randrange(2, p - 1)
    elif cfg["kind"] == "almost_smooth":
        p, factors, Q = gen_almost_smooth(cfg["smooth_bits"], cfg["big_bits"], rng)
        all_factors = factors + [Q]
        M = 1
        for q in factors:
            M *= q
        a = rng.randrange(2, M)                 # a < partie smooth : résoluble
    elif cfg["kind"] == "small_subgroup":
        p, g_sub, q, R = gen_small_subgroup(cfg["q_bits"], cfg["r_bits"], rng)
        factors = [q]                            # facteur exploitable (petit)
        all_factors = [2, q, R]
        a = rng.randrange(2, q)                  # a < q : résoluble par BSGS dans <g>
    else:
        raise ValueError(f"kind inconnu: {cfg['kind']}")

    # Pour small_subgroup, g est imposé (ordre q). Sinon on le cherche.
    if cfg["kind"] == "small_subgroup":
        g = g_sub
    else:
        g = find_generator(p, all_factors)

    b = rng.randrange(2, p - 1)
    A, B = pow(g, a, p), pow(g, b, p)
    s = pow(B, a, p)
    assert s == pow(A, b, p), "incohérence DH"

    key = derive_key(s, p)
    record = json.dumps({
        "from": SENDER, "to": RECIPIENT, "ts": TIMESTAMP,
        "betreff": "Zugangsdaten", "flag": flag,
    }, ensure_ascii=False).encode()
    nonce = bytes(rng.getrandbits(8) for _ in range(12))
    ct = AESGCM(key).encrypt(nonce, record, None)
    capture = build_capture(index, challenge, p, g, A, B, nonce, ct)

    solution = {
        "index": index, "challenge": challenge,
        "p": str(p), "g": str(g), "A": str(A), "B": str(B),
        "a": str(a), "b": str(b), "s": str(s),
        "smooth_factors": [str(f) for f in factors],
        "Q": str(Q) if Q else None,
        "bits_p": p.bit_length(),
        "flag": flag,
    }
    if cfg["kind"] == "small_subgroup":
        solution["subgroup_order_q"] = str(factors[0])
    return capture, solution


def _make_mitm_instance(index, cfg, rng, flag):
    """
    C6 — MITM. Deux handshakes actifs :
      Anna <-> Mallory (M1) : clé s_left = A^m1 = M1^a
      Bob  <-> Mallory (M2) : clé s_right = B^m2 = M2^b
    Le flag est SCINDÉ en deux fragments, un par direction, pour forcer
    l'étudiant à déchiffrer les DEUX messages :
      - Anna->Bob  : contient la première moitié du flag
      - Bob->Anna  : contient la seconde moitié
    """
    p, q = gen_safe_prime(cfg["prime_bits"], rng)
    # Générateur : élément d'ordre q (grand) — suffisant pour DH, DLP infaisable.
    g = 2 if pow(2, q, p) != 1 else 3

    # Secrets réels d'Anna et Bob (jamais nécessaires à l'étudiant).
    a = rng.randrange(2, p - 1)
    b = rng.randrange(2, p - 1)
    A, B = pow(g, a, p), pow(g, b, p)

    # Secrets de Mallory (un par côté). Dans la capture, l'étudiant les reçoit.
    m1 = rng.randrange(2, p - 1)   # côté Anna
    m2 = rng.randrange(2, p - 1)   # côté Bob
    M1 = pow(g, m1, p)             # ce qu'Anna prend pour la clé de Bob
    M2 = pow(g, m2, p)             # ce que Bob prend pour la clé d'Anna

    # Clés de session telles que calculées par chaque partie :
    s_left = pow(A, m1, p)         # = pow(M1, a, p), la clé Anna<->Mallory
    s_right = pow(B, m2, p)        # = pow(M2, b, p), la clé Bob<->Mallory
    assert s_left == pow(M1, a, p) and s_right == pow(M2, b, p), "incohérence MITM"

    key_left = derive_key(s_left, p)
    key_right = derive_key(s_right, p)

    # Flag scindé : moitié dans chaque direction.
    half = len(flag) // 2
    frag_ab = flag[:half]          # Anna -> Bob
    frag_ba = flag[half:]          # Bob -> Anna

    rec_ab = json.dumps({
        "from": "a.bauer@nordwind.example", "to": "b.brandt@nordwind.example",
        "ts": TIMESTAMP, "richtung": "Anna->Bob",
        "hinweis": "erste Haelfte der Flagge", "flag_teil_1": frag_ab,
    }, ensure_ascii=False).encode()
    rec_ba = json.dumps({
        "from": "b.brandt@nordwind.example", "to": "a.bauer@nordwind.example",
        "ts": TIMESTAMP, "richtung": "Bob->Anna",
        "hinweis": "zweite Haelfte der Flagge", "flag_teil_2": frag_ba,
    }, ensure_ascii=False).encode()

    nonce_ab = bytes(rng.getrandbits(8) for _ in range(12))
    nonce_ba = bytes(rng.getrandbits(8) for _ in range(12))
    ct_ab = AESGCM(key_left).encrypt(nonce_ab, rec_ab, None)
    ct_ba = AESGCM(key_right).encrypt(nonce_ba, rec_ba, None)

    capture = build_mitm_capture(index, p, g, A, B, M1, M2, m1, m2,
                                 nonce_ab, ct_ab, nonce_ba, ct_ba)

    solution = {
        "index": index, "challenge": "challenge_6",
        "p": str(p), "g": str(g), "A": str(A), "B": str(B),
        "a": str(a), "b": str(b),
        "m1": str(m1), "m2": str(m2), "M1": str(M1), "M2": str(M2),
        "s_left": str(s_left), "s_right": str(s_right),
        "bits_p": p.bit_length(),
        "flag": flag, "flag_teil_1": frag_ab, "flag_teil_2": frag_ba,
        "detection": "M1 != B  (Anna sieht nicht Bobs echten Schluessel)",
    }
    return capture, solution


# ======================================================================
# Pilote principal
# ======================================================================
def generate(master_seed, n_variants, out_root):
    assets_root = os.path.join(out_root, "custom", "assets", "0200")
    tools_dir = os.path.join(out_root, "tools")
    os.makedirs(assets_root, exist_ok=True)
    os.makedirs(tools_dir, exist_ok=True)

    solution_data = {
        "meta": {"seed": master_seed, "variants": n_variants,
                 "challenges": CHALLENGE_ORDER, "flags": FLAGS},
        "variants": {},
    }

    for index in range(n_variants):
        vdir = os.path.join(assets_root, str(index))
        os.makedirs(vdir, exist_ok=True)
        solution_data["variants"][str(index)] = {}

        for challenge in CHALLENGE_ORDER:
            capture, solution = make_instance(master_seed, index, challenge)
            with open(os.path.join(vdir, f"{challenge}.tcvcap"), "w",
                      encoding="utf-8") as f:
                f.write(capture)
            solution_data["variants"][str(index)][challenge] = solution

    with open(os.path.join(tools_dir, "solution_data.json"), "w",
              encoding="utf-8") as f:
        json.dump(solution_data, f, ensure_ascii=False, indent=2)

    return solution_data


def main():
    ap = argparse.ArgumentParser(description="Générateur Kapitel 02 — Vague 1 (sans backend).")
    ap.add_argument("--seed", type=int, required=True, help="seed maître (à committer)")
    ap.add_argument("--variants", type=int, default=200, help="nombre de variantes (défaut 200)")
    ap.add_argument("--out", type=str, required=True, help="racine du repo (DUMMY_CTF)")
    args = ap.parse_args()

    sol = generate(args.seed, args.variants, args.out)
    n = len(sol["variants"])
    print(f"OK : {n} variantes x {len(CHALLENGE_ORDER)} challenges générées.")
    print(f"  captures -> custom/assets/0200/<index>/<challenge>.tcvcap")
    print(f"  corrigé  -> tools/solution_data.json")
    print(f"  flags communs :")
    for c, fl in FLAGS.items():
        print(f"      {c}: {fl}")
    print(f"  seed maître (à committer) : {args.seed}")


if __name__ == "__main__":
    main()
