from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def current_user_info(current_user: User = Depends(get_current_user)):

    return current_user