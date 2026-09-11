from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=30,  pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int 