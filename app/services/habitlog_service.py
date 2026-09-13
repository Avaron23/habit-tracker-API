from fastapi import HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.habitlog import HabitLog
from app.models.habit import Habit
from app.schemas.habitlog import HabitLogResponse
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


class HabitLogService:


    # Создание лога о выполнении привычки
    @staticmethod
    async def create_habit_log(habit_id: int, db: AsyncSession, current_user: User) -> HabitLogResponse:

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
        now_utc = datetime.now(timezone.utc)
        user_timezone = current_user.timezone

        now_local = now_utc.astimezone(ZoneInfo(user_timezone))

        if habit.period == "daily":
            start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif habit.period == "weekly":
            start = (now_local - timedelta(now_local.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = start + timedelta(days=7)
        elif habit.period == "monthly":
            start = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        else:
            raise HTTPException(status_code=400, detail="Unknown period")
        
        # 3. Переводим старт и енд обратно в utc
        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)

        # 4. Проверяем есть ли у этой привычки лог в данном периоде
        habitlog_exist = await db.scalar(
            select(HabitLog).
            where(HabitLog.habit_id == habit_id).
            where(HabitLog.date >= start_utc, HabitLog.date < end_utc)
        )

        if habitlog_exist:
            raise HTTPException(status_code=400, detail=f"Habit already logged for this {habit.period} period")

        # 5. Создаём новый хэбитлог и кидаем в БД
        habitlog_bd = HabitLog(habit_id=habit_id, date=now_utc)

        try:
            db.add(habitlog_bd)
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create habit log")

        # 6. Обновляем и возвращаем
        await db.refresh(habitlog_bd)
        return HabitLogResponse.model_validate(habitlog_bd)


    # Получение всех логов конкретной привычки
    @staticmethod
    async def get_habit_logs(habit_id: int, db: AsyncSession, current_user: User) -> list[HabitLogResponse]:

        # 1. Ищем привычку по юзеру, если нету выкидываем 404
        habit_exist = await db.scalar(
            select(Habit)
            .where(Habit.user_id==current_user.id)
            .where(Habit.id==habit_id)
        )

        if not habit_exist:
            raise HTTPException(status_code=404, detail="Habit not found")

        # 2. Получить все логи для этой привычки и вернуть их
        result = await db.scalars(select(HabitLog).where(HabitLog.habit_id==habit_id).order_by(desc(HabitLog.date)))
        habitlogs = result.all()

        return [HabitLogResponse.model_validate(habitlog) for habitlog in habitlogs]