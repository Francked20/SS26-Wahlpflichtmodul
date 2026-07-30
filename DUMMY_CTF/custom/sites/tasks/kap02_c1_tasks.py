"""Tasks fuer Kapitel 02 - Kurs + Challenge 1"""

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
# KURS — Grundlagen (concept checks as individual Wahr/Falsch)
# ============================================================================

# 2.0 — DH principle, statement 1
task_02_00 = _wf(
    0, 5, "Kurs — DH-Prinzip (1/2)",
    "Wahr oder falsch?",
    "Bei Diffie-Hellman einigen sich Anna und Bob über einen unsicheren Kanal "
    "auf ein gemeinsames Geheimnis, ohne es je zu übertragen.",
    correct_is_true=True,
)

# 2.1 — DH principle, statement 2
task_02_01 = _wf(
    1, 5, "Kurs — DH-Prinzip (2/2)",
    "Wahr oder falsch?",
    "Öffentlich sichtbar sind p, g, A = g^a mod p und B = g^b mod p; geheim "
    "bleiben die Exponenten a und b.",
    correct_is_true=True,
)

# 2.2 — DLP, statement 1
task_02_02 = _wf(
    2, 5, "Kurs — Diskreter Logarithmus (1/2)",
    "Wahr oder falsch?",
    "Die modulare Exponentiation A = g^a mod p ist effizient berechenbar, "
    "die Umkehrung (aus A das a gewinnen) gilt jedoch als schwer.",
    correct_is_true=True,
)

# 2.3 — DLP, statement 2 (false one)
task_02_03 = _wf(
    3, 5, "Kurs — Diskreter Logarithmus (2/2)",
    "Wahr oder falsch?",
    "Der diskrete Logarithmus lässt sich für große, gut gewählte Parameter "
    "immer in konstanter Zeit berechnen.",
    correct_is_true=False,
)


# ============================================================================
# CHALLENGE 1 — Aufwärmen
# ============================================================================

# 2.4 — read the capture (proof question, common answer)
task_02_04 = TaskData(
    day=2, points=10, day_description="Diffie-Hellman",
    task_description="Challenge 1 — Die Capture", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("PARAM_P")],
    question=["Verschaffen Sie sich einen Überblick über Ihre Capture."],
    question_further=[
        "Laden Sie oben Ihre Challenge-1-Capture herunter. Die Datei ist im "
        "Klartext lesbar (KEY: WERT). Unter welchem Schlüsselwort steht die "
        "Primzahl p? Geben Sie den genauen Schlüsselnamen ein."
    ],
    placeholder_text=["Schlüsselname aus der Datei"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "Jede Zeile hat die Form KEY: WERT. Zeilen mit # sind Kommentare.", 0.7),
        TaskHint.create(0, "Der Schlüssel beginnt mit PARAM_ und enthält eine sehr große Zahl.", 0.4),
    ],
)

# 2.5 — the flag (unlocks Challenge 2 page)
task_02_05 = TaskData(
    day=2, points=20, day_description="Diffie-Hellman",
    task_description="Challenge 1 — Die Flagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{dh_warmup_discrete_log_c0ffee}")],
    question=["Brechen Sie Challenge 1 und reichen Sie die Flagge ein."],
    question_further=[
        "p ist klein (ca. 39 Bit). Lösen Sie g^a = A (mod p) per Brute-Force "
        "oder BSGS. Berechnen Sie s = B^a mod p, leiten Sie den Schlüssel ab "
        "(HKDF-SHA256, siehe Capture) und entschlüsseln Sie den AES-256-GCM-"
        "Datensatz. Die Flagge steht im Klartext. Mit dieser Flagge schalten "
        "Sie Challenge 2 frei."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "Bei so kleinem p können Sie alle a durchprobieren, bis g^a mod p = A.", 0.7),
        TaskHint.create(0, "shared_secret_bytes: s als Big-Endian, Länge ceil(bits(p)/8). Nutzen Sie 'cryptography' (HKDF, AESGCM).", 0.4),
        TaskHint.create(0, "Nonce und Ciphertext sind Base64. Nach dem Entschlüsseln: JSON mit Feld 'flag'.", 0.2),
    ],
)
