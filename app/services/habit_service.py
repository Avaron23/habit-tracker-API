from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.habit import HabitCreate, HabitResponse
from app.models.user import User
from app.models.habit import Habit


class HabitService:

    @staticmethod
    async def create_habit(habit: HabitCreate, db: AsyncSession, current_user: User):

        habit_data = habit.model_dump()

        habit_bd = Habit(user_id=current_user.id, **habit_data)

        db.add(habit_bd)

        await db.commit()
        await db.refresh(habit_bd)

        return HabitResponse.model_validate(habit_bd)


    @staticmethod
    async def get_habits(db: AsyncSession, current_user: User):

        result = await db.scalars(select(Habit).where(Habit.user_id == current_user.id))
        habits = result.all()

        return [HabitResponse.model_validate(habit) for habit in habits]