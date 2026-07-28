from website.engine.tasks.models import TaskData
from website.engine.tasks.helpers import Correct, TaskHint


task_03_00 = TaskData(
    day=3,
    points=5,
    day_description="Export Ciphers & FREAK",
    task_description="Einführung: Export-Kryptografie",
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
    answers=[Correct.create("freak")],
    question=[
        "In den 1990ern durfte starke Kryptografie in den USA nicht ohne Weiteres "
        "exportiert werden. TLS/SSL-Implementierungen bekamen deshalb eigene, absichtlich "
        "geschwächte Cipher Suites spendiert: die **RSA_EXPORT**-Suiten. Ein Server, der "
        "so eine Suite anbot, benutzte für den Schlüsselaustausch einen RSA-Schlüssel mit "
        "nur **512 Bit** - stark genug für den Export, hoffnungslos schwach für alles andere.\n\n"
        "Das Problem: diese Cipher Suites verschwanden nie ganz aus vielen Implementierungen. "
        "2015 zeigte die **FREAK-Attacke** (*Factoring RSA Export Keys*, CVE-2015-0204), dass "
        "ein Angreifer einen TLS-Client dazu bringen kann, so eine schwache Suite zu benutzen - "
        "selbst wenn beide Seiten eigentlich starke Kryptografie unterstützen. Danach reicht es, "
        "den Schlüssel zu faktorisieren (Stunden bis Tage Rechenzeit, historisch), den "
        "privaten Schlüssel zu rekonstruieren und die komplette Sitzung mitzulesen."
    ],
    question_further=[
        "**Kurzer RSA-Refresher, bevor es losgeht:**\n\n"
        "- Man wählt zwei **Primzahlen** $p$ und $q$ und berechnet den Modulus $N = p \\cdot q$.\n"
        "- Der öffentliche Schlüssel ist $(N, e)$ (meist $e = 65537$).\n"
        "- Der private Schlüssel $d$ ist das modulare Inverse von $e$ modulo $\\varphi(N) = (p-1)(q-1)$, "
        "also $d \\equiv e^{-1} \\pmod{\\varphi(N)}$.\n"
        "- Verschlüsseln: $c = m^e \\bmod N$. Entschlüsseln: $m = c^d \\bmod N$.\n"
        "- Die **gesamte** Sicherheit hängt daran, dass niemand $N$ in $p$ und $q$ zerlegen kann. "
        "Bei 512 Bit ist das mit modernen Faktorisierungs-Tools (z.B. **YAFU**, GNFS/SIQS) "
        "innerhalb von Sekunden bis Minuten machbar - bei 2048+ Bit nicht.\n\n"
        "**Tipp:** Wenn dir $p$ und $q$ bekannt sind, ist $d$ eine einfache Rechnung "
        "(erweiterter euklidischer Algorithmus) - kein Faktorisieren mehr nötig.\n\n"
        "**Ressourcen:**\n"
        "- FREAK-Attacke: https://en.wikipedia.org/wiki/FREAK\n"
        "- RFC 2246 (TLS 1.0), insbesondere §6 (Kryptografische Berechnungen) und §7.4 "
        "(Handshake-Nachrichten): https://www.rfc-editor.org/rfc/rfc2246\n"
        "- YAFU (Yet Another Factoring Utility): https://github.com/bbuhrow/yafu\n\n"
        "Tippe zur Bestätigung den Namen der Attacke ein (kleingeschrieben)."
    ],
    placeholder_text=["Name der Attacke..."],
    hints=[
        TaskHint.create(0, "Die Attacke ist nach dem englischen Wort für 'verrückt/panisch' benannt.", 1),
        TaskHint.create(0, "F.R.E.A.K. - schau dir das Akronym in der Einleitung nochmal genau an.", 1),
        TaskHint.create(0, "Die Antwort lautet: freak", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)

task_03_01 = TaskData(
    day=3,
    points=10,
    day_description="Export Ciphers & FREAK",
    task_description="Traffic Capture: Schwacher Schlüssel",
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
        "Auf der Trainings-VM läuft periodisch ein simulierter TLS-Handshake mit einer "
        "RSA_EXPORT-Cipher Suite (`TLS_RSA_EXPORT_WITH_RC4_40_MD5`). Öffne Wireshark auf der "
        "VM, und suche dir eine `Certificate`-Nachricht heraus. "
    ],
    question_further=[
        "**Tipp:** Klicke die Certificate-Nachricht im Detail-Panel auf: "
        "`Handshake Protocol: Certificate → Certificate → subjectPublicKeyInfo → RSAPublicKey → modulus`. "
        "Wireshark zeigt dir dort direkt die Bitlänge des Modulus an - genau danach fragen wir hier.\n\n"
        "**Wichtig für die nächsten Aufgaben:** Ab Aufgabe 3.3 arbeitest du nicht mehr mit einer "
        "beliebigen live mitgeschnittenen Verbindung, sondern mit deinem **persönlichen** Capture "
        "(\"Gestartet\"-Button erscheint oben auf dieser Seite, sobald du diese Aufgabe gelöst hast - "
        "starte deinen eigenen Mitschnitt, bevor du klickst) - nur darin passen N, die Zufallswerte "
        "und der Faktor aus Aufgabe 3.3 tatsächlich zusammen.\n\n"
        "**Wie viele Bit hat der RSA-Schlüssel, den der Server hier anbietet?**"
    ],
    placeholder_text=["z.B. 2048"],
    hints=[
        TaskHint.create(0, "Filtere nach tls.handshake um eine Verbindung zu finden."),
        TaskHint.create(0, "Das ist genau die Schlüsselgröße, die FREAK überhaupt erst ausnutzbar macht.", 1),
        TaskHint.create(0, "Es ist eine sehr runde Zahl, ein Vielfaches von 128.", 1),
        TaskHint.create(0, "Die Antwort lautet: 512", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)

task_03_02 = TaskData(
    day=3,
    points=30,
    day_description="Export Ciphers & FREAK",
    task_description="Aufwärmübung: 256-Bit faktorisieren",
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
    dynamic_check="export_factor256",
    answers=[Correct.create("dynamic")],
    question=[
        "Den echten 512-Bit-Schlüssel direkt zu faktorisieren würde selbst mit YAFU ein zwei Tage dauern. "
        "Stattdessen bekommst du zunächst eine **eigene, "
        "kleinere** 256-Bit-Zahl $N$. Deine persönliche Zahl findest du weiter oben auf dieser Seite."
    ],
    question_further=[
        "Bei 256 Bit (~77 Dezimalstellen) liefert das SIQS/GNFS-Verfahren die Faktoren "
        "typischerweise in unter einer Minute.\n\n"
        "(Reihenfolge egal). Bei Erfolg bekommst du einen Faktor des **echten**, "
        "512-Bit-Schlüssels geschenkt - eine Abkürzung für die nächste Aufgabe. \n"
        "Gib beide Primzahlen getrennt von einem komma getrennt ein. \n"
        "\n"
        "Du kannst für diese Aufgabe das Tool yafu verwenden."

    ],
    placeholder_text=["p,q"],
    hints=[
        TaskHint.create(0, "Tipp: -noecm überspringt die (hier meist nutzlose) Kurvenmethode und "
        "beschleunigt die Sache spürbar.\n"),
        TaskHint.create(0, "YAFU installiert? `yafu \"factor(N)\"` reicht für den Anfang, dauert nur länger ohne -gnfs -noecm.", 1),
        TaskHint.create(0, "Tipp: Prüfe zur Kontrolle selbst, dass $p \\cdot q = N$ gilt, bevor du abschickst.\n\n"),
        TaskHint.create(0, "Format der Antwort: zwei Dezimalzahlen mit Komma getrennt, z.B. 12345,67890", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)

task_03_03 = TaskData(
    day=3,
    points=15,
    day_description="Export Ciphers & FREAK",
    task_description="Den zweiten Faktor berechnen",
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
    dynamic_check="export_factor512",
    answers=[Correct.create("dynamic")],
    question=[
        "Du kennst jetzt einen Faktor $p$ des echten 512-Bit-Moduls $N$ - er wurde dir nach "
        "der letzten Aufgabe angezeigt. $N$ selbst siehst du im Zertifikat aus **deinem "
        "persönlichen Capture** (\"Gestartet\"-Button oben auf dieser Seite - nicht aus einer "
        "beliebigen live mitgeschnittenen Verbindung, siehe Hinweis in Aufgabe 3.2)."
    ],
    question_further=[
        "**Tipp:** verwende Python oder einen Taschenrechner, der BigIntegers unterstützt."
        "reicht völlig: `q = N // p` und `assert N % p == 0` zur Kontrolle.\n\n"
        "Gib den fehlenden Faktor $q$ ein."
    ],
    placeholder_text=["q"],
    hints=[
        TaskHint.create(0, "N steht im Zertifikat (Certificate-Handshake-Nachricht) in deinem persönlichen Capture-Download, nicht in einer zufälligen Live-Verbindung.", 1),
        TaskHint.create(0, "q = N // p - eine einzige Ganzzahldivision.", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)

task_03_04 = TaskData(
    day=3,
    points=25,
    day_description="Export Ciphers & FREAK",
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
    dynamic_check="export_master_secret",
    answers=[Correct.create("dynamic")],
    question=[
        "Du hast jetzt $p$ und $q$ und damit den privaten Schlüssel des Servers "
        "($d \\equiv e^{-1} \\pmod{(p-1)(q-1)}$, $e = 65537$). Zeit, die Session zu brechen."
    ],
    question_further=[
        "**Schritt für Schritt (RFC 2246 §6.1, §7.4.7.1):**\n\n"
        "1. Entschlüssle in deinem persönlichen Capture die `ClientKeyExchange`-Nachricht mit "
        "deinem privaten Schlüssel (RSA/PKCS#1 v1.5) → das ergibt das 48-Byte "
        "**pre_master_secret**.\n"
        "2. Extrahiere `client_random` (aus `ClientHello`) und `server_random` (aus "
        "`ServerHello`) - je 32 Byte.\n"
        "3. `master_secret = PRF(pre_master_secret, \"master secret\", client_random + "
        "server_random)[0:48]`\n\n"
        "Die TLS-1.0-PRF ist `P_MD5(secret[:24], seed) XOR P_SHA1(secret[24:], seed)` mit "
        "`P_hash(secret,seed) = HMAC(secret, A(1)+seed) + HMAC(secret, A(2)+seed) + ...` und "
        "`A(0)=seed, A(i)=HMAC(secret,A(i-1))` - alles mit Python-Bordmitteln (`hmac`, "
        "`hashlib`) machbar, siehe RFC 2246 §6.1 für die exakte Definition.\n\n"
        "**Tipp:** Achte auf Byte- vs. Hex-Darstellung - gib das Master Secret als "
        "Hex-String (96 Zeichen) ein.\n\n"
        "**Tipp:** In Wireshark unter *Preferences → Protocols → TLS → (Pre)-Master-Secret "
        "log filename* kannst du dein berechnetes Master Secret eintragen lassen und prüfen, "
        "ob Wireshark die Anwendungsdaten damit entschlüsselt."
    ],
    placeholder_text=["Master Secret als Hex..."],
    hints=[
        TaskHint.create(0, "RFC 2246 §7.4.7.1 beschreibt exakt das Byte-Layout der ClientKeyExchange-Nachricht.", 1),
        TaskHint.create(0, "PKCS#1-v1.5-Padding beim Entschlüsseln: 0x00 0x02 [zufällige Bytes] 0x00 [Nachricht] - der Teil nach der 0x00-Trennung ist deine gesuchte Nachricht.", 1),
        TaskHint.create(0, "Die TLS-1.0-PRF kombiniert MD5 und SHA1 über HMAC - beide Hashes sind in Pythons hashlib enthalten.", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)

task_03_05 = TaskData(
    day=3,
    points=15,
    day_description="Export Ciphers & FREAK",
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
    dynamic_check="export_flag",
    answers=[Correct.create("dynamic")],
    question=[
        "Letzter Schritt: aus dem Master Secret die Sitzungsschlüssel ableiten und damit die "
        "verschlüsselten Anwendungsdaten im Capture entschlüsseln."
    ],
    question_further=[
        "**Schlüsselableitung (RFC 2246 §6.3, §6.3.1):**\n\n"
        "1. `key_block = PRF(master_secret, \"key expansion\", server_random + client_random)` "
        "- Reihenfolge der Randoms ist hier **vertauscht** gegenüber Schritt 3 vorher!\n"
        "2. Die ersten 32 Byte sind `client_write_MAC_secret` (16) + `server_write_MAC_secret` "
        "(16), danach je 5 Byte `client_write_key`/`server_write_key` (nur 40 Bit - das ist "
        "die eigentliche Schwäche der Export-Suite).\n"
        "3. Für die finalen 40-Bit-RC4-Schlüssel (§6.3.1): "
        "`final_write_key = PRF(write_key[0:5], \"client write key\"/\"server write key\", "
        "client_random + server_random)[0:16]` - **gleiche** Reihenfolge für beide Seiten, "
        "anders als bei key_block.\n"
        "4. RC4 ist ein Stream Cipher: ein durchgängiger Keystream über alle Records einer "
        "Richtung (nicht pro Record neu initialisiert).\n"
        "5. Jeder Record ist `RC4(Klartext + HMAC-MD5(MAC-Secret, seq_num + type + version + "
        "länge + Klartext))` - die Flagge steckt im letzten, größten `ApplicationData`-Record.\n\n"
        "**Tipp:** Die Server→Client-Records (inkl. der Flagge) benutzen den "
        "`server_write_key`, nicht den `client_write_key`.\n\n"
        "**Tipp:** Wenn dein Master Secret aus der vorigen Aufgabe stimmt, klappt auch die "
        "Wireshark-Entschlüsselung (siehe Tipp dort) - eine gute Kontrolle, bevor du hier "
        "von Hand weiterrechnest."
    ],
    placeholder_text=["crypto{...}"],
    hints=[
        TaskHint.create(0, "Die Byte-Reihenfolge in Schritt 1 (server_random + client_random) unterscheidet sich von der Master-Secret-Berechnung!", 1),
        TaskHint.create(0, "Nur 5 Byte des extrahierten write_key sind tatsächlich geheim - der Rest der 16 Byte kommt erst durch die PRF in Schritt 3 dazu.", 1),
        TaskHint.create(0, "Die Flagge liegt im letzten TLS-Record des Captures, Content Type 23 (Application Data).", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)
