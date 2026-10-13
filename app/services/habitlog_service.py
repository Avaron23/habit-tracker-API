from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import Habit
from app.models.habitlog import HabitLog
from app.models.user import User
from app.schemas.habitlog import HabitLogResponse
from app.services.calculate_period_bounds import calculate_period_bounds
from app.services.get_now_utc import get_now_utc


class HabitLogService:
    # Создание лога о выполнении привычки
    @staticmethod
    async def create_habit_log(
        habit_id: int, db: AsyncSession, current_user: User
    ) -> HabitLogResponse:

        # 1. Ищем привычку и если ее нету выкидываем ошибку
        habit = await db.scalar(
            select(Habit)
            .where(Habit.user_id == current_user.id)
            .where(Habit.id == habit_id)
            .with_for_update()
        )

        if not habit:
            raise HTTPException(status_code=404, detail="Habit not found")

        # 2. Проверяем периодичность привычки и делаем тайм стампы для проверки существующего лога
        now_utc = get_now_utc()
        user_timezone = current_user.timezone

        times_info = calculate_period_bounds(now_utc, user_timezone, habit.period)

        start_utc = times_info["start"]
        end_utc = times_info["end"]

        # 4. Проверяем есть ли у этой привычки лог в данном периоде
        habitlog_exist = await db.scalar(
            select(HabitLog)
            .where(HabitLog.habit_id == habit_id)
            .where(HabitLog.date >= start_utc, HabitLog.date < end_utc)
        )

        if habitlog_exist:
            raise HTTPException(
                status_code=400,
                detail=f"Habit already logged for this {habit.period} period",
            )

        # 5. Создаём новый хэбитлог и кидаем в БД
        habitlog_bd = HabitLog(habit_id=habit_id, date=now_utc)

        try:
            db.add(habitlog_bd)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create habit log",
            )

        # 6. Обновляем и возвращаем
        await db.refresh(habitlog_bd)
        return HabitLogResponse.model_validate(habitlog_bd)

    # Получение всех логов конкретной привычки
    @staticmethod
    async def get_habit_logs(
        habit_id: int, db: AsyncSession, current_user: User, limit: int, offset: int
    ) -> list[HabitLogResponse]:

        # 1. Ищем привычку по юзеру, если нету выкидываем 404
        habit_exist = await db.scalar(
            select(Habit)
            .where(Habit.user_id == current_user.id)
            .where(Habit.id == habit_id)
        )

        if not habit_exist:
            raise HTTPException(status_code=404, detail="Habit not found")

        # 2. Получить все логи для этой привычки и вернуть их
        result = await db.scalars(
            select(HabitLog)
            .where(HabitLog.habit_id == habit_id)
            .order_by(desc(HabitLog.date))
            .limit(limit)
            .offset(offset)
        )
        habitlogs = result.all()

        return [HabitLogResponse.model_validate(habitlog) for habitlog in habitlogs]
