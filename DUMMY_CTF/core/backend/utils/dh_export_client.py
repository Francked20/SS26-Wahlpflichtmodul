"""HTTP client fuer die dynamic_check Delegation der day-4 (weak-DH) Tasks."""

import os

import httpx

_CHALLENGE_BASE_URL = os.getenv("CHALLENGE_BACKEND_URL", "http://challenge:8000")
_CHALLENGE_API_KEY = os.getenv("CHALLENGE_API_KEY")


async def check_dynamic_answer(dynamic_check: str, username: str, answer: str) -> bool:
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
