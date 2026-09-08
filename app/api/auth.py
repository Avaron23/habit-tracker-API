from fastapi import APIRouter, Depends, Response, Cookie
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.db.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):

    return await AuthService.register(user, db)


@router.post("/login", response_model=TokenResponse)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):


    return await AuthService.login(
        response,
        UserCreate(
            username=form_data.username,
            password=form_data.password
        ),
        db,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(response: Response, refresh_token: str = Cookie(None), db: AsyncSession = Depends(get_db)):

    return await AuthService.refresh(response, refresh_token, db)


@router.post("/logout")
async def logout(response: Response, refresh_token: str = Cookie(None), db: AsyncSession = Depends(get_db)):

    return  await AuthService.logout(response, refresh_token, db)