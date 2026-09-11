from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Literal


class HabitCreate(BaseModel):
    title: str = Field(min_length=1, max_length=30)
    description: str = Field(min_length=1, max_length=500)
    goal: int = Field(gt=0)
    period: Literal["daily", "weekly", "monthly"]


class HabitResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    goal: int
    period: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)