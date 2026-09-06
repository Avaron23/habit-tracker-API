from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, UserResponse, LoginResponse
from app.db.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):

    return await AuthService.register(user, db)


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):


    return await AuthService.login(
        UserCreate(
            username=form_data.username,
            password=form_data.password
        ),
        db
    )