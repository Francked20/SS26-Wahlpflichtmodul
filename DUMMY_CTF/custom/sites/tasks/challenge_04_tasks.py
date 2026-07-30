"""Task definitions for Chapter 4 ("Schwache Diffie-Hellman-Parameter" / Logjam).

Each `task_04_XX` is a `TaskData` object describing one step of the Logjam attack
chain, from concept to captured flag:
  4.0 intro -> 4.1 spot the 512-bit p in the capture -> 4.2 why it is breakable
  (Pohlig-Hellman) -> 4.3 factor p-1 (yafu) -> 4.4 discrete log s -> 4.5 TLS
  master secret -> 4.6 decrypt the flag.
Tasks 4.3-4.6 use per-player `dynamic_check` validators (see dh_export_pool.py)
instead of a fixed answer. All learner-facing text is intentionally in German.
These objects are imported and rendered by the Chapter 4 site pages.
"""

from website.engine.tasks.models import TaskData
from website.engine.tasks.helpers import Correct, TaskHint


# Shared day_description reused by every task in this chapter.
DAY_DESC = "Schwache Diffie-Hellman-Parameter (Logjam)"


# ----------------------------------------------------------------------------
# 4.0 - Introduction
# ----------------------------------------------------------------------------
task_04_00 = TaskData(
    day=4,
    points=5,
    day_description=DAY_DESC,
    task_description="Einführung: Schwaches Diffie-Hellman",
    error_cost=0,
    allow_reset=False,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=False,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    answers=[Correct.create("logjam")],
    question=[
        "Im vorigen Kapitel hast du gesehen, wie ein zu kleiner **RSA**-Schlüssel "
        "(FREAK) eine TLS-Sitzung öffnet. Diffie-Hellman (DH) hat dasselbe Problem "
        "aus derselben Zeit: die **DHE_EXPORT**-Cipher-Suiten. Um die US-"
        "Exportregeln der 1990er zu erfüllen, benutzten Server dort absichtlich "
        "**schwache DH-Parameter** - eine kleine Primzahl $p$ (typisch **512 Bit**).\n\n"
        "2015 zeigte die **Logjam**-Attacke, dass ein Angreifer einen Client per "
        "Man-in-the-Middle auf so eine Export-Suite herabstufen kann (\"downgrade\") "
        "- selbst wenn beide Seiten starkes DH beherrschen. Danach genügt es, den "
        "diskreten Logarithmus in der kleinen Gruppe zu lösen, um das gemeinsame "
        "Geheimnis - und damit die ganze Sitzung - zu rekonstruieren."
    ],
    question_further=[
        "**Kurzer DH-Refresher, bevor es losgeht:**\n\n"
        "- Beide Seiten einigen sich öffentlich auf eine Primzahl $p$ und einen "
        "Erzeuger $g$.\n"
        "- Der Server wählt geheim $s$ und sendet $Y_s = g^s \\bmod p$; der Client "
        "wählt geheim $c$ und sendet $Y_c = g^c \\bmod p$.\n"
        "- Beide berechnen dasselbe Geheimnis $Z = Y_s^{\\,c} = Y_c^{\\,s} = "
        "g^{sc} \\bmod p$. Daraus wird der TLS-Schlüssel abgeleitet.\n"
        "- Die **gesamte** Sicherheit hängt daran, dass niemand aus $Y_s$ das "
        "geheime $s$ zurückrechnen kann - das ist das **diskrete Logarithmus-"
        "problem (DLP)**.\n\n"
        "Das DLP ist nur schwer, wenn $p$ groß **und** gut gewählt ist. Ist "
        "$p-1$ ein Produkt vieler **kleiner** Primzahlen (\"glatt\"), zerfällt "
        "das DLP mit dem **Satz von Pohlig-Hellman** in viele winzige Teilprobleme "
        "- und wird trivial.\n\n"
        "**Ressourcen:**\n"
        "- Logjam-Attacke: https://weakdh.org und "
        "https://en.wikipedia.org/wiki/Logjam_(computer_security)\n"
        "- RFC 2246 (TLS 1.0), §7.4.3 (ServerKeyExchange / ServerDHParams) und "
        "§8.1.2 (DH shared secret): https://www.rfc-editor.org/rfc/rfc2246\n"
        "- Pohlig-Hellman: https://en.wikipedia.org/wiki/Pohlig%E2%80%93Hellman_algorithm\n"
        "- yafu (Faktorisierung): https://github.com/bbuhrow/yafu\n\n"
        "Tippe zur Bestätigung den Namen der Attacke ein (kleingeschrieben)."
    ],
    placeholder_text=["Name der Attacke..."],
    hints=[
        TaskHint.create(0, "Der Name klingt wie ein 'Stau aus Baumstämmen' - ein englisches Wort.", 1),
        TaskHint.create(0, "Log-jam: die Attacke auf schwaches Diffie-Hellman von 2015.", 1),
        TaskHint.create(0, "Die Antwort lautet: logjam", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ----------------------------------------------------------------------------
# 4.1 - Capture: identify the key size (how many bits is p?)
# ----------------------------------------------------------------------------
task_04_01 = TaskData(
    day=4,
    points=10,
    day_description=DAY_DESC,
    task_description="Traffic Capture: Wie groß ist p?",
    error_cost=1,
    allow_reset=False,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=True,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    answers=[Correct.create("512")],
    question=[
        "Schneide auf der Trainings-VM deinen **persönlichen** DHE_EXPORT-Handshake "
        "mit: starte Wireshark (Filter `tcp.port == 4434`), klicke im Panel oben auf "
        "**\"Gestartet\"** und öffne dann die **ServerKeyExchange**-Nachricht in deinem "
        "Mitschnitt."
    ],
    question_further=[
        "**Schritt für Schritt in Wireshark (auf der VM):**\n\n"
        "1. Starte den Mitschnitt auf der VM-Schnittstelle (z.B. `eth1`) mit dem "
        "Filter `tcp.port == 4434` und klicke oben auf \"Gestartet\".\n"
        "2. Finde die Nachricht `Handshake Protocol: Server Key Exchange`.\n"
        "3. Klappe sie auf: "
        "`Server Key Exchange → Diffie-Hellman Server Params → p`. Wireshark zeigt "
        "dir dort `p` als Bytefolge **und** dessen Länge in Bit an.\n\n"
        "Anders als bei RSA (FREAK) steht die schwache Zahl hier **im Klartext** "
        "auf der Leitung: der Server verrät $p$, $g$ und $Y_s$ freiwillig im "
        "ServerKeyExchange - genau das brauchst du für den Angriff.\n\n"
        "**Wichtig für die nächsten Aufgaben:** Ab Aufgabe 4.3 arbeitest du mit den "
        "Werten aus **deinem eigenen** Mitschnitt - nur darin passen $p$, $g$, "
        "$Y_s$, $Y_c$ und die Zufallswerte tatsächlich zusammen. Tipp: In Wireshark "
        "kannst du jedes Feld per Rechtsklick → *Copy* → *…as a Hex Stream* "
        "kopieren.\n\n"
        "**Wie viele Bit hat die Primzahl $p$, die der Server hier benutzt?**"
    ],
    placeholder_text=["z.B. 2048"],
    hints=[
        TaskHint.create(0, "Filtere nach tls.handshake und suche 'Server Key Exchange'.", 1),
        TaskHint.create(0, "Es ist genau die Größe, die Logjam gegen Export-Server praktikabel machte.", 1),
        TaskHint.create(0, "Eine sehr runde Zahl, ein Vielfaches von 128.", 1),
        TaskHint.create(0, "Die Antwort lautet: 512", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ----------------------------------------------------------------------------
# 4.2 - Feasibility: why is it breakable? (name the algorithm)
# ----------------------------------------------------------------------------
task_04_02 = TaskData(
    day=4,
    points=10,
    day_description=DAY_DESC,
    task_description="Machbarkeit: Warum ist das knackbar?",
    error_cost=1,
    allow_reset=False,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=False,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    answers=[Correct.create("pohlig-hellman"), Correct.create("pohlig hellman"),
             Correct.create("pohlig-hellman-algorithmus")],
    question=[
        "512 Bit klingt viel - warum ist der diskrete Logarithmus hier trotzdem "
        "in Sekunden lösbar? Der Trick liegt nicht in der Größe von $p$, sondern "
        "in der **Struktur** von $p-1$."
    ],
    question_further=[
        "**Die Idee - warum ein glattes $p-1$ alles kaputt macht:**\n\n"
        "Der Erzeuger $g$ erzeugt eine Gruppe der Ordnung $p-1$. Wenn "
        "$p - 1 = 2 \\cdot q_1 \\cdot q_2 \\cdots q_n$ nur aus **kleinen** Primzahlen "
        "$q_i$ besteht (man sagt: $p-1$ ist *glatt*), dann besagt der **Satz von "
        "Pohlig-Hellman**:\n\n"
        "> Man kann den diskreten Logarithmus modulo jedem kleinen Faktor $q_i$ "
        "einzeln lösen (jeweils ein winziges Problem der Größe $\\sqrt{q_i}$ mit "
        "Baby-Step-Giant-Step) und die Teilergebnisse mit dem **Chinesischen "
        "Restsatz (CRT)** zum vollständigen $s$ zusammensetzen.\n\n"
        "Statt einer Suche der Größe $\\sqrt{p} \\approx 2^{256}$ (unmöglich) "
        "hast du also viele Suchen der Größe $\\sqrt{q_i}$ (je ein Kinderspiel). "
        "Genau deshalb ist die **Wahl der Parameter** - nicht die Bitlänge allein "
        "- entscheidend. Ein sicherer DH-Server benutzt ein $p$, bei dem "
        "$p-1$ einen **großen** Primfaktor hat (\"safe prime\").\n\n"
        "**Frage:** Wie heißt der Algorithmus, der das DLP über die kleinen "
        "Faktoren von $p-1$ zerlegt? (Name eingeben)"
    ],
    placeholder_text=["Name des Algorithmus..."],
    hints=[
        TaskHint.create(0, "Zwei Nachnamen, mit Bindestrich verbunden - benannt nach seinen Erfindern (1978).", 1),
        TaskHint.create(0, "Er kombiniert die Teil-Logarithmen modulo kleiner Primfaktoren per CRT.", 1),
        TaskHint.create(0, "Die Antwort lautet: pohlig-hellman", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ----------------------------------------------------------------------------
# 4.3 - Factor p-1 with yafu   (dynamic check)
# ----------------------------------------------------------------------------
task_04_03 = TaskData(
    day=4,
    points=30,
    day_description=DAY_DESC,
    task_description="p-1 faktorisieren (yafu)",
    error_cost=2,
    allow_reset=False,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=True,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    dynamic_check="dh_factors",
    answers=[Correct.create("dynamic")],
    question=[
        "Der erste echte Schritt des Angriffs: Zerlege $p - 1$ in seine "
        "Primfaktoren. Nimm das $p$ aus **deinem eigenen Mitschnitt** "
        "(ServerKeyExchange) und faktorisiere $p - 1$."
    ],
    question_further=[
        "**Warum $p-1$?** Der diskrete Logarithmus lebt in einer Gruppe der "
        "Ordnung $p-1$. Pohlig-Hellman (Aufgabe 4.2) braucht die Primfaktoren "
        "**dieser Ordnung** - also die Faktorisierung von $p-1$.\n\n"
        "Das `p` liest du in Wireshark unter "
        "`Server Key Exchange → Diffie-Hellman Server Params → p` ab "
        "(Rechtsklick → *Copy* → *…as a Hex Stream*).\n\n"
        "**Weg 1 - yafu (wie im FREAK-Kapitel):**\n"
        "```bash\n"
        "# p-1 zuerst als Dezimalzahl ausrechnen (p ist hex aus Wireshark):\n"
        "python3 -c \"p=0x<DEIN_P_HEX>; print(p-1)\"\n\n"
        "# dann in yafu faktorisieren:\n"
        "yafu \"factor(<P_MINUS_1>)\"\n"
        "```\n"
        "Weil $p-1$ hier **glatt** ist (viele kleine Faktoren), findet yafu die "
        "Faktoren in Sekunden.\n\n"
        "**Weg 2 - SageCell (empfohlen, ohne Installation):** Öffne "
        "https://sagecell.sagemath.org/ und füge diesen Muster-Code ein - ersetze "
        "nur `<DEIN_P_HEX>` durch das aus Wireshark kopierte `p`:\n"
        "```python\n"
        "# --- Wert aus deinem Wireshark-Mitschnitt (ServerKeyExchange) ---\n"
        "p = Integer(\"<DEIN_P_HEX>\", 16)   # p als Hex-String einfügen\n\n"
        "print(\"p hat\", p.nbits(), \"Bit, prim:\", p.is_prime())\n"
        "fac = factor(p - 1)\n"
        "print(fac)                         # z.B. 2 * q1 * q2 * ... * qn\n"
        "print([q for q, _ in fac])         # Liste der Primfaktoren\n"
        "```\n"
        "Weil $p-1$ glatt ist, ist `factor(p-1)` in Sekunden fertig - das ist "
        "genau die Struktur, die Pohlig-Hellman (Aufgabe 4.4) ausnutzt.\n\n"
        "**Antwortformat:** Gib **alle** Primfaktoren von $p-1$ als kommagetrennte "
        "Dezimalzahlen ein (Reihenfolge egal, der triviale Faktor 2 ist optional). "
        "Beispiel: `2,1009,3221,...`\n\n"
        "Zur Kontrolle: das Produkt aller Faktoren muss wieder exakt $p-1$ ergeben."
    ],
    placeholder_text=["q1,q2,q3,..."],
    hints=[
        TaskHint.create(0, "Zuerst p-1 bilden, DANN faktorisieren - nicht p selbst (p ist prim).", 1),
        TaskHint.create(0, "yafu: `yafu \"factor(N)\"`. Der Schalter -noecm kann helfen, muss aber nicht.", 1),
        TaskHint.create(0, "Prüfe selbst: multipliziere alle Faktoren - es muss p-1 herauskommen.", 1),
        TaskHint.create(0, "Format: Dezimalzahlen mit Komma getrennt, z.B. 2,1009,3221,50021", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ----------------------------------------------------------------------------
# 4.4 - Discrete logarithm via Pohlig-Hellman   (dynamic check)
# ----------------------------------------------------------------------------
task_04_04 = TaskData(
    day=4,
    points=30,
    day_description=DAY_DESC,
    task_description="Diskreter Logarithmus (Pohlig-Hellman)",
    error_cost=2,
    allow_reset=False,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=True,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    dynamic_check="dh_server_secret",
    answers=[Correct.create("dynamic")],
    question=[
        "Jetzt löst du das eigentliche DLP: Finde das geheime $s$ des Servers mit "
        "$Y_s = g^s \\bmod p$. Du kennst $g$, $p$, $Y_s$ (aus dem Capture) und die "
        "Faktoren von $p-1$ (aus Aufgabe 4.3)."
    ],
    question_further=[
        "Alle drei Werte liest du in Wireshark aus dem **ServerKeyExchange** ab: "
        "`p`, `g` und die Server-`Pubkey` ($Y_s$). "
        "Rechtsklick auf das Feld → *Copy* → *…as a Hex Stream*.\n\n"
        "**Der bequeme Weg - SageCell macht Pohlig-Hellman automatisch:** Öffne "
        "https://sagecell.sagemath.org/ und füge diesen Muster-Code ein - ersetze "
        "die drei Hex-Werte durch deine aus Wireshark:\n\n"
        "```python\n"
        "# --- Werte aus deinem Wireshark-Mitschnitt (ServerKeyExchange) ---\n"
        "p  = Integer(\"<DEIN_P_HEX>\",  16)\n"
        "Ys = Integer(\"<DEIN_Ys_HEX>\", 16)   # Server-'Pubkey'\n"
        "g  = 2                               # 'g' aus dem ServerKeyExchange\n"
        "\n"
        "F = GF(p)                            # Restklassenkörper modulo p\n"
        "s = discrete_log(F(Ys), F(g))        # nutzt intern Pohlig-Hellman\n"
        "print('s =', s)\n"
        "\n"
        "# Gegenprobe:\n"
        "print(power_mod(g, s, p) == Ys)      # muss True sein\n"
        "```\n\n"
        "Weil $p-1$ glatt ist, zerlegt `discrete_log` das Problem automatisch über "
        "die kleinen Faktoren und ist in Sekunden fertig.\n\n"
        "**Der lehrreiche Weg - Pohlig-Hellman von Hand (Skizze):**\n\n"
        "1. Für jeden Primfaktor $q_i$ von $p-1$:\n"
        "   - $g_i = g^{(p-1)/q_i} \\bmod p$, $\\;h_i = Y_s^{(p-1)/q_i} \\bmod p$\n"
        "   - löse $g_i^{x_i} = h_i$ mit Baby-Step-Giant-Step $\\Rightarrow "
        "x_i = s \\bmod q_i$\n"
        "2. Setze alle $x_i$ mit dem **Chinesischen Restsatz** zu $s \\bmod (p-1)$ "
        "zusammen.\n\n"
        "```python\n"
        "# skizzenhaft in reinem Python (BSGS + CRT):\n"
        "from sympy.ntheory.residue_ntheory import discrete_log as dlog\n"
        "# oder eine eigene BSGS-Routine pro Faktor, dann CRT\n"
        "```\n\n"
        "**Antwort:** Gib das gefundene geheime $s$ als Dezimalzahl ein."
    ],
    placeholder_text=["s (Dezimalzahl)"],
    hints=[
        TaskHint.create(0, "In SageMath genügt discrete_log(F(Ys), F(g)) mit F = GF(p).", 1),
        TaskHint.create(0, "Kontrolle: power_mod(g, s, p) muss wieder Ys ergeben.", 1),
        TaskHint.create(0, "Von Hand: pro Faktor q_i ein BSGS auf g^((p-1)/q_i), dann alles per CRT vereinen.", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ----------------------------------------------------------------------------
# 4.5 - TLS master secret   (dynamic check)
# ----------------------------------------------------------------------------
task_04_05 = TaskData(
    day=4,
    points=25,
    day_description=DAY_DESC,
    task_description="Das TLS Master Secret berechnen",
    error_cost=2,
    allow_reset=False,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=False,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    dynamic_check="dh_master_secret",
    answers=[Correct.create("dynamic")],
    question=[
        "Du hast $s$ - damit kannst du das gemeinsame DH-Geheimnis und daraus das "
        "TLS **Master Secret** berechnen. Zeit, die Sitzung zu brechen."
    ],
    question_further=[
        "**Idee (RFC 2246 §8.1.2, §6.3, §8.1):** Mit deinem $s$ berechnest du das "
        "gemeinsame Geheimnis $Z = Y_c^{\\,s} \\bmod p$ (dasselbe, das der Server "
        "als $g^{sc}$ hat). $Z$ als Big-Endian-Bytes ist das **pre_master_secret**; "
        "daraus liefert die TLS-1.0-PRF das **Master Secret**.\n\n"
        "**Werte aus Wireshark (Rechtsklick → *Copy* → *…as a Hex Stream*):**\n"
        "- $Y_c$ = die `Pubkey` in der **ClientKeyExchange**-Nachricht\n"
        "- `client_random` (32 Byte) = Feld `Random` im **ClientHello**\n"
        "- `server_random` (32 Byte) = Feld `Random` im **ServerHello**\n\n"
        "**Muster-Code für SageCell** (https://sagecell.sagemath.org/) - SageCell "
        "führt normales Python inkl. `hmac`/`hashlib` aus. Ersetze die vier "
        "Hex-Werte und trage dein $s$ aus Aufgabe 4.4 ein:\n\n"
        "```python\n"
        "import hmac, hashlib\n"
        "\n"
        "# --- aus Wireshark + s aus Aufgabe 4.4 ---\n"
        "p  = int(\"<DEIN_P_HEX>\", 16)\n"
        "s  = <DEIN_S>                       # Dezimalzahl aus Aufgabe 4.4\n"
        "Yc = int(\"<DEIN_Yc_HEX>\", 16)       # ClientKeyExchange, Pubkey\n"
        "client_random = bytes.fromhex(\"<CLIENT_RANDOM_HEX>\")  # 32 Byte\n"
        "server_random = bytes.fromhex(\"<SERVER_RANDOM_HEX>\")  # 32 Byte\n"
        "\n"
        "# 1) pre_master_secret = Z als Big-Endian-Bytes (ohne führende Nullen)\n"
        "Z = pow(Yc, s, p)\n"
        "pms = Z.to_bytes((Z.bit_length() + 7) // 8, 'big')\n"
        "\n"
        "# 2) TLS-1.0-PRF = P_MD5(S1) XOR P_SHA1(S2)\n"
        "def p_hash(digest, secret, seed, length):\n"
        "    out, a = b'', seed\n"
        "    while len(out) < length:\n"
        "        a = hmac.new(secret, a, digest).digest()\n"
        "        out += hmac.new(secret, a + seed, digest).digest()\n"
        "    return out[:length]\n"
        "\n"
        "def prf(secret, label, seed, length):\n"
        "    half = (len(secret) + 1) // 2\n"
        "    s1, s2 = secret[:half], secret[-half:]\n"
        "    return bytes(x ^ y for x, y in zip(\n"
        "        p_hash(hashlib.md5,  s1, label + seed, length),\n"
        "        p_hash(hashlib.sha1, s2, label + seed, length)))\n"
        "\n"
        "# 3) Master Secret (Seed-Reihenfolge: client_random + server_random)\n"
        "master_secret = prf(pms, b'master secret', client_random + server_random, 48)\n"
        "print(master_secret.hex())\n"
        "```\n\n"
        "Das ist **dieselbe PRF wie im FREAK-Kapitel** - nur das pre_master_secret "
        "kommt jetzt aus DH statt aus RSA.\n\n"
        "**Tipp (Kontrolle in Wireshark):** Trage unter *Preferences → Protocols → "
        "TLS → (Pre)-Master-Secret log filename* eine Datei mit der Zeile "
        "`CLIENT_RANDOM <client_random_hex> <master_secret_hex>` ein - wenn "
        "Wireshark daraufhin die Application Data entschlüsselt, stimmt dein Wert.\n\n"
        "**Antwort:** Master Secret als Hex-String (96 Zeichen)."
    ],
    placeholder_text=["Master Secret als Hex..."],
    hints=[
        TaskHint.create(0, "pre_master_secret = Yc^s mod p, als Big-Endian-Bytes (RFC 2246 §8.1.2).", 1),
        TaskHint.create(0, "Die PRF ist identisch zum FREAK-Kapitel - nur die Herkunft des pre_master_secret unterscheidet sich.", 1),
        TaskHint.create(0, "Reihenfolge im Seed: client_random + server_random (für das Master Secret).", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ----------------------------------------------------------------------------
# 4.6 - The flag: derive session keys and decrypt   (dynamic check)
# ----------------------------------------------------------------------------
task_04_06 = TaskData(
    day=4,
    points=15,
    day_description=DAY_DESC,
    task_description="Die Flagge entschlüsseln",
    error_cost=1,
    allow_reset=False,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=False,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    dynamic_check="dh_flag",
    answers=[Correct.create("dynamic")],
    question=[
        "Letzter Schritt: aus dem Master Secret die Sitzungsschlüssel ableiten und "
        "damit die verschlüsselten Application Data im Capture entschlüsseln - die "
        "Flagge steckt im letzten Record."
    ],
    question_further=[
        "**Der einfachste Weg - Wireshark entschlüsselt selbst:** Trage dein "
        "Master Secret aus 4.5 als `CLIENT_RANDOM <client_random_hex> "
        "<master_secret_hex>`-Zeile unter *Preferences → Protocols → TLS → "
        "(Pre)-Master-Secret log filename* ein. Wireshark entschlüsselt dann die "
        "**Application Data** direkt - die Flagge steht im letzten, größten Record "
        "(Content Type 23, Server→Client).\n\n"
        "**Der lehrreiche Weg - Schlüssel selbst ableiten (RFC 2246 §6.3, §6.3.1, "
        "identisch zum FREAK-Kapitel):** Kopiere den **server_flight_2** aus "
        "Wireshark (die Records ChangeCipherSpec + verschlüsseltes Finished + "
        "ApplicationData vom Server, Rechtsklick → *Copy* → *…as a Hex Stream* auf "
        "die TLS-Bytes) und nutze diesen Muster-Code in SageCell "
        "(https://sagecell.sagemath.org/):\n\n"
        "```python\n"
        "import hmac, hashlib\n"
        "\n"
        "# --- aus Aufgabe 4.5 / Wireshark ---\n"
        "master_secret = bytes.fromhex(\"<MASTER_SECRET_HEX>\")   # aus 4.5\n"
        "client_random = bytes.fromhex(\"<CLIENT_RANDOM_HEX>\")\n"
        "server_random = bytes.fromhex(\"<SERVER_RANDOM_HEX>\")\n"
        "server_flight_2 = bytes.fromhex(\"<SERVER_FLIGHT_2_HEX>\")\n"
        "\n"
        "def p_hash(digest, secret, seed, length):\n"
        "    out, a = b'', seed\n"
        "    while len(out) < length:\n"
        "        a = hmac.new(secret, a, digest).digest()\n"
        "        out += hmac.new(secret, a + seed, digest).digest()\n"
        "    return out[:length]\n"
        "def prf(secret, label, seed, length):\n"
        "    half = (len(secret) + 1) // 2\n"
        "    s1, s2 = secret[:half], secret[-half:]\n"
        "    return bytes(x ^ y for x, y in zip(\n"
        "        p_hash(hashlib.md5, s1, label+seed, length),\n"
        "        p_hash(hashlib.sha1, s2, label+seed, length)))\n"
        "\n"
        "# 1) key_block - ACHTUNG: hier server_random + client_random (vertauscht!)\n"
        "kb = prf(master_secret, b'key expansion', server_random + client_random, 2*16+2*5)\n"
        "server_write_mac = kb[16:32]\n"
        "server_write_key_short = kb[37:42]          # nur 5 Byte = 40 Bit (Export!)\n"
        "# 2) finaler 40-Bit-RC4-Key: client_random + server_random (gleiche Reihenfolge)\n"
        "server_write_key = prf(server_write_key_short, b'server write key',\n"
        "                       client_random + server_random, 16)\n"
        "\n"
        "# 3) RC4 (ein durchgehender Keystream pro Richtung)\n"
        "class RC4:\n"
        "    def __init__(self, key):\n"
        "        s = list(range(256)); j = 0\n"
        "        for i in range(256):\n"
        "            j = (j + s[i] + key[i % len(key)]) % 256\n"
        "            s[i], s[j] = s[j], s[i]\n"
        "        self.s, self.i, self.j = s, 0, 0\n"
        "    def crypt(self, data):\n"
        "        s, i, j = self.s, self.i, self.j; out = bytearray(len(data))\n"
        "        for k, b in enumerate(data):\n"
        "            i = (i+1) % 256; j = (j + s[i]) % 256\n"
        "            s[i], s[j] = s[j], s[i]\n"
        "            out[k] = b ^ s[(s[i]+s[j]) % 256]\n"
        "        self.i, self.j = i, j; return bytes(out)\n"
        "\n"
        "def records(buf):\n"
        "    out, off = [], 0\n"
        "    while off < len(buf):\n"
        "        ln = int.from_bytes(buf[off+3:off+5], 'big')\n"
        "        out.append((buf[off], buf[off+5:off+5+ln])); off += 5 + ln\n"
        "    return out\n"
        "\n"
        "rc4 = RC4(server_write_key); seq = 0; flag = None\n"
        "for ctype, frag in records(server_flight_2):\n"
        "    if ctype == 20:                      # ChangeCipherSpec: unverschlüsselt\n"
        "        continue\n"
        "    pt = rc4.crypt(frag)[:-16]           # RC4, dann 16-Byte-MAC (MD5) abtrennen\n"
        "    seq += 1\n"
        "    if ctype == 23:                      # ApplicationData = Flagge\n"
        "        flag = pt\n"
        "print(flag.decode(errors='replace'))\n"
        "```\n\n"
        "**Achtung, zwei Stolperfallen:** (1) die Random-Reihenfolge in Schritt 1 "
        "(`server_random + client_random`) ist gegenüber 4.5 **vertauscht**; (2) "
        "RC4 ist ein **durchgehender** Keystream - das server-Finished (seq 0) muss "
        "**vor** der ApplicationData (seq 1) entschlüsselt werden, sonst stimmt der "
        "Keystream nicht. Server→Client benutzt den `server_write_key`.\n\n"
        "**Antwort:** die Flagge im Format `crypto{...}`."
    ],
    placeholder_text=["crypto{...}"],
    hints=[
        TaskHint.create(0, "Reihenfolge in Schritt 1 (server_random + client_random) unterscheidet sich von der Master-Secret-Berechnung!", 1),
        TaskHint.create(0, "Nur 5 Byte des write_key sind geheim - die vollen 16 Byte entstehen erst durch die PRF in Schritt 3.", 1),
        TaskHint.create(0, "Die Flagge liegt im letzten TLS-Record, Content Type 23 (Application Data), Server→Client.", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)
