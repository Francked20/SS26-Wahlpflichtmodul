"""
Tasks for Kapitel 02 — Challenge 4 and 5 (Akt II, part 1).

Same design: split Wahr/Falsch concept checks, proof questions with a common
answer, static flag. No backend.

Numbering: task_02_13 .. task_02_18.
  Challenge 4 (small subgroup): 13 (WF), 14 (proof: order of g), 15 (flag)
  Challenge 5 (Logjam):         16 (WF), 17 (WF), 18 (flag)
"""

from website.engine.tasks.models import TaskData
from website.engine.tasks.helpers import Correct, Incorrect, TaskHint


def _wf(day_idx, points, desc, question, further, correct_is_true):
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
# CHALLENGE 4 — Der schwache Erzeuger (small subgroup)
# ============================================================================

# 2.13 — concept: weak generator
task_02_13 = _wf(
    13, 5, "Challenge 4 — Verständnis",
    "Wahr oder falsch?",
    "Selbst wenn p sehr groß ist, kann das Geheimnis schwach sein, wenn der "
    "Erzeuger g nur eine kleine Ordnung hat.",
    correct_is_true=True,
)

# 2.14 — proof: order of g (common answer: q, the small subgroup order)
# The student must actually compute ord(g); the ANSWER is the numeric order,
# which is variant-dependent... so instead we ask a CONCEPT-level proof with a
# common answer: the relationship g^q = 1.
task_02_14 = TaskData(
    day=2, points=15, day_description="Diffie-Hellman",
    task_description="Challenge 4 — Die Ordnung von g", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("1")],
    question=["Bestimmen Sie die Ordnung des Erzeugers g."],
    question_further=[
        "Faktorisieren Sie p-1. Es hat die Form 2·q·R. Der Erzeuger g hat die "
        "kleine Ordnung q. Berechnen Sie g^q mod p — welchen Wert erhalten Sie? "
        "(Das beweist, dass q die Ordnung von g ist.)"
    ],
    placeholder_text=["Wert von g^q mod p"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "Ein Element der Ordnung q erfüllt definitionsgemäß g^q ≡ ? (mod p).", 0.6),
        TaskHint.create(0, "Die Ordnung ist die kleinste Zahl t mit g^t ≡ 1. Also ist g^q ≡ 1.", 0.3),
    ],
)

# 2.15 — flag (unlocks Challenge 5)
task_02_15 = TaskData(
    day=2, points=30, day_description="Diffie-Hellman",
    task_description="Challenge 4 — Die Flagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{dh_small_subgroup_the_generator_betrayed_you_5150}")],
    question=["Brechen Sie Challenge 4 über die kleine Untergruppe."],
    question_further=[
        "Der Erzeuger g hat die kleine Ordnung q (aus p-1 = 2·q·R). Lösen Sie "
        "g^a ≡ A (mod p) per BSGS in der Untergruppe der Ordnung q. Da a < q, "
        "ist das bereits das vollständige a. Dann wie gewohnt: s = B^a mod p, "
        "Schlüssel ableiten, entschlüsseln. Mit dieser Flagge schalten Sie "
        "Challenge 5 frei."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "q ist der kleine Primfaktor von p-1 (neben 2 und dem großen Rest R).", 0.7),
        TaskHint.create(0, "BSGS in der Untergruppe der Ordnung q braucht nur ca. sqrt(q) Schritte.", 0.4),
        TaskHint.create(0, "Ab a identisch zu den vorigen Challenges: s = B^a mod p, Schlüssel, entschlüsseln.", 0.2),
    ],
)


# ============================================================================
# CHALLENGE 5 — Logjam-Echo (export-grade)
# ============================================================================

# 2.16 — concept: export crypto (1/2)
task_02_16 = _wf(
    16, 5, "Challenge 5 — Verständnis (1/2)",
    "Wahr oder falsch?",
    "Logjam nutzt absichtlich geschwächte, standardisierte DH-Gruppen aus — das "
    "Diffie-Hellman-Gegenstück zur RSA-Export-Schwäche von FREAK.",
    correct_is_true=True,
)

# 2.17 — concept: shared weak group (2/2)
task_02_17 = _wf(
    17, 5, "Challenge 5 — Verständnis (2/2)",
    "Wahr oder falsch?",
    "Weil dieselbe schwache Gruppe von vielen Systemen geteilt wird, amortisiert "
    "sich eine einmalige Vorberechnung über alle betroffenen Sitzungen.",
    correct_is_true=True,
)

# 2.18 — flag (final of Akt II part 1)
task_02_18 = TaskData(
    day=2, points=30, day_description="Diffie-Hellman",
    task_description="Challenge 5 — Die Flagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{dh_logjam_export_grade_is_a_backdoor_1996}")],
    question=["Brechen Sie die schwache Export-Gruppe und bergen Sie die Flagge."],
    question_further=[
        "Die Export-Primzahl ist klein und hat glatte Ordnung. Wenden Sie "
        "Pohlig-Hellman + CRT an (wie in Challenge 2): p-1 faktorisieren (yafu), "
        "in prime Untergruppen projizieren, kleine DLP lösen, per CRT "
        "kombinieren. Dann s = B^a mod p, Schlüssel ableiten, entschlüsseln."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "Die Technik ist identisch zu Challenge 2 — nur der Kontext (Export-Gruppe) ist neu.", 0.7),
        TaskHint.create(0, "yafu factor(p-1), dann Pohlig-Hellman über die Primfaktoren, dann CRT.", 0.4),
        TaskHint.create(0, "Ab a: s = B^a mod p, HKDF-Schlüssel, AES-256-GCM entschlüsseln, Flagge lesen.", 0.2),
    ],
)
