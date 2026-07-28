"""API-key protection for internal challenge-backend endpoints.

Provides a FastAPI dependency that guards internal routes with a shared secret
passed in the `X-Challenge-Api-Key` header. If no key is configured, the guard
is a no-op (development mode).
"""

import os

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

# Expected key, read once from the environment (None -> dev mode, guard disabled).
_challenge_api_key = os.getenv("CHALLENGE_API_KEY")
# Extract the key from the request header; auto_error=False so we control the response.
_api_key_header = APIKeyHeader(name="X-Challenge-Api-Key", auto_error=False)


async def require_challenge_api_key(x_challenge_api_key: str = Security(_api_key_header)):
    """Dependency protecting internal endpoints. No-op if CHALLENGE_API_KEY is
    unset (dev mode); enforces the header match if it is set."""
    if _challenge_api_key is None:
        return  # dev mode: internal network is trusted, no key configured
    if x_challenge_api_key != _challenge_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing challenge API key",
        )
