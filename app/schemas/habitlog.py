from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)
