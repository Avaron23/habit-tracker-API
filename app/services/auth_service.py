from app.schemas.user import UserCreate, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.user import User
from app.core.security import get_password_hash


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

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return UserResponse(db_user)