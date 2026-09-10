from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitResponse
from app.services.habit_service import HabitService
from typing import List


router = APIRouter(prefix="/habits", tags=["Habits"])


@router.post("/", response_model=HabitResponse)
async def create_habit(habit: HabitCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    return await HabitService.create_habit(habit, db, current_user)


@router.get("/", response_model=List[HabitResponse])
async def get_habits(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    return await HabitService.get_habits(db, current_user)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit_by_id(habit_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    return await HabitService.get_habit_by_id(habit_id, db, current_user)