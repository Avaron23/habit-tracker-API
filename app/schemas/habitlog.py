from pydantic import BaseModel
from datetime import datetime


class HabitlogCreate(BaseModel):
    habit_id: int


class HabitlogResponse(BaseModel):
    id: int
    habit_id: int
    date: datetime