"""
Theory building blocks for Kapitel 02.

Each function returns an rx.Component. Content is in German (student-facing),
anonymized (no personal names), and anchored on standard cryptographic
definitions and the course curriculum.
"""

import reflex as rx


def _box(*children, accent: str = "#04B486") -> rx.Component:
    return rx.box(
        rx.vstack(*children, spacing="3", align_items="start"),
        style={
            "maxWidth": "1200px", "width": "100%", "margin": "20px auto",
            "padding": "25px", "borderRadius": "16px",
            "background": ("linear-gradient(135deg, "
                          "rgba(180, 210, 255, 0.14) 0%, "
                          "rgba(160, 190, 255, 0.07) 100%)"),
            "border": "1px solid rgba(255, 255, 255, 0.16)",
            "boxSizing": "border-box", "borderLeft": f"4px solid {accent}",
        },
    )


def _h(text: str, color: str) -> rx.Component:
    return rx.text(rx.text.strong(text),
                   font_family="IBM Plex Mono, monospace",
                   font_size="1.4em", color=color)


def _svg(markup: str) -> rx.Component:
    return rx.html(markup, style={"width": "100%", "maxWidth": "760px",
                                  "margin": "8px auto", "display": "block"})


# ---------------------------------------------------------------------------
# Groups, order, generators
# ---------------------------------------------------------------------------
def groups(color: str) -> rx.Component:
    return _box(
        _h("Das Fundament: Gruppen, Ordnung, Erzeuger", color),
        rx.markdown(
            r"""
Diffie-Hellman lebt in der multiplikativen Gruppe $\mathbb{Z}_p^* = \{1, 2,
\dots, p-1\}$ einer Primzahl $p$. Drei Begriffe brauchen Sie:

**Gruppenordnung.** Die Anzahl der Elemente heißt Ordnung der Gruppe,
$\mathrm{ord}(G)$. Für eine Primzahl $p$ gilt $\mathrm{ord}(\mathbb{Z}_p^*) =
\varphi(p) = p-1$.

**Ordnung eines Elements.** Die kleinste Zahl $t$ mit $g^t \equiv 1 \pmod p$.
Nach dem **Satz von Lagrange** teilt sie stets die Gruppenordnung:
$t \mid \mathrm{ord}(G)$.

**Erzeuger (Generator).** Ein $g$ mit maximaler Ordnung $p-1$ erzeugt die ganze
Gruppe — jede Zahl in $\mathbb{Z}_p^*$ ist eine Potenz von $g$. Wichtig: $g$ darf
**nicht willkürlich** gewählt werden, es sollte maximale Ordnung haben.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# The discrete logarithm problem
# ---------------------------------------------------------------------------
def dlp(color: str) -> rx.Component:
    return _box(
        _h("Das diskrete Logarithmusproblem (DLP)", color),
        rx.markdown(
            r"""
Der Kern der Sicherheit von DH ist eine **Einweg-Funktion**: leicht vorwärts,
schwer rückwärts.

Gegeben eine Basis $a$, eine Zahl $n$ und $f_a(x) = a^x \bmod n = y$. Die
**modulare Exponentiation** $y = a^x \bmod n$ ist effizient berechenbar. Die
Umkehrung — zu gegebenem $y$ das $x$ finden — ist das

$$x \equiv \log_a y \pmod n \quad\text{(diskretes Logarithmusproblem).}$$

Für große, gut gewählte Parameter kennt man kein effizientes Verfahren dafür.
Diese Asymmetrie macht DH sicher — solange die Parameter stimmen.
            """
        ),
        accent=color,
    )


_DH_HANDSHAKE_SVG = r"""
<svg width="100%" viewBox="0 0 680 360" xmlns="http://www.w3.org/2000/svg" role="img">
<title>Diffie-Hellman-Handshake</title>
<desc>Anna und Bob tauschen oeffentliche Werte und berechnen dasselbe gemeinsame Geheimnis.</desc>
<defs>
<marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</marker>
</defs>
<rect x="60" y="30" width="150" height="40" rx="8" fill="#1D9E75" fill-opacity="0.18" stroke="#0F6E56" stroke-width="1"/>
<text x="135" y="55" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#0F6E56" font-weight="500">Anna (A)</text>
<rect x="470" y="30" width="150" height="40" rx="8" fill="#185FA5" fill-opacity="0.18" stroke="#0C447C" stroke-width="1"/>
<text x="545" y="55" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#185FA5" font-weight="500">Bob (B)</text>
<line x1="135" y1="70" x2="135" y2="330" stroke="#888780" stroke-width="1"/>
<line x1="545" y1="70" x2="545" y2="330" stroke="#888780" stroke-width="1"/>
<text x="135" y="100" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#5F5E5A">wählt geheim a</text>
<text x="545" y="100" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#5F5E5A">wählt geheim b</text>
<line x1="140" y1="130" x2="540" y2="130" stroke="#5F5E5A" stroke-width="1" marker-end="url(#ar)"/>
<text x="340" y="123" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#444441">öffentlich: p, g</text>
<text x="135" y="170" text-anchor="middle" font-family="monospace" font-size="13" fill="#0F6E56">A = g^a mod p</text>
<text x="545" y="170" text-anchor="middle" font-family="monospace" font-size="13" fill="#185FA5">B = g^b mod p</text>
<line x1="140" y1="195" x2="540" y2="195" stroke="#5F5E5A" stroke-width="1" marker-end="url(#ar)"/>
<text x="340" y="188" text-anchor="middle" font-family="monospace" font-size="12" fill="#444441">A</text>
<line x1="540" y1="220" x2="140" y2="220" stroke="#5F5E5A" stroke-width="1" marker-end="url(#ar)"/>
<text x="340" y="238" text-anchor="middle" font-family="monospace" font-size="12" fill="#444441">B</text>
<rect x="285" y="255" width="110" height="34" rx="17" fill="#888780" fill-opacity="0.12" stroke="#888780" stroke-width="1" stroke-dasharray="4 3"/>
<text x="340" y="277" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5F5E5A">unsicheres Medium</text>
<text x="135" y="315" text-anchor="middle" font-family="monospace" font-size="13" fill="#0F6E56">s = B^a mod p</text>
<text x="545" y="315" text-anchor="middle" font-family="monospace" font-size="13" fill="#185FA5">s = A^b mod p</text>
<text x="340" y="345" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#04B486" font-weight="500">gemeinsames Geheimnis s = g^(ab) mod p</text>
</svg>
"""


def handshake(color: str) -> rx.Component:
    return _box(
        _h("Der Diffie-Hellman-Handshake", color),
        rx.markdown(
            r"""
Anna und Bob einigen sich öffentlich auf $p$ und $g$, wählen je ein Geheimnis,
tauschen die öffentlichen Werte $A$ und $B$ und berechnen beide **denselben**
Schlüssel:
            """
        ),
        _svg(_DH_HANDSHAKE_SVG),
        rx.markdown(
            r"""
Der Trick: $s = B^a = (g^b)^a = g^{ab} = (g^a)^b = A^b \pmod p$. Beide landen
beim selben $s$, ohne es je zu übertragen.

**Der Angreifer** sieht nur $p, g, A, B$. Um an $s$ zu kommen, müsste er aus
$A = g^a \bmod p$ das geheime $a$ berechnen — also das DLP lösen. Genau hier
setzen Ihre Angriffe an.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 1 technical part
# ---------------------------------------------------------------------------
def challenge_1_technik(color: str) -> rx.Component:
    return _box(
        _h("Der Angriff: kleines p", color),
        rx.markdown(
            r"""
Hier ist $p$ klein (ca. 39 Bit) — so klein, dass sich der diskrete Logarithmus
durch **Ausprobieren** knacken lässt.

**Ihr Weg:**
1. Laden Sie Ihre Capture herunter, lesen Sie $p, g, A, B$ aus.
2. Finden Sie $a$ mit $g^a \equiv A \pmod p$ (Brute-Force oder Baby-Step-Giant-Step).
3. Berechnen Sie das gemeinsame Geheimnis $s = B^a \bmod p$.
4. Leiten Sie den Schlüssel ab (HKDF-SHA256, in der Capture beschrieben) und
   entschlüsseln Sie den AES-256-GCM-Datensatz. Die Flagge steht im Klartext.

**Baby-Step-Giant-Step** schafft das in $\sqrt{p}$ statt $p$ Schritten: man
schreibt $a = i\cdot m + j$ mit $m \approx \sqrt{p}$, tabelliert die Baby Steps
$g^j$ und sucht per Giant Steps eine Kollision. Bei diesem kleinen $p$ reicht
aber schon pures Durchprobieren.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 2: smooth order + Pohlig-Hellman
# ---------------------------------------------------------------------------
_PH_PROJECTION_SVG = r"""
<svg width="100%" viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg" role="img">
<title>Pohlig-Hellman: Zerlegung des DLP in prime Untergruppen</title>
<desc>Das grosse DLP wird in kleine Teilprobleme je Primfaktor zerlegt und per CRT zusammengesetzt.</desc>
<defs>
<marker id="ar2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</marker>
</defs>
<rect x="220" y="24" width="240" height="46" rx="8" fill="#993C1D" fill-opacity="0.15" stroke="#993C1D" stroke-width="1"/>
<text x="340" y="44" text-anchor="middle" font-family="monospace" font-size="13" fill="#993C1D" font-weight="500">DLP: A = g^a mod p</text>
<text x="340" y="61" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#712B13">ord(G) = p-1 = 2·q1·q2·q3</text>
<line x1="270" y1="70" x2="130" y2="110" stroke="#5F5E5A" stroke-width="1" marker-end="url(#ar2)"/>
<line x1="340" y1="70" x2="340" y2="110" stroke="#5F5E5A" stroke-width="1" marker-end="url(#ar2)"/>
<line x1="410" y1="70" x2="550" y2="110" stroke="#5F5E5A" stroke-width="1" marker-end="url(#ar2)"/>
<rect x="55" y="112" width="150" height="60" rx="8" fill="#1D9E75" fill-opacity="0.15" stroke="#0F6E56" stroke-width="1"/>
<text x="130" y="134" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#0F6E56" font-weight="500">Untergruppe q1</text>
<text x="130" y="153" text-anchor="middle" font-family="monospace" font-size="11" fill="#0F6E56">a mod q1</text>
<rect x="265" y="112" width="150" height="60" rx="8" fill="#1D9E75" fill-opacity="0.15" stroke="#0F6E56" stroke-width="1"/>
<text x="340" y="134" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#0F6E56" font-weight="500">Untergruppe q2</text>
<text x="340" y="153" text-anchor="middle" font-family="monospace" font-size="11" fill="#0F6E56">a mod q2</text>
<rect x="475" y="112" width="150" height="60" rx="8" fill="#1D9E75" fill-opacity="0.15" stroke="#0F6E56" stroke-width="1"/>
<text x="550" y="134" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#0F6E56" font-weight="500">Untergruppe q3</text>
<text x="550" y="153" text-anchor="middle" font-family="monospace" font-size="11" fill="#0F6E56">a mod q3</text>
<text x="130" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5F5E5A">BSGS (klein)</text>
<text x="340" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5F5E5A">BSGS (klein)</text>
<text x="550" y="192" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5F5E5A">BSGS (klein)</text>
<line x1="130" y1="200" x2="300" y2="232" stroke="#5F5E5A" stroke-width="1" marker-end="url(#ar2)"/>
<line x1="340" y1="200" x2="340" y2="232" stroke="#5F5E5A" stroke-width="1" marker-end="url(#ar2)"/>
<line x1="550" y1="200" x2="380" y2="232" stroke="#5F5E5A" stroke-width="1" marker-end="url(#ar2)"/>
<rect x="240" y="234" width="200" height="46" rx="8" fill="#534AB7" fill-opacity="0.15" stroke="#3C3489" stroke-width="1"/>
<text x="340" y="254" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#3C3489" font-weight="500">CRT</text>
<text x="340" y="271" text-anchor="middle" font-family="monospace" font-size="11" fill="#26215C">a mod (p-1)</text>
</svg>
"""


def challenge_2_intro(color: str) -> rx.Component:
    return _box(
        _h("Glatte Ordnung: das Prinzip", color),
        rx.markdown(
            r"""
Jetzt ist $p$ groß (ca. 120 Bit). Brute-Force ist aussichtslos, BSGS über die
ganze Gruppe ebenso. Und **trotzdem** ist diese Variante angreifbar — wegen der
Struktur von $p-1$.

**Glatte Ordnung.** Zerfällt $p-1 = 2 \cdot q_1 \cdot q_2 \cdot q_3$ in lauter
kleine Primfaktoren, heißt die Gruppenordnung *glatt* (smooth). Statt das DLP im
Ganzen zu lösen, zerlegen Sie es in kleine Teilprobleme — eines pro Primfaktor —
und setzen die Ergebnisse per **Chinesischem Restsatz** zusammen. Das ist
**Pohlig-Hellman**.
            """
        ),
        _svg(_PH_PROJECTION_SVG),
        accent=color,
    )


def challenge_2_pohlig_hellman(color: str) -> rx.Component:
    return _box(
        _h("Pohlig-Hellman Schritt für Schritt", color),
        rx.markdown(
            r"""
Ein durchgerechnetes Beispiel. Gegeben:

$$G = \mathbb{Z}_{967}^*,\quad \mathrm{ord}(G) = \varphi(967) = 966 = 2\cdot 3\cdot 7\cdot 23,\quad g = 5.$$

Gesucht ist $a$ im DLP $A = 640 \equiv 5^a \pmod{967}$.

**Schritt 1 — Projektion.** Für jeden Primfaktor $q$ bilden wir mit dem
**Kofaktor** $h = \mathrm{ord}(G)/q$ in die Untergruppe der Ordnung $q$ ab:
$g_q = g^{h} \bmod p$ und $A_q = A^{h} \bmod p$.

**Schritt 2 — kleine DLP lösen.** In jeder Untergruppe ist das Problem winzig:

- $q=2$: liefert $a \equiv 1 \pmod 2$
- $q=3$: liefert $a \equiv 0 \pmod 3$
- $q=7$: liefert $a \equiv 1 \pmod 7$
- $q=23$: erschöpfende Suche liefert $a \equiv 20 \pmod{23}$

**Schritt 3 — CRT.** Das Kongruenzsystem

$$a\equiv 1\!\!\pmod 2,\ a\equiv 0\!\!\pmod 3,\ a\equiv 1\!\!\pmod 7,\ a\equiv 20\!\!\pmod{23}$$

hat per Chinesischem Restsatz eine eindeutige Lösung $a \bmod 966$. Fertig.

> **Merke:** Die Komplexität des Angriffs hängt hauptsächlich vom **größten
> primen Untergruppenfaktor** ab. Deshalb muss die Gruppenordnung einen
> *größtmöglichen* Primteiler besitzen — und die Kenntnis der Faktorisierung
> von $\varphi(p)$ ist essentiell.

In Ihrer Challenge ist $p$ größer, aber das Prinzip ist identisch: erst $p-1$
mit **yafu** faktorisieren, dann Pohlig-Hellman + CRT.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 3: almost smooth (the trap)
# ---------------------------------------------------------------------------
def challenge_3_technik(color: str) -> rx.Component:
    return _box(
        _h("Die Falle: fast glatt", color),
        rx.markdown(
            r"""
Diese Variante sieht **sicher aus**: $p$ ist noch größer (ca. 176 Bit). Ein
flüchtiger Blick sagt: unknackbar. Doch schauen Sie genau auf $p-1$.

**Fast glatt.** Diesmal gilt

$$p-1 = 2 \cdot q_1 \cdot q_2 \cdot q_3 \cdot Q,$$

wobei die $q_i$ klein und glatt sind — aber $Q$ ein **großer Primfaktor** ist,
den Sie mit yafu **nicht** faktorisieren können.

**Die Lösung: ignorieren Sie $Q$.** Wenden Sie Pohlig-Hellman nur auf den
glatten Teil $M = 2 \cdot q_1 \cdot q_2 \cdot q_3$ an. Das liefert Ihnen
$a \bmod M$ — nicht $a$ selbst.

**Warum genügt das?** Weil der geheime Exponent $a$ hier *kleiner als $M$*
gewählt wurde. Dann gilt schlicht $a \bmod M = a$ — Sie haben $a$ vollständig,
ohne $Q$ je berührt zu haben.

> Die Lehre: **die Größe von $p$ war ein Ablenkungsmanöver.** Angreifbar ist
> nicht, was groß ist, sondern was *strukturell schwach* ist. Genau deshalb
> verwendet man in der Praxis **Safe Primes** — dort ist sichergestellt, dass
> $\varphi(p)$ einen größtmöglichen Primteiler besitzt.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 4: weak generator / small subgroup
# ---------------------------------------------------------------------------
def challenge_4_technik(color: str) -> rx.Component:
    return _box(
        _h("Der schwache Erzeuger: Small-Subgroup", color),
        rx.markdown(
            r"""
Bisher lag die Schwäche in der **Primzahl** $p$. Diesmal ist $p$ tadellos groß —
die Schwäche liegt im **Erzeuger** $g$.

**Die Ordnung von $g$.** Erinnern Sie sich: nach dem Satz von Lagrange teilt die
Ordnung eines Elements stets $\mathrm{ord}(G) = p-1$. Ein *guter* Erzeuger hat
maximale Ordnung $p-1$. Wählt man $g$ aber schlecht, kann seine Ordnung ein
**winziger** Teiler $q$ von $p-1$ sein.

Konkret: hier ist $p-1 = 2 \cdot q \cdot R$ mit einem **kleinen** $q$ und einem
großen, nicht faktorisierbaren $R$. Der Erzeuger $g$ hat die kleine Ordnung $q$.

**Die Folge.** Alle öffentlichen Werte $A = g^a$ leben dann in einer winzigen
Untergruppe mit nur $q$ Elementen. Der geheime Exponent $a$ ist nur noch
**modulo $q$** relevant — und $q$ ist so klein, dass Sie $a \bmod q$ mit
Baby-Step-Giant-Step in Sekundenbruchteilen finden.

**Ihr Weg:**
1. Bestimmen Sie die (kleine) Ordnung $q$ von $g$: der kleinste Teiler von $p-1$
   mit $g^q \equiv 1 \pmod p$.
2. Lösen Sie $g^a \equiv A \pmod p$ per BSGS in der Untergruppe der Ordnung $q$.
3. Da $a < q$ gewählt wurde, ist das bereits das vollständige $a$.
4. Entschlüsseln Sie wie gewohnt.

> Die Lehre: Nicht nur $p$, auch $g$ muss korrekt gewählt werden. Ein Erzeuger
> mit kleiner Ordnung sperrt das gesamte Geheimnis in einen winzigen Käfig.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 5: Logjam / export-grade
# ---------------------------------------------------------------------------
def challenge_5_technik(color: str) -> rx.Component:
    return _box(
        _h("Logjam: die absichtlich schwache Gruppe", color),
        rx.markdown(
            r"""
Dieser Angriff hat einen realen Hintergrund — und schließt den Bogen zum
**FREAK**-Angriff aus Kapitel 01.

**Export-Kryptographie.** In den 1990ern beschränkten Exportgesetze die Stärke
von Kryptographie. Systeme wurden mit absichtlich **schwachen** Parametern
ausgeliefert — bei RSA zu kleine Module (das war FREAK), bei Diffie-Hellman zu
kleine, standardisierte Gruppen. Der reale **Logjam**-Angriff (2015) nutzte
genau solche schwachen DH-Gruppen aus.

**Das Prinzip.** Die hier verwendete Primzahl ist eine solche „export-grade"-
Gruppe: klein genug, dass der diskrete Logarithmus machbar ist. Da $p-1$ zudem
eine glatte Struktur hat, wenden Sie **Pohlig-Hellman** an — dieselbe Technik
wie in Challenge 2.

**Der eigentliche Clou von Logjam.** In der Realität wird dieselbe schwache
Gruppe von **tausenden** Servern geteilt. Ein Angreifer investiert einmalig eine
teure Vorberechnung für diese eine Gruppe — und kann danach **jede** Sitzung, die
sie nutzt, quasi in Echtzeit brechen. Die gemeinsame Nutzung schwacher Standards
ist die eigentliche Katastrophe.

**Ihr Weg:** Faktorisieren Sie $p-1$ (yafu), lösen Sie per Pohlig-Hellman + CRT,
entschlüsseln Sie. Sie kennen die Technik bereits — hier zählt das *Verständnis*
der realen Schwachstelle.

> Die Lehre: Schwache, geteilte Standard-Parameter sind eine Hintertür mit
> Ansage. Die Gegenmaßnahme: ausreichend große, moderne Gruppen (RFC 3526) oder
> frische Parameter pro Verbindung.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 6 technical part — Man-in-the-Middle
# ---------------------------------------------------------------------------
_MITM_SVG = r"""
<svg width="100%" viewBox="0 0 680 400" xmlns="http://www.w3.org/2000/svg" role="img">
<title>Man-in-the-Middle-Angriff auf Diffie-Hellman</title>
<desc>Mallory sitzt zwischen Anna und Bob und fuehrt zwei getrennte Handshakes.</desc>
<defs>
<marker id="arm" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</marker>
</defs>
<rect x="30" y="30" width="130" height="40" rx="8" fill="#1D9E75" fill-opacity="0.18" stroke="#0F6E56" stroke-width="1"/>
<text x="95" y="55" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#0F6E56" font-weight="500">Anna (A)</text>
<rect x="275" y="30" width="130" height="40" rx="8" fill="#B23A3A" fill-opacity="0.18" stroke="#8C2A2A" stroke-width="1"/>
<text x="340" y="55" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#B23A3A" font-weight="600">Mallory (Sie)</text>
<rect x="520" y="30" width="130" height="40" rx="8" fill="#185FA5" fill-opacity="0.18" stroke="#0C447C" stroke-width="1"/>
<text x="585" y="55" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#185FA5" font-weight="500">Bob (B)</text>
<line x1="95" y1="70" x2="95" y2="380" stroke="#888780" stroke-width="1"/>
<line x1="340" y1="70" x2="340" y2="380" stroke="#B23A3A" stroke-width="1.2"/>
<line x1="585" y1="70" x2="585" y2="380" stroke="#888780" stroke-width="1"/>
<text x="95" y="98" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5F5E5A">wählt geheim a</text>
<text x="340" y="98" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#8C2A2A">wählt m1, m2</text>
<text x="585" y="98" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5F5E5A">wählt geheim b</text>
<line x1="100" y1="130" x2="335" y2="130" stroke="#0F6E56" stroke-width="1" marker-end="url(#arm)"/>
<text x="217" y="123" text-anchor="middle" font-family="monospace" font-size="12" fill="#0F6E56">A = g^a</text>
<line x1="335" y1="160" x2="100" y2="160" stroke="#B23A3A" stroke-width="1.3" marker-end="url(#arm)"/>
<text x="217" y="176" text-anchor="middle" font-family="monospace" font-size="12" fill="#B23A3A">M1 = g^m1  (statt B!)</text>
<line x1="345" y1="130" x2="580" y2="130" stroke="#B23A3A" stroke-width="1.3" marker-end="url(#arm)"/>
<text x="462" y="123" text-anchor="middle" font-family="monospace" font-size="12" fill="#B23A3A">M2 = g^m2  (statt A!)</text>
<line x1="580" y1="160" x2="345" y2="160" stroke="#185FA5" stroke-width="1" marker-end="url(#arm)"/>
<text x="462" y="176" text-anchor="middle" font-family="monospace" font-size="12" fill="#185FA5">B = g^b</text>
<rect x="40" y="210" width="150" height="60" rx="8" fill="#1D9E75" fill-opacity="0.10" stroke="#0F6E56" stroke-width="1" stroke-dasharray="4 3"/>
<text x="115" y="233" text-anchor="middle" font-family="monospace" font-size="11" fill="#0F6E56">Anna denkt:</text>
<text x="115" y="252" text-anchor="middle" font-family="monospace" font-size="12" fill="#0F6E56">s = M1^a = g^(m1·a)</text>
<rect x="265" y="210" width="150" height="60" rx="8" fill="#B23A3A" fill-opacity="0.12" stroke="#8C2A2A" stroke-width="1"/>
<text x="340" y="230" text-anchor="middle" font-family="monospace" font-size="11" fill="#8C2A2A">Mallory kennt beide:</text>
<text x="340" y="248" text-anchor="middle" font-family="monospace" font-size="11" fill="#8C2A2A">s1 = A^m1</text>
<text x="340" y="263" text-anchor="middle" font-family="monospace" font-size="11" fill="#8C2A2A">s2 = B^m2</text>
<rect x="490" y="210" width="150" height="60" rx="8" fill="#185FA5" fill-opacity="0.10" stroke="#0C447C" stroke-width="1" stroke-dasharray="4 3"/>
<text x="565" y="233" text-anchor="middle" font-family="monospace" font-size="11" fill="#185FA5">Bob denkt:</text>
<text x="565" y="252" text-anchor="middle" font-family="monospace" font-size="12" fill="#185FA5">s = M2^b = g^(m2·b)</text>
<text x="340" y="315" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#8C2A2A" font-weight="500">Zwei getrennte Schlüssel — Mallory entschlüsselt und liest alles.</text>
<text x="340" y="350" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#444441">Anna und Bob teilen NIE denselben Schlüssel: s1 ≠ s2.</text>
<text x="340" y="372" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5F5E5A">Der diskrete Logarithmus wird nie gebrochen — er muss es auch nicht.</text>
</svg>
"""


def challenge_6_technik(color: str) -> rx.Component:
    return _box(
        _h("Man-in-the-Middle: der aktive Angriff", color),
        rx.markdown(
            r"""
Alle bisherigen Angriffe waren **passiv**: Sie haben mitgehört und im
Nachhinein den diskreten Logarithmus gebrochen. Diesmal ist alles anders —
und in gewisser Weise viel einfacher.

**Warum Sie nichts brechen müssen.** Die Parameter sind hier bewusst
**perfekt**: $p$ ist eine sichere Primzahl (safe prime, $p = 2q+1$ mit
primem $q$), $g$ hat große Ordnung. Der diskrete Logarithmus ist praktisch
unlösbar. Trotzdem lesen Sie jede Nachricht — weil Sie **aktiv** in die
Verbindung eingreifen.
            """
        ),
        _svg(_MITM_SVG),
        rx.markdown(
            r"""
**Das Prinzip.** Sie sitzen als *Mallory* zwischen Anna und Bob. Sie fangen
Annas öffentlichen Wert $A$ ab und schicken Bob stattdessen Ihren eigenen
Wert $M_2 = g^{m_2}$. Bobs Wert $B$ fangen Sie ebenso ab und schicken Anna
$M_1 = g^{m_1}$. Ergebnis: Sie führen **zwei getrennte Handshakes**.

- Mit **Anna** teilen Sie den Schlüssel $s_1 = A^{m_1} = M_1^{\,a} \bmod p$.
- Mit **Bob** teilen Sie den Schlüssel $s_2 = B^{m_2} = M_2^{\,b} \bmod p$.

Anna und Bob glauben, ein gemeinsames Geheimnis zu haben — in Wahrheit reden
beide nur mit Ihnen. Sie entschlüsseln eine Richtung, lesen (oder verändern!)
den Klartext, verschlüsseln neu mit dem anderen Schlüssel und leiten weiter.
Niemand merkt etwas.

**Der Nachweis (Detektion).** Woran erkennt man den Angriff überhaupt? Der
Schlüssel, den Anna für „Bobs Schlüssel" hält, ist $M_1$ — **nicht** Bobs
echter Wert $B$. Wer $M_1$ und $B$ vergleichen kann, sieht sofort: *sie
stimmen nicht überein.* Genau das ist die Signatur eines MITM.

**Ihr Weg:** In Ihrer Capture stehen (nur für diese Übung) Mallorys
Geheimnisse $m_1, m_2$. Berechnen Sie $s_1 = A^{m_1}$ und $s_2 = B^{m_2}$,
leiten Sie **zwei** Schlüssel ab und entschlüsseln Sie **beide** Datensätze —
Anna→Bob und Bob→Anna. Jede Richtung trägt eine **Hälfte** der Flagge.

> Die Lehre: Diffie-Hellman schützt die Vertraulichkeit, aber **nicht die
> Authentizität**. Ohne einen Nachweis, *wer* am anderen Ende sitzt (Signaturen,
> Zertifikate), ist selbst perfekte Mathematik wertlos. Deshalb signiert TLS die
> DH-Werte — genau um diesen Angriff zu verhindern.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 7 technical part — ECDH intro (elliptic curves)
# ---------------------------------------------------------------------------
_EC_ADDITION_SVG = r"""
<svg width="100%" viewBox="0 0 680 380" xmlns="http://www.w3.org/2000/svg" role="img">
<title>Punktaddition auf einer elliptischen Kurve</title>
<desc>Die Gerade durch P und Q schneidet die Kurve in einem dritten Punkt; gespiegelt ergibt das P+Q.</desc>
<path d="M60 300 Q 120 60 240 150 Q 340 225 340 190 Q 340 40 600 70"
      fill="none" stroke="#0F6E56" stroke-width="2.5"/>
<line x1="40" y1="190" x2="640" y2="190" stroke="#888780" stroke-width="1" stroke-dasharray="3 3"/>
<line x1="120" y1="118" x2="560" y2="286" stroke="#B23A3A" stroke-width="1.5"/>
<circle cx="150" cy="130" r="5" fill="#185FA5"/>
<text x="150" y="118" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#185FA5" font-weight="600">P</text>
<circle cx="300" cy="187" r="5" fill="#185FA5"/>
<text x="300" y="175" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#185FA5" font-weight="600">Q</text>
<circle cx="470" cy="245" r="5" fill="#7A6A20"/>
<text x="492" y="249" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#7A6A20">R (Schnitt)</text>
<line x1="470" y1="245" x2="470" y2="135" stroke="#7A6A20" stroke-width="1" stroke-dasharray="4 3"/>
<circle cx="470" cy="135" r="6" fill="#B23A3A"/>
<text x="470" y="123" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#B23A3A" font-weight="700">P+Q</text>
<text x="340" y="345" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#444441">Gerade durch P und Q → dritter Schnittpunkt R → an der x-Achse gespiegelt = P+Q</text>
</svg>
"""

_ECDH_SVG = r"""
<svg width="100%" viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg" role="img">
<title>ECDH-Schlüsselaustausch</title>
<desc>Alice und Bob tauschen öffentliche Punkte und berechnen denselben geheimen Punkt.</desc>
<defs>
<marker id="are" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</marker>
</defs>
<rect x="40" y="30" width="160" height="40" rx="8" fill="#1D9E75" fill-opacity="0.18" stroke="#0F6E56"/>
<text x="120" y="55" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#0F6E56" font-weight="500">Anna — geheim: a</text>
<rect x="480" y="30" width="160" height="40" rx="8" fill="#185FA5" fill-opacity="0.18" stroke="#0C447C"/>
<text x="560" y="55" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#185FA5" font-weight="500">Bob — geheim: b</text>
<text x="120" y="100" text-anchor="middle" font-family="monospace" font-size="13" fill="#0F6E56">A = a·G</text>
<text x="560" y="100" text-anchor="middle" font-family="monospace" font-size="13" fill="#185FA5">B = b·G</text>
<line x1="205" y1="120" x2="475" y2="120" stroke="#0F6E56" stroke-width="1.2" marker-end="url(#are)"/>
<text x="340" y="112" text-anchor="middle" font-family="monospace" font-size="12" fill="#0F6E56">A →</text>
<line x1="475" y1="150" x2="205" y2="150" stroke="#185FA5" stroke-width="1.2" marker-end="url(#are)"/>
<text x="340" y="166" text-anchor="middle" font-family="monospace" font-size="12" fill="#185FA5">← B</text>
<rect x="40" y="195" width="160" height="55" rx="8" fill="#1D9E75" fill-opacity="0.10" stroke="#0F6E56" stroke-dasharray="4 3"/>
<text x="120" y="217" text-anchor="middle" font-family="monospace" font-size="12" fill="#0F6E56">S = a·B</text>
<text x="120" y="237" text-anchor="middle" font-family="monospace" font-size="11" fill="#0F6E56">= a·(b·G)</text>
<rect x="480" y="195" width="160" height="55" rx="8" fill="#185FA5" fill-opacity="0.10" stroke="#0C447C" stroke-dasharray="4 3"/>
<text x="560" y="217" text-anchor="middle" font-family="monospace" font-size="12" fill="#185FA5">S = b·A</text>
<text x="560" y="237" text-anchor="middle" font-family="monospace" font-size="11" fill="#185FA5">= b·(a·G)</text>
<text x="340" y="222" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#B23A3A" font-weight="600">S = (a·b)·G</text>
<text x="340" y="242" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#444441">gleicher Punkt!</text>
<text x="340" y="282" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5F5E5A">Schlüssel = HKDF( x-Koordinate von S )</text>
</svg>
"""


def challenge_7_technik(color: str) -> rx.Component:
    return _box(
        _h("Diffie-Hellman auf elliptischen Kurven (ECDH)", color),
        rx.markdown(
            r"""
Bisher lebte alles in $(\mathbb{Z}/p\mathbb{Z})^*$: Zahlen, die man modulo $p$
multipliziert. Elliptische Kurven bieten eine **andere Gruppe** für dasselbe
Spiel — mit einem großen Vorteil: Für gleiche Sicherheit genügen viel kleinere
Zahlen. Deshalb nutzt die moderne Kryptografie (TLS, Signal, Bitcoin) fast
überall Kurven.

**Die Kurve.** Wir betrachten eine Kurve der Form
$$y^2 = x^3 + a\,x + b \pmod p.$$
Die „Elemente" sind die **Punkte** $(x, y)$, die diese Gleichung erfüllen, plus
ein spezieller Punkt im Unendlichen $\mathcal{O}$ (die „Null" der Gruppe).
            """
        ),
        _svg(_EC_ADDITION_SVG),
        rx.markdown(
            r"""
**Die Verknüpfung ist eine Addition von Punkten.** Statt zu multiplizieren,
*addiert* man Punkte geometrisch: Man legt eine Gerade durch $P$ und $Q$, findet
den dritten Schnittpunkt mit der Kurve und spiegelt ihn an der $x$-Achse. Das
Ergebnis heißt $P + Q$. Was in $(\mathbb{Z}/p\mathbb{Z})^*$ die Multiplikation
war, ist hier die Punktaddition.

**Und die Exponentiation?** Sie wird zur **skalaren Multiplikation**: $k \cdot G$
bedeutet, den Punkt $G$ genau $k$-mal zu sich selbst zu addieren
($G + G + \dots + G$). Das ist effizient (analog zum schnellen Potenzieren).

**Das schwere Problem (ECDLP).** Gegeben $G$ und $Q = k \cdot G$ — wie findet
man $k$? Das ist der **elliptische diskrete Logarithmus**, und er gilt als schwer,
*sofern die Kurve groß genug ist*. Genau hier liegt die Schwäche dieser Challenge.
            """
        ),
        _svg(_ECDH_SVG),
        rx.markdown(
            r"""
**Der Schlüsselaustausch (ECDH).** Anna wählt geheim $a$ und schickt
$A = a \cdot G$. Bob wählt geheim $b$ und schickt $B = b \cdot G$. Beide bilden

$$S = a \cdot B = a \cdot (b \cdot G) = b \cdot (a \cdot G) = b \cdot A.$$

Beide erhalten **denselben Punkt** $S$. Der Sitzungsschlüssel ist dann
$\text{HKDF}$ der $x$-Koordinate von $S$ — genau wie beim echten ECDH.

**Ihr Angriff.** Die Kurve dieser Challenge hat eine **kleine, primzahlige
Ordnung** $n$ (in der Capture als `CURVE_ORDER_N`). Damit ist der Suchraum für
$a$ klein: Mit **Baby-Step-Giant-Step auf der Kurve** finden Sie $a$ in etwa
$\sqrt{n}$ Schritten. Danach ist alles wie gewohnt: $S = a \cdot B$, Schlüssel
aus $x(S)$ ableiten, entschlüsseln.

> Die Lehre: Elliptische Kurven sind nicht automatisch sicher. Die **Ordnung**
> des Basispunktes muss groß und (idealer­weise) prim sein. Eine zu kleine Kurve
> fällt genauso wie ein zu kleines $p$ ganz am Anfang — dasselbe Prinzip, neues
> Spielfeld.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 8 technical part — Invalid Curve Attack
# ---------------------------------------------------------------------------
_INVALID_CURVE_SVG = r"""
<svg width="100%" viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg" role="img">
<title>Invalid-Curve-Angriff</title>
<desc>Der Angreifer sendet Punkte schwacher Kurven; Bob rechnet d*P ohne Pruefung.</desc>
<defs>
<marker id="ari" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</marker>
</defs>
<rect x="30" y="130" width="150" height="80" rx="10" fill="#B23A3A" fill-opacity="0.15" stroke="#8C2A2A"/>
<text x="105" y="160" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#B23A3A" font-weight="600">Angreifer (Sie)</text>
<text x="105" y="182" text-anchor="middle" font-family="monospace" font-size="11" fill="#8C2A2A">Punkt P auf E'(b')</text>
<text x="105" y="198" text-anchor="middle" font-family="monospace" font-size="11" fill="#8C2A2A">Ordnung q (klein!)</text>
<rect x="500" y="130" width="150" height="80" rx="10" fill="#185FA5" fill-opacity="0.15" stroke="#0C447C"/>
<text x="575" y="158" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#185FA5" font-weight="600">Bob</text>
<text x="575" y="180" text-anchor="middle" font-family="monospace" font-size="11" fill="#185FA5">geheim: d</text>
<text x="575" y="196" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#185FA5">prueft P NICHT</text>
<line x1="185" y1="155" x2="495" y2="155" stroke="#8C2A2A" stroke-width="1.3" marker-end="url(#ari)"/>
<text x="340" y="147" text-anchor="middle" font-family="monospace" font-size="12" fill="#8C2A2A">sendet P  →</text>
<line x1="495" y1="188" x2="185" y2="188" stroke="#185FA5" stroke-width="1.3" marker-end="url(#ari)"/>
<text x="340" y="204" text-anchor="middle" font-family="monospace" font-size="12" fill="#185FA5">←  R = d·P</text>
<rect x="120" y="245" width="440" height="70" rx="8" fill="#1D9E75" fill-opacity="0.10" stroke="#0F6E56" stroke-dasharray="4 3"/>
<text x="340" y="268" text-anchor="middle" font-family="monospace" font-size="12" fill="#0F6E56">In der kleinen Untergruppe: d mod q per Mini-BSGS</text>
<text x="340" y="290" text-anchor="middle" font-family="monospace" font-size="12" fill="#0F6E56">Viele q_i sammeln  →  CRT  →  d vollstaendig</text>
<text x="340" y="307" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#444441">b' geht NICHT in die Additionsformeln ein — deshalb funktioniert der Trick.</text>
<text x="340" y="40" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#B23A3A" font-weight="600">Bobs echte Kurve E ist stark — aber P liegt gar nicht auf E.</text>
</svg>
"""


def challenge_8_technik(color: str) -> rx.Component:
    return _box(
        _h("Der Invalid-Curve-Angriff", color),
        rx.markdown(
            r"""
Bislang lag die Schwäche immer in den **Parametern** — zu kleines $p$, glatte
Ordnung, winzige Kurve. Diesmal ist die Kurve $E$ **einwandfrei**: großer,
primzahliger Ordnung, der elliptische Log ist unangreifbar. Die Schwäche liegt
jetzt in der **Implementierung**.

**Die entscheidende Beobachtung.** Schauen Sie sich die Additionsformeln auf
$y^2 = x^3 + a x + b$ genau an: Zur Berechnung von $P + Q$ braucht man nur $a$,
die Koordinaten der Punkte und $p$ — der Parameter $b$ **kommt darin gar nicht
vor**. Das heißt: Rechnet man mit einem Punkt, der eigentlich auf einer *anderen*
Kurve $E'(b')$ mit demselben $a$, aber anderem $b'$ liegt, merkt die Formel den
Unterschied **nicht**. Man rechnet fröhlich weiter — nur eben in einer anderen
Gruppe.
            """
        ),
        _svg(_INVALID_CURVE_SVG),
        rx.markdown(
            r"""
**Bobs Fehler.** Bob besitzt einen festen geheimen Schlüssel $d$ (er nutzt ihn
wieder und wieder). Wenn ihm jemand einen Punkt $P$ schickt, berechnet er
$R = d \cdot P$ — **ohne zu prüfen, ob $P$ überhaupt auf seiner Kurve $E$ liegt**.
Genau diese fehlende Prüfung öffnet die Tür.

**Der Angriff Schritt für Schritt.**

1. Sie suchen eine schwache Kurve $E'(b')$ (gleiches $a$, anderes $b'$), deren
   Ordnung einen **kleinen Primfaktor** $q$ hat, und darauf einen Punkt $P$ der
   Ordnung $q$.
2. Sie schicken $P$ an Bob und erhalten $R = d \cdot P$. Da $P$ Ordnung $q$ hat,
   liegt auch $R$ in dieser winzigen Untergruppe. Ein **Mini-BSGS** ($\sqrt{q}$
   Schritte) liefert Ihnen $d \bmod q$.
3. Sie wiederholen das mit vielen verschiedenen $q_i$, bis deren Produkt größer
   als die Ordnung $n$ von $E$ ist.
4. Der **chinesische Restsatz (CRT)** setzt aus allen $d \bmod q_i$ das
   vollständige $d$ zusammen.

**Die Finalisierung.** Mit $d$ in der Hand berechnen Sie das echte gemeinsame
Geheimnis der abgefangenen Sitzung: $S = d \cdot A_{\text{eph}}$ (Alices
ephemerer Punkt liegt auf der echten Kurve $E$). Daraus leiten Sie den Schlüssel
ab und entschlüsseln.

> Die Lehre: Eine perfekte Kurve nützt nichts, wenn die Implementierung eingehende
> Punkte nicht validiert. Reale Bibliotheken (und ein berühmter TLS-/JWE-Bug)
> sind genau daran gescheitert. **Prüfen Sie immer, ob ein empfangener Punkt auf
> der erwarteten Kurve liegt** ($y^2 \equiv x^3 + ax + b$).
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 9 technical part — ElGamal reused nonce
# ---------------------------------------------------------------------------
def challenge_9_technik(color: str) -> rx.Component:
    return _box(
        _h("ElGamal und der wiederverwendete Nonce", color),
        rx.markdown(
            r"""
**ElGamal-Verschlüsselung.** Der Empfänger hat einen privaten Schlüssel $x$ und
veröffentlicht $y = g^x \bmod p$. Um eine Nachricht $m$ zu verschlüsseln, würfelt
der Absender einen **frischen Zufallswert** $k$ (den *Nonce*) und bildet

$$c_1 = g^k \bmod p, \qquad c_2 = m \cdot y^k \bmod p.$$

Das Chiffrat ist das Paar $(c_1, c_2)$. Der Empfänger entschlüsselt via
$m = c_2 \cdot (c_1^{\,x})^{-1}$. Die Sicherheit beruht — wie immer — darauf,
dass niemand aus $c_1 = g^k$ den Wert $k$ zurückrechnen kann (diskreter
Logarithmus). Hier ist $p$ groß (256 Bit), das ist also **aussichtslos**.

**Der fatale Fehler.** Entscheidend ist, dass $k$ bei **jeder** Verschlüsselung
neu und zufällig ist. Wird derselbe Nonce $k$ für zwei Nachrichten $m_1, m_2$
benutzt, dann ist auch $y^k$ in beiden Fällen **identisch**:

$$c_2^{(1)} = m_1 \cdot y^k, \qquad c_2^{(2)} = m_2 \cdot y^k.$$

**Woran erkennt man es?** Am gemeinsamen $c_1$! Denn $c_1 = g^k$ ist bei gleichem
$k$ in beiden Chiffraten **gleich**. Sehen Sie zwei ElGamal-Nachrichten mit
identischem $c_1$, wissen Sie sofort: derselbe Nonce.

**Der Angriff.** Kennen Sie den Klartext $m_1$ der ersten Nachricht (hier ein
bekannter Header), teilen Sie die beiden $c_2$ und heben $y^k$ heraus:

$$m_2 = c_2^{(2)} \cdot m_1 \cdot \big(c_2^{(1)}\big)^{-1} \bmod p.$$

Kein diskreter Logarithmus nötig. Der wiedergewonnene Wert $m_2$ ist das
Schlüsselmaterial: $\text{Schlüssel} = \text{HKDF}(m_2)$, damit entschlüsseln Sie
den AES-256-GCM-Datensatz.

> Die Lehre: Ein Nonce ist ein **Number used once** — im Wortsinn. Ihn
> wiederzuverwenden, hebelt selbst ein mathematisch sicheres Verfahren aus.
            """
        ),
        accent=color,
    )


# ---------------------------------------------------------------------------
# Challenge 10 technical part — DSA reused nonce
# ---------------------------------------------------------------------------
def challenge_10_technik(color: str) -> rx.Component:
    return _box(
        _h("DSA und der wiederverwendete Nonce (PS3 / Bitcoin)", color),
        rx.markdown(
            r"""
**DSA-Signatur.** Mit dem privaten Schlüssel $x$ signiert man eine Nachricht $m$.
Man würfelt einen Nonce $k$ und bildet

$$r = (g^k \bmod p) \bmod q, \qquad s = k^{-1}\,(H(m) + x\,r) \bmod q,$$

die Signatur ist $(r, s)$. Der öffentliche Schlüssel $y = g^x$ erlaubt jedem,
die Signatur zu prüfen — aber **nicht**, $x$ zu berechnen (dazu müsste man den
diskreten Logarithmus lösen).

**Der fatale Fehler — wieder der Nonce.** Auch $k$ muss bei jeder Signatur frisch
und geheim sein. Werden zwei Nachrichten $m_1, m_2$ mit **demselben** $k$
signiert, dann ist $r$ in beiden Signaturen **identisch** (denn $r$ hängt nur von
$k$ ab). Das ist das verräterische Zeichen.

**Der Angriff — Schritt für Schritt.** Aus
$$s_1 = k^{-1}(H(m_1) + x r), \qquad s_2 = k^{-1}(H(m_2) + x r)$$
folgt durch Subtraktion $s_1 - s_2 = k^{-1}(H(m_1) - H(m_2))$, also

$$k = \frac{H(m_1) - H(m_2)}{s_1 - s_2} \bmod q.$$

Mit bekanntem $k$ löst man eine der Gleichungen nach dem **privaten Schlüssel**
$x$ auf:

$$x = \frac{s_1\,k - H(m_1)}{r} \bmod q.$$

**Die Finalisierung.** Jetzt besitzen Sie $x$ — den privaten Schlüssel selbst.
Daraus leiten Sie den AES-Schlüssel ab ($\text{HKDF}(x)$) und entschlüsseln die
letzte Nachricht.

> Die Lehre: Genau dieser Fehler machte 2010 die **PlayStation 3** angreifbar
> (Sony benutzte einen konstanten Nonce) und leerte später **Bitcoin-Wallets**
> mit schwachem Zufallsgenerator. Ein einziger wiederverwendeter Zufallswert
> genügt, um den geheimen Schlüssel vollständig zu enthüllen.
            """
        ),
        accent=color,
    )
