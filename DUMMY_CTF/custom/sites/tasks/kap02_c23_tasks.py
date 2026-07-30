"""Tasks fuer Kapitel 02 - Challenge 2 und 3"""

from website.engine.tasks.models import TaskData
from website.engine.tasks.helpers import Correct, Incorrect, TaskHint


def _wf(day_idx, points, desc, question, further, correct_is_true):
    """Helper: a single Wahr/Falsch question"""
    if correct_is_true:
        answers = [Correct.create("Wahr"), Incorrect.create("Falsch")]
    else:
        answers = [Incorrect.create("Wahr"), Correct.create("Falsch")]
    return TaskData(
        day=2, points=points, day_description="Diffie-Hellman",
        task_description=desc, error_cost=0,
        allow_reset=True, allow_random_order=False,
        allow_download=False, allow_link=False, allow_vscode=False,
        injectible=False, allow_kali=False, allow_cyber_range=False,
        master_task=False, task_type="select",
        answers=answers,
        question=[question], question_further=[further],
        placeholder_text=[""], download_text=[""], download_path=[""],
        link_text=[""], link_path=[""],
    )


# ============================================================================
# CHALLENGE 2 — Die glatte Ordnung
# ============================================================================

# 2.6 — concept: smooth order (1/2)
task_02_06 = _wf(
    6, 5, "Challenge 2 — Verständnis (1/2)",
    "Wahr oder falsch?",
    "Für die Sicherheit ist nicht die Größe von p entscheidend, sondern die "
    "Primfaktorzerlegung von p-1.",
    correct_is_true=True,
)

# 2.7 — concept: smooth order (2/2, false)
task_02_07 = _wf(
    7, 5, "Challenge 2 — Verständnis (2/2)",
    "Wahr oder falsch?",
    "Ein sehr großes p garantiert immer Sicherheit, unabhängig von der Struktur "
    "von p-1.",
    correct_is_true=False,
)

# 2.8 — proof: number of non-trivial prime factors (common answer: 3)
task_02_08 = TaskData(
    day=2, points=15, day_description="Diffie-Hellman",
    task_description="Challenge 2 — Faktorisieren", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("3")],
    question=["Faktorisieren Sie p-1 Ihrer Challenge-2-Capture."],
    question_further=[
        "p ist groß (ca. 120 Bit) — von Hand nicht faktorisierbar, aber yafu "
        "erledigt es in Sekunden. Faktorisieren Sie p-1. Wie viele "
        "NICHT-TRIVIALE Primfaktoren (also ohne die 2) hat p-1? Geben Sie die "
        "Anzahl als Zahl ein."
    ],
    placeholder_text=["Anzahl (Zahl)"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "In Kali/VSCode: 'yafu' starten und factor(p-1) eingeben.", 0.7),
        TaskHint.create(0, "p-1 ist gerade (Faktor 2). Zählen Sie nur die übrigen großen Primfaktoren.", 0.4),
    ],
)

# 2.9 — flag (unlocks Challenge 3)
task_02_09 = TaskData(
    day=2, points=30, day_description="Diffie-Hellman",
    task_description="Challenge 2 — Die Flagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{dh_smooth_order_pohlig_hellman_1337}")],
    question=["Lösen Sie das DLP mit Pohlig-Hellman und bergen Sie die Flagge."],
    question_further=[
        "Projizieren Sie das Problem in jede prime Untergruppe "
        "(g_q = g^((p-1)/q) mod p, analog A_q), lösen Sie dort je ein kleines "
        "DLP (BSGS) und setzen Sie die Ergebnisse per CRT zu a zusammen. Dann "
        "wie in Challenge 1: s = B^a mod p, Schlüssel ableiten, entschlüsseln, "
        "Flagge einreichen. Mit dieser Flagge schalten Sie Challenge 3 frei."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "g^((p-1)/q) mod p erzeugt ein Element der Ordnung q — dort ist der Log klein.", 0.7),
        TaskHint.create(0, "Sie erhalten a mod q1, a mod q2, a mod q3. Der CRT kombiniert sie zu a.", 0.4),
        TaskHint.create(0, "Ab hier identisch zu Challenge 1: gemeinsames Geheimnis, Schlüssel, Entschlüsselung.", 0.2),
    ],
)


# ============================================================================
# CHALLENGE 3 — Die Falle
# ============================================================================

# 2.10 — concept: the trap
task_02_10 = _wf(
    10, 5, "Challenge 3 — Verständnis",
    "Wahr oder falsch?",
    "Wenn p-1 einen großen, nicht faktorisierbaren Primfaktor Q enthält, aber "
    "der geheime Exponent klein ist, genügt der glatte Teil von p-1 zum Angriff.",
    correct_is_true=True,
)

# 2.11 — proof: which factor is NOT exploited (common answer: Q)
task_02_11 = TaskData(
    day=2, points=15, day_description="Diffie-Hellman",
    task_description="Challenge 3 — Die glatte Teilstruktur", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("Q")],
    question=["Analysieren Sie p-1 Ihrer Challenge-3-Capture."],
    question_further=[
        "Faktorisieren Sie p-1 mit yafu. Es findet die kleinen Primfaktoren "
        "schnell, scheitert aber an einem großen Rest. Wie heißt (gemäß "
        "Kurs-Notation) dieser große Primfaktor, den Sie NICHT ausnutzen? "
        "Geben Sie den Buchstaben ein."
    ],
    placeholder_text=["Buchstabe"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "In der Theorie steht p-1 = 2·q1·q2·q3·Q. Der große Rest trägt einen Großbuchstaben.", 0.6),
        TaskHint.create(0, "Es ist der Buchstabe Q.", 0.2),
    ],
)

# 2.12 — final flag
task_02_12 = TaskData(
    day=2, points=40, day_description="Diffie-Hellman",
    task_description="Challenge 3 — Die Meisterflagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{dh_almost_smooth_the_prime_is_a_lie_4200}")],
    question=["Bezwingen Sie die Falle und bergen Sie die letzte Flagge."],
    question_further=[
        "Wenden Sie Pohlig-Hellman NUR auf den glatten Teil M = 2·q1·q2·q3 an "
        "(Q bleibt außen vor). Das liefert a mod M. Der Clou: der geheime "
        "Exponent a wurde kleiner als M gewählt, also gilt a mod M = a — Sie "
        "haben a vollständig, ohne Q zu berühren. Entschlüsseln Sie dann wie "
        "gewohnt und reichen Sie die Flagge ein."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "Ignorieren Sie Q komplett. Wenden Sie PH+CRT nur mit q1, q2, q3 an — wie in Challenge 2.", 0.7),
        TaskHint.create(0, "Der CRT liefert a mod M mit M = 2·q1·q2·q3. Da a < M, ist das bereits das vollständige a.", 0.4),
        TaskHint.create(0, "Ab a identisch: s = B^a mod p, Schlüssel ableiten, entschlüsseln, Flagge einreichen.", 0.2),
    ],
)
