from website.engine.tasks.models import TaskData
from website.engine.tasks.helpers import Correct, Incorrect, TaskHint


# ============================================================================
# KAPITEL 02 — Diffie-Hellman & der diskrete Logarithmus
# VAGUE 1 : Akt I, Challenges 1-3 (klassisches DH)
#
# Modell (THM/HTB-Stil, OHNE Backend):
#   - Der Studierende lädt seine persönliche Capture herunter, greift LOKAL an
#     (faktorisieren, Pohlig-Hellman, entschlüsseln) und reicht die Flagge ein.
#   - Validierung 100% statisch über das Framework.
#   - Zwischenfragen mit GEMEINSAMER Antwort prüfen echtes Verständnis/Handeln,
#     ohne variantenabhängige Werte (z.B. "Wie viele nicht-triviale Primfaktoren
#     hat p-1?" -> 3, nur durch echtes Faktorisieren beantwortbar).
#   - Keine Task-Randomisierung: allow_random_order=False, jede Liste hat 1 Eintrag.
#
# Aufgabennummerierung (task_02_XX) und Freischaltung (day_02_task_XX) laufen
# fortlaufend über alle Aufgaben des Kapitels.
# ============================================================================


# ----------------------------------------------------------------------------
# 2.0 — Einstieg: Ziel & diskreter Logarithmus (Konzept-QCM)
# ----------------------------------------------------------------------------
task_02_00 = TaskData(
    day=2,
    points=5,
    day_description="Diffie-Hellman",
    task_description="Das Prinzip",
    error_cost=0,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=False,
    allow_cyber_range=False,
    master_task=False,
    task_type="multiple",
    answers=[
        Correct.create("Alice und Bob einigen sich über einen unsicheren Kanal auf ein gemeinsames Geheimnis, ohne es je zu übertragen."),
        Incorrect.create("Alice und Bob tauschen ihren geheimen Schlüssel direkt im Klartext aus."),
        Correct.create("Die Sicherheit beruht auf der Schwierigkeit des diskreten Logarithmus."),
        Correct.create("Öffentlich sind p, g, A = g^a mod p und B = g^b mod p; geheim bleiben a und b."),
    ],
    question=["Wie funktioniert Diffie-Hellman im Kern? (Mehrfachauswahl)"],
    question_further=[
        "Öffentlich bekannt sind eine große Primzahl p und ein Erzeuger g. "
        "Alice wählt geheim a und veröffentlicht A = g^a mod p; Bob wählt b und "
        "veröffentlicht B = g^b mod p. Beide berechnen dasselbe s = g^(ab) mod p."
    ],
    placeholder_text=[""],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ----------------------------------------------------------------------------
# 2.1 — Das diskrete Logarithmusproblem (Konzept-QCM)
# ----------------------------------------------------------------------------
task_02_01 = TaskData(
    day=2,
    points=5,
    day_description="Diffie-Hellman",
    task_description="Der diskrete Logarithmus",
    error_cost=0,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=False,
    allow_cyber_range=False,
    master_task=False,
    task_type="multiple",
    answers=[
        Correct.create("Die modulare Exponentiation A = g^a mod p ist effizient berechenbar."),
        Correct.create("Aus A, g und p den Exponenten a zurückzugewinnen gilt im Allgemeinen als schwer."),
        Incorrect.create("Der diskrete Logarithmus lässt sich immer in konstanter Zeit berechnen."),
        Correct.create("Diese Einbahn-Eigenschaft macht DH überhaupt erst sicher."),
    ],
    question=["Was ist das diskrete Logarithmusproblem (DLP)? (Mehrfachauswahl)"],
    question_further=[
        "Prof. Schramm definiert: zu gegebener Basis a, Zahl n und Funktion "
        "f_a(x) = a^x mod n ist der diskrete Logarithmus die Aufgabe, zu y das x "
        "mit y = a^x mod n zu finden. Leicht in eine Richtung, schwer zurück — "
        "eine Einweg-Funktion."
    ],
    placeholder_text=[""],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ============================================================================
# CHALLENGE 1 — Aufwärmen (kleines p, BSGS/Brute-Force)
# ============================================================================

# ----------------------------------------------------------------------------
# 2.2 — Capture lesen (Beweis-Frage, gemeinsame Antwort)
# ----------------------------------------------------------------------------
task_02_02 = TaskData(
    day=2,
    points=10,
    day_description="Diffie-Hellman",
    task_description="Challenge 1 — Die Capture",
    error_cost=1,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=True,
    injectible=False,
    allow_kali=True,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    answers=[
        Correct.create("PARAM_P"),
    ],
    question=["Verschaffen Sie sich einen Überblick über Ihre persönliche Capture."],
    question_further=[
        "Laden Sie oben Ihre Challenge-1-Capture herunter. Die Datei ist im "
        "Klartext lesbar (KEY: WERT). Unter welchem Schlüsselwort steht die "
        "Primzahl p? Geben Sie den genauen Schlüsselnamen ein."
    ],
    placeholder_text=["Schlüsselname aus der .tcvcap-Datei"],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
    hints=[
        TaskHint.create(0, "Jede Zeile hat die Form KEY: WERT. Zeilen mit # sind Kommentare.", 0.7),
        TaskHint.create(0, "Der gesuchte Schlüssel beginnt mit PARAM_ und enthält eine sehr große Zahl.", 0.4),
    ],
)


# ----------------------------------------------------------------------------
# 2.3 — Challenge 1: Flagge (kleines p per BSGS/Brute-Force lösen)
# ----------------------------------------------------------------------------
task_02_03 = TaskData(
    day=2,
    points=20,
    day_description="Diffie-Hellman",
    task_description="Challenge 1 — Die Flagge",
    error_cost=1,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=True,
    injectible=False,
    allow_kali=True,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    answers=[
        Correct.create("hiy{dh_warmup_discrete_log_c0ffee}"),
    ],
    question=["Brechen Sie Challenge 1 und reichen Sie die Flagge ein."],
    question_further=[
        "p ist klein (ca. 39 Bit). Lösen Sie den diskreten Logarithmus g^a = A "
        "(mod p) per Brute-Force oder Baby-Step-Giant-Step. Berechnen Sie dann das "
        "gemeinsame Geheimnis s = B^a mod p, leiten Sie den Schlüssel ab "
        "(HKDF-SHA256, siehe Capture) und entschlüsseln Sie den AES-256-GCM-"
        "Datensatz. Die Flagge steht im Klartext."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
    hints=[
        TaskHint.create(0, "Bei so kleinem p können Sie alle a durchprobieren, bis g^a mod p = A gilt.", 0.7),
        TaskHint.create(0, "shared_secret_bytes: s als Big-Endian, Länge ceil(bits(p)/8). Nutzen Sie die 'cryptography'-Bibliothek (HKDF, AESGCM).", 0.4),
        TaskHint.create(0, "Nonce und Ciphertext sind Base64-codiert. Nach dem Entschlüsseln finden Sie ein JSON mit dem Feld 'flag'.", 0.2),
    ],
)


# ============================================================================
# CHALLENGE 2 — Glatte Ordnung (yafu + Pohlig-Hellman + CRT)
# ============================================================================

# ----------------------------------------------------------------------------
# 2.4 — Konzept: glatte Ordnung (QCM)
# ----------------------------------------------------------------------------
task_02_04 = TaskData(
    day=2,
    points=5,
    day_description="Diffie-Hellman",
    task_description="Challenge 2 — Glatte Ordnung",
    error_cost=0,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=False,
    allow_cyber_range=False,
    master_task=False,
    task_type="multiple",
    answers=[
        Correct.create("Entscheidend ist nicht die Größe von p, sondern die Primfaktorzerlegung von p-1 = ord(G)."),
        Correct.create("Zerfällt p-1 in lauter kleine Primfaktoren, heißt die Ordnung 'glatt' (smooth)."),
        Correct.create("Bei glatter Ordnung lässt sich das DLP in kleine Teilprobleme zerlegen (Pohlig-Hellman)."),
        Incorrect.create("Ein großes p garantiert immer Sicherheit, unabhängig von der Struktur von p-1."),
    ],
    question=["Warum ist eine glatte Gruppenordnung gefährlich? (Mehrfachauswahl)"],
    question_further=[
        "Der diskrete Logarithmus lebt in einer Gruppe der Ordnung ord(G) = p-1. "
        "Nach Prof. Schramm hängt die Komplexität des Angriffs hauptsächlich vom "
        "größten Primteiler von p-1 ab."
    ],
    placeholder_text=[""],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ----------------------------------------------------------------------------
# 2.5 — Beweis-Frage: Anzahl nicht-trivialer Primfaktoren (gemeinsame Antwort 3)
# ----------------------------------------------------------------------------
task_02_05 = TaskData(
    day=2,
    points=15,
    day_description="Diffie-Hellman",
    task_description="Challenge 2 — Faktorisieren",
    error_cost=1,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=True,
    injectible=False,
    allow_kali=True,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    answers=[
        Correct.create("3"),
    ],
    question=["Faktorisieren Sie p-1 Ihrer Challenge-2-Capture."],
    question_further=[
        "p ist jetzt groß (ca. 120 Bit) — von Hand nicht mehr faktorisierbar, "
        "aber yafu erledigt es in Sekunden. Faktorisieren Sie p-1. "
        "Wie viele NICHT-TRIVIALE Primfaktoren (also ohne die 2) hat p-1? "
        "Geben Sie die Anzahl als Zahl ein."
    ],
    placeholder_text=["Anzahl (Zahl)"],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
    hints=[
        TaskHint.create(0, "In Kali/VSCode: 'yafu' starten und factor(p-1) eingeben. p-1 erhalten Sie, indem Sie von p eins abziehen.", 0.7),
        TaskHint.create(0, "p-1 ist gerade, enthält also den trivialen Faktor 2. Zählen Sie nur die übrigen (großen) Primfaktoren.", 0.4),
    ],
)


# ----------------------------------------------------------------------------
# 2.6 — Challenge 2: Flagge (Pohlig-Hellman + CRT)
# ----------------------------------------------------------------------------
task_02_06 = TaskData(
    day=2,
    points=30,
    day_description="Diffie-Hellman",
    task_description="Challenge 2 — Die Flagge",
    error_cost=1,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=True,
    injectible=False,
    allow_kali=True,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    answers=[
        Correct.create("hiy{dh_smooth_order_pohlig_hellman_1337}"),
    ],
    question=["Lösen Sie das DLP mit Pohlig-Hellman und bergen Sie die Flagge."],
    question_further=[
        "Nutzen Sie die glatte Struktur: projizieren Sie das Problem in jede "
        "prime Untergruppe (g_q = g^((p-1)/q) mod p, analog A_q), lösen Sie dort "
        "je ein kleines DLP (BSGS) und setzen Sie die Ergebnisse per Chinesischem "
        "Restsatz (CRT) zu a zusammen. Dann wie in Challenge 1: s = B^a mod p, "
        "Schlüssel ableiten, entschlüsseln, Flagge einreichen."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
    hints=[
        TaskHint.create(0, "Die Projektion g^((p-1)/q) mod p erzeugt ein Element der Ordnung q — dort ist der Log klein (ca. sqrt(q) Schritte per BSGS).", 0.7),
        TaskHint.create(0, "Sie erhalten a mod q_1, a mod q_2, a mod q_3. Der CRT (z.B. sympy.ntheory.modular.crt) kombiniert sie zu a.", 0.4),
        TaskHint.create(0, "Ab hier ist der Weg identisch zu Challenge 1: gemeinsames Geheimnis, Schlüssel, Entschlüsselung.", 0.2),
    ],
)


# ============================================================================
# CHALLENGE 3 — Fast glatt (die Falle: großes p, aber a < M)
# ============================================================================

# ----------------------------------------------------------------------------
# 2.7 — Konzept: die Falle erkennen (QCM)
# ----------------------------------------------------------------------------
task_02_07 = TaskData(
    day=2,
    points=5,
    day_description="Diffie-Hellman",
    task_description="Challenge 3 — Die Falle",
    error_cost=0,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=False,
    injectible=False,
    allow_kali=False,
    allow_cyber_range=False,
    master_task=False,
    task_type="multiple",
    answers=[
        Correct.create("p ist deutlich größer (ca. 176 Bit) und wirkt dadurch 'sicher'."),
        Correct.create("p-1 enthält einen großen Primfaktor Q, der nicht faktorisierbar ist."),
        Correct.create("Man nutzt nur die glatte Teilstruktur aus und ignoriert Q bewusst."),
        Incorrect.create("Weil p groß ist, ist der diskrete Logarithmus hier garantiert unlösbar."),
    ],
    question=["Diese Variante sieht sicher aus. Was ist die Falle? (Mehrfachauswahl)"],
    question_further=[
        "Schauen Sie genau auf p-1 = 2·q1·q2·q3·Q. Die q_i sind klein und glatt, "
        "nur Q ist ein großer, nicht faktorisierbarer Rest."
    ],
    placeholder_text=[""],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
)


# ----------------------------------------------------------------------------
# 2.8 — Beweis-Frage: was nutzt man NICHT aus? (gemeinsame Antwort: Q)
# ----------------------------------------------------------------------------
task_02_08 = TaskData(
    day=2,
    points=15,
    day_description="Diffie-Hellman",
    task_description="Challenge 3 — Die glatte Teilstruktur",
    error_cost=1,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=True,
    injectible=False,
    allow_kali=True,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    answers=[
        Correct.create("Q"),
    ],
    question=["Analysieren Sie p-1 Ihrer Challenge-3-Capture."],
    question_further=[
        "Faktorisieren Sie p-1 mit yafu. Es findet die kleinen Primfaktoren "
        "q1, q2, q3 schnell, scheitert aber an einem großen Rest. Wie heißt "
        "(gemäß Kurs-Notation) dieser große Primfaktor, den Sie NICHT ausnutzen? "
        "Geben Sie den Buchstaben ein."
    ],
    placeholder_text=["Buchstabe"],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
    hints=[
        TaskHint.create(0, "In der Theorie wird p-1 = 2·q1·q2·q3·Q geschrieben. Der große Restfaktor trägt einen Großbuchstaben.", 0.6),
        TaskHint.create(0, "Es ist der Buchstabe Q.", 0.2),
    ],
)


# ----------------------------------------------------------------------------
# 2.9 — Challenge 3: Meisterflagge (PH nur auf glattem Teil, a < M)
# ----------------------------------------------------------------------------
task_02_09 = TaskData(
    day=2,
    points=40,
    day_description="Diffie-Hellman",
    task_description="Challenge 3 — Die Meisterflagge",
    error_cost=1,
    allow_reset=True,
    allow_random_order=False,
    allow_download=False,
    allow_link=False,
    allow_vscode=True,
    injectible=False,
    allow_kali=True,
    allow_cyber_range=False,
    master_task=False,
    task_type="input",
    answers=[
        Correct.create("hiy{dh_almost_smooth_the_prime_is_a_lie_4200}"),
    ],
    question=["Bezwingen Sie die Falle und bergen Sie die letzte Flagge."],
    question_further=[
        "Wenden Sie Pohlig-Hellman NUR auf den glatten Teil M = 2·q1·q2·q3 an "
        "(Q bleibt außen vor). Das liefert a mod M. Der Clou: der geheime "
        "Exponent a wurde kleiner als M gewählt, also gilt a mod M = a — Sie haben "
        "a vollständig, ohne Q je zu berühren. Die Größe von p war ein "
        "Ablenkungsmanöver. Entschlüsseln Sie dann wie gewohnt und reichen Sie "
        "die Flagge ein."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""],
    download_path=[""],
    link_text=[""],
    link_path=[""],
    hints=[
        TaskHint.create(0, "Ignorieren Sie Q komplett. Wenden Sie PH+CRT nur mit q1, q2, q3 an — genau wie in Challenge 2.", 0.7),
        TaskHint.create(0, "Der CRT liefert a mod M mit M = 2·q1·q2·q3. Da a < M ist, ist das bereits das vollständige a.", 0.4),
        TaskHint.create(0, "Ab a ist der Weg identisch: s = B^a mod p, Schlüssel ableiten, entschlüsseln, Flagge einreichen.", 0.2),
    ],
)
