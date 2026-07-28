"""Kapitel 04 - Beginner-Version: "Schwaches Diffie-Hellman (Logjam)".

Gleicher Angriff, gleicher Varianten-Pool, gleiches Backend wie
challenge_04.py (custom/challengebackend/dh_export_*) - ruft dessen bereits
bestehende Endpunkte unveraendert auf, keine einzige Zeile dort wird
angefasst. Nur Erklaerungstiefe und Code-Geruest unterscheiden sich: jeder
Fachbegriff hat eine eigene "Was ist X?"-Box, jedes Skript ist bis auf genau
eine zentrale Luecke pro Schritt fertig vorgegeben (siehe
challenge_04_beginner_tasks.py fuer die Aufgabendefinitionen).

Eigener day-Wert 94 (siehe challenge_04_beginner_tasks.py), damit Beginner-
und Advanced-Version unabhaengig voneinander loesbar sind.
"""

import hashlib
from urllib.parse import quote

import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from website.unlock_settings import *
from website.auth_lib import AuthCookie, BackendRequests

from ..tasks.challenge_04_beginner_tasks import (
    task_04b_00, task_04b_01, task_04b_02, task_04b_03,
    task_04b_04, task_04b_05, task_04b_06,
)
# Muss zu challengebackend/utils/dh_export_pool.py: POOL_SIZE passen.
DH_EXPORT_POOL_SIZE = 100


# ---------------------------------------------------------------------------
# Kleine, lokale UI-Helfer (nur diese eine Seite braucht sie - siehe
# entscheidungen.md-Prinzip: Auslagerung erst ab der zweiten Seite, die sie
# braucht).
# ---------------------------------------------------------------------------
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
            header=rx.text.strong(f"❓ Was ist {title}?"),
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
    """Eigener Download-Button statt kap02_shared.download_button (das
    <a download> HTML-Attribut) - Safari behandelt .pcap-Binaerdaten dabei
    nachweislich (per xxd verifiziert: Haeufung von EF BF BD = UTF-8-
    Replacement-Zeichen) irgendwo im Download-Pfad als Text und zerstoert sie,
    unabhaengig von Content-Type/Content-Disposition-Headern. `rx.download()`
    ist Reflex' eingebauter Mechanismus (schon anderswo im Projekt fuer PDF-
    Downloads benutzt, z.B. website/sites/welcome.py) und lädt Binaerdaten
    zuverlaessig ueber alle Browser hinweg, ohne dieses Problem."""
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


# ---------------------------------------------------------------------------
# Backend-Zugriff: identisch zu MyDhVariantState in challenge_04.py, ruft
# dieselben, unveraenderten Endpunkte auf.
# ---------------------------------------------------------------------------
class ChallengeBackendRequests(BackendRequests):
    url = "http://challenge:8000"


class BeginnerDhVariantState(AuthCookie):
    index: int = 0
    p: str = ""
    g: str = ""
    Ys: str = ""
    loaded: bool = False
    capture_status: str = ""

    @rx.var
    def pcap_url(self) -> str:
        """Berechnet den Download-Link direkt aus dem Usernamen (dieselbe
        Formel wie challengebackend/utils/dh_export_pool.py:
        variant_index_for_user) - so ist der Link sofort da, ohne auf die
        async load()-Antwort vom Backend warten zu muessen."""
        try:
            username = self.data_cookie
            if not username:
                return ""
            digest = hashlib.sha256(username.lower().encode()).hexdigest()
            idx = int(digest, 16) % DH_EXPORT_POOL_SIZE
            return f"/custom/0400/{idx}/capture.pcap"
        except (TypeError, AttributeError):
            return ""

    async def load(self):
        safe_username = quote(self.get_username, safe="")
        response = await ChallengeBackendRequests.get(f"/dh_export/variant/{safe_username}")
        if response.status_code == 200:
            data = response.json()
            self.index = data["index"]
            self.p = data["p"]
            self.g = data["g"]
            self.Ys = data["Ys"]
            self.loaded = True

    async def trigger_capture(self):
        async with self:
            self.capture_status = "sending"
        response = await ChallengeBackendRequests.post(f"/dh_export/{self.index}/start_capture")
        async with self:
            self.capture_status = "sent" if response.status_code == 200 else "error"


class Kapitel_04_Beginner(AbstractSiteBuilder):
    PAGE_ID = "challenge_04_beginner"

    def _capture_panel(self) -> rx.Component:
        return rx.cond(
            BeginnerDhVariantState.loaded,
            box(
                rx.markdown(
                    "Das ist Ihr persönlicher, für Sie einzigartiger Mitschnitt (abhängig "
                    "von Ihrem Benutzernamen). Sie haben **zwei gleichwertige Wege**, ihn zu "
                    "bekommen — wählen Sie einen:"
                ),
                rx.vstack(
                    rx.text.strong("Option 1 — Herunterladen:"),
                    pcap_download_button("Meine Capture herunterladen (.pcap)", BeginnerDhVariantState.pcap_url),
                    spacing="2", align_items="center", width="100%", margin_top="0.75em",
                ),
                rx.vstack(
                    rx.text.strong("Option 2 — Live mitschneiden:"),
                    rx.text(
                        "Bevor Sie klicken: Öffnen Sie zuerst Wireshark in Ihrer "
                        "Kali-Umgebung, wählen Sie oben in der Liste das passende Netzwerk-"
                        "Interface aus und starten Sie den Mitschnitt (blaues Hai-Flossen-"
                        "Symbol bzw. Strg+E) — erst danach unten auf 'Live-Mitschnitt starten' "
                        "klicken, sonst ist der Handshake schon vorbei, bevor Wireshark "
                        "mitschneidet.",
                        size="2", color="#cccccc",
                    ),
                    rx.button(
                        rx.cond(BeginnerDhVariantState.capture_status == "sending",
                                rx.spinner(size="2"), rx.icon(tag="play")),
                        rx.cond(BeginnerDhVariantState.capture_status == "sent",
                                "Erneut senden", "Live-Mitschnitt starten"),
                        on_click=BeginnerDhVariantState.trigger_capture,
                        disabled=BeginnerDhVariantState.capture_status == "sending",
                    ),
                    rx.cond(
                        BeginnerDhVariantState.capture_status == "sent",
                        rx.callout("Handshake gesendet - falls die Trainings-VM erreichbar ist, "
                                   "sehen Sie ihn jetzt live in Wireshark.",
                                   icon="check", color_scheme="green"),
                    ),
                    rx.cond(
                        BeginnerDhVariantState.capture_status == "error",
                        rx.callout("Live-Mitschnitt nicht verfügbar - nutzen Sie stattdessen den "
                                   ".pcap-Download oben, das funktioniert identisch.",
                                   icon="triangle-alert", color_scheme="orange"),
                    ),
                    spacing="2", align_items="center", width="100%", margin_top="1em",
                ),
            ),
            rx.spinner(),
        )

    def _dh_values_panel(self) -> rx.Component:
        return rx.cond(
            BeginnerDhVariantState.loaded,
            box(
                rx.text.strong("Ihre persönlichen DH-Parameter (schon aus Ihrer Capture ausgelesen):"),
                rx.vstack(
                    rx.hstack(rx.text.strong("p ="), rx.code(BeginnerDhVariantState.p, size="2",
                              style={"wordBreak": "break-all"}), align_items="start"),
                    rx.hstack(rx.text.strong("g ="), rx.code(BeginnerDhVariantState.g, size="2")),
                    rx.hstack(rx.text.strong("Ys ="), rx.code(BeginnerDhVariantState.Ys, size="2",
                              style={"wordBreak": "break-all"}), align_items="start"),
                    spacing="1", margin_top="0.5em", align_items="start", width="100%",
                ),
                rx.text(
                    "Diese drei Werte gelten NUR für Sie — kopieren Sie sie direkt in Ihr "
                    "Python-Skript, kein erneutes Wireshark-Ablesen nötig.",
                    margin_top="0.75em",
                ),
                rx.text(
                    "⚠️ Falls Sie dieselben Werte zum Vergleich auch in Wireshark nachschauen: "
                    "Wireshark zeigt p/g/Pubkey als Hexadezimalzahl (Basis 16, z.B. "
                    "\"933c8383...\"), hier oben stehen sie als Dezimalzahl (Basis 10, die "
                    "übliche Schreibweise). Das ist dieselbe Zahl, nur anders dargestellt — "
                    "keine zwei verschiedenen Werte! Umrechnen in Python: "
                    "int(\"933c8383...\", 16).",
                    margin_top="0.5em", size="2", color="#cccccc",
                ),
                accent=self.main_color,
            ),
            rx.spinner(),
        )

    def _content(self) -> rx.Component:
        c = self.main_color
        return rx.vstack(
            box(
                h("Die Geschichte: Ein Server, der zu freundlich ist", c),
                rx.markdown(
                    r"""
1990er-USA: Verschlüsselungssoftware durfte nicht "zu stark" exportiert
werden. Server behielten deshalb absichtlich eine **schwache**
Diffie-Hellman-Variante (**DHE_EXPORT**) für alte Clients bei. 2015 zeigte
die **Logjam**-Attacke: Diese Export-Variante lässt sich noch heute brechen
— und mit einem Trick sogar Verbindungen angreifen, die eigentlich starkes
DH benutzen wollten.

**Warum das wichtig ist:** Ein grünes Schloss-Symbol im Browser ("https")
sagt nur "es ist irgendwie verschlüsselt" — nicht "es ist sicher
verschlüsselt". 2015 betraf Logjam schätzungsweise **8% der Top-1-Million-
HTTPS-Server weltweit**: Ein Angreifer im selben Netzwerk (z.B. offenes
WLAN) konnte mitlesen, was eigentlich privat sein sollte — Passwörter,
Nachrichten, alles. Genau das machen Sie hier nach, mit denselben
Techniken, gegen einen absichtlich verwundbaren Übungsserver.

**Ihre Aufgabe:** Einen echten TLS-Handshake mitschneiden, die Schwäche in
den DH-Parametern ausnutzen, das gemeinsame Geheimnis rekonstruieren und die
verschlüsselte Nachricht lesen.

Das ist die aufwendigste Challenge in diesem Kurs — dafür ist hier für
**jeden** Schritt eine komplette, lauffähige Skript-Vorlage vorbereitet.
Sie müssen nie mehr als eine kleine, klar markierte Lücke selbst ausfüllen.
                    """
                ),
                accent=c,
            ),
            explain_box(
                "Diffie-Hellman?",
                r"""
Diffie-Hellman (DH) ist ein Verfahren, mit dem sich zwei Seiten — ohne sich
vorher zu kennen und über eine öffentlich mitlesbare Leitung — auf ein
**gemeinsames Geheimnis** einigen können. Grundidee:

1. Beide einigen sich öffentlich auf eine Primzahl $p$ und eine Zahl $g$
   (den "Erzeuger").
2. Jede Seite wählt für sich geheim eine Zufallszahl (Server: $s$, Client:
   $c$) — diese verrät niemand.
3. Jede Seite schickt der anderen öffentlich $g^{\text{eigene Zahl}} \bmod
   p$ (Server schickt $Y_s = g^s \bmod p$, Client schickt $Y_c = g^c \bmod
   p$).
4. Beide berechnen jetzt denselben Wert: Server rechnet $Y_c^{\,s} \bmod
   p$, Client rechnet $Y_s^{\,c} \bmod p$ — beides ergibt $g^{sc} \bmod p$.

Ein Lauscher sieht $p$, $g$, $Y_s$, $Y_c$ — aber ohne $s$ **oder** $c$ kann
er $g^{sc}$ nicht ausrechnen (das ist der diskrete Logarithmus, siehe
unten) — **solange $p$ groß genug und gut gewählt ist.** Genau diese
Voraussetzung verletzt DHE_EXPORT absichtlich.

**Namenshinweis für später:** In Wireshark heißen $Y_s$ und $Y_c$ nicht so —
dort finden Sie beide unter dem Feldnamen **`Pubkey`** (einmal bei den
Server-, einmal bei den Client-Parametern).
                """,
            ),
            explain_box(
                "ein TLS-Handshake?",
                r"""
Bevor zwei Rechner verschlüsselt kommunizieren (z.B. Browser und Webserver
bei "https://"), einigen sie sich in einem **Handshake** auf einen
gemeinsamen Schlüssel — genau das Diffie-Hellman-Verfahren von oben, nur
eingebettet in ein festes Nachrichtenformat. Grob:
`ClientHello` (Client sagt: "ich will reden, das kann ich") →
`ServerHello` (Server antwortet, legt Verfahren fest) →
`ServerKeyExchange` (Server schickt seine öffentlichen DH-Werte $p,g,Y_s$ —
in Wireshark: `p`, `g`, `Pubkey`) →
`ClientKeyExchange` (Client schickt seinen öffentlichen Wert $Y_c$ — in
Wireshark ebenfalls `Pubkey`, diesmal bei den Client-Parametern) →
`Finished` (beide bestätigen verschlüsselt, dass alles geklappt hat) →
danach fließen die eigentlichen Nutzdaten (`Application Data`), ab hier
alles verschlüsselt.
                """,
            ),
            explain_box(
                "eine Cipher Suite / DHE_EXPORT?",
                r"""
Eine **Cipher Suite** ist ein Paket aus Verfahren, auf das sich Client und
Server einigen (z.B. "Schlüsselaustausch per DH, Verschlüsselung per RC4,
Absicherung per MD5"). **DHE_EXPORT** ist eine sehr alte, absichtlich
geschwächte Suite: Sie benutzt Diffie-Hellman, aber mit einer viel zu
kleinen Primzahl $p$ (hier 512 Bit statt heute üblichen 2048+).
                """,
            ),
            explain_box(
                "Wireshark?",
                r"""
**Wireshark** ist ein kostenloses Programm, das den gesamten Netzwerk-
verkehr auf Ihrem Rechner (oder aus einer gespeicherten Datei) sichtbar
macht — Paket für Paket, mit allen Feldern lesbar aufgeschlüsselt. Für
diese Challenge nutzen Sie es, um eine **aufgezeichnete Verbindung**
(`.pcap`-Datei) zu öffnen und darin genau die Werte zu finden, die der
Server im Klartext verschickt hat ($p$, $g$, $Y_s$, …).

Herunterladen: https://www.wireshark.org/download.html — installieren,
öffnen, `Datei → Öffnen` und Ihre `.pcap` auswählen. Mehr braucht es zum
Start nicht.
                """,
            ),
            render_task(self.PAGE_ID, 0, "Schritt 1: Einführung", TaskWidget(task_04b_00)),
            rx.cond(
                PlayerCardState.tasks_solved["day_94_task_00"] | PlayerCardState.enable_test_mode,
                rx.fragment(
                    checkpoint(
                        "**Bevor es losgeht:** Alle Werkzeuge, die Sie brauchen (Wireshark, "
                        "Python 3, `sympy`, **yafu**), stehen fertig eingerichtet in der "
                        "**Kali-Umgebung** dieser Challenge bereit — Button 'Kali' direkt bei "
                        "der jeweiligen Aufgabe, keine eigene Installation nötig. Nur falls die "
                        "Kali-Umgebung bei Ihnen gerade nicht verfügbar ist: Sie können "
                        "Wireshark (https://www.wireshark.org) und `pip install sympy` "
                        "problemlos lokal installieren. **yafu** dagegen gibt es nur für "
                        "Linux/Windows, keinen offiziellen macOS-Build — betrifft Sie das, "
                        "nutzen Sie ersatzweise `sympy.factorint()` (Aufgabe 4 erklärt das "
                        "genauer), liefert hier dasselbe Ergebnis."
                    ),
                    self._capture_panel(),
                    render_task(self.PAGE_ID, 1, "Schritt 2: Wie groß ist p?", TaskWidget(task_04b_01)),
                    rx.cond(
                        PlayerCardState.tasks_solved["day_94_task_01"] | PlayerCardState.enable_test_mode,
                        rx.fragment(
                            explain_box(
                                "der diskrete Logarithmus?",
                                r"""
Sie kennen $g$, $p$ und $Y_s = g^s \bmod p$. Der diskrete Logarithmus ist
die Umkehr-Aufgabe: aus $Y_s$ das geheime $s$ zurückrechnen. Bei einer
großen, gut gewählten Primzahl $p$ ist das praktisch unmöglich — genau
darauf verlässt sich Diffie-Hellman normalerweise.
                                """,
                            ),
                            explain_box(
                                "Pohlig-Hellman?",
                                r"""
Ist $p-1$ ein Produkt aus lauter **kleinen** Primzahlen $q_1, q_2, \dots$
("glatt"), lässt sich der diskrete Logarithmus für **jeden kleinen Faktor
einzeln** lösen (winziges Teilproblem) und die Ergebnisse anschließend mit
dem Chinesischen Restsatz zum vollständigen $s$ zusammensetzen. Genau diese
glatte Struktur hat $p-1$ bei DHE_EXPORT.

**Die Formel dahinter** — für jeden Faktor $q$ von $p-1$ "reduziert" man
$g$ und $Y_s$ auf die kleine Untergruppe der Ordnung $q$:
$$g_i = g^{(p-1)/q} \bmod p, \qquad h_i = Y_s^{(p-1)/q} \bmod p.$$
In dieser kleinen Untergruppe findet man dann leicht $x_i$ mit
$g_i^{x_i} = h_i$ — das ist $s \bmod q$. Genau diese beiden Zeilen füllen
Sie später in Schritt 5 aus.
                                """,
                            ),
                            explain_box(
                                "der Chinesische Restsatz (CRT)?",
                                r"""
Kennen Sie $s \bmod q_1$, $s \bmod q_2$, … für mehrere teilerfremde $q_i$,
legt der CRT eindeutig fest, welchen Wert $s$ insgesamt hat (solange $s$
kleiner ist als das Produkt aller $q_i$). Wir nutzen dafür die fertige
Funktion `sympy.ntheory.modular.crt` — das Zusammensetzen selbst müssen Sie
nicht von Hand programmieren.
                                """,
                            ),
                            render_task(self.PAGE_ID, 2, "Schritt 3: Warum ist das knackbar?", TaskWidget(task_04b_02)),
                            rx.cond(
                                PlayerCardState.tasks_solved["day_94_task_02"] | PlayerCardState.enable_test_mode,
                                rx.fragment(
                                    self._dh_values_panel(),
                                    box(
                                        h("Schritt 4 — p-1 faktorisieren (yafu)", c),
                                        rx.markdown(
                                            r"""
Kein Code hier — nur ein externes Werkzeug. Öffnen Sie ein Terminal (z.B.
über den "Kali"-Button bei der Aufgabe unten):

```bash
python3 -c "p = <IHR_P_VON_OBEN>; print(p - 1)"
yafu "factor(<ERGEBNIS>)"
```

Schreiben Sie sich die gefundenen Primfaktoren auf (ohne die 2, die brauchen
Sie separat) — die brauchen Sie im nächsten Schritt.
                                            """
                                        ),
                                        accent=c,
                                    ),
                                    render_task(self.PAGE_ID, 3, "Schritt 4: p-1 faktorisieren", TaskWidget(task_04b_03)),
                                    rx.cond(
                                        PlayerCardState.tasks_solved["day_94_task_03"] | PlayerCardState.enable_test_mode,
                                        rx.fragment(
                                            box(
                                                h("Schritt 5 — Diskreten Logarithmus finden (Teil 1/3 Ihres Skripts)", c),
                                                rx.markdown(
                                                    r"""
Neue Datei anlegen (z.B. `loesung.py`). Die `None`/leere Liste unten sind
**absichtlich** keine echten Werte:

```python
import math
from sympy.ntheory.modular import crt

p = None    # <- Ihr p (Kasten oben)
g = None    # <- Ihr g (Kasten oben)
Ys = None   # <- Ihr Ys (Kasten oben)

# Ihre Primfaktoren von p-1 aus Schritt 4 (OHNE die 2 - die kommt automatisch dazu):
faktoren = []   # <- z.B. [1009, 3221, 50021] mit IHREN Werten
faktoren = [2] + faktoren

def teilproblem_werte(q):
    # TODO: reduzieren Sie g und Ys auf die Untergruppe der Ordnung q.
    # Formel (siehe "Was ist Pohlig-Hellman?" oben):
    #   gi = g^((p-1)/q) mod p
    #   hi = Ys^((p-1)/q) mod p
    return None, None   # <- (gi, hi)

def bsgs(g, h, p, n):
    # Baby-Step-Giant-Step: findet x mit 0<=x<n und g^x = h (mod p).
    # Fertig vorgegeben - Sie müssen diese Funktion nicht verändern.
    m = math.isqrt(n) + 1
    table = {}
    e = 1
    for j in range(m):
        table[e] = j
        e = (e * g) % p
    faktor = pow(g, -m, p)
    e = h
    for i in range(m):
        if e in table:
            return i * m + table[e]
        e = (e * faktor) % p
    raise ValueError("kein Ergebnis gefunden - stimmen p/g/Ys?")

residuen = []
for q in faktoren:
    gi, hi = teilproblem_werte(q)
    xi = bsgs(gi, hi, p, q)
    residuen.append(xi)

s, _ = crt(faktoren, residuen)
s = int(s)
print("gefunden: s =", s)
print("Kontrolle (muss True sein):", pow(g, s, p) == Ys)
```

`bsgs` müssen Sie nicht verstehen, um die Aufgabe zu lösen — nur, dass es
für jeden Faktor `q` das kleine Teilproblem löst. Die einzige Stelle, die
**Sie** ausfüllen, ist `teilproblem_werte` — das ist genau der Kerngedanke
von Pohlig-Hellman aus Schritt 3.
                                                    """
                                                ),
                                                accent=c,
                                            ),
                                            checkpoint(
                                                "**Selbstkontrolle:** Das Skript druckt bereits "
                                                "`True`/`False` für `pow(g, s, p) == Ys`. Steht "
                                                "dort `False`, ist entweder ein Faktor aus Schritt 4 "
                                                "falsch/fehlt, oder die Formel in `teilproblem_werte` "
                                                "stimmt noch nicht."
                                            ),
                                            render_task(self.PAGE_ID, 4, "Schritt 5: Diskreter Logarithmus", TaskWidget(task_04b_04)),
                                            rx.cond(
                                                PlayerCardState.tasks_solved["day_94_task_04"] | PlayerCardState.enable_test_mode,
                                                rx.fragment(
                                                    explain_box(
                                                        "das TLS Master Secret / pre_master_secret?",
                                                        r"""
Das **pre_master_secret** ist das rohe Diffie-Hellman-Geheimnis
($Z = Y_c^{\,s} \bmod p = Y_s^{\,c} \bmod p$ — beide Seiten berechnen
denselben Wert, ohne dass ein Angreifer $c$ oder $s$ kennt... außer, $s$
lässt sich wie hier zurückrechnen). Aus diesem rohen Geheimnis wird über
eine Hash-Funktion (die **PRF**, "Pseudo-Random Function") das
**master_secret** abgeleitet — ein sauberer, fester 48-Byte-Block, aus dem
später alle eigentlichen Schlüssel kommen.
                                                        """,
                                                    ),
                                                    box(
                                                        h("Wireshark: die restlichen Werte auslesen", c),
                                                        rx.markdown(
                                                            r"""
Öffnen Sie wieder Ihre Capture in Wireshark, Filter `tls.handshake`:

1. **ClientHello** anklicken → aufklappen bis `Random` (32 Byte) →
   Rechtsklick auf das Feld `Random` → `Copy` → `...as a Hex Stream`.
   Das ist Ihr `client_random`.
2. **ServerHello** anklicken → genauso das Feld `Random` kopieren. Das ist
   `server_random`.
3. **Client Key Exchange** anklicken → aufklappen bis
   `Diffie-Hellman Client Params → Pubkey` → Rechtsklick → `Copy` →
   `...as a Hex Stream`. Das ist `Yc` (als Hex-Text, noch keine Zahl) — das
   Feld heißt auch hier `Pubkey`, genau wie bei den Server-Parametern in
   Schritt 2.
                                                            """
                                                        ),
                                                        accent=c,
                                                    ),
                                                    box(
                                                        h("Schritt 6 — Master Secret berechnen (Teil 2/3, direkt anhängen)", c),
                                                        rx.markdown(
                                                            r"""
```python
import hmac, hashlib

def p_hash(digestmod, secret, seed, length):
    # Fertig vorgegeben.
    out = b""
    a = seed
    while len(out) < length:
        a = hmac.new(secret, a, digestmod).digest()
        out += hmac.new(secret, a + seed, digestmod).digest()
    return out[:length]

def tls10_prf(secret, label, seed, length):
    # Fertig vorgegeben - die TLS-1.0-PRF aus RFC 2246.
    half = (len(secret) + 1) // 2
    s1, s2 = secret[:half], secret[-half:]
    p_md5 = p_hash(hashlib.md5, s1, label + seed, length)
    p_sha1 = p_hash(hashlib.sha1, s2, label + seed, length)
    return bytes(a ^ b for a, b in zip(p_md5, p_sha1))

# Aus Wireshark (siehe Anleitung oben) - als Hex-Text in Anführungszeichen:
client_random = bytes.fromhex("HIER_HEX_EINFUEGEN")
server_random = bytes.fromhex("HIER_HEX_EINFUEGEN")
Yc = int("HIER_HEX_EINFUEGEN", 16)

# TODO: Z = Yc^s mod p - dasselbe DH-Prinzip wie immer, diesmal mit
# Ihrem in Schritt 5 gefundenen s als Exponent.
Z = None

pms = Z.to_bytes((Z.bit_length() + 7) // 8, "big")
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
                                                    render_task(self.PAGE_ID, 5, "Schritt 6: TLS Master Secret", TaskWidget(task_04b_05)),
                                                    rx.cond(
                                                        PlayerCardState.tasks_solved["day_94_task_05"] | PlayerCardState.enable_test_mode,
                                                        rx.fragment(
                                                            box(
                                                                h("Wireshark: die verschlüsselten Datensätze kopieren", c),
                                                                rx.markdown(
                                                                    r"""
Weiter im Filter `tls.handshake or tls.app_data`: Suchen Sie das **eine**
Paket vom Server, dessen Info-Spalte mit **"Change Cipher Spec"** beginnt
(meist steht dort in einer Zeile gleich noch mehr, z.B. "..., Encrypted
Handshake Message, Application Data" — das ist alles **ein einziges
Paket**, keine drei verschiedenen). Anklicken und im Detail-Baum aufklappen
— Sie sehen dort **drei separate** `TLSv1 Record Layer`-Einträge
untereinander:

1. `TLSv1 Record Layer: Change Cipher Spec` — **ignorieren**, nichts zu tun.
2. `TLSv1 Record Layer: Handshake Protocol: Encrypted Handshake Message` →
   aufklappen bis zum Feld `Encrypted Handshake Message` → Rechtsklick →
   `Copy` → `...as a Hex Stream`. Das ist `finished_ciphertext`.
3. `TLSv1 Record Layer: Application Data` → Feld `Encrypted Application
   Data` → genauso kopieren. Das ist `application_data_ciphertext` — hier
   steckt die Flagge.
                                                                    """
                                                                ),
                                                                accent=c,
                                                            ),
                                                            box(
                                                                h("Schritt 7 — Flagge entschlüsseln (Teil 3/3, direkt anhängen)", c),
                                                                rx.markdown(
                                                                    r"""
Hier gibt es **keine Lücke mehr** — nur noch fertigen Code, der alles
zusammenführt. Lesen Sie ihn trotzden einmal durch, bevor Sie ihn ausführen:

```python
key_block = tls10_prf(master_secret, b"key expansion", server_random + client_random, 42)
server_mac_secret = key_block[16:32]
server_write_key_raw = key_block[37:42]

def final_write_key(write_key_raw, label):
    return tls10_prf(write_key_raw, label, client_random + server_random, 16)

server_write_key = final_write_key(server_write_key_raw, b"server write key")

class RC4:
    # Fertig vorgegeben - der RC4-Stream-Cipher-Algorithmus.
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
    # Fertig vorgegeben - prueft die HMAC-MD5-Pruefsumme und entschluesselt.
    decrypted = rc4.crypt(ciphertext)
    plaintext, mac = decrypted[:-16], decrypted[-16:]
    mac_input = (seq_num.to_bytes(8, "big") + bytes([content_type]) +
                 b"\x03\x01" + len(plaintext).to_bytes(2, "big") + plaintext)
    ok = mac == hmac.new(mac_secret, mac_input, hashlib.md5).digest()
    return plaintext, ok

# Aus Wireshark (siehe Anleitung oben) - als Hex-Text in Anführungszeichen:
finished_ciphertext = bytes.fromhex("HIER_HEX_EINFUEGEN")
application_data_ciphertext = bytes.fromhex("HIER_HEX_EINFUEGEN")

rc4 = RC4(server_write_key)
_, ok1 = mac_then_decrypt(22, finished_ciphertext, server_mac_secret, rc4, 0)
flag_bytes, ok2 = mac_then_decrypt(23, application_data_ciphertext, server_mac_secret, rc4, 1)
print("MAC-Prüfung ok:", ok1, ok2)
print("Flagge:", flag_bytes.decode())
```

**Wichtig:** `rc4 = RC4(...)` nur EINMAL erzeugen und danach beide
`mac_then_decrypt`-Aufrufe in genau dieser Reihenfolge damit ausführen — RC4
ist ein fortlaufender Strom, kein Aufruf pro Datensatz für sich.
                                                                    """
                                                                ),
                                                                accent=c,
                                                            ),
                                                            checkpoint(
                                                                "**Bekommen Sie `MAC-Prüfung ok: False False`?** Dann "
                                                                "stimmt vermutlich `server_write_key` nicht — meist, "
                                                                "weil `s` (Schritt 5) oder `Z`/`master_secret` "
                                                                "(Schritt 6) noch falsch war. Prüfen Sie dort zuerst."
                                                            ),
                                                            render_task(self.PAGE_ID, 6, "Schritt 8: Flagge einreichen", TaskWidget(task_04b_06)),
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
                ),
            ),
            rx.cond(
                PlayerCardState.tasks_solved["day_94_task_06"] | PlayerCardState.enable_test_mode,
                success_box(
                    "**Geschafft!** Sie haben einen echten TLS-Handshake gebrochen — von "
                    "Wireshark über Pohlig-Hellman bis zur fertig entschlüsselten Nachricht. "
                    "Genau dieser Angriff (Logjam) betraf 2015 einen erheblichen Teil aller "
                    "HTTPS-Server weltweit.",
                    c,
                ),
            ),
            spacing="4", width="100%", align_items="stretch",
        )

    def page(self) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.heading("Kapitel 4: Schwaches Diffie-Hellman — Beginner Walkthrough", color=self.main_color, size="8",
                           style={"background": "linear-gradient(90deg, #04B486, #00FFFF)",
                                  "WebkitBackgroundClip": "text",
                                  "WebkitTextFillColor": "transparent"}),
                rx.text("🔑", size="8", align_self="center"),
                align_items="center", width="100%", spacing="2",
                style={"marginBottom": "24px"},
            ),
            rx.cond(
                CondState.is_ready & PlayerCardState.update_day_ready[94],
                rx.cond(
                    CondState.event_enabled,
                    self._content(),
                    rx.vstack(rx.text(
                        "Bitte warten Sie, bis der Spielleiter das Event startet!")),
                ),
                rx.vstack(rx.spinner()),
            ),
            on_mount=lambda: AccordionState.init(self.PAGE_ID, 7),
        )

    def configure(self) -> None:
        self.url = "/challenge_04_beginner"
        self.name = "04b: Schwaches DH (Beginner Walkthrough)"
        self.icon = "key-round"
        self.main_color = "#04B486"
        self.on_load = [
            CondState.reset_check_status,
            CondState.do_checks,
            CondState.do_check_cyberrange,
            PlayerCardState.update_day(94),
            BeginnerDhVariantState.load,
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always
