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
        "Auf der Trainings-VM läuft periodisch ein simulierter TLS-Handshake mit "
        "einer DHE_EXPORT-Cipher-Suite. Alternativ kannst du dein **persönliches "
        "Capture** (`.pcap`) oben auf dieser Seite herunterladen. Öffne es in "
        "Wireshark und suche die **ServerKeyExchange**-Nachricht heraus."
    ],
    question_further=[
        "**Schritt für Schritt in Wireshark:**\n\n"
        "1. Filtere den Verkehr mit `tls.handshake` - so blendest du die "
        "Decoy-Pakete (HTTP/DNS) aus, die absichtlich mit im Capture liegen.\n"
        "2. Finde die Nachricht `Handshake Protocol: Server Key Exchange`.\n"
        "3. Klappe sie auf: "
        "`Server Key Exchange → Diffie-Hellman Server Params → p`. Wireshark zeigt "
        "dir dort `p` als Bytefolge **und** dessen Länge in Bit an.\n\n"
        "Anders als bei RSA (FREAK) steht die schwache Zahl hier **im Klartext** "
        "auf der Leitung: der Server verrät $p$, $g$ und $Y_s$ freiwillig im "
        "ServerKeyExchange - genau das brauchst du für den Angriff.\n\n"
        "**Wichtig für die nächsten Aufgaben:** Ab Aufgabe 4.3 musst du mit "
        "**deinem persönlichen** Capture arbeiten (Button oben) - nur darin passen "
        "$p$, $g$, $Y_s$, $Y_c$ und die Zufallswerte tatsächlich zusammen.\n\n"
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
        "Primfaktoren. Nimm das $p$ aus **deinem persönlichen Capture** (Button "
        "oben) und faktorisiere $p - 1$ mit **yafu**."
    ],
    question_further=[
        "**Warum $p-1$?** Der diskrete Logarithmus lebt in einer Gruppe der "
        "Ordnung $p-1$. Pohlig-Hellman (Aufgabe 4.2) braucht die Primfaktoren "
        "**dieser Ordnung** - also die Faktorisierung von $p-1$.\n\n"
        "**Walkthrough mit yafu:**\n\n"
        "```bash\n"
        "# p aus dem ServerKeyExchange deines Captures (als Dezimalzahl)\n"
        "# p-1 vorher ausrechnen, z.B. in Python:\n"
        "python3 -c \"p=<DEIN_P>; print(p-1)\"\n\n"
        "# dann in yafu faktorisieren:\n"
        "yafu \"factor(<P_MINUS_1>)\"\n"
        "```\n\n"
        "Weil $p-1$ hier **glatt** ist (viele kleine Faktoren), findet yafu die "
        "Faktoren in Sekunden - die kleinen Primzahlen fallen sofort über "
        "Probedivision und die Pollard-Rho-/ECM-Stufen.\n\n"
        "**Alternative in SageMath:**\n"
        "```python\n"
        "p = <DEIN_P>\n"
        "factor(p - 1)      # gibt z.B. 2 * q1 * q2 * ... * qn\n"
        "```\n\n"
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
        "**Der bequeme Weg - SageMath macht Pohlig-Hellman automatisch:**\n\n"
        "```python\n"
        "p  = <DEIN_P>\n"
        "g  = <DEIN_G>          # aus dem ServerKeyExchange\n"
        "Ys = <DEIN_Ys>         # 'pubkey' des Servers im ServerKeyExchange\n"
        "\n"
        "F = GF(p)              # Restklassenkörper modulo p\n"
        "s = discrete_log(F(Ys), F(g))   # nutzt intern Pohlig-Hellman\n"
        "print('s =', s)\n"
        "\n"
        "# Gegenprobe:\n"
        "print(power_mod(g, s, p) == Ys)  # muss True sein\n"
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
        "**Schritt für Schritt (RFC 2246 §8.1.2, §6.3, §8.1):**\n\n"
        "1. **Gemeinsames Geheimnis (pre_master_secret):** Nimm den öffentlichen "
        "Client-Wert $Y_c$ aus der `ClientKeyExchange`-Nachricht deines Captures "
        "und rechne\n"
        "$$Z = Y_c^{\\,s} \\bmod p.$$\n"
        "Das ist exakt dasselbe Geheimnis, das auch der Server berechnet hat "
        "($Z = g^{sc}$). In TLS ist das **pre_master_secret** die Big-Endian-"
        "Bytedarstellung von $Z$ (führende Nullen werden nicht aufgefüllt, "
        "RFC 2246 §8.1.2).\n\n"
        "```python\n"
        "Z = power_mod(Yc, s, p)\n"
        "pms = int(Z).to_bytes((int(Z).bit_length()+7)//8, 'big')\n"
        "```\n\n"
        "2. **client_random / server_random** (je 32 Byte) aus `ClientHello` bzw. "
        "`ServerHello` auslesen (in Wireshark direkt sichtbar).\n\n"
        "3. **Master Secret** über die TLS-1.0-PRF:\n"
        "$$\\text{master\\_secret} = \\text{PRF}(\\text{pms}, \\texttt{\"master secret\"}, "
        "\\text{client\\_random} + \\text{server\\_random})[0..48].$$\n\n"
        "Die TLS-1.0-PRF ist "
        "$P_{MD5}(S_1, \\text{seed}) \\oplus P_{SHA1}(S_2, \\text{seed})$, wobei "
        "$S_1$ die erste, $S_2$ die zweite Hälfte des Secrets ist, und "
        "$P_{hash}(S,\\text{seed}) = \\text{HMAC}(S, A_1+\\text{seed}) \\,\\|\\, "
        "\\text{HMAC}(S, A_2+\\text{seed}) \\,\\|\\, \\dots$ mit "
        "$A_0=\\text{seed},\\; A_i=\\text{HMAC}(S, A_{i-1})$.\n\n"
        "Alles mit Python-Bordmitteln (`hmac`, `hashlib`) machbar - identisch zur "
        "PRF aus dem FREAK-Kapitel (nur das pre_master_secret kommt jetzt aus DH "
        "statt aus RSA).\n\n"
        "**Tipp (Kontrolle in Wireshark):** Trage dein Master Secret unter "
        "*Preferences → Protocols → TLS → (Pre)-Master-Secret log filename* ein - "
        "wenn Wireshark daraufhin die Application Data entschlüsselt, stimmt es.\n\n"
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
        "**Schlüsselableitung (RFC 2246 §6.3, §6.3.1) - identisch zum FREAK-Kapitel:**\n\n"
        "1. `key_block = PRF(master_secret, \"key expansion\", "
        "server_random + client_random)` - **Achtung:** die Reihenfolge der "
        "Randoms ist hier **vertauscht** gegenüber der Master-Secret-Berechnung!\n"
        "2. Aufteilung des key_block: 16 Byte `client_write_MAC_secret`, 16 Byte "
        "`server_write_MAC_secret`, dann je 5 Byte `client_write_key` / "
        "`server_write_key` (nur **40 Bit** - die eigentliche Export-Schwäche des "
        "symmetrischen Teils).\n"
        "3. Finale 40-Bit-RC4-Schlüssel (§6.3.1): "
        "`final_write_key = PRF(write_key[0:5], \"client write key\"/"
        "\"server write key\", client_random + server_random)[0:16]` - hier "
        "**gleiche** Random-Reihenfolge für beide Seiten.\n"
        "4. RC4 ist ein Stream Cipher: **ein** durchgehender Keystream pro "
        "Richtung (nicht pro Record neu).\n"
        "5. Jeder Record ist `RC4(Klartext || HMAC-MD5(MAC_secret, seq_num || "
        "type || version || länge || Klartext))`. Die Flagge steckt im letzten, "
        "größten `ApplicationData`-Record (Content Type 23).\n\n"
        "**Tipp:** Die Server→Client-Records (inkl. Flagge) benutzen den "
        "`server_write_key`, nicht den `client_write_key`.\n\n"
        "**Tipp:** Wenn dein Master Secret aus Aufgabe 4.5 stimmt, entschlüsselt "
        "auch Wireshark die Application Data automatisch (siehe Tipp dort) - eine "
        "gute Kontrolle, bevor du von Hand weiterrechnest.\n\n"
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
