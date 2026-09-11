from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.habitlog import HabitLogResponse
from app.db.db import get_db
from app.dependencies.auth import get_current_user
from app.services.habitlog_service import HabitLogService


router = APIRouter(prefix="/habitlogs", tags=["Habit Logs"])


@router.post("/{habit_id}", response_model=HabitLogResponse)
async def create_habit_log(habit_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    return await HabitLogService.create_habit_log(habit_id, db, current_user)


@router.get("/{habit_id}", response_model=list[HabitLogResponse])
async def get_habit_logs(habit_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    return await HabitLogService.get_habit_logs(habit_id, db, current_user)