from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.habitlog import HabitLog
from app.models.habit import Habit
from app.schemas.habitlog import HabitLogResponse
from datetime import datetime, timedelta


class HabitLogService:


    # Создание лога о выполнении привычки
    @staticmethod
    async def create_habit_log(habit_id: int, db: AsyncSession, current_user: User):

        # 1. Ищем привычку и если ее нету выкидываем ошибку
        habit = await db.scalar(
            select(Habit)
            .where(Habit.user_id == current_user.id)
            .where(Habit.id == habit_id)
        )

        if not habit:
            raise HTTPException(status_code=404, detail="Habit not found")

        # 2. Проверяем периодичность привычки и делаем тайм стампы для проверки существующего лога
        # TODO: не готово пока
        pass

    # Получение всех логов конкретной привычки
    @staticmethod
    async def get_habit_logs(habit_id: int, db: AsyncSession, current_user: User):


        pass
    