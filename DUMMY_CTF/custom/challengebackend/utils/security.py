import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

challenge_api_key = os.getenv("CHALLENGE_API_KEY")
if not challenge_api_key:
    raise RuntimeError("CHALLENGE_API_KEY not set in environment")

challenge_api_key_header = APIKeyHeader(name="X-Challenge-Api-Key", auto_error=False)


async def require_challenge_api_key(x_challenge_api_key: str = Security(challenge_api_key_header)):
    """Schuetzt interne Endpunkte per API-Key"""
    if x_challenge_api_key != challenge_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Challenge-Api-Key",
        )
