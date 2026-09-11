from pydantic import BaseModel, ConfigDict
from datetime import datetime


class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)