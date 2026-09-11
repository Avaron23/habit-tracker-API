from app.schemas.user import UserCreate, UserResponse, TokenResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException, Response
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.security import create_refresh_token, get_token_hash, get_password_hash, verify_password, create_access_token
from datetime import datetime, timedelta, timezone
from app.core.config import settings


class AuthService:


    @staticmethod
    async def register(user: UserCreate, db: AsyncSession) -> UserResponse:
        # Проверка на свободность логина
        # Получаем логин из бд
        existing_user = await db.scalar(select(User).where(User.username == user.username))

        # Если он существует то выкидываем ошибку
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        password_hash = get_password_hash(user.password)

        db_user = User(username=user.username, password_hash=password_hash)

        try:
            db.add(db_user)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(400, "Username already taken")
        
        await db.refresh(db_user)

        return UserResponse.model_validate(db_user)


    @staticmethod
    async def login(response: Response, user: UserCreate, db: AsyncSession) -> TokenResponse:
        # Получаем юзера из бд
        db_user = await db.scalar(select(User).where(User.username == user.username))

        # Если он не существует то выкидываем ошибку
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Проверяем пароль
        if not verify_password(user.password, db_user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        data = {
            "sub": str(db_user.id)
        }

        access_token = create_access_token(data)

        # Тут логика только для рефреш токена
        refresh_token = create_refresh_token()
        refresh_token_hash = get_token_hash(refresh_token)
        refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

        refresh_token_bd = RefreshToken(
            user_id=db_user.id,
            refresh_token_hash=refresh_token_hash,
            expires_at=refresh_token_expires
        )

        try:
            db.add(refresh_token_bd)
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(500, "Failed to refresh token")

        # Отправим рефреш токен в куки
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.secure_cookie, # if production then True
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60
        )

        return TokenResponse(access_token=access_token, token_type="bearer", expires_in=settings.access_token_expire_minutes*60)


    @staticmethod
    async def refresh(response: Response, refresh_token: str | None, db: AsyncSession) -> TokenResponse:
        # Проверяем передан ли рефреш токен
        if refresh_token is None:
                raise HTTPException(status_code=401, detail="Refresh token missing")

        # Хэшируем токен и ищем в бд
        refresh_token_hash = get_token_hash(refresh_token)

        refresh_token_bd = await db.scalar(select(RefreshToken).where(RefreshToken.refresh_token_hash == refresh_token_hash).with_for_update())

        if not refresh_token_bd or refresh_token_bd.revoked or datetime.now(timezone.utc) >= refresh_token_bd.expires_at:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        refresh_token_bd.revoked = True

        # Создаём новые токены
        access_token_data = {
            "sub": str(refresh_token_bd.user_id)
        }
        access_token = create_access_token(access_token_data)
        refresh_token_new = create_refresh_token()

        refresh_token_new_hash = get_token_hash(refresh_token_new)
        refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        # Создаём новую запись в бд
        refresh_token_new_bd = RefreshToken(
            user_id=refresh_token_bd.user_id,
            refresh_token_hash=refresh_token_new_hash,
            expires_at=refresh_token_expires
        )

        try:
            db.add(refresh_token_new_bd)
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(500, "Failed to refresh token")

        # Вовзращаем рефреш в куки а аксес в теле
        response.set_cookie(
            key="refresh_token",
            value=refresh_token_new,
            httponly=True,
            secure=settings.secure_cookie, # if production then True
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes*60
        )


    @staticmethod
    async def logout(response: Response, refresh_token: str | None, db: AsyncSession):

        # Проверяем передан ли рефреш токен
        if refresh_token is not None:

            refresh_token_hash = get_token_hash(refresh_token)

            refresh_token_bd = await db.scalar(select(RefreshToken).where(RefreshToken.refresh_token_hash == refresh_token_hash).with_for_update())

            if refresh_token_bd and not refresh_token_bd.revoked:
                
                refresh_token_bd.revoked = True
                await db.commit()

        response.delete_cookie(
            key="refresh_token",
            path="/",
            domain=None,
            secure=settings.secure_cookie, # if production then True
            httponly=True,
            samesite="lax"
        )

        return {"message": "Logout success"}