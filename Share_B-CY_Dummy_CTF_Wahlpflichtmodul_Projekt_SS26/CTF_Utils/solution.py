#!/usr/bin/env python3
"""Begleit-Skript für die Export-Cipher-Challenge (Tag 3, FREAK-Angriff).

Führt interaktiv durch die Aufgaben 3.4 - 3.7 und übernimmt jeweils die
Berechnung, sobald die nötigen Werte (aus Wireshark bzw. der Website)
eingegeben wurden. Aufgabe 3.3 (256-Bit faktorisieren) läuft extern über
YAFU - dieses Skript prüft nur, ob die gefundenen Faktoren stimmen.

Stdlib-only (hmac, hashlib) - keine Abhängigkeiten nötig.

Usage:
    python3 solution.py
"""
import hashlib
import hmac


def prompt_int(msg: str) -> int:
    while True:
        raw = input(msg).strip()
        try:
            return int(raw, 0) if raw.lower().startswith("0x") else int(raw)
        except ValueError:
            print("  Ungültige Zahl, nochmal versuchen.")


def prompt_hex_bytes(msg: str) -> bytes:
    while True:
        raw = input(msg).strip().lower().replace("0x", "").replace(" ", "")
        try:
            return bytes.fromhex(raw)
        except ValueError:
            print("  Ungültiger Hex-String, nochmal versuchen.")


def step_header(number: str, title: str) -> None:
    print(f"\n{'=' * 60}\nAufgabe {number}: {title}\n{'=' * 60}")


# --- TLS 1.0 PRF (RFC 2246 §6.1) ---

def p_hash(hash_func, secret: bytes, seed: bytes, length: int) -> bytes:
    result = b""
    a = seed
    while len(result) < length:
        a = hmac.new(secret, a, hash_func).digest()
        result += hmac.new(secret, a + seed, hash_func).digest()
    return result[:length]


def tls10_prf(secret: bytes, label: bytes, seed: bytes, length: int) -> bytes:
    half = (len(secret) + 1) // 2
    s1, s2 = secret[:half], secret[-half:]
    seed_full = label + seed
    md5_out = p_hash(hashlib.md5, s1, seed_full, length)
    sha1_out = p_hash(hashlib.sha1, s2, seed_full, length)
    return bytes(a ^ b for a, b in zip(md5_out, sha1_out))


# --- RC4 (RFC 2246 §6.3) ---

class RC4:
    def __init__(self, key: bytes):
        s = list(range(256))
        j = 0
        for i in range(256):
            j = (j + s[i] + key[i % len(key)]) % 256
            s[i], s[j] = s[j], s[i]
        self._s, self._i, self._j = s, 0, 0

    def crypt(self, data: bytes) -> bytes:
        out = bytearray()
        s, i, j = self._s, self._i, self._j
        for b in data:
            i = (i + 1) % 256
            j = (j + s[i]) % 256
            s[i], s[j] = s[j], s[i]
            out.append(b ^ s[(s[i] + s[j]) % 256])
        self._i, self._j = i, j
        return bytes(out)


def main() -> None:
    print("Export-Cipher (FREAK) - interaktives Lösungs-Skript")
    print("Werte an jedem Schritt aus Wireshark bzw. der Website eintragen.")

    # --- Aufgabe 3.3: 256-Bit faktorisieren (nur Kontrolle) ---
    step_header("3.3", "256-Bit faktorisieren (Kontrolle der YAFU-Ausgabe)")
    n256 = prompt_int("n256 (deine persönliche 256-Bit-Zahl, dezimal): ")
    p256 = prompt_int("p256 (erster Faktor von YAFU, dezimal): ")
    q256 = prompt_int("q256 (zweiter Faktor von YAFU, dezimal): ")
    if p256 * q256 != n256:
        print("  WARNUNG: p256 * q256 != n256 - Faktoren stimmen nicht!")
    else:
        print(f">>> Antwort für 3.3: {p256},{q256}")

    # --- Aufgabe 3.4: Zweiter Faktor ---
    step_header("3.4", "Zweiter Faktor (q = N // p)")
    N = prompt_int("N (512-Bit-Modulus aus dem Zertifikat, dezimal): ")
    p = prompt_int("p (Faktor, nach Aufgabe 3.3 angezeigt, dezimal): ")
    if N % p != 0:
        print("  WARNUNG: N ist nicht durch p teilbar - stimmen N/p?")
    q = N // p
    print(f">>> Antwort für 3.4 (q): {q}")

    # Privaten Schlüssel d berechnen (nicht separat abgefragt, RFC 2246 §7.4.7.1)
    e = 65537
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    print(f"    (privater Schlüssel d = {d})")

    # --- Aufgabe 3.5: Pre-Master-Secret ---
    step_header("3.5", "Pre-Master-Secret entschlüsseln")
    ciphertext = prompt_hex_bytes("Verschlüsseltes Pre-Master-Secret aus ClientKeyExchange (hex): ")
    k = (N.bit_length() + 7) // 8
    m = pow(int.from_bytes(ciphertext, "big"), d, N)
    eb = m.to_bytes(k, "big")
    if eb[0] != 0x00 or eb[1] != 0x02:
        print("  WARNUNG: PKCS#1-v1.5-Padding ungültig - falscher Ciphertext/N/p?")
        return
    pre_master_secret = eb[eb.index(b"\x00", 2) + 1:]
    print(f">>> Antwort für 3.5 (pre_master_secret): {pre_master_secret.hex()}")

    # --- Aufgabe 3.6: Master Secret ---
    step_header("3.6", "TLS Master Secret berechnen")
    client_random = prompt_hex_bytes("client_random aus ClientHello (32 Byte, hex): ")
    server_random = prompt_hex_bytes("server_random aus ServerHello (32 Byte, hex): ")
    master_secret = tls10_prf(pre_master_secret, b"master secret", client_random + server_random, 48)
    print(f">>> Antwort für 3.6 (master_secret): {master_secret.hex()}")

    # --- Aufgabe 3.7: Flagge entschlüsseln ---
    step_header("3.7", "Sitzungsschlüssel ableiten & Flagge entschlüsseln")
    key_block = tls10_prf(master_secret, b"key expansion", server_random + client_random, 42)
    server_write_key_raw = key_block[37:42]
    final_server_write_key = tls10_prf(
        server_write_key_raw, b"server write key", client_random + server_random, 16
    )
    print(f"    (server_write_key = {final_server_write_key.hex()})")

    print(
        "\nGib jetzt die Server->Client-Records NACH dem Handshake der Reihe nach ein "
        "(1. Finished-Record, danach die ApplicationData-Records - Reihenfolge wichtig, "
        "RC4 ist ein durchgängiger Keystream). Leere Eingabe beendet die Liste."
    )
    rc4 = RC4(final_server_write_key)
    record_num = 0
    while True:
        raw = input(f"  Record #{record_num} (verschlüsselte Bytes, hex, leer = fertig): ").strip()
        if not raw:
            break
        try:
            record_ciphertext = bytes.fromhex(raw.replace(" ", ""))
        except ValueError:
            print("  Ungültiger Hex-String, nochmal.")
            continue
        plaintext_and_mac = rc4.crypt(record_ciphertext)
        content = plaintext_and_mac[:-16]  # letzte 16 Byte = HMAC-MD5-MAC
        print(f"    Klartext (hex): {content.hex()}")
        print(f"    Klartext (Text): {content.decode(errors='replace')!r}")
        record_num += 1

    print("\nFertig - die Flagge steht im letzten (größten) entschlüsselten Record.")


if __name__ == "__main__":
    main()
