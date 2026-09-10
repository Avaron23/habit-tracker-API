from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.habit import HabitCreate, HabitResponse
from app.models.user import User
from app.models.habit import Habit
from typing import List


class HabitService:

    # Добавление новой привычки
    @staticmethod
    async def create_habit(habit: HabitCreate, db: AsyncSession, current_user: User) -> HabitResponse:

        habit_data = habit.model_dump()

        habit_bd = Habit(user_id=current_user.id, **habit_data)

        db.add(habit_bd)

        await db.commit()
        await db.refresh(habit_bd)

        return HabitResponse.model_validate(habit_bd)


    # Получение всех привычек(для конкретного пользователя)
    @staticmethod
    async def get_habits(db: AsyncSession, current_user: User) -> List[HabitResponse]:

        result = await db.scalars(select(Habit).where(Habit.user_id == current_user.id))
        habits = result.all()

        return [HabitResponse.model_validate(habit) for habit in habits]


    # Получение привычки по её айди
    @staticmethod
    async def get_habit_by_id(habit_id: int, db: AsyncSession, current_user: User) -> HabitResponse:

        habit = await db.scalar(select(Habit).where(Habit.user_id == current_user.id).where(Habit.id == habit_id))

        if not habit:
            raise HTTPException(status_code=404, detail="Habit not found")

        return HabitResponse.model_validate(habit)