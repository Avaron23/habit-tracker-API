import asyncio
from app.db.db import engine
from app.db.base import Base

from app.models.user import User
from app.models.habit import Habit
from app.models.habitlog import Habitlog


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    asyncio.run(init_models())