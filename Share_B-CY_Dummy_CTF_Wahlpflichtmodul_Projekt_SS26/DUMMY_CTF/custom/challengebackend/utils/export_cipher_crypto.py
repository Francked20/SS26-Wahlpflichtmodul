"""Hand-rolled TLS 1.0 RSA_EXPORT (FREAK-style) handshake crypto.

Real OpenSSL cannot negotiate TLS_RSA_EXPORT_* cipher suites anymore (removed
after the FREAK disclosure, CVE-2015-0204), so this module builds the wire
bytes by hand, per RFC 2246 (TLS 1.0). Cipher suite used throughout:
TLS_RSA_EXPORT_WITH_RC4_40_MD5 (0x00, 0x03).

Reuses the same primality-test / extended-Euclid / DER-encoding approach as
../../../RSA-generator/generator.py, extended with a minimal self-signed
X.509 certificate and the TLS 1.0 record/handshake/PRF layers.
"""

import hashlib
import hmac
import os
import random
import time
from dataclasses import dataclass
from typing import Literal

E = 65537  # RSA public exponent, matches RSA-generator/generator.py

CONTENT_TYPE_CHANGE_CIPHER_SPEC = 20
CONTENT_TYPE_HANDSHAKE = 22
CONTENT_TYPE_APPLICATION_DATA = 23

HANDSHAKE_CLIENT_HELLO = 1
HANDSHAKE_SERVER_HELLO = 2
HANDSHAKE_CERTIFICATE = 11
HANDSHAKE_SERVER_HELLO_DONE = 14
HANDSHAKE_CLIENT_KEY_EXCHANGE = 16
HANDSHAKE_FINISHED = 20

CIPHER_SUITE_RSA_EXPORT_RC4_40_MD5 = b"\x00\x03"
TLS_VERSION = b"\x03\x01"  # TLS 1.0


def miller_rabin(n: int, k: int = 20) -> bool:
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
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(n):
            return n


def generate_rsa_primes(bits_each: int) -> tuple[int, int]:
    while True:
        p, q = generate_prime(bits_each), generate_prime(bits_each)
        if p != q and (p * q).bit_length() == 2 * bits_each:
            return p, q


def extended_euclid(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_euclid(b, a % b)
    return gcd, y1, x1 - (a // b) * y1


def mod_inverse(e: int, phi_n: int) -> int:
    gcd, d, _ = extended_euclid(e, phi_n)
    if gcd != 1:
        raise ValueError("e and phi(n) are not coprime, no inverse exists.")
    return d % phi_n


# --- minimal DER/X.509 encoding (extends RSA-generator/generator.py's helpers) ---

def encode_length(length: int) -> bytes:
    if length < 128:
        return bytes([length])
    length_bytes = length.to_bytes((length.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(length_bytes)]) + length_bytes


def encode_int(x: int) -> bytes:
    if x == 0:
        b = b"\x00"
    else:
        b = x.to_bytes((x.bit_length() + 7) // 8, "big")
        if b[0] & 0x80:
            b = b"\x00" + b
    return b"\x02" + encode_length(len(b)) + b


def encode_seq(*items: bytes) -> bytes:
    body = b"".join(items)
    return b"\x30" + encode_length(len(body)) + body


def encode_bitstring(data: bytes) -> bytes:
    body = b"\x00" + data  # 0 unused bits
    return b"\x03" + encode_length(len(body)) + body


def encode_null() -> bytes:
    return b"\x05\x00"


def encode_printable_string(s: str) -> bytes:
    b = s.encode("ascii")
    return b"\x13" + encode_length(len(b)) + b


def encode_utctime(t: time.struct_time) -> bytes:
    s = time.strftime("%y%m%d%H%M%SZ", t)
    b = s.encode("ascii")
    return b"\x17" + encode_length(len(b)) + b


OID_RSA_ENCRYPTION = bytes.fromhex("06092A864886F70D010101")
OID_SHA1_WITH_RSA_ENCRYPTION = bytes.fromhex("06092A864886F70D010105")
OID_COMMON_NAME = bytes.fromhex("06035504 03".replace(" ", ""))


def encode_rsa_public_key_der(n: int, e: int) -> bytes:
    return encode_seq(encode_int(n), encode_int(e))


def encode_name(common_name: str) -> bytes:
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
    k = (n.bit_length() + 7) // 8
    ps_len = k - 3 - len(message)
    if ps_len < 8:
        raise ValueError("Message too long for this RSA key size")
    ps = bytes(random.randint(1, 255) for _ in range(ps_len))
    eb = b"\x00\x02" + ps + b"\x00" + message
    m = int.from_bytes(eb, "big")
    c = pow(m, e, n)
    return c.to_bytes(k, "big")


def rsa_pkcs1_decrypt(n: int, d: int, ciphertext: bytes) -> bytes:
    k = (n.bit_length() + 7) // 8
    c = int.from_bytes(ciphertext, "big")
    m = pow(c, d, n)
    eb = m.to_bytes(k, "big")
    if eb[0] != 0x00 or eb[1] != 0x02:
        raise ValueError("Invalid PKCS#1 v1.5 padding")
    sep = eb.index(b"\x00", 2)
    return eb[sep + 1:]


# --- RC4 (RFC 2246 6.3, stream cipher, one continuous keystream per direction) ---

class RC4Stream:
    def __init__(self, key: bytes):
        s = list(range(256))
        j = 0
        for i in range(256):
            j = (j + s[i] + key[i % len(key)]) % 256
            s[i], s[j] = s[j], s[i]
        self._s = s
        self._i = 0
        self._j = 0

    def crypt(self, data: bytes) -> bytes:
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
    out = b""
    a = seed
    while len(out) < length:
        a = hmac.new(secret, a, digestmod).digest()
        out += hmac.new(secret, a + seed, digestmod).digest()
    return out[:length]


def tls10_prf(secret: bytes, label: bytes, seed: bytes, length: int) -> bytes:
    half = (len(secret) + 1) // 2
    s1, s2 = secret[:half], secret[-half:]
    p_md5 = _p_hash(hashlib.md5, s1, label + seed, length)
    p_sha1 = _p_hash(hashlib.sha1, s2, label + seed, length)
    return bytes(a ^ b for a, b in zip(p_md5, p_sha1))


# --- record / handshake framing ---

def _handshake_message(msg_type: int, body: bytes) -> bytes:
    return bytes([msg_type]) + len(body).to_bytes(3, "big") + body


def _record(content_type: int, fragment: bytes) -> bytes:
    return bytes([content_type]) + TLS_VERSION + len(fragment).to_bytes(2, "big") + fragment


def _mac_then_encrypt(content_type: int, plaintext: bytes, mac_secret: bytes, rc4: RC4Stream, seq_num: int) -> bytes:
    pseudo_header = (
        seq_num.to_bytes(8, "big") + bytes([content_type]) + TLS_VERSION + len(plaintext).to_bytes(2, "big")
    )
    mac = hmac.new(mac_secret, pseudo_header + plaintext, hashlib.md5).digest()
    return rc4.crypt(plaintext + mac)


def _mac_then_decrypt(content_type: int, ciphertext: bytes, mac_secret: bytes, rc4: RC4Stream, seq_num: int) -> bytes:
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


# --- full handshake crafting ---

@dataclass
class VariantBytes:
    client_flight_1: bytes  # ClientHello
    server_flight_1: bytes  # ServerHello, Certificate, ServerHelloDone
    client_flight_2: bytes  # ClientKeyExchange, ChangeCipherSpec, Finished(client)
    server_flight_2: bytes  # ChangeCipherSpec, Finished(server), ApplicationData(flag)
    client_random: bytes
    server_random: bytes
    master_secret: bytes


def _tls_random() -> bytes:
    return int(time.time()).to_bytes(4, "big") + os.urandom(28)


def craft_variant(n512: int, p512: int, q512: int, flag: bytes) -> VariantBytes:
    client_random = _tls_random()
    server_random = _tls_random()
    pre_master_secret = TLS_VERSION + os.urandom(46)

    transcript = b""

    client_hello_body = TLS_VERSION + client_random + b"\x00" + b"\x00\x02" + CIPHER_SUITE_RSA_EXPORT_RC4_40_MD5 + b"\x01\x00"
    client_hello_msg = _handshake_message(HANDSHAKE_CLIENT_HELLO, client_hello_body)
    transcript += client_hello_msg
    client_flight_1 = _record(CONTENT_TYPE_HANDSHAKE, client_hello_msg)

    server_hello_body = TLS_VERSION + server_random + b"\x00" + CIPHER_SUITE_RSA_EXPORT_RC4_40_MD5 + b"\x00"
    server_hello_msg = _handshake_message(HANDSHAKE_SERVER_HELLO, server_hello_body)
    transcript += server_hello_msg

    cert_der = build_self_signed_certificate_der(n512, E)
    cert_list = len(cert_der).to_bytes(3, "big") + cert_der
    certificate_body = len(cert_list).to_bytes(3, "big") + cert_list
    certificate_msg = _handshake_message(HANDSHAKE_CERTIFICATE, certificate_body)
    transcript += certificate_msg

    server_hello_done_msg = _handshake_message(HANDSHAKE_SERVER_HELLO_DONE, b"")
    transcript += server_hello_done_msg

    server_flight_1 = (
        _record(CONTENT_TYPE_HANDSHAKE, server_hello_msg)
        + _record(CONTENT_TYPE_HANDSHAKE, certificate_msg)
        + _record(CONTENT_TYPE_HANDSHAKE, server_hello_done_msg)
    )

    encrypted_pms = rsa_pkcs1_encrypt(n512, E, pre_master_secret)
    client_key_exchange_body = len(encrypted_pms).to_bytes(2, "big") + encrypted_pms
    client_key_exchange_msg = _handshake_message(HANDSHAKE_CLIENT_KEY_EXCHANGE, client_key_exchange_body)
    transcript += client_key_exchange_msg

    keys = derive_keys(pre_master_secret, client_random, server_random)
    client_rc4 = RC4Stream(keys.client_write_key)
    server_rc4 = RC4Stream(keys.server_write_key)

    client_finished_verify_data = tls10_prf(
        keys.master_secret, b"client finished", hashlib.md5(transcript).digest() + hashlib.sha1(transcript).digest(), 12
    )
    client_finished_msg = _handshake_message(HANDSHAKE_FINISHED, client_finished_verify_data)
    transcript += client_finished_msg
    client_finished_encrypted = _mac_then_encrypt(
        CONTENT_TYPE_HANDSHAKE, client_finished_msg, keys.client_write_mac_secret, client_rc4, seq_num=0
    )

    client_flight_2 = (
        _record(CONTENT_TYPE_HANDSHAKE, client_key_exchange_msg)
        + _record(CONTENT_TYPE_CHANGE_CIPHER_SPEC, b"\x01")
        + _record(CONTENT_TYPE_HANDSHAKE, client_finished_encrypted)
    )

    server_finished_verify_data = tls10_prf(
        keys.master_secret, b"server finished", hashlib.md5(transcript).digest() + hashlib.sha1(transcript).digest(), 12
    )
    server_finished_msg = _handshake_message(HANDSHAKE_FINISHED, server_finished_verify_data)
    server_finished_encrypted = _mac_then_encrypt(
        CONTENT_TYPE_HANDSHAKE, server_finished_msg, keys.server_write_mac_secret, server_rc4, seq_num=0
    )
    application_data_encrypted = _mac_then_encrypt(
        CONTENT_TYPE_APPLICATION_DATA, flag, keys.server_write_mac_secret, server_rc4, seq_num=1
    )

    server_flight_2 = (
        _record(CONTENT_TYPE_CHANGE_CIPHER_SPEC, b"\x01")
        + _record(CONTENT_TYPE_HANDSHAKE, server_finished_encrypted)
        + _record(CONTENT_TYPE_APPLICATION_DATA, application_data_encrypted)
    )

    return VariantBytes(
        client_flight_1=client_flight_1,
        server_flight_1=server_flight_1,
        client_flight_2=client_flight_2,
        server_flight_2=server_flight_2,
        client_random=client_random,
        server_random=server_random,
        master_secret=keys.master_secret,
    )


def decrypt_as_attacker(
    client_flight_1: bytes, server_flight_1: bytes, client_flight_2: bytes, server_flight_2: bytes,
    p512: int, q512: int,
) -> tuple[bytes, bytes]:
    """Recovers the master secret and flag using only what a participant would
    have: the recovered private-key factors and the captured wire bytes - never
    touches any precomputed "expected" value. Used by the standalone
    verification script to prove the crafted bytes are genuinely decryptable.
    """
    n = p512 * q512
    d = mod_inverse(E, (p512 - 1) * (q512 - 1))

    # handshake message layout: type(1) + length(3) + body; body starts with
    # client/server_version(2) then random(32) - random is at message offset 6.
    client_hello_records = iter_records(client_flight_1)
    client_hello_msg = client_hello_records[0][1]
    client_random = client_hello_msg[6:6 + 32]

    server_hello_records = iter_records(server_flight_1)
    server_hello_msg = server_hello_records[0][1]
    server_random = server_hello_msg[6:6 + 32]

    client_flight_2_records = iter_records(client_flight_2)
    client_key_exchange_msg = client_flight_2_records[0][1]
    encrypted_pms_len = int.from_bytes(client_key_exchange_msg[4:6], "big")
    encrypted_pms = client_key_exchange_msg[6:6 + encrypted_pms_len]

    pre_master_secret = rsa_pkcs1_decrypt(n, d, encrypted_pms)
    keys = derive_keys(pre_master_secret, client_random, server_random)

    server_rc4 = RC4Stream(keys.server_write_key)
    server_flight_2_records = iter_records(server_flight_2)
    # records: ChangeCipherSpec, Finished(encrypted), ApplicationData(encrypted)
    _finished_plaintext = _mac_then_decrypt(
        CONTENT_TYPE_HANDSHAKE, server_flight_2_records[1][1], keys.server_write_mac_secret, server_rc4, seq_num=0
    )
    flag = _mac_then_decrypt(
        CONTENT_TYPE_APPLICATION_DATA, server_flight_2_records[2][1], keys.server_write_mac_secret, server_rc4, seq_num=1
    )

    return keys.master_secret, flag
