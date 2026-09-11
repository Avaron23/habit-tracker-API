from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, String, DateTime, func
from datetime import datetime


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(500))
    goal: Mapped[int] = mapped_column(Integer)
    period: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)