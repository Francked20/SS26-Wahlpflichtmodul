import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

challenge_api_key = os.getenv("CHALLENGE_API_KEY")
if not challenge_api_key:
    raise RuntimeError("CHALLENGE_API_KEY not set in environment")

challenge_api_key_header = APIKeyHeader(name="X-Challenge-Api-Key", auto_error=False)


async def require_challenge_api_key(x_challenge_api_key: str = Security(challenge_api_key_header)):
    """Protects internal-only endpoints (core/backend -> this service calls,
    the VM companion script) - mirrors core/backend/utils/security.py's
    require_admin_token, just scoped to this service's own API key."""
    if x_challenge_api_key != challenge_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Challenge-Api-Key",
        )
