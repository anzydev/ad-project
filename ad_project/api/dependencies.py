"""Reusable API dependencies for authentication and authorization."""

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prisma import Prisma

from ad_project.api.config import Settings, get_settings
from ad_project.api.database import database_session
from ad_project.api.security import decode_access_token


bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    db: Prisma = Depends(database_session),
    settings: Settings = Depends(get_settings),
):
    """Resolve the authenticated user or return a safe 401 response."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        claims = decode_access_token(credentials.credentials, settings)
        user_id = claims.get("sub")
        if not user_id:
            raise ValueError("Missing subject")
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = await db.user.find_unique(where={"id": user_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return user


def require_admin(user):
    """Reject non-admin users at the authorization boundary."""
    if user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator role required")
    return user
