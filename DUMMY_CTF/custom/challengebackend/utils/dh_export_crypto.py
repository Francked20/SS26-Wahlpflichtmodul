"""Low-level crypto and TLS 1.0 wire-format helpers for the weak-DH (Logjam)
export challenge.

Builds a complete, syntactically valid TLS 1.0 DHE_EXPORT handshake (4 flights)
around deliberately weak Diffie-Hellman parameters (p = 2q+1 with p-1 fully
smooth), so the recorded traffic can be attacked with yafu (factor p-1) +
Pohlig-Hellman. The RSA/DER/certificate/RC4/PRF/record helpers are shared with
the RSA-export (FREAK) challenge; the DH-specific parts start further down.
"""

import hashlib
import hmac
import os
import random
import time
from dataclasses import dataclass

E = 65537  # RSA public exponent for the server certificate

# TLS record content types (RFC 2246 6.2.1).
CONTENT_TYPE_CHANGE_CIPHER_SPEC = 20
CONTENT_TYPE_HANDSHAKE = 22
CONTENT_TYPE_APPLICATION_DATA = 23

# Handshake message types (RFC 2246 7.4).
HANDSHAKE_CLIENT_HELLO = 1
HANDSHAKE_SERVER_HELLO = 2
HANDSHAKE_CERTIFICATE = 11
HANDSHAKE_SERVER_KEY_EXCHANGE = 12
HANDSHAKE_SERVER_HELLO_DONE = 14
HANDSHAKE_CLIENT_KEY_EXCHANGE = 16
HANDSHAKE_FINISHED = 20

TLS_VERSION = b"\x03\x01"  # TLS 1.0
# DHE_RSA_EXPORT_WITH_RC4_40_MD5 is not a real IANA code; we use the closest
# real EXPORT/DHE marker so Wireshark shows an EXPORT-grade DHE flow. We use
# TLS_DHE_RSA_EXPORT_WITH_DES40_CBC_SHA (0x00,0x14) as the advertised suite id
# but keep RC4_40_MD5 record protection under the hood (documented divergence).
CIPHER_SUITE_DHE_EXPORT = b"\x00\x14"



def miller_rabin(n: int, k: int = 20) -> bool:
    """Probabilistic primality test with k rounds (default 20)."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(k):
        a = random.randrange(2, n - 2)
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


def generate_prime(bits: int) -> int:
    """Random prime with the top and bottom bits set (exactly `bits` long, odd)."""
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(n):
            return n


def generate_rsa_primes(bits_each: int) -> tuple[int, int]:
    """Two distinct primes whose product is exactly 2*bits_each long."""
    while True:
        p, q = generate_prime(bits_each), generate_prime(bits_each)
        if p != q and (p * q).bit_length() == 2 * bits_each:
            return p, q


def extended_euclid(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean algorithm: returns (gcd, x, y) with a*x + b*y = gcd."""
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_euclid(b, a % b)
    return gcd, y1, x1 - (a // b) * y1


def mod_inverse(e: int, phi_n: int) -> int:
    """Modular inverse of e mod phi_n (raises if e and phi_n are not coprime)."""
    gcd, d, _ = extended_euclid(e, phi_n)
    if gcd != 1:
        raise ValueError("e and phi(n) are not coprime, no inverse exists.")
    return d % phi_n


# --- minimal DER/X.509 encoding (extends RSA-generator/generator.py's helpers) ---

def encode_length(length: int) -> bytes:
    """DER length octets (short form < 128, else long form)."""
    if length < 128:
        return bytes([length])
    length_bytes = length.to_bytes((length.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(length_bytes)]) + length_bytes


def encode_int(x: int) -> bytes:
    """DER INTEGER (tag 0x02), with a leading 0x00 when the high bit is set."""
    if x == 0:
        b = b"\x00"
    else:
        b = x.to_bytes((x.bit_length() + 7) // 8, "big")
        if b[0] & 0x80:
            b = b"\x00" + b
    return b"\x02" + encode_length(len(b)) + b


def encode_seq(*items: bytes) -> bytes:
    """DER SEQUENCE (tag 0x30) wrapping the concatenated items."""
    body = b"".join(items)
    return b"\x30" + encode_length(len(body)) + body


def encode_bitstring(data: bytes) -> bytes:
    """DER BIT STRING (tag 0x03) with 0 unused trailing bits."""
    body = b"\x00" + data  # 0 unused bits
    return b"\x03" + encode_length(len(body)) + body


def encode_null() -> bytes:
    """DER NULL (tag 0x05)."""
    return b"\x05\x00"


def encode_printable_string(s: str) -> bytes:
    """DER PrintableString (tag 0x13)."""
    b = s.encode("ascii")
    return b"\x13" + encode_length(len(b)) + b


def encode_utctime(t: time.struct_time) -> bytes:
    """DER UTCTime (tag 0x17), YYMMDDHHMMSSZ."""
    s = time.strftime("%y%m%d%H%M%SZ", t)
    b = s.encode("ascii")
    return b"\x17" + encode_length(len(b)) + b


OID_RSA_ENCRYPTION = bytes.fromhex("06092A864886F70D010101")
OID_SHA1_WITH_RSA_ENCRYPTION = bytes.fromhex("06092A864886F70D010105")
OID_COMMON_NAME = bytes.fromhex("06035504 03".replace(" ", ""))


def encode_rsa_public_key_der(n: int, e: int) -> bytes:
    """DER RSAPublicKey ::= SEQUENCE { modulus, publicExponent }."""
    return encode_seq(encode_int(n), encode_int(e))


def encode_name(common_name: str) -> bytes:
    """DER X.501 Name holding a single CN (CommonName) attribute."""
    attr = encode_seq(OID_COMMON_NAME, encode_printable_string(common_name))
    rdn = b"\x31" + encode_length(len(attr)) + attr  # SET OF
    return b"\x30" + encode_length(len(rdn)) + rdn  # RDNSequence


def build_self_signed_certificate_der(n: int, e: int, common_name: str = "legacy-export.local") -> bytes:
    """A syntactically valid, DER-encoded self-signed X.509v1 certificate wrapping
    the given (weak, export-grade) RSA public key. The signature is not a real
    signature over the TBSCertificate (nothing validates a trust chain here) -
    only the SubjectPublicKeyInfo needs to be genuine, and it is.
    """
    now = time.gmtime()
    later = time.gmtime(time.time() + 365 * 24 * 3600)

    signature_alg = encode_seq(OID_SHA1_WITH_RSA_ENCRYPTION, encode_null())
    issuer = encode_name(common_name)
    subject = issuer
    validity = encode_seq(encode_utctime(now), encode_utctime(later))
    spki = encode_seq(
        encode_seq(OID_RSA_ENCRYPTION, encode_null()),
        encode_bitstring(encode_rsa_public_key_der(n, e)),
    )

    tbs_certificate = encode_seq(
        encode_int(1),  # serialNumber
        signature_alg,
        issuer,
        validity,
        subject,
        spki,
    )

    dummy_signature = hashlib.sha1(tbs_certificate).digest()
    return encode_seq(tbs_certificate, signature_alg, encode_bitstring(dummy_signature))


# --- RSA PKCS#1 v1.5 (used for ClientKeyExchange, RFC 2246 7.4.7.1) ---

def rsa_pkcs1_encrypt(n: int, e: int, message: bytes) -> bytes:
    """RSA encryption with PKCS#1 v1.5 type-02 padding (random nonzero PS)."""
    k = (n.bit_length() + 7) // 8
    ps_len = k - 3 - len(message)
    if ps_len < 8:
        raise ValueError("Message too long for this RSA key size")
    ps = bytes(random.randint(1, 255) for _ in range(ps_len))
    eb = b"\x00\x02" + ps + b"\x00" + message
    m = int.from_bytes(eb, "big")
    c = pow(m, e, n)
    return c.to_bytes(k, "big")


# --- RC4 (RFC 2246 6.3, stream cipher, one continuous keystream per direction) ---

class RC4Stream:
    """RC4 stream cipher with persistent state, one instance per direction."""

    def __init__(self, key: bytes):
        # Key-scheduling algorithm (KSA): permute the 0..255 state array.
        s = list(range(256))
        j = 0
        for i in range(256):
            j = (j + s[i] + key[i % len(key)]) % 256
            s[i], s[j] = s[j], s[i]
        self._s = s
        self._i = 0
        self._j = 0

    def crypt(self, data: bytes) -> bytes:
        """XOR data with the next keystream bytes (encrypt == decrypt)."""
        s, i, j = self._s, self._i, self._j
        out = bytearray(len(data))
        for idx, byte in enumerate(data):
            i = (i + 1) % 256
            j = (j + s[i]) % 256
            s[i], s[j] = s[j], s[i]
            out[idx] = byte ^ s[(s[i] + s[j]) % 256]
        self._i, self._j = i, j
        return bytes(out)


# --- TLS 1.0 PRF (RFC 2246 6.1) ---

def _p_hash(digestmod, secret: bytes, seed: bytes, length: int) -> bytes:
    """P_hash data-expansion function (RFC 2246 5): iterated HMAC to `length`."""
    out = b""
    a = seed
    while len(out) < length:
        a = hmac.new(secret, a, digestmod).digest()
        out += hmac.new(secret, a + seed, digestmod).digest()
    return out[:length]


def tls10_prf(secret: bytes, label: bytes, seed: bytes, length: int) -> bytes:
    """TLS 1.0 PRF: P_MD5(S1) XOR P_SHA1(S2) over the two halves of the secret."""
    half = (len(secret) + 1) // 2
    s1, s2 = secret[:half], secret[-half:]
    p_md5 = _p_hash(hashlib.md5, s1, label + seed, length)
    p_sha1 = _p_hash(hashlib.sha1, s2, label + seed, length)
    return bytes(a ^ b for a, b in zip(p_md5, p_sha1))


# --- record / handshake framing ---

def _handshake_message(msg_type: int, body: bytes) -> bytes:
    """Wrap a handshake body: 1-byte type + 3-byte length + body."""
    return bytes([msg_type]) + len(body).to_bytes(3, "big") + body


def _record(content_type: int, fragment: bytes) -> bytes:
    """Wrap a fragment in a TLS record: type + version + 2-byte length + data."""
    return bytes([content_type]) + TLS_VERSION + len(fragment).to_bytes(2, "big") + fragment


def _mac_then_encrypt(content_type: int, plaintext: bytes, mac_secret: bytes, rc4: RC4Stream, seq_num: int) -> bytes:
    """MAC-then-encrypt: append HMAC-MD5 over (seq||header||plaintext), then RC4."""
    pseudo_header = (
        seq_num.to_bytes(8, "big") + bytes([content_type]) + TLS_VERSION + len(plaintext).to_bytes(2, "big")
    )
    mac = hmac.new(mac_secret, pseudo_header + plaintext, hashlib.md5).digest()
    return rc4.crypt(plaintext + mac)


def _mac_then_decrypt(content_type: int, ciphertext: bytes, mac_secret: bytes, rc4: RC4Stream, seq_num: int) -> bytes:
    """Inverse of _mac_then_encrypt: RC4-decrypt, split off the 16-byte MAC,
    verify it, and return the plaintext (raises on MAC mismatch)."""
    plaintext_and_mac = rc4.crypt(ciphertext)
    plaintext, mac = plaintext_and_mac[:-16], plaintext_and_mac[-16:]
    pseudo_header = (
        seq_num.to_bytes(8, "big") + bytes([content_type]) + TLS_VERSION + len(plaintext).to_bytes(2, "big")
    )
    expected_mac = hmac.new(mac_secret, pseudo_header + plaintext, hashlib.md5).digest()
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError("TLS record MAC mismatch")
    return plaintext


def iter_records(buf: bytes) -> list[tuple[int, bytes]]:
    """Split a byte buffer into (content_type, fragment) TLS records."""
    records = []
    offset = 0
    while offset < len(buf):
        content_type = buf[offset]
        length = int.from_bytes(buf[offset + 3:offset + 5], "big")
        fragment = buf[offset + 5:offset + 5 + length]
        records.append((content_type, fragment))
        offset += 5 + length
    return records


# --- key derivation (RFC 2246 6.3 / export key expansion 6.3.1) ---

@dataclass
class ConnectionKeys:
    master_secret: bytes
    client_write_mac_secret: bytes
    server_write_mac_secret: bytes
    client_write_key: bytes  # final, expanded 16-byte key actually used for RC4
    server_write_key: bytes


def derive_keys(pre_master_secret: bytes, client_random: bytes, server_random: bytes) -> ConnectionKeys:
    """Derive the master secret and the MAC/write keys from the pre-master
    secret and the two randoms, following the EXPORT key expansion."""
    master_secret = tls10_prf(pre_master_secret, b"master secret", client_random + server_random, 48)

    # hash_size=16 (MD5) per MAC secret, key_material_length=5 (40 bits) per
    # write-key secret for the EXPORT cipher - this is the actual "weak key"
    # mechanism (RFC 2246 6.3.1): only 40 bits of entropy feed the write keys.
    key_block = tls10_prf(master_secret, b"key expansion", server_random + client_random, 2 * 16 + 2 * 5)
    client_write_mac_secret = key_block[0:16]
    server_write_mac_secret = key_block[16:32]
    client_write_key_short = key_block[32:37]
    server_write_key_short = key_block[37:42]

    # RFC 2246 6.3.1: TLS 1.0 replaced SSLv3's MD5-based export key expansion
    # with the PRF, and both directions use the SAME seed order (client_random
    # + server_random) - unlike key_block's PRF call just above, which uses
    # server_random + client_random.
    final_client_write_key = tls10_prf(
        client_write_key_short, b"client write key", client_random + server_random, 16
    )
    final_server_write_key = tls10_prf(
        server_write_key_short, b"server write key", client_random + server_random, 16
    )

    return ConnectionKeys(
        master_secret=master_secret,
        client_write_mac_secret=client_write_mac_secret,
        server_write_mac_secret=server_write_mac_secret,
        client_write_key=final_client_write_key,
        server_write_key=final_server_write_key,
    )


# ============================================================================
# NEW for DHE: weak DH parameters + ServerKeyExchange/ClientKeyExchange
# ============================================================================

def gen_weak_dh_params(total_bits: int, factor_bits: int, rng: random.Random,
                       max_tries: int = 200000):
    """Generate a weak prime p = 2q + 1 with q = product of small primes (p-1
    fully smooth), a generator g, and return (p, g, factors).

    This is the intended weakness: p-1 factors easily with yafu and the discrete
    log breaks via Pohlig-Hellman. `factor_bits` sets the size of the small
    primes (hence the per-factor BSGS cost: ~2^(factor_bits/2))."""
    target_q_bits = total_bits - 1
    for _ in range(max_tries):
        factors, q = [], 1
        while q.bit_length() < target_q_bits - factor_bits:
            qi = _rand_prime(factor_bits, rng)
            if qi in factors:
                continue
            factors.append(qi)
            q *= qi
        remaining = target_q_bits - q.bit_length()
        if remaining >= 8:
            qi = _rand_prime(remaining, rng)
            if qi not in factors:
                factors.append(qi)
                q *= qi
        p = 2 * q + 1
        if abs(p.bit_length() - total_bits) <= 2 and miller_rabin(p):
            factors = sorted(factors)
            g = _find_generator(p, factors)
            if g is not None:
                return p, g, factors
    raise RuntimeError("gen_weak_dh_params: no weak p found")


def _rand_prime(bits: int, rng: random.Random) -> int:
    """Small prime of ~bits bits (deterministic via rng)."""
    while True:
        n = rng.randrange(1 << (bits - 1), (1 << bits) - 1) | 1
        if miller_rabin(n):
            return n


def _find_generator(p: int, factors: list[int]):
    """Generator of order p-1 (checked against each prime factor of p-1)."""
    order = p - 1
    all_f = set([2] + list(factors))
    for g in range(2, 500):
        if all(pow(g, order // qq, p) != 1 for qq in all_f):
            return g
    return None


def _dh_encode(x: int) -> bytes:
    """opaque<1..2^16-1>: 2-byte length prefix + big-endian value."""
    b = x.to_bytes((x.bit_length() + 7) // 8, "big")
    return len(b).to_bytes(2, "big") + b


def _server_dh_params(p: int, g: int, Ys: int) -> bytes:
    """ServerDHParams (RFC 2246 7.4.3): dh_p, dh_g, dh_Ys."""
    return _dh_encode(p) + _dh_encode(g) + _dh_encode(Ys)


def _rsa_sign_md5sha1(n: int, d: int, data: bytes) -> bytes:
    """RSA signature as in TLS 1.0's signed ServerKeyExchange: concatenated
    MD5+SHA1 hash (36 bytes), PKCS#1 v1.5 type-01 padding, then RSA."""
    digest = hashlib.md5(data).digest() + hashlib.sha1(data).digest()  # 36 bytes
    k = (n.bit_length() + 7) // 8
    ps = b"\xff" * (k - 3 - len(digest))
    eb = b"\x00\x01" + ps + b"\x00" + digest
    m = int.from_bytes(eb, "big")
    sig = pow(m, d, n)
    return sig.to_bytes(k, "big")


def _dh_shared_secret_bytes(Z: int) -> bytes:
    """DH pre-master secret (RFC 2246 8.1.2): the value Z = Ys^c = Yc^s in
    big-endian. (Leading zeros are not padded in TLS 1.0.)"""
    return Z.to_bytes((Z.bit_length() + 7) // 8, "big")


@dataclass
class DhVariantBytes:
    client_flight_1: bytes  # ClientHello
    server_flight_1: bytes  # ServerHello, Certificate, ServerKeyExchange, ServerHelloDone
    client_flight_2: bytes  # ClientKeyExchange, ChangeCipherSpec, Finished(client)
    server_flight_2: bytes  # ChangeCipherSpec, Finished(server), ApplicationData(flag)
    client_random: bytes
    server_random: bytes
    master_secret: bytes
    # exposed parameters (for the reference solver / the database):
    p: int
    g: int
    Ys: int
    Yc: int
    server_secret: int      # s (to be recovered by the attacker)
    Z: int                  # shared secret
    factors: list           # factors of p-1 (excluding 2)


def _tls_random(rng: random.Random) -> bytes:
    """TLS Random: 4-byte gmt_unix_time + 28 random bytes."""
    return int(time.time()).to_bytes(4, "big") + bytes(rng.getrandbits(8) for _ in range(28))


def craft_dh_variant(p: int, g: int, factors: list, n_rsa: int, d_rsa: int,
                     flag: bytes, rng: random.Random) -> DhVariantBytes:
    """Build a complete TLS 1.0 DHE_EXPORT handshake (4 flights) with weak DH
    parameters. Only the key exchange differs from the RSA variant (DHE instead
    of RSA). n_rsa/d_rsa = the server certificate key (used to sign the
    ServerKeyExchange)."""
    client_random = _tls_random(rng)
    server_random = _tls_random(rng)

    # Ephemeral DH secrets
    q = (p - 1) // 2
    s = rng.randrange(2, q)                 # server secret (to be broken)
    c = rng.randrange(2, q)                 # client secret
    Ys = pow(g, s, p)                       # server public key
    Yc = pow(g, c, p)                       # client public key
    Z = pow(Ys, c, p)                       # = pow(Yc, s, p): shared secret
    assert Z == pow(Yc, s, p), "DH mismatch"
    pre_master_secret = _dh_shared_secret_bytes(Z)

    transcript = b""

    # --- Client flight 1: ClientHello ---
    client_hello_body = (TLS_VERSION + client_random + b"\x00"
                         + b"\x00\x02" + CIPHER_SUITE_DHE_EXPORT + b"\x01\x00")
    client_hello_msg = _handshake_message(HANDSHAKE_CLIENT_HELLO, client_hello_body)
    transcript += client_hello_msg
    client_flight_1 = _record(CONTENT_TYPE_HANDSHAKE, client_hello_msg)

    # --- Server flight 1: ServerHello, Certificate, ServerKeyExchange, ServerHelloDone ---
    server_hello_body = TLS_VERSION + server_random + b"\x00" + CIPHER_SUITE_DHE_EXPORT + b"\x00"
    server_hello_msg = _handshake_message(HANDSHAKE_SERVER_HELLO, server_hello_body)
    transcript += server_hello_msg

    cert_der = build_self_signed_certificate_der(n_rsa, E)
    cert_list = len(cert_der).to_bytes(3, "big") + cert_der
    certificate_body = len(cert_list).to_bytes(3, "big") + cert_list
    certificate_msg = _handshake_message(HANDSHAKE_CERTIFICATE, certificate_body)
    transcript += certificate_msg

    # ServerKeyExchange: ServerDHParams + RSA signature over (client_random + server_random + params)
    dh_params = _server_dh_params(p, g, Ys)
    signed_data = client_random + server_random + dh_params
    signature = _rsa_sign_md5sha1(n_rsa, d_rsa, signed_data)
    server_key_exchange_body = dh_params + len(signature).to_bytes(2, "big") + signature
    server_key_exchange_msg = _handshake_message(HANDSHAKE_SERVER_KEY_EXCHANGE, server_key_exchange_body)
    transcript += server_key_exchange_msg

    server_hello_done_msg = _handshake_message(HANDSHAKE_SERVER_HELLO_DONE, b"")
    transcript += server_hello_done_msg

    server_flight_1 = (
        _record(CONTENT_TYPE_HANDSHAKE, server_hello_msg)
        + _record(CONTENT_TYPE_HANDSHAKE, certificate_msg)
        + _record(CONTENT_TYPE_HANDSHAKE, server_key_exchange_msg)
        + _record(CONTENT_TYPE_HANDSHAKE, server_hello_done_msg)
    )

    # --- Client flight 2: ClientKeyExchange (Yc), ChangeCipherSpec, Finished ---
    client_key_exchange_body = _dh_encode(Yc)   # ClientDiffieHellmanPublic (explicit)
    client_key_exchange_msg = _handshake_message(HANDSHAKE_CLIENT_KEY_EXCHANGE, client_key_exchange_body)
    transcript += client_key_exchange_msg

    keys = derive_keys(pre_master_secret, client_random, server_random)
    client_rc4 = RC4Stream(keys.client_write_key)
    server_rc4 = RC4Stream(keys.server_write_key)

    client_finished_verify = tls10_prf(
        keys.master_secret, b"client finished",
        hashlib.md5(transcript).digest() + hashlib.sha1(transcript).digest(), 12,
    )
    client_finished_msg = _handshake_message(HANDSHAKE_FINISHED, client_finished_verify)
    transcript += client_finished_msg
    client_finished_enc = _mac_then_encrypt(
        CONTENT_TYPE_HANDSHAKE, client_finished_msg, keys.client_write_mac_secret, client_rc4, 0)

    client_flight_2 = (
        _record(CONTENT_TYPE_HANDSHAKE, client_key_exchange_msg)
        + _record(CONTENT_TYPE_CHANGE_CIPHER_SPEC, b"\x01")
        + _record(CONTENT_TYPE_HANDSHAKE, client_finished_enc)
    )

    # --- Server flight 2: ChangeCipherSpec, Finished, ApplicationData(flag) ---
    server_finished_verify = tls10_prf(
        keys.master_secret, b"server finished",
        hashlib.md5(transcript).digest() + hashlib.sha1(transcript).digest(), 12,
    )
    server_finished_msg = _handshake_message(HANDSHAKE_FINISHED, server_finished_verify)
    server_finished_enc = _mac_then_encrypt(
        CONTENT_TYPE_HANDSHAKE, server_finished_msg, keys.server_write_mac_secret, server_rc4, 0)
    application_data_enc = _mac_then_encrypt(
        CONTENT_TYPE_APPLICATION_DATA, flag, keys.server_write_mac_secret, server_rc4, 1)

    server_flight_2 = (
        _record(CONTENT_TYPE_CHANGE_CIPHER_SPEC, b"\x01")
        + _record(CONTENT_TYPE_HANDSHAKE, server_finished_enc)
        + _record(CONTENT_TYPE_APPLICATION_DATA, application_data_enc)
    )

    return DhVariantBytes(
        client_flight_1=client_flight_1, server_flight_1=server_flight_1,
        client_flight_2=client_flight_2, server_flight_2=server_flight_2,
        client_random=client_random, server_random=server_random,
        master_secret=keys.master_secret,
        p=p, g=g, Ys=Ys, Yc=Yc, server_secret=s, Z=Z, factors=factors,
    )
