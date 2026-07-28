"""
Tasks for Kapitel 02 — Challenge 6 (Man-in-the-Middle).

Numbering: task_02_19 .. task_02_21.
  Challenge 6: 19 (concept WF), 20 (detection Ja/Nein), 21 (flag)

The flag is split across the two decrypted directions (Anna->Bob and
Bob->Anna); the student must decrypt BOTH records with the two MITM session
keys and concatenate the halves.
"""

from website.engine.tasks.models import TaskData
from website.engine.tasks.helpers import Correct, Incorrect, TaskHint


def _wf(day_idx, points, desc, question, further, correct_is_true):
    """Single Wahr/Falsch question (matches the C1-C5 helper)."""
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


def _jn(day_idx, points, desc, question, further, correct_is_yes):
    """Single Ja/Nein question — used for the MITM detection check."""
    if correct_is_yes:
        answers = [Correct.create("Ja"), Incorrect.create("Nein")]
    else:
        answers = [Incorrect.create("Ja"), Correct.create("Nein")]
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
# CHALLENGE 6 — Man-in-the-Middle
# ============================================================================

# 2.19 — concept: MITM works despite unbreakable DLP
task_02_19 = _wf(
    19, 5, "Challenge 6 - Verständnis",
    "Wahr oder falsch?",
    "Ein Man-in-the-Middle-Angriff auf Diffie-Hellman funktioniert selbst dann, "
    "wenn der diskrete Logarithmus praktisch unlösbar ist — denn der Angreifer "
    "bricht das DLP gar nicht, sondern führt zwei getrennte Handshakes.",
    correct_is_true=True,
)

# 2.20 — detection: does the key Anna sees match Bob's real key? (answer: Nein)
task_02_20 = _jn(
    20, 15, "Challenge 6 - Nachweis des Angriffs",
    "Weisen Sie den Angriff nach.",
    "Vergleichen Sie in Ihrer Capture den Wert MALLORY_TO_ALICE_M1 (den Anna "
    "für „Bobs Schlüssel“ hält) mit BOB_PUBLIC_B (Bobs echtem öffentlichem "
    "Wert). Stimmen die beiden Werte überein? (Ihre Antwort ist zugleich der "
    "Beweis: Stimmen sie NICHT überein, sitzt jemand in der Mitte.)",
    correct_is_yes=False,
)

# 2.21 — flag (split across both directions)
task_02_21 = TaskData(
    day=2, points=40, day_description="Diffie-Hellman",
    task_description="Challenge 6 — Die Flagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{dh_mitm_you_are_the_man_in_the_middle_2a2b}")],
    question=["Entschlüsseln Sie beide Richtungen und bergen Sie die Flagge."],
    question_further=[
        "Sie sind Mallory. Ihre Capture enthält Ihre Geheimnisse m1 und m2 "
        "sowie die echten Werte A (Anna) und B (Bob). Berechnen Sie die zwei "
        "Sitzungsschlüssel: s1 = A^m1 mod p (Richtung Anna) und s2 = B^m2 mod p "
        "(Richtung Bob). Leiten Sie aus jedem per HKDF-SHA256 einen Schlüssel "
        "ab und entschlüsseln Sie BEIDE Datensätze (RECORD_AB_* und "
        "RECORD_BA_*). Jede Richtung enthält eine HÄLFTE der Flagge — setzen "
        "Sie beide Teile zur vollständigen Flagge zusammen. Der diskrete "
        "Logarithmus wird dabei NIE gebrochen."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "Kein DLP nötig! Sie kennen m1 und m2 direkt. s1 = pow(A, m1, p), s2 = pow(B, m2, p).", 0.7),
        TaskHint.create(0, "Zwei Schlüssel, zwei Datensätze: RECORD_AB mit dem Anna-Schlüssel (s1), RECORD_BA mit dem Bob-Schlüssel (s2).", 0.4),
        TaskHint.create(0, "flag_teil_1 (aus Anna->Bob) + flag_teil_2 (aus Bob->Anna) ergeben zusammen die vollständige Flagge.", 0.2),
    ],
)
