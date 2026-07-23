"""Thin HTTP client for the day-3 export-cipher challenge chain. All the
actual crypto/variant-pool logic lives in custom/challengebackend now - this
service only resolves the JWT username and awards points, delegating the
actual answer check over the network. Same pattern already used for the
external Cyber-Range service in endpoints/cyberrange.py.
"""

import logging
import os
from typing import Optional

import httpx

CHALLENGE_BACKEND_URL = "http://challenge:8000"
CHALLENGE_API_KEY = os.getenv("CHALLENGE_API_KEY")
_HEADERS = {"X-Challenge-Api-Key": CHALLENGE_API_KEY}

logger = logging.getLogger("export-cipher-client")


async def check_dynamic_answer(dynamic_check: str, username: str, answer: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{CHALLENGE_BACKEND_URL}/export_cipher/check_answer",
                headers=_HEADERS,
                json={"dynamic_check": dynamic_check, "username": username, "answer": answer},
            )
    except httpx.HTTPError:
        logger.exception("Failed to reach challenge backend for check_answer - failing closed")
        return False

    if resp.status_code != 200:
        return False
    return resp.json().get("correct", False)


async def get_reveal_factor(username: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{CHALLENGE_BACKEND_URL}/export_cipher/reveal_factor/{username}",
                headers=_HEADERS,
            )
    except httpx.HTTPError:
        logger.exception("Failed to reach challenge backend for reveal_factor")
        return None

    if resp.status_code != 200:
        return None
    return resp.json().get("factor")
