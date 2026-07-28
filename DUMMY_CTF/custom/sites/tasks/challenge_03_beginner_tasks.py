"""Task definitions for the Beginner version of Chapter 3 ("Export Ciphers &
FREAK").

Same underlying attack, same variant pool, same dynamic_check backend as
Jonas' challenge_03_tasks.py (custom/challengebackend/export_cipher_*) -
reuses its existing endpoints unmodified; no changes to core/backend or
challengebackend needed for this file. Reuses the existing dynamic_check
values ("export_factor256", "export_factor512", "export_master_secret",
"export_flag") unmodified.

Own day (95), separate from the advanced day=3, so a student can attempt
either chapter independently without task_id collisions.

  95.0 intro -> 95.1 spot the 512-bit RSA key -> 95.2 factor the 256-bit
  practice N -> 95.3 find the second factor of the real N -> 95.4 TLS
  master secret (RSA private key + PRF) -> 95.5 decrypt the flag.
"""

from website.engine.tasks.models import TaskData
from website.engine.tasks.helpers import Correct, TaskHint

DAY_DESC = "Beginner: Export Ciphers & FREAK"


# ----------------------------------------------------------------------------
# 95.0 - Einfuehrung
# ----------------------------------------------------------------------------
task_03b_00 = TaskData(
    day=95, points=5, day_description=DAY_DESC,
    task_description="Einführung: Export-Kryptografie",
    error_cost=0,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=False, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("freak")],
    question=[
        "Sie greifen jetzt eine echte, historische Sicherheitslücke an: **FREAK** "
        "(2015, CVE-2015-0204). Ein Server bietet aus Kompatibilitätsgründen eine "
        "uralte, absichtlich geschwächte RSA-Variante an (**RSA_EXPORT**) — mit "
        "einem viel zu kleinen Schlüssel. Ihre Aufgabe: den TLS-Handshake "
        "mitschneiden, die Schwäche ausnutzen und die verschlüsselte Nachricht "
        "lesen."
    ],
    question_further=[
        "Keine Sorge, falls Ihnen die Begriffe hier neu sind — jeder Schritt "
        "unten hat eine eigene 'Was ist X?'-Box und ein vollständiges, "
        "lauffähiges Code-Gerüst. Sie müssen nicht alles auf einmal verstehen, "
        "nur jeweils den nächsten Schritt.\n\n"
        "**Tippen Sie zur Bestätigung den Namen der Attacke ein (kleingeschrieben).**"
    ],
    placeholder_text=["Name der Attacke..."],
    hints=[
        TaskHint.create(0, "Der Name klingt wie das englische Wort für 'verrückt/panisch'.", 0.7),
        TaskHint.create(0, "F.R.E.A.K. ist ein Akronym — schauen Sie sich die Einleitung nochmal genau an.", 0.4),
        TaskHint.create(0, "Die Antwort lautet: freak", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 95.1 - Capture: RSA-Schluessellaenge in Wireshark finden
# ----------------------------------------------------------------------------
task_03b_01 = TaskData(
    day=95, points=10, day_description=DAY_DESC,
    task_description="Traffic Capture: Wie groß ist der RSA-Schlüssel?",
    error_cost=1,
    allow_reset=True, allow_random_order=False,
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
        "2. Oben ins Filter-Feld eintippen: `tls.handshake` und Enter drücken.\n"
        "3. In der Paketliste nach einer Zeile suchen, bei der in der Spalte "
        "'Info' **Certificate** steht. Anklicken.\n"
        "4. Im unteren Bereich ('Packet Details') aufklappen: "
        "`Transport Layer Security` ▶ `TLSv1 Record Layer: Handshake Protocol: "
        "Certificate` ▶ `Handshake Protocol: Certificate` ▶ `Certificates` ▶ "
        "`Certificate` ▶ `signedCertificate` ▶ `subjectPublicKeyInfo` ▶ "
        "`subjectPublicKey: RSAPublicKey` ▶ `modulus`.\n"
        "5. Dort finden Sie **zwei separate Zeilen**: eine Längenangabe **in "
        "Byte** und direkt darunter den eigentlichen Hex-Wert des Modulus $N$.\n\n"
        "**Achtung Zahlenformat:** Wireshark zeigt $N$ als **Hexadezimalzahl** "
        "(z.B. `a1b2c3...`). Weiter unten auf dieser Seite bekommen Sie densel"
        "ben Wert später auch als gewöhnliche **Dezimalzahl** — beide "
        "Schreibweisen sehen komplett unterschiedlich aus, meinen aber "
        "dieselbe Zahl (Umrechnung in Python: `int(\"a1b2c3...\", 16)`).\n\n"
        "**Wichtig:** Der Server verrät seinen öffentlichen RSA-Schlüssel "
        "$(N, e)$ hier komplett offen im Zertifikat — das ist bei TLS so "
        "vorgesehen, die Sicherheit soll allein daran hängen, dass $N$ groß "
        "genug ist, um es nicht faktorisieren zu können. Genau das ist hier "
        "nicht der Fall.\n\n"
        "**Wie viele Bit hat der RSA-Schlüssel?** (Länge steht in Byte da — "
        "1 Byte = 8 Bit.)"
    ],
    placeholder_text=["z.B. 2048"],
    hints=[
        TaskHint.create(0, "Filter: `tls.handshake`, dann nach 'Certificate' in der Info-Spalte suchen.", 0.7),
        TaskHint.create(0, "Der Pfad im Detail-Baum: TLS → Certificate → subjectPublicKeyInfo → RSAPublicKey → modulus.", 0.5),
        TaskHint.create(0, "Die Längenangabe steht in Byte, nicht Bit — die gesuchte Zahl ist Länge mal 8.", 0.3),
        TaskHint.create(0, "Die Antwort lautet: 512", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 95.2 - 256-Bit Uebungszahl faktorisieren (dynamic_check)
# ----------------------------------------------------------------------------
task_03b_02 = TaskData(
    day=95, points=25, day_description=DAY_DESC,
    task_description="Aufwärmübung: 256-Bit faktorisieren",
    error_cost=2,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    dynamic_check="export_factor256",
    answers=[Correct.create("dynamic")],
    question=[
        "Den echten 512-Bit-Schlüssel direkt zu faktorisieren würde selbst mit "
        "yafu ein bis zwei Tage dauern. Deshalb bekommen Sie zuerst eine "
        "**eigene, kleinere 256-Bit-Zahl** $N_{256}$ zum Üben — die finden Sie "
        "oben im blauen Kasten."
    ],
    question_further=[
        "**Warum das nicht nur Übung ist:** Wenn Sie $N_{256}$ erfolgreich "
        "faktorisieren, bekommen Sie automatisch **einen Faktor Ihres echten, "
        "512-Bit-Schlüssels geschenkt** — eine Abkürzung für den nächsten "
        "Schritt. Das ist kein Zufall, sondern didaktische Absicht: Sie müssen "
        "nie die volle 512-Bit-Zahl faktorisieren.\n\n"
        "**Mit yafu (in der Kali-Umgebung, Button 'Kali' bei dieser Aufgabe):**\n"
        "```bash\n"
        "yafu \"factor(<IHR_N256>)\"\n"
        "```\n"
        "Bei 256 Bit (~77 Dezimalstellen) liefert yafu die Faktoren "
        "typischerweise in unter einer Minute.\n\n"
        "**Kein yafu zur Hand (z.B. lokal auf macOS, kein offizieller Build "
        "verfügbar)?** Weil $N_{256}$ hier bewusst klein genug ist, reicht "
        "auch reines Python:\n"
        "```python\n"
        "from sympy import factorint\n"
        "print(factorint(n256))\n"
        "```\n\n"
        "**Kontrolle, bevor Sie abgeben:** Multiplizieren Sie beide Faktoren — "
        "das Ergebnis muss wieder exakt $N_{256}$ ergeben.\n\n"
        "**Antwortformat:** beide Primfaktoren, kommagetrennt (Reihenfolge "
        "egal), z.B. `12345,67890`."
    ],
    placeholder_text=["p,q"],
    hints=[
        TaskHint.create(0, "yafu-Aufruf: `yafu \"factor(N)\"` mit N = Ihrer 256-Bit-Zahl von oben.", 0.7),
        TaskHint.create(0, "Kein yafu? `sympy.factorint(n256)` liefert dasselbe Ergebnis.", 0.5),
        TaskHint.create(0, "Selbstkontrolle: Produkt beider Faktoren muss exakt N_256 ergeben.", 0.3),
        TaskHint.create(0, "Format: zwei Dezimalzahlen mit Komma getrennt, z.B. 12345,67890", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 95.3 - Zweiten Faktor des echten N berechnen (dynamic_check)
# ----------------------------------------------------------------------------
task_03b_03 = TaskData(
    day=95, points=15, day_description=DAY_DESC,
    task_description="Den zweiten Faktor berechnen",
    error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    dynamic_check="export_factor512",
    answers=[Correct.create("dynamic")],
    question=[
        "Sie kennen jetzt einen Faktor $p$ Ihres echten 512-Bit-Moduls $N$ — "
        "er wurde Ihnen nach der letzten Aufgabe angezeigt (siehe Kasten oben). "
        "$N$ selbst kennen Sie schon aus Schritt 2 (Wireshark) bzw. finden es "
        "auch im blauen Kasten oben als Dezimalzahl."
    ],
    question_further=[
        "Das Code-Gerüst unten ist komplett fertig — bis auf **eine** Lücke: "
        "die Formel, mit der Sie aus $N$ und $p$ den fehlenden Faktor $q$ "
        "berechnen. Die Vorgehensweise steht ausführlich im Kasten 'Schritt 4' "
        "oben."
    ],
    placeholder_text=["q"],
    hints=[
        TaskHint.create(0, "Wenn N = p * q und Sie p kennen, ist q eine einzige Ganzzahldivision.", 0.6),
        TaskHint.create(0, "Fast-Lösung: `q = n512 // p`.", 0.3),
        TaskHint.create(0, "Kontrolle: `n512 % p512` muss 0 ergeben, sonst haben Sie den falschen Faktor.", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 95.4 - TLS Master Secret (RSA-Privatschluessel + PRF) (dynamic_check)
# ----------------------------------------------------------------------------
task_03b_04 = TaskData(
    day=95, points=25, day_description=DAY_DESC,
    task_description="Das TLS Master Secret berechnen",
    error_cost=2,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    dynamic_check="export_master_secret",
    answers=[Correct.create("dynamic")],
    question=[
        "Sie kennen jetzt beide Primfaktoren $p$ und $q$ von $N$. Damit können "
        "Sie den privaten RSA-Schlüssel $d$ des Servers berechnen — und damit "
        "die verschlüsselte Sitzung brechen."
    ],
    question_further=[
        "Die Vorgehensweise und das vollständige Skript stehen ausführlich im "
        "Kasten 'Schritt 5' oben — dort ist auch die einzige Lücke markiert "
        "(die Formel für den privaten Schlüssel $d$)."
    ],
    placeholder_text=["Master Secret als Hex..."],
    hints=[
        TaskHint.create(0,
            "Hinweis zur Lücke: $d$ ist das modulare Inverse von $e$ modulo "
            "$\\varphi(N) = (p-1)(q-1)$ — genau die Formel aus der 'Was ist "
            "RSA?'-Box oben.",
            0.6),
        TaskHint.create(0, "Fast-Lösung: `d = pow(e, -1, phi)` (Python 3.8+ kann das direkt).", 0.3),
        TaskHint.create(0,
            "Kontrolle in Wireshark: Master Secret unter Preferences → Protocols "
            "→ TLS → (Pre)-Master-Secret log filename eintragen — entschlüsselt "
            "Wireshark danach die Application Data, stimmt Ihr Wert.",
            0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)


# ----------------------------------------------------------------------------
# 95.5 - Flag entschluesseln (dynamic_check)
# ----------------------------------------------------------------------------
task_03b_05 = TaskData(
    day=95, points=15, day_description=DAY_DESC,
    task_description="Die Flagge entschlüsseln",
    error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=False,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    dynamic_check="export_flag",
    answers=[Correct.create("dynamic")],
    question=[
        "Letzter Schritt: aus dem Master Secret die Sitzungsschlüssel ableiten "
        "und damit die verschlüsselten Daten im Capture entschlüsseln — die "
        "Flagge steckt im letzten Datensatz."
    ],
    question_further=[
        "Das komplette, fertige Skript (keine Lücke mehr — hier ist nur noch "
        "wichtig, dass Sie es verstehen und ausführen) steht im Kasten "
        "'Schritt 6' oben."
    ],
    placeholder_text=["crypto{...}"],
    hints=[
        TaskHint.create(0, "Wenn Ihr Master Secret aus Schritt 5 stimmt, läuft dieses Skript ohne Änderungen durch.", 0.6),
        TaskHint.create(0, "Die Flagge liegt im letzten entschlüsselten Datensatz, den der Server an den Client schickt.", 0.35),
        TaskHint.create(0, "Bekommen Sie eine falsche MAC-Prüfung? Dann stimmt vermutlich d oder das Master Secret aus einem vorigen Schritt nicht.", 0.15),
    ],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
)
