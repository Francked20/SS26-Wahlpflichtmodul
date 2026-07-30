"""Tasks fuer Kapitel 02 - Challenge 9 (ElGamal) + Challenge 10 (DSA)"""

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
# CHALLENGE 9 — ElGamal reused nonce
# ============================================================================

# 2.28 — concept
task_02_28 = _wf(
    28, 5, "Challenge 9 — Verständnis",
    "Wahr oder falsch?",
    "Wird bei ElGamal derselbe Zufallswert k für zwei Nachrichten verwendet, so "
    "ist der Term y^k in beiden Chiffraten identisch — und die zweite Nachricht "
    "lässt sich aus der ersten (bekannten) rekonstruieren, ohne den diskreten "
    "Logarithmus zu lösen.",
    correct_is_true=True,
)

# 2.29 — proof: same c1 across both ciphertexts? (common answer: Ja)
task_02_29 = _jn(
    29, 15, "Challenge 9 — Das verräterische Zeichen",
    "Erkennen Sie den wiederverwendeten Nonce.",
    "Vergleichen Sie in Ihrer Capture MESSAGE1_C1 und MESSAGE2_C1. Sind die "
    "beiden Werte gleich? (Ein gemeinsames c1 = g^k beweist, dass beide "
    "Nachrichten denselben Zufallswert k benutzen.)",
    correct_is_yes=True,
)

# 2.30 — flag
task_02_30 = TaskData(
    day=2, points=35, day_description="Diffie-Hellman",
    task_description="Challenge 9 — Die Flagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{elgamal_nonce_reuse_two_ciphertexts_one_secret_a9f0}")],
    question=["Rekonstruieren Sie die geheime Nachricht und bergen Sie die Flagge."],
    question_further=[
        "Der Nonce k ist wiederverwendet (gleiches c1). Von Nachricht 1 kennen "
        "Sie den Klartext m1 (MESSAGE1_KNOWN_M1). Da y^k identisch ist, gilt: "
        "m2 = MESSAGE2_C2 · m1 · MESSAGE1_C2^(-1) mod p. Der so gewonnene Wert m2 "
        "ist das Schlüsselmaterial: Schlüssel = HKDF-SHA256(m2 als big-endian, "
        "ceil(bits(p)/8) Bytes). Entschlüsseln Sie damit den AES-256-GCM-"
        "Datensatz. Den diskreten Logarithmus brauchen Sie NICHT."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "m2 = c2_2 * m1 * inverse(c2_1) mod p. Alle drei Werte stehen in der Capture.", 0.7),
        TaskHint.create(0, "pow(c2_1, -1, p) liefert das Inverse. Dann m2 in Bytes wandeln (big-endian).", 0.4),
        TaskHint.create(0, "Schlüssel = HKDF-SHA256(m2-Bytes), dann AES-256-GCM mit RECORD_NONCE_B64 entschlüsseln.", 0.2),
    ],
)


# ============================================================================
# CHALLENGE 10 — DSA reused nonce (finale)
# ============================================================================

# 2.31 — concept
task_02_31 = _wf(
    31, 5, "Challenge 10 — Verständnis",
    "Wahr oder falsch?",
    "Werden zwei DSA-Signaturen mit demselben Nonce k erstellt, so ist r in "
    "beiden identisch, und aus den beiden Signaturen lässt sich zuerst k und "
    "dann der private Schlüssel x direkt berechnen.",
    correct_is_true=True,
)

# 2.32 — proof: same r across both signatures? (common answer: Ja)
task_02_32 = _jn(
    32, 15, "Challenge 10 — Das verräterische Zeichen",
    "Erkennen Sie den wiederverwendeten Nonce.",
    "Vergleichen Sie in Ihrer Capture SIG1_R und SIG2_R. Sind die beiden Werte "
    "gleich? (Ein gemeinsames r beweist, dass beide Signaturen denselben "
    "Zufallswert k benutzen — genau der Fehler, der die PS3 knackte.)",
    correct_is_yes=True,
)

# 2.33 — flag (final flag of the whole chapter)
task_02_33 = TaskData(
    day=2, points=50, day_description="Diffie-Hellman",
    task_description="Challenge 10 — Die Meisterflagge", error_cost=1,
    allow_reset=True, allow_random_order=False,
    allow_download=False, allow_link=False, allow_vscode=True,
    injectible=False, allow_kali=True, allow_cyber_range=False,
    master_task=False, task_type="input",
    answers=[Correct.create("hiy{dsa_nonce_reuse_ps3_style_private_key_recovery_beef}")],
    question=["Berechnen Sie den privaten Schlüssel und bergen Sie die letzte Flagge."],
    question_further=[
        "Beide Signaturen nutzen denselben Nonce (gleiches r). Berechnen Sie "
        "zuerst die Hashes: H(m) = SHA-256(Nachricht) mod q für beide Nachrichten "
        "(SIG1_MESSAGE_UTF8, SIG2_MESSAGE_UTF8; die UTF-8-Bytes hashen). Dann: "
        "k = (H(m1) - H(m2)) · (s1 - s2)^(-1) mod q, und daraus der private "
        "Schlüssel x = (s1·k - H(m1)) · r^(-1) mod q. Zuletzt: Schlüssel = "
        "HKDF-SHA256(x als big-endian, ceil(bits(q)/8) Bytes), AES-256-GCM "
        "entschlüsseln. Damit schließen Sie das gesamte Kapitel ab."
    ],
    placeholder_text=["hiy{...}"],
    download_text=[""], download_path=[""], link_text=[""], link_path=[""],
    hints=[
        TaskHint.create(0, "H(m) = int.from_bytes(sha256(msg).digest(),'big') % q. msg sind die UTF-8-Bytes der Nachricht.", 0.7),
        TaskHint.create(0, "k = (h1-h2) * pow(s1-s2, -1, q) % q. Dann x = (s1*k - h1) * pow(r, -1, q) % q.", 0.5),
        TaskHint.create(0, "Schlüssel = HKDF-SHA256(x-Bytes big-endian), dann AES-256-GCM mit RECORD_NONCE_B64 entschlüsseln.", 0.2),
    ],
)
