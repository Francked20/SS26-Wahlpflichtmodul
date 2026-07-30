"""Tasks fuer Kapitel 02 - Challenge 8 (Invalid Curve Attack)"""

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


def _jn(day_idx, points, desc, question, further, correct_is_yes):
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
# CHALLENGE 8 — Invalid Curve Attack
# ============================================================================

# 2.25 — concept: why the attack works (b not used in addition)
task_02_25 = _wf(
    25, 5, "Challenge 8 — Verständnis",
    "Wahr oder falsch?",
    "Der Parameter b kommt in den Additionsformeln einer elliptischen Kurve "
    "nicht vor. Daher merkt eine Implementierung, die eingehende Punkte nicht "
    "prüft, nicht, wenn ein Punkt in Wirklichkeit auf einer anderen (schwachen) "
    "Kurve E'(b') liegt.",
    correct_is_true=True,
)

# 2.26 — proof: is the first probe point on the REAL curve E? (common answer: Nein)
task_02_26 = _jn(
    26, 15, "Challenge 8 — Der falsche Punkt",
    "Prüfen Sie einen Sondenpunkt.",
    "Nehmen Sie aus Ihrer Capture den ersten Sondenpunkt P_0 = "
    "(PROBE_0_PX, PROBE_0_PY) und Bobs echte Kurve E mit den Parametern a, b, p "
    "(CURVE_A, CURVE_B, CURVE_P). Prüfen Sie die Kurvengleichung von E: Gilt "
    "y² ≡ x³ + a·x + b (mod p) für P_0? Liegt P_0 also auf Bobs echter Kurve? "
    "(Das ist der Kern des Angriffs.)",
    correct_is_yes=False,
)

# 2.27 — flag
task_02_27 = TaskData(
    day=2, points=45, day_description="Diffie-Hellman",
    task_description="Challenge 8 — Die Flagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{invalid_curve_bob_forgot_to_check_the_point_cr7}")],
    question=["Rekonstruieren Sie Bobs Schlüssel d und bergen Sie die Flagge."],
    question_further=[
        "Bobs echte Kurve E ist zu groß für einen direkten Angriff. Nutzen Sie "
        "die Sonden: Jede liefert einen Punkt P_i der kleinen Ordnung q_i "
        "(PROBE_i_Q) auf einer schwachen Kurve und Bobs Antwort R_i = d·P_i "
        "(PROBE_i_RX/RY). Lösen Sie in jeder kleinen Untergruppe R_i = d·P_i per "
        "BSGS -> d mod q_i. Achtung: ist R_i der Punkt im Unendlichen (0,0), so "
        "ist d ≡ 0 mod q_i. Kombinieren Sie alle d mod q_i per CRT zu d. Danach: "
        "S = d·A_eph (ALICE_EPH_AX/AY, auf der echten Kurve E), Schlüssel aus "
        "x(S) ableiten (HKDF-SHA256) und den AES-256-GCM-Datensatz entschlüsseln. "
        "Die gesamte Punktarithmetik läuft mit Bobs a (das b' der Sonden brauchen "
        "Sie nicht)."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "Für jede Sonde: kleiner BSGS in der Untergruppe der Ordnung q_i liefert d mod q_i. Rechnen Sie mit a der ECHTEN Kurve.", 0.7),
        TaskHint.create(0, "Ist PROBE_i_RX=0 und PROBE_i_RY=0, dann ist R_i = O (Unendlich), also d ≡ 0 (mod q_i).", 0.5),
        TaskHint.create(0, "CRT über alle (d mod q_i, q_i) ergibt d. Dann S = d·A_eph, key = HKDF(x(S)), AES-256-GCM entschlüsseln.", 0.2),
    ],
)
