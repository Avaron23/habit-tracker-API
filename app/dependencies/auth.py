from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.db.db import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from sqlalchemy import select
from jwt.exceptions import InvalidTokenError
import jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload.get("sub"))
        if not user_id:
            raise credentials_exception
    except (InvalidTokenError, TypeError, ValueError):
        raise credentials_exception

    user = await db.scalar(select(User).where(User.id == user_id))

    if not user:
        raise credentials_exception

    return user