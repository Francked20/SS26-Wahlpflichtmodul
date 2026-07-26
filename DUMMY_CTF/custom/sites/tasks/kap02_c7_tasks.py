"""
Tasks for Kapitel 02 — Challenge 7 (ECDH intro, Akt II part 3 / elliptic curves).

Same design as C1-C6: split concept checks, a proof question with a COMMON
answer (real work, not variant-dependent), static flag, no backend.

Numbering: task_02_22 .. task_02_24.
  Challenge 7: 22 (concept WF), 23 (proof: is A on the curve? -> Ja), 24 (flag)

The proof question (2.23) forces the student to implement/use the curve
membership test y^2 == x^3 + a*x + b (mod p) on a real point from their capture.
The answer is the same for everyone (the public point IS on the curve), so it
is not guessable and not variant-dependent — but it requires doing the EC work.
"""

from website.engine.tasks.models import TaskData
from website.engine.tasks.helpers import Correct, Incorrect, TaskHint


def _wf(day_idx, points, desc, question, further, correct_is_true):
    """Single Wahr/Falsch question (matches the C1-C6 helper)."""
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
    """Single Ja/Nein question (matches the C6 helper)."""
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
# CHALLENGE 7 — ECDH intro
# ============================================================================

# 2.22 — concept: ECDLP + small curve
task_02_22 = _wf(
    22, 5, "Challenge 7 — Verständnis",
    "Wahr oder falsch?",
    "Die Sicherheit von ECDH beruht auf dem elliptischen diskreten Logarithmus: "
    "aus G und Q = k·G das geheime k zu bestimmen. Ist die Ordnung der Kurve "
    "klein, lässt sich k durchsuchen — die Kurve ist dann unsicher.",
    correct_is_true=True,
)

# 2.23 — proof: is Alice's public point A on the curve? (common answer: Ja)
task_02_23 = _jn(
    23, 15, "Challenge 7 — Rechnen auf der Kurve",
    "Prüfen Sie einen Punkt.",
    "Nehmen Sie aus Ihrer Capture den öffentlichen Punkt A = "
    "(ALICE_PUBLIC_AX, ALICE_PUBLIC_AY) und die Kurvenparameter a, b, p. "
    "Prüfen Sie die Kurvengleichung: Gilt y² ≡ x³ + a·x + b (mod p) für A? "
    "(So stellen Sie sicher, dass A wirklich ein gültiger Kurvenpunkt ist.)",
    correct_is_yes=True,
)

# 2.24 — flag
task_02_24 = TaskData(
    day=2, points=35, day_description="Diffie-Hellman",
    task_description="Challenge 7 — Die Flagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{ecdh_small_curve_order_bsgs_on_the_curve_e11c}")],
    question=["Brechen Sie den elliptischen Log und bergen Sie die Flagge."],
    question_further=[
        "Die Kurvenordnung n (CURVE_ORDER_N) ist klein (~40 Bit). Lösen Sie das "
        "ECDLP A = a·G mit Baby-Step-Giant-Step auf der Kurve (~√n Schritte). "
        "Da a < n, ist das bereits das vollständige a. Berechnen Sie dann den "
        "gemeinsamen Punkt S = a·B, leiten Sie den Schlüssel aus der "
        "x-Koordinate von S ab (HKDF-SHA256, siehe Capture) und entschlüsseln "
        "Sie den AES-256-GCM-Datensatz. Tipp: Bibliotheken wie tinyec oder "
        "SageMath nehmen Ihnen die Punktarithmetik ab."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "Punktaddition + skalare Multiplikation selbst schreiben oder tinyec/Sage nutzen. BSGS wie in Challenge 1, nur mit Punkten statt Zahlen.", 0.7),
        TaskHint.create(0, "BSGS: Babysteps j·G in eine Tabelle, dann Giantsteps A - i·(m·G) vergleichen. m ≈ √n.", 0.4),
        TaskHint.create(0, "Ab a: S = a·B, dann key = HKDF-SHA256(x(S) als big-endian, ceil(bits(p)/8) Bytes). Danach AES-256-GCM entschlüsseln.", 0.2),
    ],
)
