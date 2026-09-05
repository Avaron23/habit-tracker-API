from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, UserResponse
from app.db.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):

    return await AuthService.register(user, db)