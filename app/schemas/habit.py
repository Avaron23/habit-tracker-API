from pydantic import BaseModel, ConfigDict
from datetime import datetime


class HabitCreate(BaseModel):
    user_id: int
    title: str
    description: str
    goal: int
    period: str


class HabitResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    goal: int
    period: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)