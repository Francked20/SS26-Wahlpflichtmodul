"""Muster-Loeser (starter code) fuer die Challenges des Kapitels 02"""

MUSTER_C1 = r"""
# ============================================================
# Kapitel 02 - Challenge 1: Kleines p (Brute-Force / BSGS)
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   1. Oeffne deine .tcvcap-Datei
#   2. Ersetze unten die vier TODO-Werte durch DEINE Werte aus der Capture
#   3. Fuehre den Code aus (Evaluate). Die Flagge erscheint am Ende
# ============================================================
import base64, hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- 1) Werte aus deiner Capture eintragen ---------------------------------
p     = 377456046827          # TODO: PARAM_P aus deiner Capture
g     = 2                     # TODO: PARAM_G
A     = 50056127533           # TODO: ALICE_PUBLIC_A
B     = 73366910900           # TODO: BOB_PUBLIC_B
NONCE = "7qmiE965SrDJP5O5"    # TODO: RECORD_NONCE_B64
CT    = "DNicCz6LJ67aEOo7zZTHXsKtHS3eEYr8AojKMlGNLnHqYpxvJI7EdWiP592YjcYGry4ZLCRQGs0to8Nc0fO4tpT8yPTN12m8nqTp26NzIFvH8Ph5QIByXp+0TNxZFLpT0JQtxJMIS+hAHC+vfFbxHmpBqMgfPaR6ydSaD3XKzw6cIdIoTrZVfnyLgb5jj13cMU/DLSrqM+VkQ/rGiZopWwO/6PSuRMRM+erA8uMRywx9WHc4kZ2q2ErzdkGQBw=="  # TODO: RECORD_CIPHERTEXT_B64

# --- 2) Diskreten Logarithmus loesen: finde a mit g^a = A (mod p) -----------
# Sage kann das direkt (nutzt intern BSGS):
a = discrete_log(Mod(A, p), Mod(g, p))
print("a =", a, " | Probe g^a == A:", power_mod(g, a, p) == A)

# --- 3) Gemeinsames Geheimnis: s = B^a (mod p) -----------------------------
s = power_mod(B, int(a), p)

# --- 4) Schluessel ableiten (HKDF-SHA256) und entschluesseln (AES-256-GCM) --
s_bytes = int(s).to_bytes((p.nbits() + 7) // 8, "big")
key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
           info=b"kapitel-02-dh-aead-v1").derive(s_bytes)
klartext = AESGCM(key).decrypt(base64.b64decode(NONCE), base64.b64decode(CT), None)
print(klartext.decode())
"""

MUSTER_C2 = r"""
# ============================================================
# Kapitel 02 - Challenge 2: Glatte Ordnung (Pohlig-Hellman)
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   1. Oeffne deine .tcvcap-Datei
#   2. Ersetze die TODO-Werte durch DEINE Werte aus der Capture
#   3. Fuehre den Code aus (Evaluate). Die Flagge erscheint am Ende
#
#   p ist gross, aber p-1 ist glatt (nur kleine Primfaktoren)
#   Sage loest den diskreten Logarithmus automatisch per Pohlig-Hellman
# ============================================================
import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Werte aus deiner Capture eintragen ---
p     = 2720918177271600975457360111196245739   # TODO: PARAM_P
g     = 2   # TODO: PARAM_G
A     = 243402370870275794683392234971450128   # TODO: ALICE_PUBLIC_A
B     = 2290275266269247503787157687101722361   # TODO: BOB_PUBLIC_B
NONCE = "PcZhFizdW6C4VPsk"   # TODO: RECORD_NONCE_B64
CT    = "gXTWFplY4J/zY87G0Yf3vpCHhIWBfwuyoyu7AdhWyH0blCg+cd2wC5BpiTyshW9ZACl3jECpEN0H5agZQyKLPjCtz4CaZ4I31RvgD/9oTa1Yicb7AQ7zfr8hFvagqZGifjzsM1cYittTRd1tFL/e0+QxabvQ+ogioeG6QlWA4fNyoTsp/LV3Wj+k1dl20PbpWy0vOZHSV7AuJvO9qL55PDgramuad+JeCIC2rdHTe7UeH4aDmxVqLW769hh+n6ceLSUNbA=="   # TODO: RECORD_CIPHERTEXT_B64

# --- Diskreten Logarithmus loesen: g^a = A (mod p) ---
a = discrete_log(Mod(A, p), Mod(g, p))
print("a =", a, " | Probe:", power_mod(g, int(a), p) == A)

# --- Gemeinsames Geheimnis: s = B^a (mod p) ---
s = power_mod(B, int(a), p)

# --- Schluessel ableiten (HKDF-SHA256) und entschluesseln (AES-256-GCM) ---
s_bytes = int(s).to_bytes((p.nbits() + 7) // 8, "big")
key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
           info=b"kapitel-02-dh-aead-v1").derive(s_bytes)
klartext = AESGCM(key).decrypt(base64.b64decode(NONCE), base64.b64decode(CT), None)
print(klartext.decode())
"""

MUSTER_C3 = r"""
# ============================================================
# Kapitel 02 - Challenge 3: Fast glatt
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   1. Oeffne deine .tcvcap-Datei
#   2. Ersetze die TODO-Werte durch DEINE Werte aus der Capture
#   3. Fuehre den Code aus (Evaluate). Die Flagge erscheint am Ende
#
#   p-1 ist fast glatt (ein groesserer Faktor). discrete_log kommt dennoch zum Ziel
# ============================================================
import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Werte aus deiner Capture eintragen ---
p     = 88608901131831736299794584851221214801779886121893947   # TODO: PARAM_P
g     = 2   # TODO: PARAM_G
A     = 24037164050826977639251719023521846389539579057240949   # TODO: ALICE_PUBLIC_A
B     = 16363518001348137588471035515622517678356972635735750   # TODO: BOB_PUBLIC_B
NONCE = "I5OikU5pcVvW6+kX"   # TODO: RECORD_NONCE_B64
CT    = "yyOK88O+Mxe2HQ7CLs08WQVzTfYIdof8Qt5K3DUAlgrqCLBP6738MzCqSjRjcNznyzp8XhI2XHWizETO2eZe7AyCEOsFH3cbPxbzJYx1Ixy74jCoIr+wK/bSIWy0Q4f/EwYkb6CnVeGm3I2f5N2kefngIU1/OTlxauYGpQk+nQ0zh2gL81Sm8k9VtlPdaa7fGa18/S5SJi56WdVOyGjg4v9SiwnaOvJH9GbULv2xJ0599emo8jxF/24R8PbPiuRmSRXE+GUq4GCh"   # TODO: RECORD_CIPHERTEXT_B64

# --- Diskreten Logarithmus loesen: g^a = A (mod p) ---
a = discrete_log(Mod(A, p), Mod(g, p))
print("a =", a, " | Probe:", power_mod(g, int(a), p) == A)

# --- Gemeinsames Geheimnis: s = B^a (mod p) ---
s = power_mod(B, int(a), p)

# --- Schluessel ableiten (HKDF-SHA256) und entschluesseln (AES-256-GCM) ---
s_bytes = int(s).to_bytes((p.nbits() + 7) // 8, "big")
key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
           info=b"kapitel-02-dh-aead-v1").derive(s_bytes)
klartext = AESGCM(key).decrypt(base64.b64decode(NONCE), base64.b64decode(CT), None)
print(klartext.decode())
"""

MUSTER_C4 = r"""
# ============================================================
# Kapitel 02 - Challenge 4: Kleine Untergruppe (Small Subgroup)
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   1. Oeffne deine .tcvcap-Datei
#   2. Ersetze die TODO-Werte durch DEINE Werte aus der Capture
#   3. Fuehre den Code aus (Evaluate). Die Flagge erscheint am Ende
#
#   Der Generator g erzeugt nur eine kleine Untergruppe der Ordnung q
#   Der geheime Exponent a ist daher klein (a < q) und per BSGS zu finden
# ============================================================
import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Werte aus deiner Capture eintragen ---
p     = 125117480866976575931603573748110648606826608056921061757742160219   # TODO: PARAM_P
g     = 64754661630569050756171019652647966390497989621669876080406332252   # TODO: PARAM_G
A     = 9731074663770522642071512169418592290298573536622561994848340291   # TODO: ALICE_PUBLIC_A
B     = 102466500915980716508487056645661075702065547301505016271592021744   # TODO: BOB_PUBLIC_B
NONCE = "8EST1OtQN3hZPZwR"   # TODO: RECORD_NONCE_B64
CT    = "dQtujvpvMw6/2yHER6CvEX9ZpLIbIXYgyL0ARymJpldN6+aBUsDyr+kkKcNMpnSLWoF4w5x+UlivmwaYtD8HJ47KqspvERCR3AOFY6iiVPqUMbispuHFZhSrQtXnsG3WvZHiafjeDSilIISAJb9QnADsGoxdTMdLsOE6DdtrDPQMJBh2fWDCexn4g2md12uMGYp9l0Zl1m1F0x3ItGJ2mHmg4tq+z8ArXWgd0fMHusDBzHllCLUC5KTLj5ay6dMIk3v8YmEJ5lfU7rEoBTkdn3mb"   # TODO: RECORD_CIPHERTEXT_B64

# --- Diskreten Logarithmus loesen (Sage nutzt die kleine Ordnung automatisch) ---
a = discrete_log(Mod(A, p), Mod(g, p))
print("a =", a, " | Probe:", power_mod(g, int(a), p) == A)

# --- Gemeinsames Geheimnis: s = B^a (mod p) ---
s = power_mod(B, int(a), p)

# --- Schluessel ableiten (HKDF-SHA256) und entschluesseln (AES-256-GCM) ---
s_bytes = int(s).to_bytes((p.nbits() + 7) // 8, "big")
key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
           info=b"kapitel-02-dh-aead-v1").derive(s_bytes)
klartext = AESGCM(key).decrypt(base64.b64decode(NONCE), base64.b64decode(CT), None)
print(klartext.decode())
"""

MUSTER_C5 = r"""
# ============================================================
# Kapitel 02 - Challenge 5: Logjam (Export-Grade DH)
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   1. Oeffne deine .tcvcap-Datei
#   2. Ersetze die TODO-Werte durch DEINE Werte aus der Capture
#   3. Fuehre den Code aus (Evaluate). Die Flagge erscheint am Ende
#
#   Klassischer Logjam: p-1 ist das Produkt vieler kleiner Faktoren
# ============================================================
import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Werte aus deiner Capture eintragen ---
p     = 238630386630064486207520250571251439746816319758346181862160048631565951469222109478420579698214949070284883435222382858990851169432860071826316823880459   # TODO: PARAM_P
g     = 2   # TODO: PARAM_G
A     = 121142758113483947618179903592795905642752413772697536015512363809094843329704772036467451325670471176305990549316204888948488683863239659446354856526136   # TODO: ALICE_PUBLIC_A
B     = 62919033598672898033463815335587653591184854120342442371309104019823399097971272000725868170515236186007511533795876321111532096824021503838698710316412   # TODO: BOB_PUBLIC_B
NONCE = "BS/DyN28K/H0vBq3"   # TODO: RECORD_NONCE_B64
CT    = "nLuuIj4DBYTYGbAtsvHDBicwGxkT3bGxFys5jzjiT6vezrd1SYqri1CcFf//JHAjAo+MtugBoY3q1aIzWDVgz/nAK+Pm/pzPTIBT3nmhswK/THgg0/vxPxMElihk2vN8sf0JGHKtrI7MoYryIjrppzhp3o3NDeBr+Biqu7/663BxK36rGtxe3ogkaLabz01SyjGb40ayNnzzp7nAde7gyeh11mtLgWdyr04c06w+i99TOKOQ3lCwCv7duaHuXzW9ZKYJTnDjsUjDHA=="   # TODO: RECORD_CIPHERTEXT_B64

# --- Diskreten Logarithmus loesen: g^a = A (mod p) ---
a = discrete_log(Mod(A, p), Mod(g, p))
print("a =", a, " | Probe:", power_mod(g, int(a), p) == A)

# --- Gemeinsames Geheimnis: s = B^a (mod p) ---
s = power_mod(B, int(a), p)

# --- Schluessel ableiten (HKDF-SHA256) und entschluesseln (AES-256-GCM) ---
s_bytes = int(s).to_bytes((p.nbits() + 7) // 8, "big")
key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
           info=b"kapitel-02-dh-aead-v1").derive(s_bytes)
klartext = AESGCM(key).decrypt(base64.b64decode(NONCE), base64.b64decode(CT), None)
print(klartext.decode())
"""

MUSTER_C6 = r"""
# ============================================================
# Kapitel 02 - Challenge 6: Man-in-the-Middle
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   1. Oeffne deine .tcvcap-Datei
#   2. Ersetze die TODO-Werte durch DEINE Werte aus der Capture
#   3. Fuehre den Code aus (Evaluate). Die Flagge erscheint am Ende
#
#   Du bist Mallory. Du hast BEIDE Handshakes gekapert und kennst deine
#   geheimen Exponenten m1 (Richtung Alice) und m2 (Richtung Bob). Die Flagge
#   ist auf beide Richtungen aufgeteilt - du musst BEIDE Records entschluesseln
#   und die zwei Haelften zusammensetzen
# ============================================================
import base64, json
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Werte aus deiner Capture eintragen ---
p  = 59152271878566265456195890903497407678290450241976750544680784161298979382099   # TODO: PARAM_P
A  = 44407444212363634781574110534226990230417968227696666130568714069295643360087   # TODO: ALICE_PUBLIC_A
B  = 14506653973204526979144992490144351372701200166953835179121544353042423813351   # TODO: BOB_PUBLIC_B
m1 = 6611944823525507772173560146158198162997005591084619187779077781209972220173   # TODO: MALLORY_SECRET_M1  (dein Geheimnis mit Alice)
m2 = 37107579076649031131220999043394529222755963436208128115350415266374014375274   # TODO: MALLORY_SECRET_M2  (dein Geheimnis mit Bob)
# Record Alice->Mallory:
NONCE_AB = "pWa7e7QeoirhO5GS"   # TODO: RECORD_AB_NONCE_B64
CT_AB    = "I30OwoXhb2kKMlzu7MCd0qJl3+lqCDnodAzd0YPsEEc8GGh7SDbxzGlhZou1E0YN3ezokeW55Yj3Avw7h7s/+8Ch+IwEM59kDNydBxvahp1nGXfZR4ybhilJa8sDFhuu16MIfuIWwX6JbE1vbY6zyN6wkoTQfGNXf1WP4pOoi43OA4ijBvxcSrQVmsnzsD313dVEbpXWX9756B8CaJDjeMbPCe/CDn65ZShnCK/MZ9fc/sr6y2XDrEXe/AV9kV+/6rrpHWsJ3ZFSnwD1NusWK/mRvmF8qEC134uFDXGD/g=="   # TODO: RECORD_AB_CIPHERTEXT_B64
# Record Bob->Mallory:
NONCE_BA = "p7W4/YmvzokXGy0S"   # TODO: RECORD_BA_NONCE_B64
CT_BA    = "QydtOGc28CHXa+und1n9Be1LKYQw5iK16ck03MGn16jTkQ+RBXL8dsbXEo38ztE7QJVpRFIzRaGtq0Sjy0iTt7sRSph6l4Z4c+TJCwsup8mLO1+CGE7qjgYXb5BtRYW+rE57fHUQ+JOotKBhpG+KxJkDy1wQNBamYOh6/BWuUBDP1RVqnGfWzYAkbSuQ7oh4fPhxNgSkBPVQBzb8tJR59JvdzAYoCw2GM8fJACe3Fxr3WW5CfY92ajfzGqd+3Mco9sDmnWBDa58JjZ3TQpYtZpc32lw2OCjIlvL+s0uOpBWm"   # TODO: RECORD_BA_CIPHERTEXT_B64

nbytes = (p.nbits() + 7) // 8
def entschluessle(s, nonce_b64, ct_b64):
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
               info=b"kapitel-02-dh-aead-v1").derive(int(s).to_bytes(nbytes, "big"))
    pt = AESGCM(key).decrypt(base64.b64decode(nonce_b64), base64.b64decode(ct_b64), None)
    return json.loads(pt)

# --- Geheimnis mit Alice: s = A^m1 ; Geheimnis mit Bob: s = B^m2 ---
j1 = entschluessle(power_mod(A, m1, p), NONCE_AB, CT_AB)
j2 = entschluessle(power_mod(B, m2, p), NONCE_BA, CT_BA)

# --- Beide Haelften der Flagge zusammensetzen ---
print("Teil 1:", j1.get("flag_teil_1", ""))
print("Teil 2:", j2.get("flag_teil_2", ""))
print("FLAGGE:", j1.get("flag_teil_1", "") + j2.get("flag_teil_2", ""))
"""

MUSTER_C7 = r"""
# ============================================================
# Kapitel 02 - Challenge 7: ECDH auf kleiner Kurve
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   1. Oeffne deine .tcvcap-Datei
#   2. Ersetze die TODO-Werte durch DEINE Werte aus der Capture
#   3. Fuehre den Code aus (Evaluate). Die Flagge erscheint am Ende
#
#   ECDH auf einer Kurve kleiner Ordnung. Wir bauen die Kurve in Sage nach,
#   loesen den diskreten Logarithmus auf der Kurve (a mit A = a*G) und
#   berechnen den gemeinsamen Punkt S = a*B. Der Schluessel kommt aus x(S)
# ============================================================
import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def decrypt_and_print(s_int, nbytes, nonce_b64, ct_b64):
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
               info=b"kapitel-02-dh-aead-v1").derive(
        int(s_int).to_bytes(nbytes, "big"))
    pt = AESGCM(key).decrypt(base64.b64decode(nonce_b64), base64.b64decode(ct_b64), None)
    print(pt.decode())

# --- Werte aus deiner Capture eintragen ---
a_curve = 602581363848   # TODO: CURVE_A
b_curve = 21792701757   # TODO: CURVE_B
p       = 1011922880207   # TODO: CURVE_P
Gx = 725991110945; Gy = 626997067432   # TODO: GENERATOR_GX/GY
Ax = 276530420948; Ay = 415469722920   # TODO: ALICE_PUBLIC_AX/AY
Bx = 781209195106; By = 519116801709   # TODO: BOB_PUBLIC_BX/BY
NONCE = "QV8Rpyhc6g/DKAFs"   # TODO: RECORD_NONCE_B64
CT    = "bjw9UUfwwO4mSn/HLYKg+9vskm1n9hjC5oVcvhQhl73x58qDVfE7ye4jS3emW6P7/3GQk22VJ+5l8zx05+ExgiFGBxiABHOqGEZQYvScW0LlShngGq88//eoHtBey6RHmIAolrVkk89CA9xz+OVEpIB3qf13ATdLBFqQVEcEd8+J2zuEcllhFXbVlp/YB/qhFGDF1D9RS6suc6Yh8zXhpc8INibrcviJPAXQ1hMlyOEf0GqoCJRzobDUUsEPBKDS8Q9PcpIyYe/mkPCPELw="   # TODO: RECORD_CIPHERTEXT_B64

# --- Kurve und Punkte in Sage aufbauen ---
E = EllipticCurve(GF(p), [a_curve, b_curve])
G = E(Gx, Gy); Apt = E(Ax, Ay); Bpt = E(Bx, By)

# --- Diskreten Logarithmus auf der Kurve: finde a mit A = a*G ---
a = G.discrete_log(Apt)
print("a =", a, " | Probe:", a*G == Apt)

# --- Gemeinsamer Punkt S = a*B, Schluessel aus x(S) ---
S = a * Bpt
x_S = int(S.xy()[0])
nbytes = (p.nbits() + 7) // 8
decrypt_and_print(x_S, nbytes, NONCE, CT)
"""

MUSTER_C8 = r"""
# ============================================================
# Kapitel 02 - Challenge 8: Invalid-Curve-Angriff
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   Diese Challenge hat viele Sonden (Probes). Statt jeden Wert einzeln
#   einzutragen, fuegst du deine KOMPLETTE Capture unten zwischen die
#   dreifachen Anfuehrungszeichen ein (TODO). Der Rest laeuft automatisch
#
#   Angriff: Bob prueft den empfangenen Punkt nicht. Fuer jede Sonde liegt
#   ein Punkt R = d*P auf einer schwachen Kurve E'(b_invalid) mit kleiner
#   Untergruppe der Ordnung q. Per BSGS findet man d mod q; alle Reste
#   werden per CRT zu Bobs Geheimnis d zusammengesetzt
# ============================================================
import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- TODO: deine komplette .tcvcap hier einfuegen ---
CAPTURE = '''
<<< HIER DEINE KOMPLETTE CAPTURE EINFUEGEN >>>
'''

# --- Capture einlesen ---
c = {}
for line in CAPTURE.splitlines():
    line = line.strip()
    if not line or line.startswith("#") or ":" not in line: continue
    k, _, val = line.partition(":")
    c[k.strip()] = val.strip()

a_curve = int(c["CURVE_A"]); p = int(c["CURVE_P"])
Bx = int(c["BOB_PUBLIC_BX"]); By = int(c["BOB_PUBLIC_BY"])
nprobes = int(c["N_PROBES"])

# --- pro Sonde: d mod q per BSGS auf der schwachen Kurve ---
res, mod = [], []
for i in range(nprobes):
    b_inv = int(c[f"PROBE_{i}_BINVALID"]); q = int(c[f"PROBE_{i}_Q"])
    Rx = int(c[f"PROBE_{i}_RX"]); Ry = int(c[f"PROBE_{i}_RY"])
    Px = int(c[f"PROBE_{i}_PX"]); Py = int(c[f"PROBE_{i}_PY"])
    Einv = EllipticCurve(GF(p), [a_curve, b_inv])
    P = Einv(Px, Py); R = Einv(Rx, Ry)
    d_mod_q = P.discrete_log(R)     # kleine Ordnung q -> schnell
    res.append(int(d_mod_q)); mod.append(q)

# --- CRT: alle Reste zu d zusammensetzen ---
d = crt(res, mod)
print("Bobs Geheimnis d rekonstruiert.")

# --- gemeinsames Geheimnis auf der ECHTEN Kurve: S = d*(Alice-Punkt)? ---
# Der Schluessel kommt aus x(S) = x(d * G) auf der echten Kurve; hier nutzen
# wir Bobs oeffentlichen Punkt und den Generator der echten Kurve:
b_curve = int(c["CURVE_B"])
E = EllipticCurve(GF(p), [a_curve, b_curve])
Gx = int(c["GENERATOR_GX"]); Gy = int(c["GENERATOR_GY"])
S = d * E(Gx, Gy)
x_S = int(S.xy()[0])
nbytes = (p.nbits() + 7) // 8
key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
           info=b"kapitel-02-dh-aead-v1").derive(int(x_S).to_bytes(nbytes, "big"))
pt = AESGCM(key).decrypt(base64.b64decode(c["RECORD_NONCE_B64"]),
                         base64.b64decode(c["RECORD_CIPHERTEXT_B64"]), None)
print(pt.decode())
"""

MUSTER_C9 = r"""
# ============================================================
# Kapitel 02 - Challenge 9: ElGamal Nonce-Wiederverwendung
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   1. Oeffne deine .tcvcap-Datei
#   2. Ersetze die TODO-Werte durch DEINE Werte aus der Capture
#   3. Fuehre den Code aus (Evaluate). Die Flagge erscheint am Ende
#
#   Zwei Nachrichten wurden mit DEMSELBEN Zufallswert k verschluesselt
#   (gleiche C1!). Aus der bekannten Nachricht m1 folgt m2 direkt -
#   OHNE den diskreten Logarithmus zu loesen:  m2 = c2_2 * m1 / c2_1 (mod p)
# ============================================================
import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def decrypt_and_print(s_int, nbytes, nonce_b64, ct_b64):
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
               info=b"kapitel-02-dh-aead-v1").derive(
        int(s_int).to_bytes(nbytes, "big"))
    pt = AESGCM(key).decrypt(base64.b64decode(nonce_b64), base64.b64decode(ct_b64), None)
    print(pt.decode())

# --- Werte aus deiner Capture eintragen ---
p    = 111197738933640642024022982475954342470402926145472487192315146398982866409827   # TODO: PARAM_P
m1   = 36667803315537953186949453076607199808050471817664296577332800268760392907914   # TODO: MESSAGE1_KNOWN_M1
c2_1 = 19019241733404907111254791521410915548925920968751019277989920780420730978337   # TODO: MESSAGE1_C2
c2_2 = 1312685349007490913422303432626162094883923798795368172876169893398134906397   # TODO: MESSAGE2_C2
NONCE = "SwO/T/ayzk4QTxYJ"   # TODO: RECORD_NONCE_B64
CT    = "db9iSIHvtKy1YNH2Foj0kekLwhoJ6qHI5MKASIPUq9cxgyoXmxqleNwlhAfTRfcY7jWxponwgOANjRCK/hhveTlsrgg1Bp2i7oaTN7SkRxxrQR/eGEwqh5MPZfx/6uO7W22FsP4NmopQKnAxYNwL3B8QpQ9YiVl2tdOQL+XtsMRMZPZOUpAef+X92Md5Sc6ELeOzex+gxOOD0m18AfxIzKHln90wNKvNaOsEG54dRB2KHhbKJR0fBki7oehD7fGOg38SFkH1rGL1/wB2JlwRrwluHuM="   # TODO: RECORD_CIPHERTEXT_B64

# --- Geheime Nachricht m2 rekonstruieren (Nonce-Reuse) ---
m2 = (c2_2 * m1 * inverse_mod(c2_1, p)) % p
print("m2 rekonstruiert.")

# --- Schluessel aus m2 ableiten und entschluesseln ---
nbytes = (p.nbits() + 7) // 8
decrypt_and_print(m2, nbytes, NONCE, CT)
"""

MUSTER_C10 = r"""
# ============================================================
# Kapitel 02 - Challenge 10: DSA Nonce-Wiederverwendung (PS3-Style)
# Muster-Loeser fuer https://sagecell.sagemath.org/
#
# Anleitung:
#   1. Oeffne deine .tcvcap-Datei
#   2. Ersetze die TODO-Werte durch DEINE Werte aus der Capture
#   3. Fuehre den Code aus (Evaluate). Die Flagge erscheint am Ende
#
#   Zwei Signaturen mit demselben r -> derselbe Nonce k. Daraus folgt
#   k = (h1-h2)/(s1-s2) mod q, dann der private Schluessel
#   x = (s1*k - h1)/r mod q. Der Schluessel kommt aus x
# ============================================================
import base64
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def decrypt_and_print(s_int, nbytes, nonce_b64, ct_b64):
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
               info=b"kapitel-02-dh-aead-v1").derive(
        int(s_int).to_bytes(nbytes, "big"))
    pt = AESGCM(key).decrypt(base64.b64decode(nonce_b64), base64.b64decode(ct_b64), None)
    print(pt.decode())

import hashlib
# --- Werte aus deiner Capture eintragen ---
q  = 1003817332073527104584703450766462259787793692589   # TODO: PARAM_Q
r  = 717920423447845656052111411285015830304296038439   # TODO: SIG1_R (in beiden Signaturen gleich!)
s1 = 779943074252451089012879968816722421792891708018   # TODO: SIG1_S
s2 = 794733964847557067699436541983874252821441710982   # TODO: SIG2_S
MSG1 = "UEBERWEISUNG-KONTO-A-2026"   # TODO: SIG1_MESSAGE_UTF8
MSG2 = "UEBERWEISUNG-KONTO-B-2026"   # TODO: SIG2_MESSAGE_UTF8
NONCE = "nB4TAiEZbo6kMNiJ"   # TODO: RECORD_NONCE_B64
CT    = "K6NAYt6Tu5JhmVAXuMAIkM1RrHwGgbZPM0Ung1cIcmPRGPZRSdy786T4YYPZxkSx8XPvUY8wInvAMWausWhwVnwwLZ3W1dHQRZBygNAuITXfu6bHdKcKF3bCPVrwRD/6LcLZVdbRPWjOD/LZMtdWV7S7PDy+GArQkisMXDdOgUHZo+DqZA83rSD+6c3Ey88AVihPxgdwCru2NIQuEkvIGNmQC7XyELTlgUcgflbnZjPuxMklT/DnetpMAMM0rklEuUC4rl+w6hblRskwG724jlEz6VY="   # TODO: RECORD_CIPHERTEXT_B64

# --- Hashes der Nachrichten (SHA-256, dann mod q) ---
h1 = int(hashlib.sha256(MSG1.encode()).hexdigest(), 16) % q
h2 = int(hashlib.sha256(MSG2.encode()).hexdigest(), 16) % q

# --- Nonce k und privaten Schluessel x rekonstruieren ---
k = ((h1 - h2) * inverse_mod((s1 - s2) % q, q)) % q
x = (((s1 * k - h1) % q) * inverse_mod(r, q)) % q
print("privater Schluessel x rekonstruiert.")

# --- Schluessel aus x ableiten (Laenge nach bits(q)!) und entschluesseln ---
nbytes = (q.bit_length() + 7) // 8
decrypt_and_print(x, nbytes, NONCE, CT)
"""
