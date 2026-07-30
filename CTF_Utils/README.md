# Schwaches Diffie-Hellman (Logjam) — Lösungs- und Betriebsanleitung

> Interne Dokumentation für Betreuung / Wartung / künftige Studierende.
> **Nicht** studierendenseitig ausgeliefert (kein Spoiler im Kurs).
> Sprache: Deutsch (studierendenbezogene Begriffe), Kommentare/Code Englisch.

Dieses Kapitel (Tag 4, `challenge_04`) demonstriert die **Logjam**-Attacke auf
DHE_EXPORT: ein 512-Bit-`p`, dessen Ordnung `p-1` *glatt* ist, wird per
Pohlig-Hellman gebrochen; daraus wird das TLS-Master-Secret abgeleitet und der
verschlüsselte Application-Data-Record (die Flagge) entschlüsselt.

Es ist das dynamische, backend-gestützte Gegenstück zum FREAK-Kapitel von Jonas
(gleiche PRF/RC4/MD5-Mechanik, nur DH statt RSA beim Schlüsselaustausch).

---

## 1. Architektur im Überblick

```
Trainings-VM (Kali)                     Host (Windows, Docker)
--------------------                     ----------------------
Wireshark (eth1, tcp.port==4434)         challengebackend  (FastAPI)
dh_export_vm_listener.py  <────fetch─────  GET /dh_export/vm_replay_data
   (spielt Server-Rolle)                    (liefert server_flight_*_hex)
        ▲                                  dh_export_sender.py
        │  spielt Client-Rolle             (via POST /dh_export/{index}/start_capture)
        └──────────────TCP:4434────────────┘
```

* **Backend** hält einen festen Pool von `POOL_SIZE = 100` Varianten (MongoDB,
  Collection `DhExportVariant`), erzeugt einmalig via
  `scripts/generate_dh_export_pool.py`.
* **Variante pro Nutzer:** `variant_index_for_user(username) = sha256(username.lower()) % 100`.
  Damit passt jede Variante deterministisch zu genau einem Konto — Nachbarn
  können keine Werte kopieren.
* **Parameter:** `p` = 512 Bit (echte Logjam-Größe), kleine Primfaktoren von
  `p-1` je ~24 Bit (schnelle Faktorisierung), Server-Zertifikat 2×256 Bit RSA.
* **Flag-Format:** `crypto{logjam_weak_dh_<index:03d>_<6-stellig>}` — gemeinsames
  Präfix `crypto` wie im FREAK-Kapitel.
* **Validierung:** vier serverseitige `dynamic_check`-Validatoren in
  `custom/challengebackend/utils/dh_export_pool.py`:
  `dh_factors`, `dh_server_secret`, `dh_master_secret`, `dh_flag`.

### Betroffene Dateien

| Zweck | Pfad (relativ zu `DUMMY_CTF/`) |
|-------|--------------------------------|
| Seite (Frontend) | `custom/sites/pages/challenge_04.py` |
| Aufgaben (Frontend) | `custom/sites/tasks/challenge_04_tasks.py` |
| Krypto-Kern | `custom/challengebackend/utils/dh_export_crypto.py` |
| Pool + dynamic_check | `custom/challengebackend/utils/dh_export_pool.py` |
| Pool-Seeding (einmalig) | `custom/challengebackend/scripts/generate_dh_export_pool.py` |
| Endpoints | `custom/challengebackend/endpoints/dh_export.py` |
| VM-Listener (Server-Rolle) | `CTF_Utils/dh_export_vm_listener.py` |

> **`core/` niemals anfassen.** Alles liegt in `custom/`.

---

## 2. Betrieb: Handshake auf der VM mitschneiden

Alles läuft **lokal**. Es gibt **kein** herunterladbares `.pcap` — die
Studierenden schneiden ihren eigenen Handshake live mit.

### 2.1 Netzwerk (einmalig einrichten)

Zwei Richtungen müssen funktionieren:

**Richtung 1 — Listener (Kali) → Backend (Host).**
Der Listener holt die Server-Flights vom Backend. Da das Backend unter
`challenge.localhost` läuft und glibc `*.localhost` fest auf `127.0.0.1`
verdrahtet (noch **vor** `/etc/hosts`), muss die Auflösung wie bei
`curl --resolve` entkoppelt werden. Dafür hat der Listener die Option
`--resolve-ip` (Python-Äquivalent zu `curl --resolve`: Socket verbindet zur IP,
SNI/Host bleiben `challenge.localhost`, damit Caddy die richtige Site liefert).

```bash
# auf der Kali:
export CHALLENGE_API_KEY="this-is-a-very-special-api-key"   # = Wert aus DUMMY_CTF/.env
python3 dh_export_vm_listener.py \
    --challenge-domain challenge.localhost \
    --resolve-ip 192.168.56.1 \        # Host-Only-IP des Windows-Hosts (Caddy)
    --insecure                          # self-signed Dev-Zertifikat
# Erwartet: "Fetched N variants ..." + "Listening on 0.0.0.0:4434 ..."
```

**Richtung 2 — Backend (Host) → Listener (Kali).**
Beim Klick auf „Gestartet“ verbindet sich der Sender im Container zur VM.
In `DUMMY_CTF/.env` setzen und den `challenge`-Service neu starten:

```
DH_EXPORT_VM_HOST=192.168.56.101   # Host-Only-IP der Kali
DH_EXPORT_VM_PORT=4434
```
```powershell
docker compose up -d --force-recreate challenge
```
Test, dass der Container die VM erreicht:
```powershell
docker compose exec challenge ping -c 3 192.168.56.101
```

> IPs anpassen: `192.168.56.1` = Host (VirtualBox Host-Only Adapter),
> `192.168.56.101` = Kali. Prüfen mit `ip -4 addr show` auf der Kali.

### 2.2 Mitschnitt auslösen

1. Wireshark auf der Kali starten, Interface **`eth1`** (die mit `192.168.56.101`),
   Filter `tcp.port == 4434`, Aufnahme starten.
2. Auf der Kursseite (Aufgabe ab 4.3) im Panel auf **„Gestartet“** klicken —
   löst `POST /dh_export/<index>/start_capture` aus.
3. Wireshark zeigt den vollständigen DHE_EXPORT-Handshake:
   ClientHello, ServerHello, Certificate, **ServerKeyExchange** (p, g, Ys),
   ServerHelloDone, **ClientKeyExchange** (Yc), ChangeCipherSpec,
   verschlüsseltes Finished, **ApplicationData** (Flagge).

Werte kopiert man in Wireshark per **Rechtsklick auf das Feld → Copy →
…as a Hex Stream**.

---

## 3. Lösungsweg (7 Aufgaben, 4.0–4.6)

| # | Ziel | Antwort | Prüfung |
|---|------|---------|---------|
| 4.0 | Name der Attacke | `logjam` | fest |
| 4.1 | Bitlänge von `p` | `512` | fest |
| 4.2 | Name des DLP-Algorithmus | `pohlig-hellman` | fest |
| 4.3 | Primfaktoren von `p-1` | `q1,q2,...` (kommagetrennt) | `dh_factors` |
| 4.4 | Server-Geheimnis `s` | Dezimalzahl | `dh_server_secret` |
| 4.5 | TLS Master Secret | Hex (96 Zeichen) | `dh_master_secret` |
| 4.6 | Flagge | `crypto{...}` | `dh_flag` |

**Werte aus Wireshark (aus dem eigenen Mitschnitt):**
- `p`, `g`, `Ys` → ServerKeyExchange
- `Yc` → ClientKeyExchange (Feld `Pubkey`)
- `client_random` (32 B) → ClientHello, Feld `Random`
- `server_random` (32 B) → ServerHello, Feld `Random`
- `server_flight_2` → die Server-Records ab ChangeCipherSpec (für 4.6)

### 4.3 — `p-1` faktorisieren

**Weg 1 (yafu, wie FREAK):**
```bash
python3 -c "p=0x<DEIN_P_HEX>; print(p-1)"
yafu "factor(<P_MINUS_1>)"
```

**Weg 2 (SageCell, empfohlen — https://sagecell.sagemath.org/):**
```python
p = Integer("<DEIN_P_HEX>", 16)
print("p:", p.nbits(), "Bit, prim:", p.is_prime())
fac = factor(p - 1)
print(fac)                      # 2 * q1 * q2 * ... * qn  (glatt)
print([q for q, _ in fac])
```
Antwort: alle Primfaktoren, kommagetrennt (Faktor 2 optional). Produkt = `p-1`.

### 4.4 — Diskreter Logarithmus (Pohlig-Hellman)

```python
p  = Integer("<DEIN_P_HEX>",  16)
Ys = Integer("<DEIN_Ys_HEX>", 16)
g  = 2
F = GF(p)
s = discrete_log(F(Ys), F(g))   # intern Pohlig-Hellman, in Sekunden
print("s =", s)
print(power_mod(g, s, p) == Ys) # True
```
Antwort: `s` als Dezimalzahl.

### 4.5 — Master Secret

```python
import hmac, hashlib
p  = int("<DEIN_P_HEX>", 16)
s  = <DEIN_S>                    # aus 4.4
Yc = int("<DEIN_Yc_HEX>", 16)
client_random = bytes.fromhex("<CLIENT_RANDOM_HEX>")   # 32 B
server_random = bytes.fromhex("<SERVER_RANDOM_HEX>")   # 32 B

Z = pow(Yc, s, p)
pms = Z.to_bytes((Z.bit_length() + 7) // 8, "big")

def p_hash(dg, secret, seed, n):
    out, a = b"", seed
    while len(out) < n:
        a = hmac.new(secret, a, dg).digest()
        out += hmac.new(secret, a + seed, dg).digest()
    return out[:n]
def prf(secret, label, seed, n):
    half = (len(secret) + 1) // 2
    s1, s2 = secret[:half], secret[-half:]
    return bytes(x ^ y for x, y in zip(
        p_hash(hashlib.md5, s1, label + seed, n),
        p_hash(hashlib.sha1, s2, label + seed, n)))

master_secret = prf(pms, b"master secret", client_random + server_random, 48)
print(master_secret.hex())       # 96 Hex-Zeichen
```
Antwort: Master Secret als Hex.

> **Kontrolle in Wireshark:** *Preferences → Protocols → TLS →
> (Pre)-Master-Secret log filename* auf eine Datei mit Zeile
> `CLIENT_RANDOM <client_random_hex> <master_secret_hex>` setzen.
> Wireshark entschlüsselt dann die Application Data selbst.

### 4.6 — Flagge entschlüsseln

Zwei Stolperfallen: (1) `key_block` benutzt **server_random + client_random**
(vertauscht ggü. 4.5); (2) RC4 ist **ein durchgehender Keystream** — das
server-Finished (seq 0) muss **vor** der ApplicationData (seq 1) entschlüsselt
werden. Server→Client nutzt `server_write_key`.

```python
import hmac, hashlib
master_secret   = bytes.fromhex("<MASTER_SECRET_HEX>")
client_random   = bytes.fromhex("<CLIENT_RANDOM_HEX>")
server_random   = bytes.fromhex("<SERVER_RANDOM_HEX>")
server_flight_2 = bytes.fromhex("<SERVER_FLIGHT_2_HEX>")

def p_hash(dg, secret, seed, n):
    out, a = b"", seed
    while len(out) < n:
        a = hmac.new(secret, a, dg).digest()
        out += hmac.new(secret, a + seed, dg).digest()
    return out[:n]
def prf(secret, label, seed, n):
    half = (len(secret) + 1) // 2
    s1, s2 = secret[:half], secret[-half:]
    return bytes(x ^ y for x, y in zip(
        p_hash(hashlib.md5, s1, label + seed, n),
        p_hash(hashlib.sha1, s2, label + seed, n)))

kb = prf(master_secret, b"key expansion", server_random + client_random, 2*16 + 2*5)
server_write_key_short = kb[37:42]                 # 5 B = 40 Bit (Export!)
server_write_key = prf(server_write_key_short, b"server write key",
                       client_random + server_random, 16)

class RC4:
    def __init__(self, key):
        s = list(range(256)); j = 0
        for i in range(256):
            j = (j + s[i] + key[i % len(key)]) % 256
            s[i], s[j] = s[j], s[i]
        self.s, self.i, self.j = s, 0, 0
    def crypt(self, data):
        s, i, j = self.s, self.i, self.j; out = bytearray(len(data))
        for k, b in enumerate(data):
            i = (i + 1) % 256; j = (j + s[i]) % 256
            s[i], s[j] = s[j], s[i]
            out[k] = b ^ s[(s[i] + s[j]) % 256]
        self.i, self.j = i, j; return bytes(out)

def records(buf):
    out, off = [], 0
    while off < len(buf):
        ln = int.from_bytes(buf[off+3:off+5], "big")
        out.append((buf[off], buf[off+5:off+5+ln])); off += 5 + ln
    return out

rc4 = RC4(server_write_key); flag = None
for ctype, frag in records(server_flight_2):
    if ctype == 20:                 # ChangeCipherSpec: unverschlüsselt
        continue
    pt = rc4.crypt(frag)[:-16]      # RC4, dann 16-B-MAC (MD5) abtrennen
    if ctype == 23:                 # ApplicationData
        flag = pt
print(flag.decode(errors="replace"))   # crypto{...}
```

---

## 4. Betrieb & Wartung (Cheatsheet)

**Pool (neu) erzeugen** — nach Änderung an Krypto/Parametern:
```bash
docker compose exec challenge python scripts/generate_dh_export_pool.py
```

**Nach Schema-Änderungen** die Fortschritts-Collection leeren, sonst
`AttributeError: 'NoneType' has no attribute 'allow_random_order'`:
```javascript
// in mongosh:
db.user_challenges.deleteMany({ day_id: 4 })
```

**Testmodus / Admin:** Swagger UI mit Header
`X-Admin-Token: this-is-a-super-secure-admin-token`.

**Eigenen Varianten-Index bestimmen** (für gezieltes Testen):
```python
import hashlib
print(int(hashlib.sha256("<username>".encode()).hexdigest(), 16) % 100)
```
> Wichtig: `start_capture` und die `dynamic_check` beziehen sich auf **diese**
> Variante. Zum Testen den passenden Index mitschneiden.

---

## 5. Offene Punkte / Design-Hinweise

* **Zwei Systeme koexistieren:** dieses backend-gestützte Kapitel (Tag 4,
  `crypto{...}`, `dynamic_check`) **und** das statische Akt-I-Kapitel
  (`challenge_02_tasks.py`, Tag 2, `hiy{...}`, `.tcvcap`-Dateien). Präfix-
  und Architekturunterschied ggf. mit dem Team abstimmen.
* **`--resolve-ip`** ist eine eigene Ergänzung ggü. Jonas' Listener; sie macht
  das Kapitel im echten MITM-Setup (separate Kali) spielbar. Für reines
  localhost-Testen nicht nötig.
* Alle studierendenseitigen Texte sind Deutsch, ohne Nennung von Namen; Code
  und Kommentare Englisch.
