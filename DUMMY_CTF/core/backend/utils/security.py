import os
from datetime import timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from fastapi_jwt import JwtAuthorizationCredentials
from fastapi_jwt.jwt import JwtAccessBearer



#Variables

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET not set in environment")

JWT_EXPIRY = timedelta(hours=int(os.getenv("JWT_EXPIRY_HOURS", 18)))

admin_secret = os.getenv("ADMIN_SECRET")
if not admin_secret:
    raise RuntimeError("ADMIN_SECRET not set in environment")



# JWT Access Handler

access_security = JwtAccessBearer(
    secret_key=JWT_SECRET,
    access_expires_delta=JWT_EXPIRY,
    auto_error=True
)



# Admin Token

admin_token_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)

async def require_admin_token(x_admin_token: str = Security(admin_token_header)):
    """Dependency to protect admin routes."""
    if x_admin_token != admin_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
