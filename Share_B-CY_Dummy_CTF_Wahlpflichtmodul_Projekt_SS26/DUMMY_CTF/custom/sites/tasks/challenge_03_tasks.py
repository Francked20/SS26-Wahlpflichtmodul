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
        "In den 1990ern durfte starke Kryptografie in den USA nicht ohne Weiteres exportiert "
        "werden. TLS/SSL bekam deshalb absichtlich geschwächte **RSA_EXPORT**-Cipher-Suiten "
        "spendiert: der Schlüsselaustausch lief über einen RSA-Schlüssel mit nur **512 Bit**.\n\n"
        "Diese Suiten verschwanden nie ganz aus vielen Implementierungen. 2015 zeigte die "
        "**FREAK-Attacke** (CVE-2015-0204), dass ein Angreifer einen TLS-Client zu so einer "
        "schwachen Suite zwingen kann - selbst wenn beide Seiten eigentlich starke Kryptografie "
        "unterstützen. Danach reicht Faktorisieren, um die Sitzung mitzulesen."
    ],
    question_further=[
        "**RSA kurz:** $N = p \\cdot q$, öffentlicher Schlüssel $(N,e)$ mit meist $e=65537$, "
        "privater Schlüssel $d \\equiv e^{-1} \\pmod{(p-1)(q-1)}$. Verschlüsseln: $c=m^e \\bmod N$, "
        "Entschlüsseln: $m=c^d \\bmod N$. Kennst du $p$ und $q$, ist $d$ eine einfache Rechnung - "
        "kein Faktorisieren mehr nötig. Bei 512 Bit dauert das Faktorisieren selbst mit modernen "
        "Tools nur Sekunden bis Minuten.\n\n"
        "**Ressourcen:**\n"
        "- FREAK: https://en.wikipedia.org/wiki/FREAK\n"
        "- CVE-2015-0204: https://nvd.nist.gov/vuln/detail/CVE-2015-0204\n"
        "- RFC 2246 (TLS 1.0): https://www.rfc-editor.org/rfc/rfc2246.html\n"
        "- YAFU: https://github.com/bbuhrow/yafu\n\n"
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
        "Der Handshake, den du oben per \"Gestartet\" ausgelöst hast, benutzt "
        "`TLS_RSA_EXPORT_WITH_RC4_40_MD5`. Such dir in deinem Mitschnitt die "
        "`Certificate`-Nachricht heraus."
    ],
    question_further=[
        "Ressource: Wireshark-TLS-Dissector-Doku: https://wiki.wireshark.org/TLS\n\n"
        "**Wichtig:** Dieser eine Mitschnitt trägt dich durch alle folgenden Aufgaben - N, "
        "Zufallswerte, verschlüsselte Daten und Flagge stammen alle daraus. Speichere ihn ab, "
        "du brauchst kein zweites Capture.\n\n"
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
        "Den echten 512-Bit-Schlüssel direkt zu faktorisieren würde selbst mit YAFU ein bis "
        "zwei Tage dauern. Du bekommst deshalb zuerst eine **eigene, kleinere** 256-Bit-Zahl "
        "$N$ (steht weiter oben auf dieser Seite)."
    ],
    question_further=[
        "Bei 256 Bit (~77 Dezimalstellen) liefert SIQS/GNFS die Faktoren meist in unter einer "
        "Minute. Bei Erfolg bekommst du einen Faktor des **echten** 512-Bit-Schlüssels geschenkt "
        "- die Abkürzung für die nächste Aufgabe.\n\n"
        "Gib beide Primzahlen kommagetrennt ein (Reihenfolge egal).\n\n"
        "YAFU: https://github.com/bbuhrow/yafu (Doku im Wiki des Repos)"
    ],
    placeholder_text=["p,q"],
    hints=[
        TaskHint.create(0, "YAFU installiert? `yafu \"factor(N)\"` reicht für den Anfang, dauert nur länger ohne -gnfs -noecm.", 1),
        TaskHint.create(0, "-noecm überspringt die (hier meist nutzlose) Kurvenmethode und beschleunigt die Sache spürbar.", 1),
        TaskHint.create(0, "Prüfe zur Kontrolle selbst, dass $p \\cdot q = N$ gilt, bevor du abschickst.", 1),
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
        "Du kennst jetzt einen Faktor $p$ des echten 512-Bit-Moduls $N$ - angezeigt nach der "
        "letzten Aufgabe. $N$ selbst steht im Zertifikat aus deinem Mitschnitt von Aufgabe 3.2."
    ],
    question_further=[
        "$N$ ist bei RSA das Produkt zweier Primzahlen. Du kennst $N$ und einen der beiden "
        "Faktoren - der fehlende zweite Faktor $q$ lässt sich daraus direkt bestimmen.\n\n"
        "Gib $q$ ein."
    ],
    placeholder_text=["q"],
    hints=[
        TaskHint.create(0, "N steht im Zertifikat (Certificate-Handshake-Nachricht) - dieselbe Nachricht, in der du in Aufgabe 3.2 schon die Schlüssellänge abgelesen hast.", 1),
        TaskHint.create(0, "$N = p \\cdot q$", 1),
        TaskHint.create(0, "q = N // p (Ganzzahldivision) - prüfe mit N % p == 0, ob's aufgeht.", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)

task_03_04 = TaskData(
    day=3,
    points=15,
    day_description="Export Ciphers & FREAK",
    task_description="Das Pre-Master-Secret entschlüsseln",
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
        "($d \\equiv e^{-1} \\pmod{(p-1)(q-1)}$, $e = 65537$). Erster Schritt, um die Session "
        "zu brechen: das `pre_master_secret` aus dem Handshake entschlüsseln."
    ],
    question_further=[
        "Die verschlüsselte `ClientKeyExchange`-Nachricht in deinem persönlichen Capture enthält "
        "das RSA/PKCS#1-v1.5-verschlüsselte, 48 Byte lange `pre_master_secret` - "
        "RFC 2246 §7.4.7.1: https://www.rfc-editor.org/rfc/rfc2246.html#section-7.4.7.1\n\n"
        "Gib es als Hex-String (96 Zeichen) ein."
    ],
    placeholder_text=["Pre-Master-Secret als Hex..."],
    hints=[
        TaskHint.create(0, "PKCS#1-v1.5-Padding-Schema: https://en.wikipedia.org/wiki/PKCS_1 - nach dem Entschlüsseln musst du es entfernen.", 1),
        TaskHint.create(0, "Format: 0x00 0x02 [zufällige Bytes ≠ 0] 0x00 [Nachricht] - alles nach der zweiten 0x00 ist deine gesuchte Nachricht.", 1),
        TaskHint.create(0, "m.to_bytes(k, \"big\") mit k = Byte-Länge von N nicht vergessen, sonst fehlen führende Nullbytes und die 0x00 0x02-Prüfung schlägt fehl.", 1),
        TaskHint.create(0, "Die ersten 2 Byte des entschlüsselten pre_master_secret sollten der TLS-Version aus deinem ClientHello entsprechen (0301 für TLS 1.0) - eine gute Kontrolle.", 1),
        TaskHint.create(0, "Abkürzung statt eigenem PKCS#1-Code: Baue dir aus p, q, e=65537 einen privaten RSA-Schlüssel als PEM (z.B. mit PyCryptodome: `RSA.construct((N, e, d, p, q)).export_key()`) und trag ihn in Wireshark unter Preferences → Protocols → TLS → \"RSA keys list\" ein. Wireshark entschlüsselt damit die Session selbst und zeigt pre_master_secret, master_secret und die Klartext-Records direkt im Paketdetails-Baum an.", 1),
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
        "Du kennst jetzt dein `pre_master_secret`. Zeit, daraus das `master_secret` "
        "abzuleiten."
    ],
    question_further=[
        "Extrahiere `client_random` (aus `ClientHello`) und `server_random` (aus "
        "`ServerHello`, je 32 Byte), dann wende die **TLS-1.0-PRF** an - "
        "RFC 2246 §6.1: https://www.rfc-editor.org/rfc/rfc2246.html#section-6.1\n\n"
        "`master_secret = PRF(pre_master_secret, \"master secret\", client_random + "
        "server_random)[0:48]`\n\n"
        "Gib es als Hex-String (96 Zeichen) ein."
        "Tipp: Falls nicht anders möglich kann Wireshark verwendet werden um das master Secret zu bestimmen."
    ],
    placeholder_text=["Master Secret als Hex..."],
    hints=[
        TaskHint.create(0, "Die beiden Randoms holst du dir in Wireshark aus dem Feld `tls.handshake.random` (ClientHello = client_random, ServerHello = server_random). Achtung: Wireshark zeigt die ersten 4 Byte teils separat als \"GMT Unix Time\" an - die gehören dazu, es sind je volle 32 Byte.", 1),
        TaskHint.create(0, "Der `seed` der PRF ist eine reine Byte-Konkatenation: label + client_random + server_random, mit label = b\"master secret\" (ASCII, ohne abschließendes Nullbyte). Das label ist also Teil des Seeds und nicht etwa der HMAC-Schlüssel - HMAC-Schlüssel ist immer das secret.", 1),
        TaskHint.create(0, "PRF(secret,label,seed) = P_MD5(S1,label+seed) XOR P_SHA1(S2,label+seed), wobei S1/S2 die zwei (bei ungerader Länge überlappenden) Hälften von secret sind.", 1),
        TaskHint.create(0, "S1/S2-Split: half = (len(secret)+1)//2, S1 = secret[:half], S2 = secret[-half:]. Bei einem 48 Byte langen pre_master_secret sind das schlicht 24 + 24 Byte ohne Überlappung.", 1),
        TaskHint.create(0, "P_hash(secret,seed) = HMAC(secret,A(1)+seed) + HMAC(secret,A(2)+seed) + ... mit A(0)=seed, A(i)=HMAC(secret,A(i-1)) - RFC 2246 §6.1 hat die exakte Definition.", 1),
        TaskHint.create(0, "Iteriere P_MD5 und P_SHA1 jeweils so lange, bis mindestens 48 Byte zusammenkommen (MD5 liefert 16 Byte pro Runde, SHA1 20 - also je 3 Runden), dann XOR die beiden Ströme byteweise und nimm davon die ersten 48 Byte.", 1),
        TaskHint.create(0, "Python-Gerüst: `hmac.new(secret, msg, hashlib.md5).digest()` bzw. `hashlib.sha1`; XOR zweier Byte-Strings mit `bytes(a ^ b for a, b in zip(x, y))`.", 1),
        TaskHint.create(0, "Selbsttest ohne Abgabe: schreib eine Datei mit der Zeile `CLIENT_RANDOM <client_random_hex> <master_secret_hex>` und trag sie in Wireshark unter Preferences → Protocols → TLS → (Pre)-Master-Secret log filename ein. Werden die ApplicationData-Records danach entschlüsselt angezeigt, stimmt dein Master Secret.", 1),
        TaskHint.create(0, "Abkürzung statt eigenem PKCS#1-Code: Baue dir aus p, q, e=65537 einen privaten RSA-Schlüssel als PEM (z.B. mit PyCryptodome: `RSA.construct((N, e, d, p, q)).export_key()`) und trag ihn in Wireshark unter Preferences → Protocols → TLS → \"RSA keys list\" ein. Wireshark entschlüsselt damit die Session selbst und zeigt pre_master_secret, master_secret und die Klartext-Records direkt im Paketdetails-Baum an.", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)

task_03_06 = TaskData(
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
        "Letzter Schritt: aus dem `master_secret` die Sitzungsschlüssel ableiten und damit "
        "die verschlüsselten Anwendungsdaten entschlüsseln."
    ],
    question_further=[
        "Schlüsselableitung: RFC 2246 §6.3 "
        "(https://www.rfc-editor.org/rfc/rfc2246.html#section-6.3) und §6.3.1 für die "
        "Export-Schlüssel (https://www.rfc-editor.org/rfc/rfc2246.html#section-6.3.1). "
        "Verschlüsselung: RC4 (https://en.wikipedia.org/wiki/RC4), MAC: HMAC-MD5.\n\n"
        "Die Flagge liegt im letzten `ApplicationData`-Record (Content Type 23) deines "
        "Captures."
    ],
    placeholder_text=["crypto{...}"],
    hints=[
        TaskHint.create(0, "key_block = PRF(master_secret, \"key expansion\", server_random + client_random) - Reihenfolge der Randoms ist hier vertauscht gegenüber der Master-Secret-Berechnung!", 1),
        TaskHint.create(0, "Erste 32 Byte von key_block: client_write_MAC_secret (16) + server_write_MAC_secret (16). Danach je 5 Byte roher client_write_key/server_write_key - nur 40 Bit, die eigentliche Export-Schwäche.", 1),
        TaskHint.create(0, "Finale 16-Byte-Schlüssel: final_write_key = PRF(write_key[0:5], \"client write key\"/\"server write key\", client_random + server_random)[0:16] - hier wieder normale Reihenfolge.", 1),
        TaskHint.create(0, "Die Server→Client-Records (inkl. Flagge) benutzen server_write_key, nicht client_write_key.", 1),
        TaskHint.create(0, "RC4 ist ein durchgängiger Keystream über alle Records einer Richtung - nicht pro Record neu initialisiert. Jeder Record: RC4(Klartext + HMAC-MD5(MAC-Secret, seq_num+type+version+länge+Klartext)).", 1),
        TaskHint.create(0, "Wenn dein Master Secret aus der vorigen Aufgabe stimmt, klappt auch die Wireshark-Entschlüsselung (siehe Tipp dort) - eine gute Kontrolle, bevor du hier von Hand weiterrechnest.", 1),
    ],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)
