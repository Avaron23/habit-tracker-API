from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.habitlog import HabitLogResponse
from app.services.habitlog_service import HabitLogService

router = APIRouter(prefix="/habitlogs", tags=["Habit Logs"])


@router.post("/{habit_id}", response_model=HabitLogResponse, status_code=status.HTTP_201_CREATED)
async def create_habit_log(
    habit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return await HabitLogService.create_habit_log(habit_id, db, current_user)


@router.get("/{habit_id}", response_model=list[HabitLogResponse])
async def get_habit_logs(
    habit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, gt=0, le=100),
    offset: int = Query(0, ge=0)
):

    return await HabitLogService.get_habit_logs(habit_id, db, current_user, limit, offset)
