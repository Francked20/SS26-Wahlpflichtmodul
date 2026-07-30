"""Kapitel 03 - Beginner-Version: Export Ciphers & FREAK.
Eigener day=95, unabhaengig von der Advanced-Version (day=3)"""

import hashlib
from urllib.parse import quote

import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from website.unlock_settings import *
from website.auth_lib import AuthCookie, BackendRequests

from ..tasks.challenge_03_beginner_tasks import (
    task_03b_00, task_03b_01, task_03b_02, task_03b_03,
    task_03b_04, task_03b_05,
)

# Muss zu challengebackend/utils/export_cipher_pool.py: POOL_SIZE passen
EXPORT_CIPHER_POOL_SIZE = 100


# Kleine, lokale UI-Helfer (challenge_04_beginner.py hat identische Kopien)
_BOX_STYLE = {
    "maxWidth": "1200px", "width": "100%", "margin": "16px auto",
    "padding": "18px", "borderRadius": "12px", "color": "#F2F2F2",
}


def box(*children, accent="#04B486"):
    return rx.box(
        *children,
        style={
            **_BOX_STYLE,
            "background": "rgba(255, 255, 255, 0.04)",
            "border": f"1px solid {accent}55",
            "borderLeft": f"4px solid {accent}",
        },
    )


def h(text, accent="#04B486"):
    return rx.heading(text, size="5", color=accent, style={"marginBottom": "8px"})


def explain_box(title, body_markdown):
    return rx.accordion.root(
        rx.accordion.item(
            header=rx.text.strong(f"❓ Was ist {title.rstrip('?')}?"),
            content=rx.markdown(body_markdown, style={"color": "#F2F2F2"}),
        ),
        collapsible=True,
        style={**_BOX_STYLE, "background": "rgba(160, 210, 255, 0.08)"},
    )


def checkpoint(text):
    return rx.box(
        rx.markdown(text, style={"color": "#F2F2F2"}),
        style={
            **_BOX_STYLE,
            "background": "rgba(255, 210, 100, 0.10)",
            "border": "1px solid rgba(255, 210, 100, 0.4)",
        },
    )


def success_box(text, accent="#04B486"):
    return rx.box(
        rx.markdown(text, style={"color": "#F2F2F2"}),
        style={**_BOX_STYLE, "background": f"{accent}22", "border": f"1px solid {accent}"},
    )


def pcap_download_button(text, href):
    """rx.download() statt <a download> - Safari zerstoert Binaerdaten sonst
    beim direkten Anchor-Download"""
    return rx.button(
        rx.hstack(
            rx.icon("download", size=18),
            rx.text(text, font_weight="500"),
            align_items="center", spacing="2",
        ),
        on_click=rx.download(url=href, filename="capture.pcap"),
        style={
            "display": "inline-flex",
            "margin": "8px auto",
            "padding": "10px 18px",
            "borderRadius": "10px",
            "background": "rgba(4, 180, 134, 0.18)",
            "border": "1px solid #04B486",
            "color": "#04B486",
            "cursor": "pointer",
        },
    )


# Backend-Zugriff: identisch zu MyVariantState in challenge_03.py
class ChallengeBackendRequests(BackendRequests):
    url = "http://challenge:8000"


class BeginnerExportCipherState(AuthCookie):
    index: int = 0
    n256: str = ""
    n512: str = ""
    loaded: bool = False
    reveal_factor: str = ""
    capture_status: str = ""

    @rx.var
    def pcap_url(self) -> str:
        """Dieselbe Formel wie export_cipher_pool.py: variant_index_for_user"""
        try:
            username = self.data_cookie
            if not username:
                return ""
            digest = hashlib.sha256(username.lower().encode()).hexdigest()
            idx = int(digest, 16) % EXPORT_CIPHER_POOL_SIZE
            return f"/custom/0300/{idx}/capture.pcap"
        except (TypeError, AttributeError):
            return ""

    async def load(self):
        safe_username = quote(self.get_username, safe="")
        response = await ChallengeBackendRequests.get(f"/export_cipher/variant/{safe_username}")
        if response.status_code == 200:
            data = response.json()
            self.index = data["index"]
            self.n256 = data["n256"]
            self.n512 = data["n512"]
            self.loaded = True

        reveal_response = await BackendRequests.get(
            "/challenges/export_cipher_reveal_factor",
            params={"day": 95, "task": 2},
            auth=self.auth_cookie,
        )
        if reveal_response.status_code == 200:
            factor = reveal_response.json().get("reveal_factor")
            if factor:
                self.reveal_factor = str(factor)

    @rx.event(background=True)
    async def trigger_capture(self):
        async with self:
            self.capture_status = "sending"
        response = await ChallengeBackendRequests.post(f"/export_cipher/{self.index}/start_capture")
        async with self:
            self.capture_status = "sent" if response.status_code == 200 else "error"


class Kapitel_03_Beginner(AbstractSiteBuilder):
    PAGE_ID = "challenge_03_beginner"

    def _capture_panel(self) -> rx.Component:
        return rx.cond(
            BeginnerExportCipherState.loaded,
            box(
                rx.markdown(
                    "Das ist Ihr persönlicher, für Sie einzigartiger Mitschnitt "
                    "(abhängig von Ihrem Benutzernamen). Sie haben **zwei "
                    "gleichwertige Wege**, ihn zu bekommen - wählen Sie einen:"
                ),
                rx.vstack(
                    rx.text.strong("Option 1 - Herunterladen:"),
                    pcap_download_button("Meine Capture herunterladen (.pcap)", BeginnerExportCipherState.pcap_url),
                    spacing="2", align_items="center", width="100%", margin_top="0.75em",
                ),
                rx.vstack(
                    rx.text.strong("Option 2 - Live mitschneiden:"),
                    rx.text(
                        "Bevor Sie klicken: Öffnen Sie zuerst Wireshark in Ihrer "
                        "Kali-Umgebung, wählen Sie oben in der Liste das passende "
                        "Netzwerk-Interface aus und starten Sie den Mitschnitt "
                        "(blaues Hai-Flossen-Symbol bzw. Strg+E) - erst danach "
                        "unten auf 'Live-Mitschnitt starten' klicken, sonst ist "
                        "der Handshake schon vorbei, bevor Wireshark mitschneidet.",
                        size="2", color="#cccccc",
                    ),
                    rx.button(
                        rx.cond(BeginnerExportCipherState.capture_status == "sending",
                                rx.spinner(size="2"), rx.icon(tag="play")),
                        rx.cond(BeginnerExportCipherState.capture_status == "sent",
                                "Erneut senden", "Live-Mitschnitt starten"),
                        on_click=BeginnerExportCipherState.trigger_capture,
                        disabled=BeginnerExportCipherState.capture_status == "sending",
                    ),
                    rx.cond(
                        BeginnerExportCipherState.capture_status == "sent",
                        rx.callout("Handshake gesendet - falls die Trainings-VM erreichbar ist, "
                                   "sehen Sie ihn jetzt live in Wireshark.",
                                   icon="check", color_scheme="green"),
                    ),
                    rx.cond(
                        BeginnerExportCipherState.capture_status == "error",
                        rx.callout("Live-Mitschnitt nicht verfügbar - nutzen Sie stattdessen den "
                                   ".pcap-Download oben, das funktioniert identisch.",
                                   icon="triangle-alert", color_scheme="orange"),
                    ),
                    spacing="2", align_items="center", width="100%", margin_top="1em",
                ),
            ),
            rx.spinner(),
        )

    def _n256_panel(self) -> rx.Component:
        return rx.cond(
            BeginnerExportCipherState.loaded,
            box(
                rx.text.strong("Ihre persönliche 256-Bit-Übungszahl:"),
                rx.hstack(rx.text.strong("N₂₅₆ ="), rx.code(BeginnerExportCipherState.n256, size="2",
                          style={"wordBreak": "break-all"}), align_items="start", margin_top="0.5em"),
                rx.text(
                    "Diese Zahl gilt NUR für Sie - kopieren Sie sie direkt in Ihr Skript.",
                    margin_top="0.75em",
                ),
                accent=self.main_color,
            ),
            rx.spinner(),
        )

    def _n512_panel(self) -> rx.Component:
        return rx.cond(
            BeginnerExportCipherState.loaded,
            box(
                rx.text.strong("Ihr echtes 512-Bit-N (für Schritt 4):"),
                rx.hstack(rx.text.strong("N ="), rx.code(BeginnerExportCipherState.n512, size="2",
                          style={"wordBreak": "break-all"}), align_items="start", margin_top="0.5em"),
                rx.text(
                    "⚠️ Wireshark (Schritt 2) zeigt dieselbe Zahl als Hexadezimalzahl - hier "
                    "oben steht sie als Dezimalzahl (Basis 10), praktischer zum Einfügen ins "
                    "Skript. Alternativ selbst umrechnen: int(\"<Ihr Hex-Wert aus Wireshark>\", 16).",
                    margin_top="0.75em", size="2", color="#cccccc",
                ),
                accent=self.main_color,
            ),
            rx.spinner(),
        )

    def _reveal_panel(self) -> rx.Component:
        return rx.cond(
            BeginnerExportCipherState.reveal_factor != "",
            rx.callout(
                rx.hstack(rx.text.strong("p ="), rx.code(BeginnerExportCipherState.reveal_factor, size="2",
                          style={"wordBreak": "break-all"}), align_items="start"),
                icon="key",
                color_scheme="amber",
                width="100%",
                style={"maxWidth": "1200px", "margin": "16px auto"},
            ),
        )

    def _content(self) -> rx.Component:
        c = self.main_color
        return rx.vstack(
            box(
                h("Die Geschichte: Ein Zertifikat, das zu schwach ist", c),
                rx.markdown(
                    r"""
1990er-USA: Verschlüsselungssoftware durfte nicht "zu stark" exportiert
werden. Server behielten deshalb absichtlich eine **schwache** RSA-Variante
(**RSA_EXPORT**) für alte Clients bei - mit einem viel zu kleinen Schlüssel.
2015 zeigte die
**FREAK**-Attacke: Ein Angreifer kann einen Client per Man-in-the-Middle
auf so eine Export-Suite herabstufen - selbst wenn beide Seiten eigentlich
starke Kryptografie beherrschen. Danach genügt es, den Schlüssel zu
faktorisieren, um den privaten Schlüssel - und damit die ganze Sitzung -
zu rekonstruieren.

**Warum das wichtig ist:** FREAK betraf 2015 schätzungsweise **36% aller
HTTPS-Server**, die Browser als "sicher" auswiesen. Ein grünes
Schloss-Symbol sagt nur "irgendwie verschlüsselt", nicht "sicher
verschlüsselt".

**Ihre Aufgabe:** Einen echten TLS-Handshake mitschneiden, den öffentlichen
Schlüssel faktorisieren, den privaten Schlüssel rekonstruieren und die
verschlüsselte Nachricht lesen.

Für **jeden** Schritt ist hier eine komplette, lauffähige Skript-Vorlage
vorbereitet. Sie müssen nie mehr als eine kleine, klar markierte Lücke
selbst ausfüllen.
                    """
                ),
                accent=c,
            ),
            explain_box(
                "RSA?",
                r"""
RSA ist ein Verschlüsselungsverfahren, das (anders als Diffie-Hellman) mit
einem **Schlüsselpaar** arbeitet: einem öffentlichen $(N, e)$, den jeder
kennen darf, und einem privaten $d$, den nur der Server kennt.

1. Man wählt zwei **Primzahlen** $p$ und $q$ und berechnet $N = p \cdot q$.
2. Der öffentliche Schlüssel ist $(N, e)$ (meist $e = 65537$).
3. Der private Schlüssel: $d \equiv e^{-1} \pmod{(p-1)(q-1)}$ - das
   "modulare Inverse" von $e$, eine reine Rechenaufgabe, **kein** Raten.
   In Python berechnet `pow(e, -1, phi)` das direkt (Python 3.8+) - Sie
   müssen keinen Algorithmus dafür selbst schreiben, nur die richtigen
   Werte einsetzen.
4. Verschlüsseln: $c = m^e \bmod N$. Entschlüsseln: $m = c^d \bmod N$.

Die **gesamte** Sicherheit hängt daran, dass niemand $N$ in $p$ und $q$
zerlegen kann. Kennt man $p$ und $q$, lässt sich $d$ direkt berechnen, ganz
ohne weiteres Faktorisieren. Bei der in Schritt 2 ermittelten Schlüsselgröße
dauert die Zerlegung selbst mit yafu ein bis zwei Tage (deshalb üben Sie an
einer kleineren 256-Bit-Zahl, siehe Schritt 3), bei 2048+ Bit ist sie mit
heutiger Technik praktisch unmöglich.
                """,
            ),
            explain_box(
                "ein TLS-Handshake?",
                r"""
Bevor zwei Rechner verschlüsselt kommunizieren (z.B. Browser und Webserver
bei "https://"), einigen sie sich in einem **Handshake** auf einen
gemeinsamen Schlüssel. Grob:
`ClientHello` (Client sagt: "ich will reden, das kann ich") →
`ServerHello` (Server antwortet, legt Verfahren fest) →
`Certificate` (Server schickt seinen öffentlichen RSA-Schlüssel $(N,e)$) →
`ClientKeyExchange` (Client verschlüsselt ein zufälliges Geheimnis mit
diesem öffentlichen Schlüssel und schickt es) →
`Finished` (beide bestätigen verschlüsselt, dass alles geklappt hat) →
danach fließen die eigentlichen Nutzdaten (`Application Data`), ab hier
alles verschlüsselt.
                """,
            ),
            explain_box(
                "eine Cipher Suite / RSA_EXPORT?",
                r"""
Eine **Cipher Suite** ist ein Paket aus Verfahren, auf das sich Client und
Server einigen. **RSA_EXPORT** ist eine sehr alte, absichtlich geschwächte
Suite: Der Schlüsselaustausch läuft über RSA, aber mit einem viel zu
kleinen Schlüssel (deutlich kleiner als die heute üblichen 2048+ Bit - wie
klein genau, finden Sie in Schritt 2 selbst heraus).
                """,
            ),
            explain_box(
                "Wireshark?",
                r"""
**Wireshark** ist ein kostenloses Programm, das Netzwerkverkehr sichtbar
macht - Paket für Paket, mit allen Feldern lesbar aufgeschlüsselt. Für
diese Challenge öffnen Sie damit eine aufgezeichnete Verbindung
(`.pcap`-Datei) und lesen die Werte aus, die der Server im Klartext
verschickt hat ($N$, $e$, …).

Herunterladen: https://www.wireshark.org/download.html
                """,
            ),
            render_task(self.PAGE_ID, 0, "Schritt 1: Einführung", TaskWidget(task_03b_00)),
            rx.cond(
                PlayerCardState.tasks_solved["day_95_task_00"] | PlayerCardState.enable_test_mode,
                rx.fragment(
                    checkpoint(
                        "**Bevor es losgeht:** Alle Werkzeuge, die Sie brauchen (Wireshark, "
                        "Python 3, `sympy`, **yafu**), stehen fertig eingerichtet in der "
                        "**Kali-Umgebung** dieser Challenge bereit - Button 'Kali' direkt bei "
                        "der jeweiligen Aufgabe, keine eigene Installation nötig. Nur falls die "
                        "Kali-Umgebung bei Ihnen gerade nicht verfügbar ist: Sie können "
                        "Wireshark (https://www.wireshark.org) und `pip install sympy` "
                        "problemlos lokal installieren. **yafu** dagegen gibt es nur für "
                        "Linux/Windows, keinen offiziellen macOS-Build - betrifft Sie das, "
                        "nutzen Sie die Kali-Umgebung für den Faktorisierungs-Schritt (Schritt 3). "
                        "`sympy.factorint()` ist dafür **kein brauchbarer Ersatz**: $N_{256}$ ist "
                        "das Produkt zweier etwa gleich großer ~128-Bit-Primzahlen, und für solche "
                        "Zahlen brauchen sympys einfache Verfahren extrem lange (anders als z.B. "
                        "bei Diffie-Hellman-Zahlen)."
                    ),
                    self._capture_panel(),
                    render_task(self.PAGE_ID, 1, "Schritt 2: Wie groß ist der RSA-Schlüssel?", TaskWidget(task_03b_01)),
                    rx.cond(
                        PlayerCardState.tasks_solved["day_95_task_01"] | PlayerCardState.enable_test_mode,
                        rx.fragment(
                            self._n256_panel(),
                            box(
                                h("Schritt 3 - Übungszahl faktorisieren", c),
                                rx.markdown(
                                    r"""
Kein Code hier - nur ein externes Werkzeug (Terminal, z.B. über den
"Kali"-Button bei der Aufgabe unten). Den genauen Befehl und alle Details
finden Sie direkt in der Aufgabe unten.

Bei Erfolg bekommen Sie automatisch **einen Faktor Ihres echten
512-Bit-Schlüssels** geschenkt - eine Abkürzung für Schritt 4.
                                    """
                                ),
                                accent=c,
                            ),
                            render_task(self.PAGE_ID, 2, "Schritt 3: 256-Bit faktorisieren", TaskWidget(task_03b_02)),
                            self._n512_panel(),
                            rx.cond(
                                PlayerCardState.tasks_solved["day_95_task_02"] | PlayerCardState.enable_test_mode,
                                rx.fragment(
                                    self._reveal_panel(),
                                    box(
                                        h("Schritt 4 - Zweiten Faktor berechnen (Teil 1/3 Ihres Skripts)", c),
                                        rx.markdown(
                                            r"""
Neue Datei anlegen (z.B. `loesung.py`). Die `None`-Werte unten sind
**absichtlich** keine echten Werte:

```python
n512 = None # <- Ihr echtes 512-Bit-N (Kasten direkt über dieser Aufgabe)
p512 = None # <- Ihr geschenkter Faktor aus Schritt 3 (Belohnungs-Kasten)

# TODO: q berechnen - wenn N = p * q und Sie p kennen, wie kommen Sie an q?
# Achtung: n512 hat >150 Dezimalstellen - die normale Division "/" liefert
# bei so großen Zahlen einen ungenauen Float. Es gibt eine Ganzzahl-Division
q512 = None

print("gefunden: q =", q512)
print("Kontrolle (muss True sein):", n512 % p512 == 0 and p512 * q512 == n512)
```
                                            """
                                        ),
                                        accent=c,
                                    ),
                                    checkpoint(
                                        "**Selbstkontrolle:** Das Skript druckt bereits, ob "
                                        "`p512 * q512 == n512` gilt. Steht dort `False`, prüfen "
                                        "Sie, ob Sie N wirklich aus Ihrer eigenen Capture "
                                        "abgelesen haben (nicht aus einer fremden)."
                                    ),
                                    render_task(self.PAGE_ID, 3, "Schritt 4: Zweiten Faktor berechnen", TaskWidget(task_03b_03)),
                                    rx.cond(
                                        PlayerCardState.tasks_solved["day_95_task_03"] | PlayerCardState.enable_test_mode,
                                        rx.fragment(
                                            explain_box(
                                                "das TLS Master Secret / pre_master_secret?",
                                                r"""
Der Client verschlüsselt beim Handshake ein zufälliges Geheimnis
(**pre_master_secret**, 48 Byte) mit dem öffentlichen RSA-Schlüssel des
Servers und schickt es in der `ClientKeyExchange`-Nachricht. Normalerweise
kann nur der Server (mit seinem privaten Schlüssel $d$) das wieder
entschlüsseln - Sie haben $d$ jetzt aber selbst berechnet. Aus dem
pre_master_secret wird über eine Hash-Funktion (die **PRF**) das
**master_secret** abgeleitet - ein fester 48-Byte-Block, aus dem später
alle eigentlichen Schlüssel kommen.
                                                """,
                                            ),
                                            box(
                                                h("Wireshark: die restlichen Werte auslesen", c),
                                                rx.markdown(
                                                    r"""
Öffnen Sie wieder Ihre Capture, Filter `tls.handshake`:

1. **ClientHello** → aufklappen bis `Random` (32 Byte) → Rechtsklick →
   `Copy` → `...as a Hex Stream`. Das ist `client_random`.
2. **ServerHello** → genauso das Feld `Random` kopieren. Das ist
   `server_random`.
3. **Client Key Exchange** → aufklappen bis zum verschlüsselten
   pre_master_secret-Feld → Rechtsklick → `Copy` → `...as a Hex Stream`.
   Das ist `encrypted_pms`.
                                                    """
                                                ),
                                                accent=c,
                                            ),
                                            box(
                                                h("Schritt 5 - Master Secret berechnen (Teil 2/3, direkt anhängen)", c),
                                                rx.markdown(
                                                    r"""
```python
import hmac, hashlib

def p_hash(digestmod, secret, seed, length):
    # Fertig vorgegeben
    out = b""
    a = seed
    while len(out) < length:
        a = hmac.new(secret, a, digestmod).digest()
        out += hmac.new(secret, a + seed, digestmod).digest()
    return out[:length]

def tls10_prf(secret, label, seed, length):
    # Fertig vorgegeben - die TLS-1.0-PRF aus RFC 2246
    half = (len(secret) + 1) // 2
    s1, s2 = secret[:half], secret[-half:]
    p_md5 = p_hash(hashlib.md5, s1, label + seed, length)
    p_sha1 = p_hash(hashlib.sha1, s2, label + seed, length)
    return bytes(a ^ b for a, b in zip(p_md5, p_sha1))

def rsa_pkcs1_decrypt(n, d, ciphertext):
    # Fertig vorgegeben - entfernt das PKCS#1-v1.5-Padding nach dem
    # Entschluesseln: 0x00 0x02 [Zufallsbytes] 0x00 [Nachricht]
    k = (n.bit_length() + 7) // 8
    c = int.from_bytes(ciphertext, "big")
    m = pow(c, d, n)
    eb = m.to_bytes(k, "big")
    if eb[0] != 0x00 or eb[1] != 0x02:
        raise ValueError("Ungueltiges PKCS#1-v1.5-Padding")
    sep = eb.index(b"\x00", 2)
    return eb[sep + 1:]

# Aus Wireshark (siehe Anleitung oben) - als Hex-Text in Anführungszeichen:
client_random = bytes.fromhex("HIER_HEX_EINFUEGEN")
server_random = bytes.fromhex("HIER_HEX_EINFUEGEN")
encrypted_pms = bytes.fromhex("HIER_HEX_EINFUEGEN")

e = 65537
phi = (p512 - 1) * (q512 - 1)

# TODO: d ist das modulare Inverse von e modulo phi (siehe "Was ist RSA?" oben)
d = None

pms = rsa_pkcs1_decrypt(n512, d, encrypted_pms)
master_secret = tls10_prf(pms, b"master secret", client_random + server_random, 48)
print("Master Secret:", master_secret.hex())
```
                                                    """
                                                ),
                                                accent=c,
                                            ),
                                            checkpoint(
                                                "**Selbstkontrolle:** Tragen Sie Ihr Master Secret "
                                                "in Wireshark unter *Preferences → Protocols → TLS "
                                                "→ (Pre)-Master-Secret log filename* ein (Format: "
                                                "`CLIENT_RANDOM <client_random_hex> <master_secret_hex>` "
                                                "in eine Textdatei). Zeigt Wireshark danach lesbare "
                                                "'Application Data' an, stimmt Ihr Wert."
                                            ),
                                            render_task(self.PAGE_ID, 4, "Schritt 5: TLS Master Secret", TaskWidget(task_03b_04)),
                                            rx.cond(
                                                PlayerCardState.tasks_solved["day_95_task_04"] | PlayerCardState.enable_test_mode,
                                                rx.fragment(
                                                    box(
                                                        h("Wireshark: die verschlüsselten Datensätze kopieren", c),
                                                        rx.markdown(
                                                            r"""
Weiter im Filter `tls.handshake or tls.app_data`. Suchen Sie das **eine**
Paket vom Server, dessen Info-Spalte mit **"Change Cipher Spec"** beginnt
(oft steht dort noch mehr in derselben Zeile - das ist alles **ein
einziges Paket**, keine mehreren). Anklicken und aufklappen - Sie sehen
dort mehrere `TLSv1 Record Layer`-Einträge untereinander:

1. `Change Cipher Spec` - **ignorieren**.
2. `Encrypted Handshake Message` → Feld kopieren (`Copy` → `...as a Hex
   Stream`). Das ist `finished_ciphertext`.
3. `Application Data` → Feld `Encrypted Application Data` → genauso
   kopieren. Das ist `application_data_ciphertext` - hier steckt die Flagge.
                                                            """
                                                        ),
                                                        accent=c,
                                                    ),
                                                    box(
                                                        h("Schritt 6 - Flagge entschlüsseln (Teil 3/3, direkt anhängen)", c),
                                                        rx.markdown(
                                                            r"""
Hier gibt es **keine Lücke mehr**, nur noch fertigen Code. Sie müssen lediglich
`finished_ciphertext` und `application_data_ciphertext` aus Ihrem Capture
(siehe Kasten oben) einsetzen:

```python
key_block = tls10_prf(master_secret, b"key expansion", server_random + client_random, 42)
server_mac_secret = key_block[16:32]
server_write_key_raw = key_block[37:42]

def final_write_key(write_key_raw, label):
    return tls10_prf(write_key_raw, label, client_random + server_random, 16)

server_write_key = final_write_key(server_write_key_raw, b"server write key")

class RC4:
    # Fertig vorgegeben - der RC4-Stream-Cipher-Algorithmus
    def __init__(self, key):
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]
        self.S, self.i, self.j = S, 0, 0
    def crypt(self, data):
        S = self.S
        i, j = self.i, self.j
        out = bytearray()
        for b in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out.append(b ^ S[(S[i] + S[j]) % 256])
        self.i, self.j = i, j
        return bytes(out)

def mac_then_decrypt(content_type, ciphertext, mac_secret, rc4, seq_num):
    # Fertig vorgegeben - prueft die HMAC-MD5-Pruefsumme und entschluesselt
    decrypted = rc4.crypt(ciphertext)
    plaintext, mac = decrypted[:-16], decrypted[-16:]
    mac_input = (seq_num.to_bytes(8, "big") + bytes([content_type]) +
                 b"\x03\x01" + len(plaintext).to_bytes(2, "big") + plaintext)
    ok = mac == hmac.new(mac_secret, mac_input, hashlib.md5).digest()
    return plaintext, ok

finished_ciphertext = bytes.fromhex("HIER_HEX_EINFUEGEN")
application_data_ciphertext = bytes.fromhex("HIER_HEX_EINFUEGEN")

rc4 = RC4(server_write_key)
_, ok1 = mac_then_decrypt(22, finished_ciphertext, server_mac_secret, rc4, 0)
flag_bytes, ok2 = mac_then_decrypt(23, application_data_ciphertext, server_mac_secret, rc4, 1)
print("MAC-Prüfung ok:", ok1, ok2)
print("Flagge:", flag_bytes.decode())
```

**Wichtig:** `rc4 = RC4(...)` nur EINMAL erzeugen, dann beide
`mac_then_decrypt`-Aufrufe in genau dieser Reihenfolge - RC4 ist ein
fortlaufender Strom, kein Neustart pro Datensatz.
                                                            """
                                                        ),
                                                        accent=c,
                                                    ),
                                                    checkpoint(
                                                        "**Bekommen Sie `MAC-Prüfung ok: False False`?** Dann "
                                                        "stimmt vermutlich `d` (Schritt 5) oder das Master "
                                                        "Secret nicht - dort zuerst prüfen."
                                                    ),
                                                    render_task(self.PAGE_ID, 5, "Schritt 6: Flagge einreichen", TaskWidget(task_03b_05)),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            rx.cond(
                PlayerCardState.tasks_solved["day_95_task_05"] | PlayerCardState.enable_test_mode,
                success_box(
                    "**Geschafft!** Sie haben einen echten TLS-Handshake gebrochen - von "
                    "Wireshark über RSA-Faktorisierung bis zur fertig entschlüsselten "
                    "Nachricht. Genau dieser Angriff (FREAK) betraf 2015 einen erheblichen "
                    "Teil aller HTTPS-Server weltweit.",
                    c,
                ),
            ),
            spacing="4", width="100%", align_items="stretch",
        )

    def page(self) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.heading("Kapitel 3: Export Ciphers & FREAK - Beginner Walkthrough", color=self.main_color, size="8",
                           style={"background": "linear-gradient(90deg, #04B486, #00FFFF)",
                                  "WebkitBackgroundClip": "text",
                                  "WebkitTextFillColor": "transparent"}),
                rx.text("🔓", size="8", align_self="center"),
                align_items="center", width="100%", spacing="2",
                style={"marginBottom": "24px"},
            ),
            rx.cond(
                CondState.is_ready & PlayerCardState.update_day_ready[95],
                rx.cond(
                    CondState.event_enabled,
                    self._content(),
                    rx.vstack(rx.text(
                        "Bitte warten Sie, bis der Spielleiter das Event startet!")),
                ),
                rx.vstack(rx.spinner()),
            ),
            on_mount=lambda: AccordionState.init(self.PAGE_ID, 6),
        )

    def configure(self) -> None:
        self.url = "/challenge_03_beginner"
        self.name = "Export Ciphers (Beginner Walkthrough)"
        self.group = "3_Beginner"
        self.position_priority = 20
        self.icon = "unlock"
        self.main_color = "#04B486"
        self.on_load = [
            CondState.reset_check_status,
            CondState.do_checks,
            CondState.do_check_cyberrange,
            PlayerCardState.update_day(95),
            BeginnerExportCipherState.load,
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always
