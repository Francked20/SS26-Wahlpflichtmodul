"""Task definitions for the Beginner version of Chapter 4 ("Schwaches
Diffie-Hellman" / Logjam).

Same underlying attack, same variant pool, same dynamic_check backend as
Francks's challenge_04_tasks.py (custom/challengebackend/dh_export_*) - only
the explanation depth and the code scaffolding differ. Reuses the existing
dynamic_check values ("dh_factors", "dh_server_secret", "dh_master_secret",
"dh_flag") unmodified; no changes to core/backend or challengebackend needed
for this file.

Own day (94), separate from the advanced day=4, so a student can attempt
either chapter independently without task_id collisions.

  94.0 intro -> 94.1 spot the 512-bit p -> 94.2 name Pohlig-Hellman ->
  94.3 factor p-1 (yafu) -> 94.4 discrete log s -> 94.5 TLS master secret ->
  94.6 decrypt the flag.
"""

from website.engine.tasks.models import TaskData
from website.engine.tasks.helpers import Correct, TaskHint

DAY_DESC = "Beginner: Schwaches Diffie-Hellman (Logjam)"


# ----------------------------------------------------------------------------
# 94.0 - Einfuehrung
# ----------------------------------------------------------------------------
task_04b_00 = TaskData(
    day=94, points=5, day_description=DAY_DESC,
    task_description="Einführung: Schwaches Diffie-Hellman",
    error_cost=0,
    allow_reset=False, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=False, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("logjam")],
    question=[
        "Sie greifen jetzt eine echte, historische Sicherheitslücke an: **Logjam** "
        "(2015, CVE-2015-4000). Ein Server bietet aus Kompatibilitätsgründen eine uralte, "
        "absichtlich geschwächte Diffie-Hellman-Variante an (**DHE_EXPORT**) - "
        "mit einer viel zu kleinen Primzahl $p$. Ihre Aufgabe: den TLS-"
        "Handshake mitschneiden, die Schwäche ausnutzen und die verschlüsselte "
        "Nachricht lesen."
    ],
    question_further=[
        "Keine Sorge, falls Ihnen die Begriffe hier neu sind - jeder Schritt "
        "unten hat eine eigene 'Was ist X?'-Box und ein vollständiges, "
        "lauffähiges Code-Gerüst. Sie müssen nicht alles auf einmal verstehen, "
        "nur jeweils den nächsten Schritt.\n\n"
        "**Tippen Sie zur Bestätigung den Namen der Attacke ein (kleingeschrieben).**"
    ],
    placeholder_text=["Name der Attacke..."],
    hints=[
        TaskHint.create(0, "Der Name klingt wie ein 'Stau aus Baumstämmen' im Fluss - ein englisches Wort.", 0.7),
        TaskHint.create(0, "Log-jam: die Attacke auf schwaches Diffie-Hellman von 2015.", 0.4),
        TaskHint.create(0, "Die Antwort lautet: logjam", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 94.1 - Capture: p in Wireshark finden (Bit-Laenge)
# ----------------------------------------------------------------------------
task_04b_01 = TaskData(
    day=94, points=10, day_description=DAY_DESC,
    task_description="Traffic Capture: Wie groß ist p?",
    error_cost=1,
    allow_reset=False, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("512")],
    question=[
        "Laden Sie oben Ihre persönliche Capture (`.pcap`) herunter und öffnen "
        "Sie sie in **Wireshark** (falls noch nicht installiert: "
        "https://www.wireshark.org/download.html)."
    ],
    question_further=[
        "**Schritt für Schritt, ganz genau:**\n\n"
        "1. Wireshark öffnen → `Datei → Öffnen` → Ihre `.pcap`-Datei auswählen.\n"
        "2. Oben ins Filter-Feld eintippen: `tls.handshake` und Enter drücken. "
        "Das blendet HTTP/DNS-Pakete aus, die absichtlich zusätzlich in der "
        "Capture liegen (Ablenkung, gehört nicht zum Angriff).\n"
        "3. In der übrig gebliebenen Paketliste nach einer Zeile suchen, bei "
        "der in der Spalte 'Info' **Server Key Exchange** steht. Anklicken.\n"
        "4. Im unteren Bereich ('Packet Details') öffnet sich ein Baum. Klappen "
        "Sie nacheinander auf (kleines Dreieck ▶ anklicken):\n"
        " `Transport Layer Security` ▶ `TLSv1 Record Layer: Handshake Protocol: "
        "Server Key Exchange` ▶ `Handshake Protocol: Server Key Exchange` ▶ "
        "`Diffie-Hellman Server Params`.\n"
        "5. Dort finden Sie **zwei separate Zeilen**: `p Length: ...` (das ist "
        "die Länge **in Byte**, nicht in Bit!) und direkt darunter `p: <langer "
        "Hex-Wert>` (der eigentliche Wert von $p$). Etwas weiter unten im "
        "selben Baum sehen Sie außerdem `Pubkey: <Hex-Wert>` - das ist der "
        "öffentliche Server-Wert, den wir mathematisch $Y_s$ nennen (in "
        "Wireshark heißt das Feld schlicht 'Pubkey', nicht '$Y_s$').\n\n"
        "**Achtung Zahlenformat:** Wireshark zeigt `p` und `Pubkey` als "
        "**Hexadezimalzahl** (z.B. `933c8383...`). Weiter unten auf dieser "
        "Seite bekommen Sie dieselben Werte später auch als gewöhnliche "
        "**Dezimalzahl** angezeigt - beide Schreibweisen sehen komplett "
        "unterschiedlich aus, meinen aber dieselbe Zahl (Umrechnung in "
        "Python: `int(\"933c8383...\", 16)`).\n\n"
        "**Wichtig:** Der Server verrät $p$, $g$ und $Y_s$ (Wireshark-Feld: "
        "'Pubkey') hier komplett offen im Klartext - das ist bei TLS so "
        "vorgesehen, die Sicherheit soll allein daran hängen, dass $p$ groß "
        "und gut gewählt ist. Genau das ist hier nicht der Fall.\n\n"
        "**Wie viele Bit hat die Primzahl $p$?** (Achtung: `p Length` steht in "
        "Byte da - 1 Byte = 8 Bit.)"
    ],
    placeholder_text=["z.B. 2048"],
    hints=[
        TaskHint.create(0, "Filter: `tls.handshake`, dann nach 'Server Key Exchange' in der Info-Spalte suchen.", 0.7),
        TaskHint.create(0, "Der Pfad im Detail-Baum: TLS → Handshake Protocol: Server Key Exchange → Diffie-Hellman Server Params → p Length.", 0.5),
        TaskHint.create(0, "`p Length` zeigt Byte, nicht Bit - die gesuchte Zahl ist `p Length` mal 8.", 0.3),
        TaskHint.create(0, "Die Antwort lautet: 512", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 94.2 - Pohlig-Hellman benennen
# ----------------------------------------------------------------------------
task_04b_02 = TaskData(
    day=94, points=10, day_description=DAY_DESC,
    task_description="Warum ist das knackbar?",
    error_cost=1,
    allow_reset=False, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=False, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("pohlig-hellman")],
    question=[
        "512 Bit klingt erstmal nach viel - trotzdem ist der diskrete Logarithmus "
        "hier in Sekunden lösbar. Der Grund liegt nicht in der Größe von $p$, "
        "sondern in der **Struktur** von $p-1$."
    ],
    question_further=[
        "**Warum ein 'glattes' $p-1$ alles kaputt macht:**\n\n"
        "Normalerweise ist der diskrete Logarithmus schwer, weil man im "
        "schlimmsten Fall $\\sqrt{p}$ Möglichkeiten durchsuchen müsste - bei "
        "großem $p$ unmöglich viele. Ist $p-1$ aber ein Produkt aus vielen "
        "**kleinen** Primzahlen $q_1, q_2, \\dots$ (\"glatt\"), gilt der **Satz "
        "von Pohlig-Hellman**: Man kann das Problem für **jeden kleinen "
        "Faktor einzeln** lösen (jeweils nur $\\sqrt{q_i}$ Schritte - ein "
        "Kinderspiel) und die Teilergebnisse am Ende mit dem **Chinesischen "
        "Restsatz (CRT)** zum vollständigen Ergebnis zusammensetzen.\n\n"
        "Genau das machen Sie in den nächsten Schritten: erst $p-1$ in seine "
        "kleinen Faktoren zerlegen (Schritt 4), dann für jeden Faktor einzeln "
        "ein winziges Teilproblem lösen (Schritt 5).\n\n"
        "**Frage:** Wie heißt der Algorithmus, der den diskreten Logarithmus "
        "über die kleinen Faktoren von $p-1$ löst?"
    ],
    placeholder_text=["Name des Algorithmus..."],
    hints=[
        TaskHint.create(0, "Zwei Nachnamen mit Bindestrich verbunden, benannt nach den Erfindern (1978).", 0.7),
        TaskHint.create(0, "Er kombiniert die Teil-Logarithmen modulo jedes kleinen Primfaktors per CRT.", 0.4),
        TaskHint.create(0, "Die Antwort lautet: pohlig-hellman", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 94.3 - p-1 faktorisieren mit yafu (dynamic_check, identisch zu Kapitel 4)
# ----------------------------------------------------------------------------
task_04b_03 = TaskData(
    day=94, points=25, day_description=DAY_DESC,
    task_description="p-1 faktorisieren (yafu)",
    error_cost=2,
    allow_reset=False, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    dynamic_check="dh_factors",
    answers=[Correct.create("dynamic")],
    question=[
        "Jetzt wird's praktisch: Zerlegen Sie $p-1$ **Ihrer** Capture (nicht "
        "irgendeiner!) in seine Primfaktoren, mit dem Werkzeug **yafu**."
    ],
    question_further=[
        "**Ihr $p$ finden Sie oben im blauen Kasten** (\"Deine persönlichen "
        "DH-Parameter\") - direkt als Zahl zum Kopieren, kein erneutes "
        "Wireshark-Gefummel nötig.\n\n"
        "**Schritt für Schritt (im Terminal, z.B. in der Kali-Umgebung dieser "
        "Aufgabe):** Ziehen Sie zuerst 1 von $p$ ab - das geht bei einer so "
        "langen Zahl im Kopf (einfach die letzte Ziffer um 1 verringern), "
        "kein Taschenrechner nötig. Das Ergebnis faktorisieren Sie dann mit "
        "yafu:\n\n"
        "```bash\n"
        "echo \"factor(<IHR_P_MINUS_1>)\" | yafu\n"
        "```\n\n"
        "**Wichtig:** yafu als reines Kommandozeilen-Argument "
        "(`yafu \"factor(...)\"`) funktioniert **nicht** - es beendet sich "
        "sofort, ohne zu rechnen. Der Ausdruck muss per `echo ... | yafu` an "
        "die Standardeingabe übergeben werden.\n\n"
        "yafu druckt am Ende eine Liste aller Primfaktoren. Weil $p-1$ hier "
        "**absichtlich glatt** ist (nur kleine Faktoren, keiner davon riesig), "
        "ist yafu in wenigen Sekunden fertig - bei einer 'normalen' Zahl "
        "dieser Größe würde das nie fertig werden.\n\n"
        "**Kein yafu zur Hand (z.B. lokal auf macOS, kein offizieller Build "
        "verfügbar)?** Weil $p-1$ so klein-faktorig ist, liefert `sympy` "
        "dieselbe Antwort genauso zuverlässig:\n"
        "```python\n"
        "from sympy import factorint\n"
        "print(factorint(p - 1))\n"
        "```\n\n"
        "**Kontrolle, bevor Sie abgeben:** Multiplizieren Sie alle gefundenen "
        "Faktoren miteinander - das Ergebnis muss wieder exakt $p-1$ ergeben. "
        "Fehlt ein Faktor, klappt die nächste Aufgabe nicht.\n\n"
        "**Antwortformat:** alle Primfaktoren, kommagetrennt, Reihenfolge "
        "egal, der Faktor 2 ist optional. Beispiel: `2,1009,3221,...`"
    ],
    placeholder_text=["q1,q2,q3,..."],
    hints=[
        TaskHint.create(0, "Erst p-1 ausrechnen, DANN faktorisieren - nicht p selbst (p ist eine Primzahl, die lässt sich nicht weiter zerlegen).", 0.7),
        TaskHint.create(0, "yafu-Aufruf: `echo \"factor(N)\" | yafu` mit N = Ihrem ausgerechneten p-1 (NICHT als reines Kommandozeilen-Argument). Kein yafu verfügbar? `sympy.factorint(p - 1)` reicht hier genauso.", 0.5),
        TaskHint.create(0, "Selbstkontrolle: Produkt aller gefundenen Faktoren muss exakt p-1 ergeben (mit Python leicht nachrechenbar: `import math; math.prod([...])`).", 0.3),
        TaskHint.create(0, "Format: Dezimalzahlen mit Komma getrennt, z.B. 2,1009,3221,50021", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 94.4 - Diskreter Logarithmus via Pohlig-Hellman (dynamic_check)
# ----------------------------------------------------------------------------
task_04b_04 = TaskData(
    day=94, points=30, day_description=DAY_DESC,
    task_description="Diskreter Logarithmus (Pohlig-Hellman)",
    error_cost=2,
    allow_reset=False, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    dynamic_check="dh_server_secret",
    answers=[Correct.create("dynamic")],
    question=[
        "Jetzt lösen Sie das eigentliche Rätsel: Finden Sie das geheime $s$ "
        "des Servers, für das $Y_s = g^s \\bmod p$ gilt. Das Code-Gerüst unten "
        "ist komplett fertig - bis auf **eine** Lücke, die genau die Idee aus "
        "Schritt 3 (Pohlig-Hellman) umsetzt."
    ],
    question_further=[
        "Die Vorgehensweise und das vollständige Skript stehen ausführlich im "
        "Kasten 'Schritt 5' oben - dort ist auch die einzige Lücke markiert "
        "(`teilproblem_werte`)."
    ],
    placeholder_text=["s (Dezimalzahl)"],
    hints=[
        TaskHint.create(0,
            "Hinweis zur Lücke: 'Reduzieren' heißt, g und Ys mit dem Exponenten "
            "(p-1)/q zu potenzieren - dieselbe Formel steht in der Erklärbox aus "
            "Schritt 3 (Pohlig-Hellman) und im Kommentar direkt über der Lücke.",
            0.6),
        TaskHint.create(0,
            "Fast-Lösung: `gi = pow(g, (p - 1) // q, p)` und `hi = pow(Ys, (p - 1) // q, p)`.",
            0.3),
        TaskHint.create(0,
            "Kontrolle: Nach dem Ausführen muss `pow(g, s, p) == Ys` gelten - "
            "das Skript prüft das bereits automatisch für Sie und meldet es.",
            0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 94.5 - TLS Master Secret (dynamic_check)
# ----------------------------------------------------------------------------
task_04b_05 = TaskData(
    day=94, points=25, day_description=DAY_DESC,
    task_description="Das TLS Master Secret berechnen",
    error_cost=2,
    allow_reset=False, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    dynamic_check="dh_master_secret",
    answers=[Correct.create("dynamic")],
    question=[
        "Sie kennen jetzt $s$. Damit berechnen Sie dasselbe gemeinsame Geheimnis, "
        "das auch Server und Client beim echten Handshake berechnet haben - und "
        "daraus das TLS **Master Secret**."
    ],
    question_further=[
        "Die Vorgehensweise und das vollständige Skript (nur eine Lücke: die "
        "Formel für $Z$) stehen im Kasten 'Schritt 6' oben."
    ],
    placeholder_text=["Master Secret als Hex..."],
    hints=[
        TaskHint.create(0,
            "Hinweis zur Lücke: dasselbe Diffie-Hellman-Prinzip wie immer - "
            "diesmal mit dem Client-Wert Yc (aus Ihrer Capture) und Ihrem "
            "gefundenen s als Exponent.",
            0.6),
        TaskHint.create(0, "Fast-Lösung: `Z = pow(Yc, s, p)`.", 0.3),
        TaskHint.create(0,
            "Kontrolle in Wireshark: Master Secret unter Preferences → Protocols "
            "→ TLS → (Pre)-Master-Secret log filename eintragen - entschlüsselt "
            "Wireshark danach die Application Data, stimmt Ihr Wert.",
            0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 94.6 - Flag entschluesseln (dynamic_check)
# ----------------------------------------------------------------------------
task_04b_06 = TaskData(
    day=94, points=15, day_description=DAY_DESC,
    task_description="Die Flagge entschlüsseln",
    error_cost=1,
    allow_reset=False, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    dynamic_check="dh_flag",
    answers=[Correct.create("dynamic")],
    question=[
        "Letzter Schritt: aus dem Master Secret die Sitzungsschlüssel ableiten "
        "und damit die verschlüsselten Daten im Capture entschlüsseln - die "
        "Flagge steckt im letzten Datensatz."
    ],
    question_further=[
        "Das komplette, fertige Skript (keine Lücke mehr, nur noch "
        "`finished_ciphertext` und `application_data_ciphertext` aus Ihrem "
        "Capture einsetzen) steht im Kasten 'Schritt 7' oben."
    ],
    placeholder_text=["crypto{...}"],
    hints=[
        TaskHint.create(0, "Wenn Ihr Master Secret aus Schritt 6 stimmt, läuft dieses Skript ohne Änderungen durch.", 0.6),
        TaskHint.create(0, "Die Flagge liegt im letzten entschlüsselten Datensatz, den der Server an den Client schickt.", 0.35),
        TaskHint.create(0, "Bekommen Sie eine falsche MAC-Prüfung? Dann stimmt vermutlich s oder das Master Secret aus einem vorigen Schritt nicht.", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)
