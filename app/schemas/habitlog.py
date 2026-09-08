from pydantic import BaseModel
from datetime import datetime


class HabitLogCreate(BaseModel):
    habit_id: int


class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    date: datetime