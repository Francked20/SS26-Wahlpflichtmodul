"""HTTP client used by core/backend to delegate dynamic answer validation for
day-4 (weak-DH / Logjam) tasks to the custom challenge backend.

Mirrors the role of Jonas' utils/export_cipher_client.py. core's
Challenge.check_answer() calls check_dynamic_answer() whenever a task has a
dynamic_check set; this forwards username + answer to the `challenge` service,
which owns the per-user DH variant and does the actual comparison.

Place this at: core/backend/utils/dh_export_client.py
(or merge into an existing challenge-backend client module if you already have
one from Jonas' work).
"""

import os

import httpx

# The challenge backend is reachable on the internal docker network by service
# name. Same base other core->challenge calls use.
_CHALLENGE_BASE_URL = os.getenv("CHALLENGE_BACKEND_URL", "http://challenge:8000")
_CHALLENGE_API_KEY = os.getenv("CHALLENGE_API_KEY")  # optional; matches utils/security.py guard


async def check_dynamic_answer(dynamic_check: str, username: str, answer: str) -> bool:
    """Ask the challenge backend whether `answer` is correct for this user's
    variant and this stage. Returns False on any transport/HTTP error so a
    backend hiccup can't be mistaken for a correct solve."""
    headers = {}
    if _CHALLENGE_API_KEY:
        headers["X-Challenge-Api-Key"] = _CHALLENGE_API_KEY

    payload = {
        "dynamic_check": dynamic_check,
        "username": username,
        "answer": answer,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{_CHALLENGE_BASE_URL}/dh_export/check_answer",
                json=payload,
                headers=headers,
            )
        if resp.status_code != 200:
            return False
        return bool(resp.json().get("correct", False))
    except (httpx.HTTPError, ValueError):
        return False
